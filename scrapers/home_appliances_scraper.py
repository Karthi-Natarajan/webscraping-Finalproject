# home_appliances_shoes_scraper.py
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
print("🏠👟 FLIPKART PHASE 2 - HOME APPLIANCES & SHOES")
print("=" * 70)

# HOME APPLIANCES
HOME_APPLIANCES = [
    # 🏠 REFRIGERATORS
    {
        'name': 'LG 260 L 3 Star Smart Inverter Frost-Free Double Door Refrigerator',
        'url': 'https://www.flipkart.com/lg-260-l-frost-free-double-door-2-star-convertible-refrigerator/p/itm283448defc119?pid=RFRFPHH7WXMP36ZF'
    },
    {
        'name': 'Samsung 253 L 3 Star Inverter Frost-Free Double Door Refrigerator',
        'url': 'https://www.flipkart.com/samsung-253-l-frost-free-double-door-2-star-refrigerator-base-drawer/p/itm0db5d6f4f8411?pid=RFRFZGJC4EW7PSTH'
    },
    {
        'name': 'Whirlpool 265 L 3 Star Inverter Frost-Free Double Door Refrigerator',
        'url': 'https://www.flipkart.com/whirlpool-265-l-frost-free-double-door-2-star-refrigerator/p/itmc4fa0d0fb434f?pid=RFRFZRNHHNHCVPZH'
    },
    # 🌀 AIR CONDITIONERS
    {
        'name': 'Voltas 1.5 Ton 3 Star Split Inverter AC',
        'url': 'https://www.flipkart.com/voltas-2024-model-1-5-ton-3-star-split-inverter-ac-white/p/itmee86accb4f614?pid=ACNGYPU5FPG9ZSJM'
    },
    {
        'name': 'LG 1.5 Ton 5 Star AI DUAL Inverter Split AC',
        'url': 'https://www.flipkart.com/lg-ai-convertible-6-in-1-cooling-2024-model-1-5-ton-5-star-split-dual-inverter-4-way-swing-hd-filter-anti-virus-protection-viraat-mode-adc-sensor-ac-white/p/itm335feed041afb?pid=ACNGX8JPHYYXJGSX'
    },
    {
        'name': 'Daikin 1.5 Ton 3 Star Inverter Split AC',
        'url': 'https://www.flipkart.com/daikin-2025-model-1-5-ton-3-star-split-inverter-ac-pm-2-5-filter-white/p/itm1d4c83331bf3a?pid=ACNHA7H3HAJS53EK'
    },
    # 🧺 WASHING MACHINES
    {
        'name': 'Samsung 7 kg Fully Automatic Top Load Washing Machine',
        'url': 'https://www.flipkart.com/samsung-7-kg-5-star-ecobubble-digital-inverter-fully-automatic-top-load-washing-machine-grey/p/itmfad620b791ea9?pid=WMNGGUWZK6VEQPXD'
    },
    {
        'name': 'LG 8 kg Fully Automatic Front Load Washing Machine',
        'url': 'https://www.flipkart.com/lg-8-kg-5-star-ai-direct-drive-technology-steam-6-motion-dd-fully-automatic-front-load-washing-machine-black/p/itm8c7244dbd53db?pid=WMNGPYWTTKRNGB5R'
    },
    {
        'name': 'Whirlpool 8 kg Fully Automatic Top Load Washing Machine',
        'url': 'https://www.flipkart.com/whirlpool-8-kg-fully-automatic-top-load-washing-machine-in-built-heater-grey/p/itm9fe0dcaaaf7bf?pid=WMNGVNUZPFXRCJAZ'
    },
    # 🍳 KITCHEN APPLIANCES
    {
        'name': 'Philips Air Fryer HD9252/90',
        'url': 'https://www.flipkart.com/philips-hd9252-90-touch-panel-uses-up-90-less-fat-7-pre-set-menu-1400w-4-1-ltr-rapid-air-technology-fryer/p/itmc4150617ed082?pid=AFRG6FGVVAAZVNXS'
    },
    {
        'name': 'Butterfly Rapid Plus Wet Grinder',
        'url': 'https://www.flipkart.com/butterfly-rapid-plus-wet-grinder-coconut-scraper-blue/p/itm579412e45a359?pid=WTGFGMHH9A2Z32VH'
    },
    {
        'name': 'Pigeon Stovekraft Electric Kettle',
        'url': 'https://www.flipkart.com/pigeon-stovekraft-hot-electric-kettle/p/itm678143060cbce?pid=EKTG6Y4PH5HMGQ8Q'
    }
]

