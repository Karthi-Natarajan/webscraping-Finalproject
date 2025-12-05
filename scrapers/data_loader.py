# backend/data_loader.py
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any
import os
import sys

class DataLoader:
    """Data loader for Flipkart reviews dataset"""
    
    def __init__(self):
        self.df = None
        self.loaded = False
        self.csv_path = None
        
    def _find_dataset(self) -> Path:
        """Find the dataset file"""
        # Try multiple possible locations
        possible_paths = [
            Path("data") / "flipkart_MASTER_DATASET_20251205_161226.csv",
            Path("data") / "flipkart_MASTER_DATASET.csv",
            Path(".") / "flipkart_MASTER_DATASET_20251205_161226.csv",
            Path(".") / "data" / "flipkart_MASTER_DATASET_20251205_161226.csv",
            Path("..") / "data" / "flipkart_MASTER_DATASET_20251205_161226.csv",
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"📂 Found dataset at: {path}")
                return path
        
        # Search for any dataset file
        search_paths = [
            Path("."),
            Path("data"),
            Path(".."),
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                csv_files = list(search_path.glob("flipkart_*.csv"))
                if csv_files:
                    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                    print(f"📂 Found dataset: {latest_file}")
                    return latest_file
        
        print("⚠️ No dataset file found!")
        return None
    
    def load_data(self) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            # Find dataset
            dataset_path = self._find_dataset()
            
            if not dataset_path:
                print("❌ No dataset found. Creating empty dataframe.")
                self.df = pd.DataFrame(columns=[
                    'review_id', 'category', 'product_name', 'rating',
                    'review_text', 'reviewer', 'date', 'verified'
                ])
                self.loaded = True
                return self.df
            
            self.csv_path = dataset_path
            
            print(f"📊 Loading dataset: {dataset_path}")
            
            # Load CSV with proper encoding
            self.df = pd.read_csv(dataset_path, encoding='utf-8-sig')
            
            # Display dataset info
            print(f"📈 Dataset shape: {self.df.shape}")
            print(f"📋 Columns: {list(self.df.columns)}")
            
            # Clean and prepare data
            self._clean_data()
            
            print(f"✅ Successfully loaded {len(self.df)} reviews")
            print(f"📦 Products: {self.df['product_name'].nunique() if 'product_name' in self.df.columns else 0}")
            print(f"🏷️ Categories: {self.df['category'].nunique() if 'category' in self.df.columns else 0}")
            
            self.loaded = True
            return self.df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            
            # Create empty dataframe as fallback
            self.df = pd.DataFrame(columns=[
                'review_id', 'category', 'product_name', 'rating',
                'review_text', 'reviewer', 'date', 'verified'
            ])
            self.loaded = True
            return self.df
    
    def _clean_data(self):
        """Clean and preprocess the data"""
        if self.df is None or self.df.empty:
            return
        
        # Ensure review_id exists and is unique
        if 'review_id' not in self.df.columns:
            self.df.insert(0, 'review_id', range(1, len(self.df) + 1))
        else:
            # Make sure review_id is numeric
            self.df['review_id'] = pd.to_numeric(self.df['review_id'], errors='coerce')
            self.df['review_id'] = self.df['review_id'].fillna(range(1, len(self.df) + 1)).astype(int)
        
        # Clean rating column
        if 'rating' in self.df.columns:
            self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce')
            self.df['rating'] = self.df['rating'].fillna(0).astype(int)
            # Ensure ratings are between 1-5
            self.df['rating'] = self.df['rating'].clip(1, 5)
        
        # Fill missing values
        text_columns = ['review_text', 'reviewer', 'product_name', 'category']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('Unknown')
        
        # Clean verified column
        if 'verified' in self.df.columns:
            self.df['verified'] = self.df['verified'].astype(str).str.lower()
            self.df['verified'] = self.df['verified'].apply(
                lambda x: 'yes' if x in ['yes', 'true', '1', 'verified'] else 'no'
            )
        
        print("🧹 Data cleaning completed")
    
    def get_reviews(self, limit: Optional[int] = None, **filters) -> List[Dict]:
        """Get reviews with optional filtering"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or self.df.empty:
            print("⚠️ No data available")
            return []
        
        filtered_df = self.df.copy()
        
        # Apply filters
        if 'category' in filters and filters['category']:
            filtered_df = filtered_df[
                filtered_df['category'].str.contains(
                    str(filters['category']), case=False, na=False
                )
            ]
        
        if 'product' in filters and filters['product']:
            filtered_df = filtered_df[
                filtered_df['product_name'].str.contains(
                    str(filters['product']), case=False, na=False
                )
            ]
        
        if 'min_rating' in filters and filters['min_rating'] is not None:
            filtered_df = filtered_df[filtered_df['rating'] >= filters['min_rating']]
        
        if 'max_rating' in filters and filters['max_rating'] is not None:
            filtered_df = filtered_df[filtered_df['rating'] <= filters['max_rating']]
        
        if 'verified' in filters and filters['verified'] is not None:
            if filters['verified']:
                filtered_df = filtered_df[filtered_df['verified'] == 'yes']
            else:
                filtered_df = filtered_df[filtered_df['verified'] == 'no']
        
        # Apply limit
        if limit and limit > 0:
            filtered_df = filtered_df.head(limit)
        
        # Convert to list of dictionaries
        result = filtered_df.to_dict('records')
        print(f"🔍 Returning {len(result)} reviews")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Calculate comprehensive statistics"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or self.df.empty:
            return {
                'total_reviews': 0,
                'total_products': 0,
                'categories': {},
                'ratings': {},
                'verified_reviews': 0,
                'status': 'empty_dataset'
            }
        
        try:
            # Basic counts
            total_reviews = len(self.df)
            
            # Product count
            product_count = 0
            if 'product_name' in self.df.columns:
                product_count = self.df['product_name'].nunique()
            
            # Category distribution
            categories = {}
            if 'category' in self.df.columns:
                category_counts = self.df['category'].value_counts()
                categories = category_counts.to_dict()
            
            # Rating distribution
            ratings = {}
            if 'rating' in self.df.columns:
                for rating in range(1, 6):
                    count = (self.df['rating'] == rating).sum()
                    ratings[str(rating)] = int(count)
            
            # Verified reviews count
            verified_count = 0
            if 'verified' in self.df.columns:
                verified_count = int((self.df['verified'] == 'yes').sum())
            
            # Average rating
            avg_rating = 0
            if 'rating' in self.df.columns and total_reviews > 0:
                avg_rating = float(self.df['rating'].mean())
            
            # Recent reviews (last 30 days if date column exists)
            recent_reviews = 0
            if 'date' in self.df.columns:
                try:
                    # Try to parse dates
                    self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
                    recent_threshold = pd.Timestamp.now() - pd.Timedelta(days=30)
                    recent_reviews = int((self.df['date'] >= recent_threshold).sum())
                except:
                    recent_reviews = 0
            
            return {
                'total_reviews': int(total_reviews),
                'total_products': int(product_count),
                'categories': categories,
                'ratings': ratings,
                'verified_reviews': int(verified_count),
                'average_rating': round(avg_rating, 2),
                'recent_reviews': int(recent_reviews),
                'status': 'loaded',
                'dataset_path': str(self.csv_path) if self.csv_path else 'unknown'
            }
            
        except Exception as e:
            print(f"❌ Error calculating stats: {e}")
            return {
                'total_reviews': 0,
                'total_products': 0,
                'categories': {},
                'ratings': {},
                'verified_reviews': 0,
                'status': f'error: {str(e)}'
            }
    
    def search_reviews(self, query: str, limit: int = 20) -> List[Dict]:
        """Search reviews by text in multiple columns"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or self.df.empty:
            return []
        
        if not query or len(str(query).strip()) < 2:
            return []
        
        query = str(query).strip().lower()
        
        try:
            # Search in multiple columns
            search_columns = ['review_text', 'product_name', 'category', 'reviewer']
            available_columns = [col for col in search_columns if col in self.df.columns]
            
            if not available_columns:
                return []
            
            # Create search mask
            mask = pd.Series(False, index=self.df.index)
            for col in available_columns:
                mask = mask | self.df[col].str.lower().str.contains(query, na=False)
            
            results_df = self.df[mask]
            
            # Sort by relevance (rating descending, then review length)
            if 'rating' in results_df.columns:
                results_df = results_df.sort_values(
                    by=['rating', 'review_text'],
                    ascending=[False, True]
                )
            
            # Apply limit
            results_df = results_df.head(limit)
            
            # Convert to list of dictionaries
            results = results_df.to_dict('records')
            
            print(f"🔍 Search '{query}' found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ Error in search: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or 'category' not in self.df.columns:
            return []
        
        categories = self.df['category'].dropna().unique().tolist()
        return [str(cat) for cat in categories]
    
    def get_products(self) -> List[str]:
        """Get list of unique products"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or 'product_name' not in self.df.columns:
            return []
        
        products = self.df['product_name'].dropna().unique().tolist()
        return [str(prod) for prod in products]
    
    def get_review_by_id(self, review_id: int) -> Optional[Dict]:
        """Get a specific review by ID"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or 'review_id' not in self.df.columns:
            return None
        
        try:
            review_df = self.df[self.df['review_id'] == review_id]
            if review_df.empty:
                return None
            
            return review_df.iloc[0].to_dict()
        except:
            return None

# Global instance
data_loader = DataLoader()

# Test the loader if run directly
if __name__ == "__main__":
    print("🧪 Testing DataLoader...")
    
    # Load data
    df = data_loader.load_data()
    
    if df is not None and not df.empty:
        print(f"✅ Test successful! Loaded {len(df)} reviews")
        
        # Test stats
        stats = data_loader.get_stats()
        print(f"📊 Stats: {stats['total_reviews']} reviews, {stats['total_products']} products")
        
        # Test getting reviews
        reviews = data_loader.get_reviews(limit=5)
        print(f"📋 Sample reviews: {len(reviews)}")
        
        # Test search
        search_results = data_loader.search_reviews("good", limit=3)
        print(f"🔍 Search results: {len(search_results)}")
    else:
        print("❌ Test failed: No data loaded")