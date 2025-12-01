# orchestrator.py
from scrapers.flipkart_scraper import scrape_flipkart_reviews

def scrape_all(keyword, website="flipkart", max_reviews=20):
    """
    Main orchestrator function
    
    Args:
        keyword: Product to search for
        website: "flipkart" or "amazon"
        max_reviews: Maximum number of reviews to return
    
    Returns:
        tuple: (meta_data, reviews_list)
    """
    
    print(f"[ORCHESTRATOR] Scraping '{website}' for: {keyword}")
    
    if website == "flipkart":
        # Scrape real Flipkart data
        data = scrape_flipkart_reviews(keyword, max_reviews=max_reviews)
        return data["meta"], data["reviews"]
    
    elif website == "amazon":
        # Return dummy Amazon data
        meta = {
            "source": "amazon",
            "url": f"https://www.amazon.in/s?k={keyword}",
            "note": "Amazon scraper returns dummy data for demonstration"
        }
        
        reviews = [
            {
                "author": "Amazon Customer",
                "rating": "4.5",
                "title": "Great product for the price",
                "text": "This is dummy data since Amazon scraper is not implemented. The product seems to work well based on specifications.",
                "source": "amazon"
            },
            {
                "author": "Verified Buyer",
                "rating": "3.0",
                "title": "Average performance",
                "text": "Placeholder review text. Actual Amazon reviews would be scraped here when implemented.",
                "source": "amazon"
            },
            {
                "author": "Tech Enthusiast",
                "rating": "5.0",
                "title": "Exceeded expectations",
                "text": "Dummy review content. The product features look impressive on paper.",
                "source": "amazon"
            }
        ]
        
        return meta, reviews[:max_reviews]
    
    else:
        # Unknown website - default to Flipkart
        print(f"[ORCHESTRATOR] Unknown website '{website}', defaulting to Flipkart")
        data = scrape_flipkart_reviews(keyword, max_reviews=max_reviews)
        return data["meta"], data["reviews"]