import requests
import logging

logger = logging.getLogger(__name__)

# Import config for timeout
try:
    from config import SCRAPE_TIMEOUT
except ImportError:
    SCRAPE_TIMEOUT = 180  # Default 3 minutes

# -----------------------------
# EC2 SCRAPER SETTINGS
# -----------------------------
EC2_SCRAPER_URL = "http://51.20.87.125:10000/scrape"

def scrape_from_ec2(keyword: str, website: str = "flipkart"):
    """Sends keyword + website to EC2 scraper"""
    try:
        params = {
            "keyword": keyword,
            "website": website
        }

        logger.info(f"Sending to EC2: {params}")
        # Use config timeout
        response = requests.get(EC2_SCRAPER_URL, params=params, timeout=SCRAPE_TIMEOUT)

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"EC2 responded with {response.status_code}"
            }

        data = response.json()
        logger.info(f"EC2 Response: {len(data.get('reviews', []))} reviews")
        
        # Ensure reviews exist
        reviews = data.get("reviews", [])
        if reviews is None:
            reviews = []
            
        # Return normalized structure
        return {
            "success": True,
            "keyword": keyword,
            "website": website,
            "reviews": reviews,
            "count": len(reviews),
            "meta": data.get("meta", {})
        }

    except requests.exceptions.Timeout:
        logger.error(f"EC2 request timed out after {SCRAPE_TIMEOUT} seconds")
        return {
            "success": False,
            "error": f"EC2 scraper timeout after {SCRAPE_TIMEOUT} seconds"
        }
    except Exception as e:
        logger.error(f"EC2 scrape error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# MAIN SCRAPE FUNCTION
def scrape(keyword, website):
    """Called by backend route /api/scrape"""
    logger.info(f"scrape() called: {keyword}, {website}")
    return scrape_from_ec2(keyword, website)