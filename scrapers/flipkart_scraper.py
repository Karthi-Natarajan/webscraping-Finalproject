from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from textblob import TextBlob
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from html import unescape

from pymongo import MongoClient
import certifi
import random
import json
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================================
#           MONGODB ATLAS CONNECTION
# =========================================
MONGO_URL = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://skarthinatarajan21_db_user:skn212005@cluster0.ebtw7zu.mongodb.net/sentimentDB"
)

def get_mongodb_client():
    try:
        client = MongoClient(
            MONGO_URL,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None

# Initialize MongoDB connection
client = get_mongodb_client()
if client is None:
    print("❌ Failed to connect to MongoDB. Exiting...")
    exit(1)

db = client["sentiment_analysis_db"]
products_collection = db["products"]
reviews_collection = db["reviews"]

print("✅ Database collections ready")

# =========================================
#           SENTIMENT ANALYSIS
# =========================================
def analyze_sentiment(text):
    if not text or not text.strip():
        return "neutral"
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    except:
        return "neutral"


# =========================================
#             SELENIUM DRIVER
# =========================================
def init_driver(headless=False):
    opts = Options()
    
    # Specify your Chrome binary path
    chrome_binary = r"C:\Projects\FinalProjectCN\scrapers\143.0.7499.41\chrome.exe"
    if os.path.exists(chrome_binary):
        opts.binary_location = chrome_binary
        print(f"✅ Using Chrome binary: {chrome_binary}")
    
    if headless:
        opts.add_argument("--headless=new")
    
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--log-level=3")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-popup-blocking")
    
    # Stealth options
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    )
    
    # Find ChromeDriver manually (or specify path)
    chromedriver_path = None
    
    # Try to find chromedriver in common locations
    possible_paths = [
        r"C:\Projects\FinalProjectCN\scrapers\chromedriver.exe",
        r"C:\Users\Karthi Natarajan\Downloads\chromedriver.exe",
        os.path.join(os.getcwd(), "chromedriver.exe"),
        "chromedriver.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            chromedriver_path = path
            print(f"✅ Found ChromeDriver at: {path}")
            break
    
    if not chromedriver_path:
        # Download chromedriver automatically
        try:
            print("📥 ChromeDriver not found, attempting to download...")
            from webdriver_manager.chrome import ChromeDriverManager
            chromedriver_path = ChromeDriverManager().install()
            print(f"✅ Downloaded ChromeDriver to: {chromedriver_path}")
        except Exception as e:
            print(f"⚠️ Could not download ChromeDriver: {e}")
            print("⚠️ Please download ChromeDriver manually and place it in the script directory")
            print("⚠️ Download from: https://chromedriver.chromium.org/")
            raise
    
    # Create service
    service = Service(chromedriver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=opts)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.set_page_load_timeout(60)
        print("✅ ChromeDriver initialized successfully")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize ChromeDriver: {e}")
        
        # Try alternative approach without service
        try:
            print("🔄 Trying alternative driver initialization...")
            driver = webdriver.Chrome(options=opts)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_page_load_timeout(60)
            print("✅ ChromeDriver initialized (alternative method)")
            return driver
        except Exception as e2:
            print(f"❌ All driver initialization methods failed: {e2}")
            raise


def polite_sleep(a=1.0, b=2.0):
    time.sleep(random.uniform(a, b))


def close_initial_login_popup(driver):
    selectors = [
        "//button[text()='✕']",
        "//button[contains(@class,'_2KpZ6l _2doB4z')]",
        "//button[contains(@class,'_2doB4z')]"
    ]
    
    for selector in selectors:
        try:
            btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            driver.execute_script("arguments[0].click();", btn)
            print("🟢 Closed login popup")
            polite_sleep(1, 1.5)
            return True
        except:
            continue
    return False


def normalize_link(href, base_url="https://www.flipkart.com"):
    if not href:
        return None
    if href.startswith("//"):
        href = "https:" + href
    if href.startswith("/"):
        href = urljoin(base_url, href)
    return href.split("?")[0].split("#")[0]


def get_search_results_links(driver, max_links=5):
    polite_sleep(3, 4)
    
    links = []
    seen = set()
    
    # Multiple strategies to find product links
    strategies = [
        # Direct links
        "//a[contains(@href,'/p/') or contains(@href,'/itm/')]",
        # Links in product containers
        "//div[contains(@class,'_1AtVbE')]//a",
        "//div[contains(@class,'_4ddWXP')]//a",
        "//div[contains(@class,'_2kHMtA')]//a"
    ]
    
    for strategy in strategies:
        try:
            anchors = driver.find_elements(By.XPATH, strategy)
            for a in anchors[:20]:  # Limit to avoid too many
                try:
                    href = a.get_attribute("href")
                    normalized = normalize_link(href)
                    if normalized and ("/p/" in normalized or "/itm/" in normalized):
                        if normalized not in seen:
                            seen.add(normalized)
                            links.append(normalized)
                            if len(links) >= max_links:
                                break
                except:
                    continue
            if len(links) >= max_links:
                break
        except:
            continue
    
    print(f"🔗 Found {len(links)} product links")
    return links[:max_links]


def extract_json_ld(html):
    try:
        scripts = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.S | re.I,
        )
        for s in scripts:
            try:
                obj = json.loads(unescape(s).strip())
                if isinstance(obj, dict) and "Product" in str(obj.get("@type", "")):
                    return obj
                if isinstance(obj, list):
                    for o in obj:
                        if isinstance(o, dict) and "Product" in str(o.get("@type", "")):
                            return o
            except:
                continue
    except:
        pass
    return None