# SHOES
SHOES = [
    # 👟 SPORTS SHOES
    {
        'name': 'Nike Revolution 7 Running Shoes',
        'url': 'https://www.flipkart.com/nike-revolution-7-running-shoes-men/p/itm2deb54755755b?pid=SHOHG6ZVCHKHZFTG'
    },
    {
        'name': 'Adidas Grand Court 2.0 Running Shoes',
        'url': 'https://www.flipkart.com/adidas-grand-court-2-0-running-shoes-men/p/itm0e9992225ff3f?pid=SHOGW4GZ4ZZ7E7QB'
    },
    {
        'name': 'Puma Retaliate 3 Running Shoes',
        'url': 'https://www.flipkart.com/puma-retaliate-3-res-running-shoes-men/p/itm10e7e03a67194?pid=SHOHDMNNZVW3P58D'
    },
    # 👞 CASUAL SHOES
    {
        'name': 'Red Tape Leather High Top Boots',
        'url': 'https://www.flipkart.com/red-tape-men-s-leather-high-top-boots-everyday-style-men/p/itm9fb88fc6bb4a6?pid=SHOHFSC5MVRNZ8MA'
    },
    {
        'name': 'Bata Walking Shoes',
        'url': 'https://www.flipkart.com/bata-walking-shoes-stylish-jogging-slip-sneakers-men/p/itma1b54d8f9f8d3?pid=SHOG8ZG4GUFWKY4V'
    },
    {
        'name': 'Sparx SM-414 Running Shoes',
        'url': 'https://www.flipkart.com/sparx-sm-414-running-shoes-men/p/itme72bb2973fb42?pid=SHOFW2VU5F8C6MXW'
    },
    # 👠 FORMAL SHOES
    {
        'name': 'Woodland Casuals Formal Shoes',
        'url': 'https://www.flipkart.com/woodland-casuals-men/p/itma9b3975158c59?pid=SHOH78SJFYVKGGF6'
    },
    {
        'name': 'Liberty Fortune Formal Shoes',
        'url': 'https://www.flipkart.com/liberty-fortune-hol-125e-formal-shoes-pu-sole-lightweight-comfortable-lacing-brogues-men/p/itm55881dbe132db?pid=SHOGM6VK2GRSA5TG'
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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    return driver

def scrape_product_reviews(product_url, product_name, category):
    """Scrape reviews for a single product"""
    print(f"\n📦 Category: {category}")
    print(f"🏷️  Product: {product_name[:60]}...")
    print(f"🔗 URL: {product_url[:80]}...")
    
    driver = setup_driver()
    all_reviews = []
    
    try:
        # Open the page
        driver.get(product_url)
        time.sleep(5)
        
        # Scroll to load content
        for i in range(3):
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)
        
        # Try to find and click reviews tab
        try:
            review_tabs = driver.find_elements(By.XPATH, "//div[contains(text(), 'Reviews') or contains(text(), 'REVIEWS')]")
            for tab in review_tabs:
                if tab.is_displayed():
                    tab.click()
                    time.sleep(3)
                    break
        except:
            pass
        
        # Try multiple selectors for reviews
        reviews_data = []
        
        # Method 1: Try common review containers
        selectors = [
            "div._2wzgFH",
            "div._1AtVbE",
            "div.t-ZTKy",
            "div.row",
            "div.col",
            "div.review"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 30 and '★' in text:
                            reviews_data.append(text)
                    break
            except:
                continue
        
        # Method 2: Get all text from page and filter
        if len(reviews_data) < 5:
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                lines = page_text.split('\n')
                for line in lines:
                    if 50 < len(line) < 500:
                        if '★' in line or 'excellent' in line.lower() or 'good' in line.lower():
                            reviews_data.append(line)
            except:
                pass
        
        # Process reviews
        unique_reviews = []
        seen_texts = set()
        
        for review_text in reviews_data:
            if review_text and review_text not in seen_texts:
                seen_texts.add(review_text)
                unique_reviews.append(review_text)
        
        for idx, review_text in enumerate(unique_reviews[:15]):  # Max 15 per product
            try:
                # Extract rating
                rating = "0"
                if '5★' in review_text[:50] or '★★★★★' in review_text[:50]:
                    rating = "5"
                elif '4★' in review_text[:50] or '★★★★' in review_text[:50]:
                    rating = "4"
                elif '3★' in review_text[:50] or '★★★' in review_text[:50]:
                    rating = "3"
                elif '2★' in review_text[:50] or '★★' in review_text[:50]:
                    rating = "2"
                elif '1★' in review_text[:50] or '★' in review_text[:50]:
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
                        reviewer = line.strip().replace('READ MORE', '').replace('...', '')
                        break
                
                # Check if verified
                verified = "No"
                if 'certified' in review_text.lower() or 'verified' in review_text.lower():
                    verified = "Yes"
                
                # Create review
                review = {
                    'category': category,
                    'product_name': product_name,
                    'product_url': product_url,
                    'rating': rating,
                    'review_text': review_text[:500].replace('\n', ' ').strip(),
                    'reviewer': reviewer[:100],
                    'date': date[:50],
                    'verified': verified,
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                all_reviews.append(review)
                
            except Exception as e:
                continue
        
        print(f"✅ Extracted {len(all_reviews)} reviews")
        return all_reviews
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return []
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    """Main scraping function"""
    print(f"\n📊 PRODUCT STATISTICS:")
    print(f"🏠 Home Appliances: {len(HOME_APPLIANCES)} products")
    print(f"👟 Shoes: {len(SHOES)} products")
    print(f"📦 Total: {len(HOME_APPLIANCES) + len(SHOES)} products")
    
    print("\n📋 SELECT OPTION:")
    print("1. Scrape Home Appliances only")
    print("2. Scrape Shoes only")
    print("3. Scrape Both (All 19 products)")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        products = HOME_APPLIANCES
        category_name = 'Home Appliance'
        print(f"\n🎯 Scraping {len(products)} Home Appliances...")
    elif choice == '2':
        products = SHOES
        category_name = 'Shoes'
        print(f"\n🎯 Scraping {len(products)} Shoes...")
    elif choice == '3':
        products = HOME_APPLIANCES + SHOES
        print(f"\n🎯 Scraping all {len(products)} products...")
    else:
        print("Exiting...")
        return
    
    all_reviews = []
    successful_count = 0
    
    # Scrape each product
    for idx, product in enumerate(products, 1):
        print(f"\n{'='*60}")
        print(f"[{idx}/{len(products)}] {product['name'][:60]}...")
        print(f"{'='*60}")
        
        # Determine category for mixed scraping
        if choice == '3':
            category = 'Home Appliance' if idx <= len(HOME_APPLIANCES) else 'Shoes'
        else:
            category = category_name
        
        try:
            reviews = scrape_product_reviews(product['url'], product['name'], category)
            
            if reviews:
                all_reviews.extend(reviews)
                successful_count += 1
                print(f"✅ Added {len(reviews)} reviews")
            else:
                print(f"⚠️ No reviews found")
            
            # Wait between products
            if idx < len(products):
                wait_time = random.randint(5, 10)
                print(f"⏳ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            continue
    
    # Save results
    if all_reviews:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_file = f"flipkart_phase2_{timestamp}.csv"
        df = pd.DataFrame(all_reviews)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 CSV saved: {csv_file} ({len(df)} rows)")
        
        # Save to JSON
        json_file = csv_file.replace('.csv', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON saved: {json_file}")
        
        # Show statistics
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Successful products: {successful_count}/{len(products)}")
        print(f"   Total reviews: {len(all_reviews)}")
        
        # Category breakdown
        if 'category' in df.columns:
            print(f"\n📈 CATEGORY BREAKDOWN:")
            for cat, count in df['category'].value_counts().items():
                print(f"   {cat}: {count} reviews")
        
        # Rating distribution
        if 'rating' in df.columns:
            print(f"\n⭐ RATING DISTRIBUTION:")
            for rating in sorted(df['rating'].unique()):
                count = (df['rating'] == rating).sum()
                print(f"   {rating} stars: {count} reviews")
        
        print(f"\n📂 Files saved in: {os.getcwd()}")
        
    else:
        print("\n❌ No reviews collected!")

if __name__ == "__main__":
    try:
        from selenium import webdriver
        import pandas as pd
    except ImportError:
        print("❌ Install dependencies: pip install selenium pandas webdriver-manager")
        exit(1)
    
    print("\n🚀 FLIPKART PHASE 2 SCRAPER")
    print("Make sure Chrome is installed.\n")
    main()