"""
Product keywords for Flipkart scraping
Organized by category
"""

PRODUCT_KEYWORDS = {
    "mobiles": [
        "iPhone 15",
        "Samsung Galaxy S23",
        "OnePlus 12",
        "Xiaomi 14",
        "Google Pixel 8",
        "Vivo V30",
        "Oppo Reno 11",
        "Realme 12 Pro",
        "Motorola Edge 50",
        "Nothing Phone 2"
    ],
    
    "laptops": [
        "MacBook Air M2",
        "Dell Inspiron 14",
        "HP Pavilion 15",
        "Lenovo IdeaPad Slim",
        "Asus Vivobook 15",
        "Acer Aspire 7",
        "MSI Katana",
        "LG Gram 14",
        "Microsoft Surface Laptop",
        "Apple MacBook Pro"
    ],
    
    "headphones": [
        "AirPods Pro",
        "Sony WH-1000XM5",
        "Boat Airdopes",
        "JBL Tune 720",
        "Realme Buds Air 5",
        "OnePlus Buds Pro 2",
        "Noise Cancelling Headphones",
        "Samsung Galaxy Buds2",
        "Sennheiser HD450BT",
        "Skullcandy Crusher"
    ],
    
    "televisions": [
        "Samsung 55 inch TV",
        "LG OLED TV",
        "Sony Bravia",
        "Mi Smart TV",
        "OnePlus TV",
        "TCL Android TV",
        "Vu 4K TV",
        "Panasonic Smart TV",
        "Thomson LED TV",
        "Realme Smart TV"
    ],
    
    "watches": [
        "Apple Watch Series 9",
        "Samsung Galaxy Watch",
        "Noise smart watch",
        "Fire-Boltt smartwatch",
        "Boat smart watch",
        "Realme smart watch",
        "Amazfit GTS",
        "Fossil Gen 6",
        "Garmin smartwatch",
        "Fastrack smartwatch"
    ]
}

def get_all_keywords():
    """Get all keywords as a flat list"""
    all_keywords = []
    for category, keywords in PRODUCT_KEYWORDS.items():
        for keyword in keywords:
            all_keywords.append((category, keyword))
    return all_keywords

def get_keywords_by_category(category, limit=10):
    """Get keywords for a specific category"""
    return PRODUCT_KEYWORDS.get(category, [])[:limit]

if __name__ == "__main__":
    print("📋 Product Categories Available:")
    for category in PRODUCT_KEYWORDS.keys():
        print(f"  • {category}")
    
    print(f"\n📊 Total keywords: {sum(len(v) for v in PRODUCT_KEYWORDS.values())}")