# =========================================
#              SCRAPER FUNCTION
# =========================================
def extract_product_info(driver, url, keyword):
    print(f"\n📦 Scraping: {url}")

    item = {
        "product_url": url,
        "keyword": keyword,
        "scrape_time": datetime.now(timezone.utc).isoformat(),
        "source": "flipkart",
        "product_title": "",
        "product_price": "",
        "product_rating": "",
        "reviews": []
    }

    try:
        driver.get(url)
        polite_sleep(4, 5)
        close_initial_login_popup(driver)

        html = driver.page_source
        jsonld = extract_json_ld(html)

        # JSON-LD INFO
        if jsonld:
            item["product_title"] = jsonld.get("name", "")
            offers = jsonld.get("offers", {})
            if isinstance(offers, dict):
                item["product_price"] = offers.get("price", "")
            elif isinstance(offers, list) and offers:
                item["product_price"] = offers[0].get("price", "")
            
            rating_block = jsonld.get("aggregateRating", {})
            if isinstance(rating_block, dict):
                item["product_rating"] = rating_block.get("ratingValue", "")

        # FALLBACK SELECTORS
        if not item["product_title"]:
            title_selectors = [
                "span.B_NuCI",
                "h1.VU-ZEz",
                "h1._2Kn22P",
                "h1._35KyD6",
                "h1._1y-9G2"
            ]
            for selector in title_selectors:
                try:
                    title_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    item["product_title"] = title_elem.text.strip()
                    if item["product_title"]:
                        break
                except:
                    continue

        if not item["product_price"]:
            price_selectors = [
                "div._30jeq3._16Jk6d",
                "div._25b18c",
                "div._30jeq3",
                "div._1vC4OE._3qQ9m1"
            ]
            for selector in price_selectors:
                try:
                    price_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    item["product_price"] = price_elem.text.strip()
                    if item["product_price"]:
                        break
                except:
                    continue

        if not item["product_rating"]:
            rating_selectors = [
                "div._3LWZlK",
                "div._2d4LTz",
                "span._2_R_DZ",
                "div._1lRcqv"
            ]
            for selector in rating_selectors:
                try:
                    rating_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    item["product_rating"] = rating_elem.text.strip()
                    if item["product_rating"]:
                        break
                except:
                    continue

        print(f"   📱 Title: {item['product_title'][:80]}...")
        print(f"   💰 Price: {item['product_price']}")
        print(f"   ⭐ Rating: {item['product_rating']}")

        # ===========================
        #   NAVIGATE TO REVIEWS PAGE
        # ===========================
        review_url = None
        
        # Try to find review link
        try:
            review_links = driver.find_elements(By.XPATH, 
                "//a[contains(@href,'product-reviews') or contains(@href,'reviews')]")
            if review_links:
                review_url = review_links[0].get_attribute("href")
                if review_url and not review_url.startswith("http"):
                    review_url = urljoin("https://www.flipkart.com", review_url)
        except:
            pass
        
        # Fallback: Construct review URL
        if not review_url and "/p/" in url:
            try:
                parts = url.split("/p/")
                if len(parts) > 1:
                    pid = parts[1].split("?")[0].split("/")[0]
                    review_url = f"{parts[0]}/product-reviews/{pid}"
            except:
                pass
        
        if review_url:
            print(f"   📝 Going to reviews page...")
            driver.get(review_url)
            polite_sleep(4, 5)
            close_initial_login_popup(driver)
        else:
            print("   ⚠️ Could not find reviews page")
            return item

        # ===========================
        #     REVIEW EXTRACTION
        # ===========================
        # Scroll to load more reviews
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            polite_sleep(2, 3)
        
        # Try multiple review container selectors
        review_blocks = []
        
        # Updated selectors for Flipkart
        container_selectors = [
            "div._27M-vq",
            "div.col._2wzgFH",
            "div._16PBlm",
            "div._1AtVbE",
            "div[class*='review']",
            "div[class*='Review']"
        ]
        
        for selector in container_selectors:
            try:
                blocks = driver.find_elements(By.CSS_SELECTOR, selector)
                if blocks:
                    # Filter by content
                    filtered = [b for b in blocks if len(b.text.strip()) > 30]
                    if filtered:
                        review_blocks = filtered
                        print(f"   ✅ Found {len(review_blocks)} review blocks")
                        break
            except:
                continue
        
        # If still not found, try generic approach
        if not review_blocks:
            try:
                # Look for elements containing star ratings
                all_elements = driver.find_elements(By.CSS_SELECTOR, "div, section, article")
                review_blocks = [el for el in all_elements 
                               if '★' in el.text or 'review' in el.text.lower()]
                if review_blocks:
                    print(f"   ✅ Found {len(review_blocks)} review blocks (generic)")
            except:
                print("   ⚠️ No review blocks found")

        # Parse each review block (limit to 10)
        max_reviews = 10
        for idx, rb in enumerate(review_blocks[:max_reviews]):
            try:
                review_text = rb.text.strip()
                if len(review_text) < 20:  # Too short, skip
                    continue
                
                review = {}
                
                # Extract rating (look for star symbols or numbers)
                rating_match = re.search(r'(\d+(\.\d+)?)\s*★', review_text)
                if rating_match:
                    review["rating"] = rating_match.group(1)
                else:
                    rating_match = re.search(r'Rating[:\s]*(\d+(\.\d+)?)', review_text, re.IGNORECASE)
                    if rating_match:
                        review["rating"] = rating_match.group(1)
                    else:
                        review["rating"] = "0"
                
                # Extract reviewer name (first line that looks like a name)
                lines = [line.strip() for line in review_text.split('\n') if line.strip()]
                reviewer_found = False
                for line in lines:
                    if (len(line) < 30 and 
                        line[0].isupper() and 
                        '★' not in line and 
                        'rating' not in line.lower() and
                        'review' not in line.lower()):
                        review["reviewer"] = line
                        reviewer_found = True
                        break
                
                if not reviewer_found:
                    review["reviewer"] = "Anonymous"
                
                # Get review text (longest paragraph)
                paragraphs = re.split(r'\n\s*\n', review_text)
                if paragraphs:
                    # Find the longest paragraph that's not the rating or name
                    longest = max(paragraphs, key=len)
                    if len(longest) > 10:
                        review["text"] = longest[:500]
                    else:
                        review["text"] = review_text[:500]
                else:
                    review["text"] = review_text[:500]
                
                # Only add if we have meaningful content
                if review.get("text", "").strip() and len(review["text"]) > 20:
                    review["sentiment"] = analyze_sentiment(review["text"])
                    review["review_id"] = f"{hash(url + review['reviewer'] + str(idx)) % 1000000}"
                    review["extracted_date"] = datetime.now(timezone.utc).isoformat()
                    
                    item["reviews"].append({
                        "review_id": review["review_id"],
                        "reviewer": review["reviewer"],
                        "rating": review["rating"],
                        "text": review["text"],
                        "sentiment": review["sentiment"],
                        "extracted_date": review["extracted_date"]
                    })
                    
                    print(f"   ✓ Review {idx+1}: {review['rating']}★ by {review['reviewer'][:20]}")
                    
            except Exception as e:
                print(f"   ✗ Skipping review {idx+1}")
                continue

        # ===========================
        #   OVERALL SENTIMENT
        # ===========================
        if item["reviews"]:
            pos = sum(1 for r in item["reviews"] if r["sentiment"] == "positive")
            neg = sum(1 for r in item["reviews"] if r["sentiment"] == "negative")
            neu = sum(1 for r in item["reviews"] if r["sentiment"] == "neutral")

            item["sentiment_summary"] = {
                "positive": pos,
                "negative": neg,
                "neutral": neu,
                "total": len(item["reviews"])
            }

            if pos > neg:
                item["overall_sentiment"] = "positive"
            elif neg > pos:
                item["overall_sentiment"] = "negative"
            else:
                item["overall_sentiment"] = "neutral"
            
            print(f"   📊 Extracted {len(item['reviews'])} reviews "
                  f"({pos} 👍, {neg} 👎, {neu} 😐)")
        else:
            item["sentiment_summary"] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
            item["overall_sentiment"] = "neutral"
            print("   📊 No reviews extracted")

    except Exception as e:
        print(f"❌ Error scraping: {e}")
        item["error"] = str(e)

    return item


