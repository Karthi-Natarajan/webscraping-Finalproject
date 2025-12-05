# complete_flipkart_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import json
from datetime import datetime
import os

print("=" * 70)
print("🚀 FLIPKART REVIEW SCRAPER - ALL PRODUCTS")
print("=" * 70)

# ALL PRODUCT URLs
PRODUCTS = [
    # 📱 MOBILES
    {
        'name': 'iPhone 15 Blue 128GB',
        'url': 'https://www.flipkart.com/apple-iphone-15-blue-128-gb/product-reviews/itmbf14ef54f645d?pid=MOBGTAGPAQNVFZZY'
    },
    {
        'name': 'iPhone 17 Pro Silver 256GB',
        'url': 'https://www.flipkart.com/apple-iphone-17-pro-silver-256-gb/product-reviews/itm106f475c264c7?pid=MOBHFN6YPFSDYRTY'
    },
    {
        'name': 'Samsung Galaxy S24 Ultra Titanium Black 256GB',
        'url': 'https://www.flipkart.com/samsung-galaxy-s24-ultra-5g-titanium-black-256-gb/product-reviews/itm60d6a4ba69e8c?pid=MOBGX2F3QGZYYZAK'
    },
    {
        'name': 'OnePlus Nord CE4 Lite 5G Super Silver 128GB',
        'url': 'https://www.flipkart.com/oneplus-nord-ce4-lite-5g-super-silver-128-gb/product-reviews/itm8fd5fdf300955?pid=MOBH25ZDPHNF38XJ'
    },
    {
        'name': 'Vivo T4x 5G Marine Blue 128GB',
        'url': 'https://www.flipkart.com/vivo-t4x-5g-marine-blue-128-gb/product-reviews/itm017656bdd097b?pid=MOBH9JUSTWEMVADU'
    },
    {
        'name': 'Redmi Note 14 SE 5G Crimson Art 128GB',
        'url': 'https://www.flipkart.com/redmi-note-14-se-5g-crimson-art-128-gb/product-reviews/itm10fbd7f3a50f1?pid=MOBHE48SXCFFFTTT'
    },
    {
        'name': 'Realme P3X 5G Midnight Blue 128GB',
        'url': 'https://www.flipkart.com/realme-p3x-5g-midnight-blue-128-gb/product-reviews/itmab5a4b09b6ccc?pid=MOBH8VGV88UADK2Z'
    },
    {
        'name': 'Motorola G57 Power 5G Pantone Regatta 128GB',
        'url': 'https://www.flipkart.com/motorola-g57-power-5g-pantone-regatta-128-gb/product-reviews/itmaea0032ab54ab?pid=MOBHGRFEGSFYUE2E'
    },
    {
        'name': 'Nothing Phone 3A Black 256GB',
        'url': 'https://www.flipkart.com/nothing-phone-3a-black-256-gb/product-reviews/itm49557c5a65f9c?pid=MOBH8G3PJJMGUFGH'
    },
    {
        'name': 'Google Pixel 10 Frost 256GB',
        'url': 'https://www.flipkart.com/google-pixel-10-frost-256-gb/product-reviews/itm180af25bcc197?pid=MOBHEXHRXDGMF8XZ'
    },
    {
        'name': 'Poco C75 5G Aqua Bliss 64GB',
        'url': 'https://www.flipkart.com/poco-c75-5g-aqua-bliss-64-gb/product-reviews/itm10b3f6f1bc616?pid=MOBH7443MMBCWPPG'
    },
    # 💻 LAPTOPS
    {
        'name': 'HP Intel Core i3 13th Gen Laptop',
        'url': 'https://www.flipkart.com/hp-intel-core-i3-13th-gen-1315u-8-gb-512-gb-ssd-windows-11-home-15-fd0568tu-thin-light-laptop/product-reviews/itm033c840630887?pid=COMHBFRJZKHTQSKM'
    },
    {
        'name': 'Dell Vostro 3530 Intel Core i5 Laptop',
        'url': 'https://www.flipkart.com/dell-15-intel-core-i5-13th-gen-16-gb-512-gb-ssd-windows-11-home-vostro-3530-rpl-laptop/product-reviews/itm131ebb1b7cdce?pid=COMHBG6HU7GJGR8G'
    },
    {
        'name': 'Lenovo Chromebook Mediatek Kompanio 520',
        'url': 'https://www.flipkart.com/lenovo-chromebook-mediatek-kompanio-520-4-gb-128-gb-emmc-storage-chrome-os-14m868/product-reviews/itm4dc67999fe3de?pid=COMGSYYSHRSUEGMG'
    },
    {
        'name': 'Apple MacBook Air M4 16GB 256GB',
        'url': 'https://www.flipkart.com/apple-macbook-air-m4-16-gb-256-gb-ssd-macos-sequoia-mw0y3hn-a/product-reviews/itmad81d112ad068?pid=COMH9ZWQXZHDDRGZ'
    },
    {
        'name': 'Samsung Galaxy Book4 Intel Core i3',
        'url': 'https://www.flipkart.com/samsung-galaxy-book4-metal-intel-core-i3-13th-gen-1315u-8-gb-512-gb-ssd-windows-11-home-np750xgj-lg9in-thin-light-laptop/product-reviews/itmc29d559898e6f?pid=COMH4Y6KKRC9YSWE'
    },
    # 🎧 ACCESSORIES
    {
        'name': 'Boat Rockerz 425 Bluetooth Headphones',
        'url': 'https://www.flipkart.com/boat-rockerz-425-25h-battery-beast-mode-enx-dual-pair-stream-ad-free-music-via-app-bluetooth/product-reviews/itme2d3b64d9891b?pid=ACCG8MXCJKCFHA7X'
    },
    {
        'name': 'Sony WH-CH520 Bluetooth Headphones',
        'url': 'https://www.flipkart.com/sony-wh-ch520-50-hrs-playtime-dsee-upscale-multipoint-connection-dual-pairing-bluetooth/product-reviews/itmf3323e4dd1211?pid=ACCGZ4MAJXCC8ED8'
    },
    {
        'name': 'Mi 20000 mAh 33W Power Bank',
        'url': 'https://www.flipkart.com/mi-20000-mah-33-w-power-bank/product-reviews/itme2dae8e64d942?pid=PWBH3VWYZDWTYBYS'
    }
]

