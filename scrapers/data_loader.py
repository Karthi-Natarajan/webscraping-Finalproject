import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from datetime import datetime
from textblob import TextBlob  # for sentiment analysis


class DataLoader:
    """Data loader for Flipkart reviews dataset with MongoDB support"""

    def __init__(self):
        self.df = None
        self.loaded = False
        self.csv_path = None
        self.mongo_client = None
        self.db = None
        self.collection = None
        
        # Initialize MongoDB connection with YOUR URL
        self._init_mongodb()

    # -------------------------------------------------------------
    # MongoDB Initialization
    # -------------------------------------------------------------
    def _init_mongodb(self):
        """Initialize MongoDB connection with your Atlas URL"""
        # Try environment variable first
        mongo_uri = os.environ.get("MONGODB_URI")
        
        if not mongo_uri:
            # Fallback to your provided URL (for testing)
            mongo_uri = "mongodb+srv://skarthinatarajan21_db_user:skn212005@cluster0.ebtw7zu.mongodb.net/sentimentDB?retryWrites=true&w=majority&appName=Cluster0"
            print("ℹ️ Using hardcoded MongoDB URL (set MONGODB_URI in environment for production)")
        
        try:
            # Connect to MongoDB
            print(f"🔗 Connecting to MongoDB: {mongo_uri.split('@')[1].split('/')[0]}...")
            self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
            
            # Test connection
            self.mongo_client.admin.command('ping')
            
            # Get database and collection
            self.db = self.mongo_client.get_database()
            self.collection = self.db["flipkart_reviews"]
            
            print(f"✅ Connected to MongoDB successfully!")
            print(f"📊 Database: {self.db.name}")
            print(f"📄 Collection: flipkart_reviews")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)[:100]}...")
            print("ℹ️ Falling back to CSV mode")
            self.mongo_client = None
            self.db = None
            self.collection = None

    # -------------------------------------------------------------
    # Locate dataset file
    # -------------------------------------------------------------
    def _find_dataset(self) -> Optional[Path]:
        """Find a dataset CSV inside /data folder"""
        # Look inside data/ folder first
        data_dir = Path("data")
        if data_dir.exists():
            csv_files = list(data_dir.glob("flipkart_*.csv"))
            if csv_files:
                latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                print(f"📂 Found dataset at: {latest_file}")
                return latest_file

        # Fallback search anywhere
        csv_files = list(Path(".").glob("flipkart_*.csv"))
        if csv_files:
            latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
            print(f"📂 Found dataset at root: {latest_file}")
            return latest_file

        print("⚠️ No dataset file found!")
        return None

    # -------------------------------------------------------------
    # Sentiment Analysis
    # -------------------------------------------------------------
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of review text"""
        if not text or not isinstance(text, str):
            return {"polarity": 0.0, "subjectivity": 0.0, "sentiment": "neutral"}
        
        try:
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine sentiment label
            if polarity > 0.2:
                sentiment = "positive"
            elif polarity < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "sentiment": sentiment
            }
        except:
            return {"polarity": 0.0, "subjectivity": 0.0, "sentiment": "neutral"}

    # -------------------------------------------------------------
    # Save to MongoDB
    # -------------------------------------------------------------
    def _save_to_mongodb(self):
        """Save DataFrame to MongoDB"""
        if self.df is None or self.df.empty:
            print("⚠️ No data to save to MongoDB")
            return
        
        if self.collection is None:
            print("⚠️ MongoDB not connected, skipping save")
            return
        
        try:
            # Convert DataFrame to list of dictionaries
            records = self.df.to_dict("records")
            
            # Add metadata and sentiment analysis
            for record in records:
                # Add timestamp
                record["created_at"] = datetime.utcnow()
                record["updated_at"] = datetime.utcnow()
                
                # FIX: Convert pandas NaT/NaN to None for MongoDB compatibility
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                
                # Add sentiment analysis
                if "review_text" in record and record["review_text"]:
                    sentiment = self._analyze_sentiment(record["review_text"])
                    record.update({
                        "sentiment_polarity": sentiment["polarity"],
                        "sentiment_subjectivity": sentiment["subjectivity"],
                        "sentiment_label": sentiment["sentiment"]
                    })
            
            # Clear existing data and insert new
            self.collection.delete_many({})
            result = self.collection.insert_many(records)
            
            print(f"💾 Saved {len(result.inserted_ids)} reviews to MongoDB")
            print(f"📊 Collection now has {self.collection.count_documents({})} documents")
            
        except Exception as e:
            print(f"❌ Error saving to MongoDB: {e}")
            import traceback
            traceback.print_exc()

    # -------------------------------------------------------------
    # Load from MongoDB
    # -------------------------------------------------------------
    def _load_from_mongodb(self) -> bool:
        """Load data from MongoDB"""
        if self.collection is None:
            return False
        
        try:
            # Check if MongoDB has data
            count = self.collection.count_documents({})
            if count == 0:
                print("📭 MongoDB collection is empty")
                return False
            
            # Load data from MongoDB
            cursor = self.collection.find({}, {"_id": 0})
            data = list(cursor)
            
            if not data:
                return False
            
            # Convert to DataFrame
            self.df = pd.DataFrame(data)
            
            # Convert date strings to datetime if needed
            if "date" in self.df.columns:
                self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            
            print(f"📊 Loaded {len(self.df)} reviews from MongoDB")
            return True
            
        except Exception as e:
            print(f"❌ Error loading from MongoDB: {e}")
            return False

    # -------------------------------------------------------------
    # Load dataset
    # -------------------------------------------------------------
    def load_data(self) -> pd.DataFrame:
        """Load data from MongoDB first, fallback to CSV"""
        try:
            # Try to load from MongoDB first
            if self._load_from_mongodb():
                self.loaded = True
                print("✅ Using data from MongoDB")
                return self.df
            
            # Fallback to CSV
            dataset_path = self._find_dataset()

            if not dataset_path:
                print("❌ No dataset found. Creating empty dataset.")
                self.df = pd.DataFrame(columns=[
                    "review_id", "category", "product_name", "rating",
                    "review_text", "reviewer", "date", "verified"
                ])
                self.loaded = True
                return self.df

            self.csv_path = dataset_path
            print(f"📊 Loading dataset from CSV: {dataset_path}")
            
            # Load CSV
            self.df = pd.read_csv(dataset_path, encoding="utf-8-sig")
            print(f"📈 Dataset shape: {self.df.shape}")
            print(f"📋 Columns: {list(self.df.columns)}")

            # Clean data
            self._clean_data()
            
            # Save to MongoDB for future use
            self._save_to_mongodb()
            
            print(f"✅ Successfully loaded {len(self.df)} reviews")

            self.loaded = True
            return self.df

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()

            self.df = pd.DataFrame(columns=[
                "review_id", "category", "product_name", "rating",
                "review_text", "reviewer", "date", "verified"
            ])
            self.loaded = True
            return self.df

    # -------------------------------------------------------------
    # Clean dataset
    # -------------------------------------------------------------
    def _clean_data(self):
        """Clean and normalize dataset"""
        if self.df is None or self.df.empty:
            return

        # Fix review_id issue
        if "review_id" in self.df.columns:
            self.df["review_id"] = pd.to_numeric(
                self.df["review_id"], errors="coerce"
            )

            missing_mask = self.df["review_id"].isna()
            if missing_mask.any():
                start_id = 1
                if not self.df["review_id"].isna().all():
                    existing_ids = self.df["review_id"].dropna()
                    if len(existing_ids) > 0:
                        start_id = int(existing_ids.max()) + 1
                
                fill_ids = list(range(start_id, start_id + missing_mask.sum()))
                self.df.loc[missing_mask, "review_id"] = fill_ids

            self.df["review_id"] = self.df["review_id"].astype(int)
        else:
            self.df.insert(0, "review_id", list(range(1, len(self.df) + 1)))

        # Rating normalization
        if "rating" in self.df.columns:
            self.df["rating"] = pd.to_numeric(
                self.df["rating"], errors="coerce"
            ).fillna(1).clip(1, 5).astype(int)

        # Fill text columns
        for col in ["review_text", "reviewer", "product_name", "category"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("Unknown")

        # Normalize "verified"
        if "verified" in self.df.columns:
            self.df["verified"] = (
                self.df["verified"]
                .astype(str)
                .str.lower()
                .apply(lambda x: "yes" if x in ["yes", "true", "verified", "1"] else "no")
            )

        # Ensure date is in datetime format (and convert NaT to None for MongoDB)
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            # Convert NaT (invalid dates) to None for MongoDB compatibility
            self.df["date"] = self.df["date"].where(self.df["date"].notna(), None)

        print("🧹 Data cleaning completed")

    # -------------------------------------------------------------
    # MongoDB Operations
    # -------------------------------------------------------------
    def add_review(self, review_data: Dict) -> bool:
        """Add a new review to MongoDB"""
        if self.collection is None:
            print("⚠️ MongoDB not connected")
            return False
        
        try:
            # Add metadata
            review_data["created_at"] = datetime.utcnow()
            review_data["updated_at"] = datetime.utcnow()
            
            # FIX: Convert any NaN values to None for MongoDB
            for key, value in review_data.items():
                if pd.isna(value):
                    review_data[key] = None
            
            # Add sentiment analysis
            if "review_text" in review_data and review_data["review_text"]:
                sentiment = self._analyze_sentiment(review_data["review_text"])
                review_data.update({
                    "sentiment_polarity": sentiment["polarity"],
                    "sentiment_subjectivity": sentiment["subjectivity"],
                    "sentiment_label": sentiment["sentiment"]
                })
            
            # Insert into MongoDB
            result = self.collection.insert_one(review_data)
            
            # Update local DataFrame
            self._refresh_from_mongodb()
            
            print(f"✅ Added review with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding review: {e}")
            return False

    def _refresh_from_mongodb(self):
        """Refresh DataFrame from MongoDB"""
        if self.collection is not None:
            self._load_from_mongodb()

    def get_mongo_stats(self) -> Dict[str, Any]:
        """Get MongoDB statistics"""
        if self.collection is None:
            return {"status": "not_connected"}
        
        try:
            stats = {
                "status": "connected",
                "total_reviews": self.collection.count_documents({}),
                "database": self.db.name,
                "collection": "flipkart_reviews",
                "connection": "mongodb+srv://skarthinatarajan21_db_user:*****@cluster0.ebtw7zu.mongodb.net"
            }
            
            # Get product counts from MongoDB
            pipeline = [
                {"$group": {"_id": "$product_name", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            products = list(self.collection.aggregate(pipeline))
            stats["top_products"] = products[:5]
            
            # Get sentiment distribution
            pipeline = [
                {"$group": {"_id": "$sentiment_label", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            sentiments = list(self.collection.aggregate(pipeline))
            stats["sentiment_distribution"] = sentiments
            
            return stats
            
        except Exception as e:
            return {"status": f"error: {str(e)}"}

    # -------------------------------------------------------------
    # Fetch reviews (with MongoDB fallback)
    # -------------------------------------------------------------
    def get_reviews(self, limit: Optional[int] = None, **filters) -> List[Dict]:
        if not self.loaded:
            self.load_data()

        df = self.df.copy()

        if df.empty:
            return []

        if filters.get("category"):
            df = df[df["category"].str.contains(filters["category"], case=False)]

        if filters.get("product"):
            df = df[df["product_name"].str.contains(filters["product"], case=False)]

        if filters.get("min_rating"):
            df = df[df["rating"] >= filters["min_rating"]]

        if filters.get("max_rating"):
            df = df[df["rating"] <= filters["max_rating"]]

        if "verified" in filters:
            if filters["verified"]:
                df = df[df["verified"] == "yes"]
            else:
                df = df[df["verified"] == "no"]

        if limit:
            df = df.head(limit)

        print(f"🔍 Returning {len(df)} reviews")
        return df.to_dict("records")

    # -------------------------------------------------------------
    # Stats (with MongoDB data)
    # -------------------------------------------------------------
    def get_stats(self) -> Dict[str, Any]:
        if not self.loaded:
            self.load_data()

        if self.df.empty:
            return {
                "total_reviews": 0,
                "total_products": 0,
                "categories": {},
                "ratings": {},
                "verified_reviews": 0,
                "status": "empty_dataset",
                "mongo_connected": self.collection is not None
            }

        df = self.df

        stats = {
            "total_reviews": int(len(df)),
            "total_products": int(df["product_name"].nunique()),
            "categories": df["category"].value_counts().to_dict(),
            "ratings": {str(i): int((df["rating"] == i).sum()) for i in range(1, 5 + 1)},
            "verified_reviews": int((df["verified"] == "yes").sum()),
            "average_rating": round(float(df["rating"].mean()), 2),
            "status": "loaded",
            "dataset_path": str(self.csv_path),
            "mongo_connected": self.collection is not None,
            "storage_mode": "mongodb" if self.collection is not None else "csv"
        }
        
        # Add sentiment stats if available
        if "sentiment_label" in df.columns:
            stats["sentiment"] = df["sentiment_label"].value_counts().to_dict()

        return stats

    # -------------------------------------------------------------
    # Search reviews
    # -------------------------------------------------------------
    def search_reviews(self, query: str, limit: int = 20) -> List[Dict]:
        if not self.loaded:
            self.load_data()

        if not query or len(query) < 2:
            return []

        query = query.lower()
        df = self.df

        mask = (
            df["review_text"].str.lower().str.contains(query) |
            df["product_name"].str.lower().str.contains(query) |
            df["category"].str.lower().str.contains(query) |
            df["reviewer"].str.lower().str.contains(query)
        )

        results = df[mask].head(limit)

        print(f"🔍 Search '{query}' found {len(results)} results")

        return results.to_dict("records")

    # -------------------------------------------------------------
    # Metadata helpers
    # -------------------------------------------------------------
    def get_categories(self) -> List[str]:
        if not self.loaded:
            self.load_data()
        return sorted(self.df["category"].dropna().unique().tolist())

    def get_products(self) -> List[str]:
        if not self.loaded:
            self.load_data()
        return sorted(self.df["product_name"].dropna().unique().tolist())

    def get_review_by_id(self, review_id: int) -> Optional[Dict]:
        if not self.loaded:
            self.load_data()

        row = self.df[self.df["review_id"] == review_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()


# -------------------------------------------------------------
# Global instance
# -------------------------------------------------------------
data_loader = DataLoader()

if __name__ == "__main__":
    print("🧪 Testing DataLoader with MongoDB")
    df = data_loader.load_data()
    print(f"Loaded {len(df)} rows")
    
    # Test MongoDB connection
    mongo_stats = data_loader.get_mongo_stats()
    print(f"MongoDB Status: {mongo_stats}")