# =========================================
#         SAVE TO MONGODB
# =========================================
def save_to_mongo(item):
    try:
        # Save product
        products_collection.update_one(
            {"product_url": item["product_url"]},
            {"$set": item},
            upsert=True
        )
        
        # Save individual reviews
        for review in item.get("reviews", []):
            review["product_url"] = item["product_url"]
            review["keyword"] = item.get("keyword", "")
            reviews_collection.update_one(
                {"review_id": review["review_id"]},
                {"$set": review},
                upsert=True
            )
        
        print(f"💾 Saved {len(item.get('reviews', []))} reviews")
        return True
    except Exception as e:
        print(f"❌ Failed to save: {e}")
        return False


# =========================================
#         CLEAR DATABASE (Optional)
# =========================================
def clear_collection():
    choice = input("Do you want to clear previous data? (y/n): ").lower().strip()
    if choice == 'y':
        print("🗑️ Clearing old data...")
        products_collection.delete_many({})
        reviews_collection.delete_many({})
        print("✅ Database cleared!")
    else:
        print("➡️ Keeping existing data")


# =========================================
#         MAIN SCRAPER
# =========================================
def run_scraper():
    # Get search query
    default_query = "iPhone 15"
    query = input(f"Enter product name to search (default: {default_query}): ").strip()
    if not query:
        query = default_query
    
    print(f"\n🔍 Searching Flipkart for: {query}")
    
    search_url = "https://www.flipkart.com/search?q=" + quote_plus(query)
    
    driver = None
    try:
        driver = init_driver(headless=False)
        
        driver.get(search_url)
        polite_sleep(5, 6)
        close_initial_login_popup(driver)
        
        # Get product links
        links = get_search_results_links(driver, max_links=3)
        
        if not links:
            print("❌ No products found")
            return
        
        print(f"\n📊 Found {len(links)} products to scrape")
        
        # Scrape each product
        all_results = []
        for i, url in enumerate(links, 1):
            print(f"\n{'='*50}")
            print(f"Product {i}/{len(links)}")
            print(f"{'='*50}")
            
            item = extract_product_info(driver, url, query)
            if save_to_mongo(item):
                all_results.append(item)
            
            polite_sleep(3, 4)
        
        # Print final summary
        print(f"\n{'='*60}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*60}")
        
        total_reviews = sum(len(r.get("reviews", [])) for r in all_results)
        print(f"✅ Products scraped: {len(all_results)}")
        print(f"✅ Total reviews extracted: {total_reviews}")
        
        for i, product in enumerate(all_results, 1):
            print(f"\nProduct {i}:")
            print(f"  Title: {product.get('product_title', 'N/A')[:60]}...")
            print(f"  Price: {product.get('product_price', 'N/A')}")
            print(f"  Rating: {product.get('product_rating', 'N/A')}")
            
            summary = product.get('sentiment_summary', {})
            print(f"  Reviews: {summary.get('total', 0)} "
                  f"(👍 {summary.get('positive', 0)} | "
                  f"👎 {summary.get('negative', 0)} | "
                  f"😐 {summary.get('neutral', 0)})")
        
        print(f"\n✅ All data saved to MongoDB Atlas")
        print(f"✅ Database: {db.name}")
        print(f"✅ Collections: {products_collection.name}, {reviews_collection.name}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print("\n✅ ChromeDriver closed")
            except:
                pass


# =========================================
#         DOWNLOAD CHROMEDRIVER
# =========================================
def download_chromedriver():
    """Helper function to download ChromeDriver if needed"""
    import zipfile
    import requests
    import stat
    
    print("🔄 Setting up ChromeDriver...")
    
    # ChromeDriver URL for Chrome 143
    chromedriver_url = "https://storage.googleapis.com/chrome-for-testing-public/143.0.7499.41/win64/chromedriver-win64.zip"
    
    try:
        # Download the ChromeDriver
        print("📥 Downloading ChromeDriver...")
        response = requests.get(chromedriver_url, stream=True)
        zip_path = "chromedriver.zip"
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        print("📦 Extracting ChromeDriver...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Find chromedriver.exe in the extracted files
        for root, dirs, files in os.walk("."):
            for file in files:
                if file == "chromedriver.exe":
                    chromedriver_path = os.path.join(root, file)
                    # Move to current directory
                    target_path = "chromedriver.exe"
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(chromedriver_path, target_path)
                    
                    # Make executable
                    os.chmod(target_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    
                    print(f"✅ ChromeDriver downloaded to: {target_path}")
                    return True
        
        print("❌ Could not find chromedriver.exe in extracted files")
        return False
        
    except Exception as e:
        print(f"❌ Failed to download ChromeDriver: {e}")
        return False


# =========================================
#         CHECK FOR CHROMEDRIVER
# =========================================
def check_chromedriver():
    """Check if ChromeDriver exists, download if not"""
    if os.path.exists("chromedriver.exe"):
        print("✅ ChromeDriver found in current directory")
        return True
    
    print("❌ ChromeDriver not found")
    choice = input("Do you want to download ChromeDriver automatically? (y/n): ").lower().strip()
    if choice == 'y':
        return download_chromedriver()
    else:
        print("⚠️ Please download ChromeDriver manually:")
        print("1. Go to: https://chromedriver.chromium.org/")
        print("2. Download version matching Chrome 143")
        print("3. Place chromedriver.exe in the same folder as this script")
        return False


# =========================================
#         MAIN EXECUTION
# =========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🛒 FLIPKART PRODUCT REVIEW SCRAPER")
    print("=" * 60)
    
    # Check for ChromeDriver
    if not check_chromedriver():
        print("❌ ChromeDriver is required. Exiting...")
        exit(1)
    
    # Optional: Clear database
    clear_collection()
    
    # Run the scraper
    run_scraper()
    
    print("\n" + "=" * 60)
    print("🎉 Scraping completed!")
    print("=" * 60)