def setup_driver():
    """Setup Chrome driver"""
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    
    # Optional: Run in headless mode (faster, no browser window)
    # options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Hide selenium
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    return driver

def scrape_product_reviews(product_url, product_name):
    """Scrape reviews for a single product"""
    print(f"\n📱 Product: {product_name}")
    print(f"🔗 URL: {product_url}")
    
    driver = setup_driver()
    all_reviews = []
    
    try:
        # Open the page
        driver.get(product_url)
        time.sleep(4)
        
        # Scroll to load more reviews
        for i in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
        
        # Wait for content to load
        time.sleep(2)
        
        # ============================================
        # EXTRACT REVIEWS USING WORKING SELECTORS
        # ============================================
        
        reviews_data = []
        
        # Method 1: Try the working selector
        try:
            review_containers = driver.find_elements(By.CSS_SELECTOR, "div.gMdEY7")
            if review_containers:
                print(f"✅ Found {len(review_containers)} review containers")
                
                for container in review_containers:
                    try:
                        # Get all text from container
                        text = container.text.strip()
                        
                        if text and len(text) > 50:  # Ensure it's a review
                            reviews_data.append(text)
                    except:
                        continue
        except:
            pass
        
        # Method 2: Alternative selector
        if not reviews_data:
            try:
                review_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'col')]")
                for elem in review_elements:
                    text = elem.text.strip()
                    if text and len(text) > 50 and ('★' in text or 'star' in text.lower()):
                        reviews_data.append(text)
            except:
                pass
        
        # Method 3: Get all divs with reasonable text
        if not reviews_data:
            try:
                all_divs = driver.find_elements(By.TAG_NAME, "div")
                for div in all_divs:
                    text = div.text.strip()
                    if 50 < len(text) < 500:  # Reasonable length for a review
                        reviews_data.append(text)
            except:
                pass
        
        # Process extracted reviews
        for idx, review_text in enumerate(reviews_data[:15]):  # Limit to 15 per product
            try:
                # Extract rating
                rating = "0"
                if '5★' in review_text or '★★★★★' in review_text or '5 star' in review_text.lower():
                    rating = "5"
                elif '4★' in review_text or '★★★★' in review_text or '4 star' in review_text.lower():
                    rating = "4"
                elif '3★' in review_text or '★★★' in review_text or '3 star' in review_text.lower():
                    rating = "3"
                elif '2★' in review_text or '★★' in review_text or '2 star' in review_text.lower():
                    rating = "2"
                elif '1★' in review_text or '★' in review_text or '1 star' in review_text.lower():
                    rating = "1"
                
                # Extract date
                date = ""
                date_patterns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                                '2023', '2024', '2025', 'days ago', 'month ago', 'year ago']
                lines = review_text.split('\n')
                for line in lines:
                    if any(pattern in line for pattern in date_patterns):
                        date = line.strip()
                        break
                
                # Extract reviewer
                reviewer = "Customer"
                for line in lines:
                    if 'certified' in line.lower() or 'buyer' in line.lower():
                        reviewer = line.strip()
                        break
                
                # Check if verified
                verified = "No"
                if 'certified' in review_text.lower() or 'verified' in review_text.lower():
                    verified = "Yes"
                
                # Create review object
                review = {
                    'product_name': product_name,
                    'product_url': product_url,
                    'review_id': f"{product_name[:10].replace(' ', '_')}_{idx}_{int(time.time())}",
                    'rating': rating,
                    'review_text': review_text[:300],  # Limit text length
                    'reviewer': reviewer,
                    'date': date,
                    'verified': verified,
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                all_reviews.append(review)
                
            except Exception as e:
                print(f"  ⚠️ Error processing review {idx+1}: {e}")
                continue
        
        print(f"✅ Extracted {len(all_reviews)} reviews")
        return all_reviews
        
    except Exception as e:
        print(f"❌ Error scraping {product_name}: {e}")
        return []
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    """Main scraping function"""
    print(f"📦 Total Products: {len(PRODUCTS)}")
    
    # Ask user
    choice = input("\nHow many products to scrape? (Enter number or 'all'): ").strip().lower()
    
    if choice == 'all':
        products_to_scrape = PRODUCTS
    else:
        try:
            num = int(choice)
            products_to_scrape = PRODUCTS[:num]
        except:
            print("⚠️ Invalid input. Scraping all products.")
            products_to_scrape = PRODUCTS
    
    print(f"\n🎯 Scraping {len(products_to_scrape)} products...")
    
    all_reviews = []
    failed_products = []
    
    # Scrape each product
    for idx, product in enumerate(products_to_scrape, 1):
        print(f"\n{'='*60}")
        print(f"[{idx}/{len(products_to_scrape)}] Processing: {product['name']}")
        print(f"{'='*60}")
        
        try:
            reviews = scrape_product_reviews(product['url'], product['name'])
            
            if reviews:
                all_reviews.extend(reviews)
                print(f"✅ Added {len(reviews)} reviews")
            else:
                failed_products.append(product['name'])
                print(f"⚠️ No reviews found")
            
            # Wait between products (to avoid blocking)
            if idx < len(products_to_scrape):
                wait_time = random.randint(3, 7)
                print(f"⏳ Waiting {wait_time} seconds before next product...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_products.append(product['name'])
            continue
    
    # Save results
    if all_reviews:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_file = f"flipkart_all_reviews_{timestamp}.csv"
        df = pd.DataFrame(all_reviews)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 CSV saved: {csv_file} ({len(df)} rows)")
        
        # Save to Excel
        excel_file = csv_file.replace('.csv', '.xlsx')
        try:
            df.to_excel(excel_file, index=False)
            print(f"💾 Excel saved: {excel_file}")
        except:
            print("ℹ️ Excel export skipped (install openpyxl: pip install openpyxl)")
        
        # Save to JSON
        json_file = csv_file.replace('.csv', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON saved: {json_file}")
        
        # Show statistics
        print(f"\n📊 STATISTICS:")
        print(f"   Total reviews collected: {len(all_reviews)}")
        print(f"   Successful products: {len(products_to_scrape) - len(failed_products)}/{len(products_to_scrape)}")
        
        if failed_products:
            print(f"\n⚠️ Failed products:")
            for product in failed_products:
                print(f"   - {product}")
        
        # Show sample data
        print(f"\n🎯 SAMPLE REVIEWS:")
        for i, review in enumerate(all_reviews[:3], 1):
            print(f"\n{i}. {review['product_name']}")
            print(f"   Rating: {review['rating']}/5")
            print(f"   Reviewer: {review['reviewer']}")
            print(f"   Date: {review['date']}")
            print(f"   Preview: {review['review_text'][:80]}...")
        
        # Open file location
        print(f"\n📂 Files saved in: {os.getcwd()}")
        
    else:
        print("\n❌ No reviews were collected!")
        if failed_products:
            print("Failed products:")
            for product in failed_products:
                print(f"  - {product}")

if __name__ == "__main__":
    # Check dependencies
    try:
        from selenium import webdriver
        import pandas as pd
    except ImportError:
        print("❌ Missing packages. Install with:")
        print("pip install selenium pandas webdriver-manager")
        exit(1)
    
    main()