import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flipkart_scraper import scrape_flipkart_reviews

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {"status": "EC2 Scraper Server Running"}

@app.route("/scrape", methods=["GET"])
def scrape():
    try:
        keyword = request.args.get("keyword")
        website = request.args.get("website", "flipkart")

        if not keyword:
            return jsonify({"error": "keyword is required"}), 400

        print(f"[EC2] Request received to scrape '{keyword}' from {website}")

        if website.lower() == "flipkart":
            meta, reviews = scrape_flipkart_reviews(keyword, max_reviews=10, headless=True)
        else:
            return jsonify({"error": "Unsupported website"}), 400

        response = {
            "meta": meta,
            "reviews": reviews,
            "count": len(reviews)
        }

        print(f"[EC2] Completed scrape → {len(reviews)} reviews")

        return jsonify(response)

    except Exception as e:
        print("[EC2 ERROR]", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting EC2 Scraper API...")
    app.run(host="0.0.0.0", port=10000)
