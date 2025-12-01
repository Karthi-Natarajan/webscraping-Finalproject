from flask import Flask, request, jsonify
from .orchestrator import scrape_all

app = Flask(__name__)


@app.route("/api/scrape", methods=["POST"])
def scrape():
    body = request.get_json()

    keyword = body.get("keyword")
    website = body.get("website", "flipkart")

    meta, reviews = scrape_all(keyword, website=website)

    return jsonify({
        "meta": meta,
        "ok": True,
        "reviews": reviews
    })


if __name__ == "__main__":
    app.run(port=10000, debug=False)
