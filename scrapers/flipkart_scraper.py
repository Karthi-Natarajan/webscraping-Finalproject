# scrapers/flipkart_scraper.py
import os
import time
import traceback
from urllib.parse import urljoin, quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup

def _build_driver(headless=True, timeout=30):
    """Build and configure Chrome driver for headless operation"""
    opts = Options()
    
    # Headless configuration for deployment
    if headless:
        opts.add_argument("--headless=new")
    
    # Essential arguments for deployment
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-features=VizDisplayCompositor")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--remote-debugging-port=9222")
    
    # User agent to mimic real browser
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    opts.add_argument(f"user-agent={user_agent}")
    
    # Additional options for better stealth
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument("--disable-blink-features")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    
    # For Heroku/Cloud deployment compatibility
    if os.environ.get('CHROME_BIN'):
        opts.binary_location = os.environ.get('CHROME_BIN')
    
    try:
        # Use webdriver_manager with ChromeType for compatibility
        service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
        driver = webdriver.Chrome(service=service, options=opts)
        
        # Execute CDP commands to avoid detection
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent + " HeadlessChrome"
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.set_page_load_timeout(timeout)
        driver.set_script_timeout(timeout)
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to build driver: {e}")
        raise

def _safe_wait_and_find(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    """Safe method to wait for and find an element"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except (TimeoutException, NoSuchElementException):
        return None

def _safe_click(driver, element):
    """Safely click an element using JavaScript"""
    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        try:
            element.click()
            return True
        except:
            return False

def _extract_review_data(block):
    """Extract review data from a review block"""
    try:
        # Author
        author_selectors = ["p._2sc7ZR", "p._2aFisS", "div._3n8G9a", "span._2aFisS"]
        author = None
        for sel in author_selectors:
            author = block.select_one(sel)
            if author:
                break
        author_text = author.get_text(strip=True) if author else "Anonymous"

        # Rating
        rating_selectors = ["div._3LWZlK", "div.MKiFS6", "div[data-star-rating]", "div.E_uFuv"]
        rating_el = None
        for sel in rating_selectors:
            rating_el = block.select_one(sel)
            if rating_el:
                break
        rating_text = rating_el.get_text(strip=True) if rating_el else "0"

        # Title
        title_selectors = ["p._2-N8zT", "p.qW2QI1", "p._2xg6Ul", "div._2sc7ZR._3Lx1Vf"]
        title_el = None
        for sel in title_selectors:
            title_el = block.select_one(sel)
            if title_el:
                break
        title_text = title_el.get_text(strip=True) if title_el else ""

        # Content
        content_selectors = ["div.t-ZTKy", "div[data-test='review-content']", 
                            "div._6K-7Co", "div.review-text", "div._2wLlW0"]
        content_el = None
        for sel in content_selectors:
            content_el = block.select_one(sel)
            if content_el:
                break
        
        content_text = ""
        if content_el:
            content_text = content_el.get_text(separator=" ", strip=True)
        else:
            # Fallback
            content_text = block.get_text(separator=" ", strip=True)
            # Clean up
            parts = content_text.split()
            if len(parts) > 100:  # If too long, take first 100 words
                content_text = " ".join(parts[:100]) + "..."

        # Clean rating text (keep only numbers)
        import re
        rating_numbers = re.findall(r'\d+\.?\d*', rating_text)
        rating_final = rating_numbers[0] if rating_numbers else "0"

        return {
            "author": author_text[:100],  # Limit author name length
            "rating": rating_final,
            "title": title_text[:200],    # Limit title length
            "text": content_text[:1000],  # Limit review text length
            "source": "flipkart"
        }
    except Exception as e:
        print(f"[ERROR] Failed to extract review data: {e}")
        return None

def scrape_flipkart_reviews(keyword, max_reviews=20, headless=True):
    """Main function to scrape Flipkart reviews - optimized for deployment"""
    result_meta = {"source": "flipkart", "url": None, "keyword": keyword}
    reviews = []
    driver = None
    
    try:
        print(f"[FLIPKART] Starting scrape for: {keyword} (headless={headless})")
        
        # Build driver
        driver = _build_driver(headless=headless)
        
        # Search URL
        search_url = f"https://www.flipkart.com/search?q={quote_plus(keyword)}"
        print(f"[FLIPKART] Navigating to: {search_url}")
        
        driver.get(search_url)
        time.sleep(3)  # Initial page load
        
        # Try to close popup if exists
        try:
            close_btn = _safe_wait_and_find(driver, "button._2KpZ6l._2doB4z", timeout=5)
            if close_btn:
                _safe_click(driver, close_btn)
                time.sleep(1)
        except:
            pass
        
        # Parse search results
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find product link
        product_selectors = [
            "a._1fQZEK", "a.CGtC98", "a.IRpwTa", "a.s1Q9rs",
            "a._2rpwqI", "a._1UoZlX", "a[href*='/p/']", "a[href*='/itm/']"
        ]
        
        product_link = None
        for selector in product_selectors:
            links = soup.select(selector)
            if links:
                for link in links:
                    href = link.get("href", "")
                    if href and ("/p/" in href or "/itm/" in href):
                        product_link = href
                        break
            if product_link:
                break
        
        if not product_link:
            print("[FLIPKART] No product found")
            return {"meta": result_meta, "reviews": reviews}
        
        # Construct full product URL
        if product_link.startswith("/"):
            product_url = urljoin("https://www.flipkart.com", product_link)
        else:
            product_url = product_link
        
        result_meta["url"] = product_url
        print(f"[FLIPKART] Product URL: {product_url}")
        
        # Navigate to product page
        driver.get(product_url)
        time.sleep(3)
        
        # Try to close popup on product page
        try:
            close_btn = _safe_wait_and_find(driver, "button._2KpZ6l._2doB4z", timeout=3)
            if close_btn:
                _safe_click(driver, close_btn)
                time.sleep(1)
        except:
            pass
        
        # Scroll to load content
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # Find reviews link
        review_url = None
        prod_soup = BeautifulSoup(driver.page_source, "html.parser")
        
        review_link_selectors = [
            "a[href*='/product-reviews/']",
            "a._3UAT2v",
            "div._3v8VuN a",
            "a[class*='review']"
        ]
        
        for selector in review_link_selectors:
            review_link = prod_soup.select_one(selector)
            if review_link:
                href = review_link.get("href", "")
                if href:
                    review_url = urljoin("https://www.flipkart.com", href)
                    break
        
        # Fallback: construct review URL from product URL
        if not review_url and "/p/" in product_url:
            base_url = product_url.split("?")[0]
            review_url = base_url.replace("/p/", "/product-reviews/")
        
        if not review_url:
            print("[FLIPKART] Could not find review URL")
            return {"meta": result_meta, "reviews": reviews}
        
        print(f"[FLIPKART] Review URL: {review_url}")
        
        # Navigate to reviews page
        driver.get(review_url)
        time.sleep(3)
        
        # Scroll to load more reviews
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {500 * (i+1)});")
            time.sleep(1.5)
        
        # Parse reviews
        page_soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find review blocks
        review_selectors = [
            "div._27M-vq",
            "div._16PBlm",
            "div.col._2wzgFH",
            "div.gtm58k",
            "div[data-id]"
        ]
        
        blocks = []
        for selector in review_selectors:
            blocks = page_soup.select(selector)
            if blocks:
                print(f"[FLIPKART] Found {len(blocks)} reviews with selector: {selector}")
                break
        
        # If no blocks found, try alternative approach
        if not blocks:
            all_divs = page_soup.select("div")
            blocks = []
            for div in all_divs:
                has_rating = div.select_one("div._3LWZlK, div.MKiFS6")
                has_text = div.select_one("div.t-ZTKy, div[class*='review']")
                if has_rating or has_text:
                    blocks.append(div)
            
            # Deduplicate
            unique_blocks = []
            for block in blocks:
                if block not in unique_blocks:
                    unique_blocks.append(block)
            blocks = unique_blocks
        
        # Extract review data
        review_count = 0
        for block in blocks:
            if review_count >= max_reviews:
                break
            
            review_data = _extract_review_data(block)
            if review_data:
                reviews.append(review_data)
                review_count += 1
        
        print(f"[FLIPKART] Successfully extracted {len(reviews)} reviews")
        
        # Update result meta
        result_meta.update({
            "success": True,
            "reviews_count": len(reviews),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return {"meta": result_meta, "reviews": reviews}
        
    except TimeoutException:
        print("[FLIPKART] Timeout error - page took too long to load")
        result_meta["error"] = "Timeout error - page took too long to load"
        return {"meta": result_meta, "reviews": reviews}
        
    except WebDriverException as e:
        print(f"[FLIPKART] WebDriver error: {e}")
        result_meta["error"] = f"WebDriver error: {str(e)}"
        return {"meta": result_meta, "reviews": reviews}
        
    except Exception as e:
        print(f"[FLIPKART] Unexpected error: {e}")
        traceback.print_exc()
        result_meta["error"] = f"Unexpected error: {str(e)}"
        return {"meta": result_meta, "reviews": reviews}
        
    finally:
        # Always quit driver
        if driver:
            try:
                driver.quit()
                print("[FLIPKART] Driver closed")
            except:
                pass