"""
Script to upload scraped CSV data to MongoDB Atlas
Run this after scraping to populate your backend database
"""

import csv
import json
import pymongo
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def connect_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        # Get connection string from environment or use default
        mongo_uri = os.getenv("MONGODB_URI", "mongodb+srv://skarthinatarajan21_db_user:skn212005@cluster0.ebtw7zu.mongodb.net/sentimentDB?retryWrites=true&w=majority&appName=Cluster0")
        
        client = pymongo.MongoClient(mongo_uri)
        db = client["sentiment_analysis_db"]  # Changed to match your database
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas")
        return db
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None

def upload_csv_to_mongodb(csv_file="dataset.csv"):
    """Upload CSV data to MongoDB collections"""
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return 0
    
    db = connect_mongodb()
    if db is None:  # Fixed: check for None
        return 0
    
    reviews = []
    
    # Read CSV
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean and transform data
            try:
                rating = row.get("rating", "0")
                if rating.isdigit():
                    row["rating"] = int(rating)
                else:
                    row["rating"] = 0
            except:
                row["rating"] = 0
            
            row["sentiment"] = "neutral"  # Will be analyzed by backend
            row["uploaded_at"] = datetime.now()
            
            # Add metadata
            if "review_id" not in row:
                import hashlib
                review_text = str(row.get("text", "")) + str(row.get("author", ""))
                row["review_id"] = hashlib.md5(review_text.encode()).hexdigest()[:10]
            
            reviews.append(row)
    
    print(f"📖 Read {len(reviews)} reviews from {csv_file}")
    
    # Upload to MongoDB
    if reviews:
        # Insert new reviews
        result = db.reviews.insert_many(reviews)
        print(f"✅ Uploaded {len(result.inserted_ids)} reviews to MongoDB")
        
        # Update product metadata
        update_product_metadata(db)
        
        # Create indexes
        db.reviews.create_index([("product_keyword", 1)])
        db.reviews.create_index([("category", 1)])
        db.reviews.create_index([("rating", 1)])
        print("✅ Created database indexes")
        
        # Save upload log
        save_upload_log(csv_file, len(reviews))
    
    return len(reviews)

def update_product_metadata(db):
    """Update product collection with aggregated data"""
    # Group reviews by product/keyword
    pipeline = [
        {
            "$group": {
                "_id": "$product_keyword",
                "review_count": {"$sum": 1},
                "avg_rating": {"$avg": "$rating"},
                "categories": {"$addToSet": "$category"},
                "last_updated": {"$max": "$uploaded_at"}
            }
        }
    ]
    
    try:
        product_stats = list(db.reviews.aggregate(pipeline))
        
        # Save to products collection
        for stat in product_stats:
            db.products.update_one(
                {"_id": stat["_id"]},
                {
                    "$set": {
                        "name": stat["_id"],
                        "review_count": stat["review_count"],
                        "avg_rating": round(float(stat.get("avg_rating", 0)), 2),
                        "category": stat["categories"][0] if stat["categories"] else "uncategorized",
                        "last_updated": stat["last_updated"],
                        "source": "flipkart"
                    }
                },
                upsert=True
            )
        
        print(f"✅ Updated metadata for {len(product_stats)} products")
    except Exception as e:
        print(f"⚠️ Could not update product metadata: {e}")

def save_upload_log(csv_file, count):
    """Save upload information to log file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "csv_file": csv_file,
        "records_uploaded": count,
        "collection": "reviews"
    }
    
    log_file = "upload_log.json"
    
    # Read existing log or create new
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    else:
        logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2)
    
    print(f"📝 Upload logged to {log_file}")

def main():
    print("📤 MongoDB CSV Upload Script")
    print("=" * 50)
    
    csv_files = ["dataset.csv", "scraped_reviews.csv", "reviews.csv"]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"\n📁 Found CSV file: {csv_file}")
            print(f"File size: {os.path.getsize(csv_file) / 1024:.2f} KB")
            
            choice = input(f"Upload {csv_file} to MongoDB? (y/n): ").strip().lower()
            
            if choice == 'y':
                count = upload_csv_to_mongodb(csv_file)
                if count > 0:
                    print(f"\n🎉 Successfully uploaded {count} records!")
                    print("\n📊 Next steps:")
                    print("1. Start your Flask backend: python app.py")
                    print("2. Open http://localhost:5000")
                    print("3. View scraped data in the dashboard")
                else:
                    print("❌ No records were uploaded.")
                return
    
    print("\n❌ No CSV files found. Please run bulk_scraper.py first.")
    print("\n💡 To create data, run:")
    print("   python bulk_scraper.py")

if __name__ == "__main__":
    main()