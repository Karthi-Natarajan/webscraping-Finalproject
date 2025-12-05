import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any


class DataLoader:
    """Data loader for Flipkart reviews dataset"""

    def __init__(self):
        self.df = None
        self.loaded = False
        self.csv_path = None

    # -------------------------------------------------------------
    # Locate dataset file
    # -------------------------------------------------------------
    def _find_dataset(self) -> Optional[Path]:
        """Find a dataset CSV inside /data folder"""

        # Look inside data/ folder first (most reliable)
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
    # Load dataset
    # -------------------------------------------------------------
    def load_data(self) -> pd.DataFrame:
        try:
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

            print(f"📊 Loading dataset: {dataset_path}")
            self.df = pd.read_csv(dataset_path, encoding="utf-8-sig")

            print(f"📈 Dataset shape: {self.df.shape}")
            print(f"📋 Columns: {list(self.df.columns)}")

            self._clean_data()

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

        # Fix review_id issue (your original error)
        if "review_id" in self.df.columns:
            self.df["review_id"] = pd.to_numeric(
                self.df["review_id"], errors="coerce"
            )

            # REPLACE invalid / missing values with sequential IDs
            missing_mask = self.df["review_id"].isna()
            self.df.loc[missing_mask, "review_id"] = (
                pd.RangeIndex(1, missing_mask.sum() + 1)
            )

            self.df["review_id"] = self.df["review_id"].astype(int)

        else:
            self.df.insert(0, "review_id", pd.RangeIndex(1, len(self.df) + 1))

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

        print("🧹 Data cleaning completed")

    # -------------------------------------------------------------
    # Fetch reviews
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
    # Stats
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
                "status": "empty_dataset"
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
            "dataset_path": str(self.csv_path)
        }

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
    print("🧪 Testing DataLoader")
    df = data_loader.load_data()
    print(f"Loaded {len(df)} rows")
