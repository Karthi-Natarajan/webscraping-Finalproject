# backend/data_loader.py
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Any
import json

class DataLoader:
    """Data loader using pandas"""
    
    def __init__(self):
        self.df = None
        self.loaded = False
        
    def load_data(self) -> pd.DataFrame:
        """Load data from CSV file using pandas"""
        try:
            # Find the latest dataset
            data_dir = Path("data")
            csv_files = list(data_dir.glob("flipkart_MASTER_DATASET_*.csv"))
            
            if not csv_files:
                csv_files = list(Path(".").glob("flipkart_MASTER_DATASET_*.csv"))
            
            if not csv_files:
                print("⚠️ No dataset found")
                return pd.DataFrame()
            
            latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
            print(f"📂 Loading dataset: {latest_file}")
            
            # Load with pandas
            self.df = pd.read_csv(latest_file, encoding='utf-8-sig')
            
            # Clean data
            if 'rating' in self.df.columns:
                self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce').fillna(0).astype(int)
            
            # Ensure review_id exists
            if 'review_id' not in self.df.columns:
                self.df.insert(0, 'review_id', range(1, len(self.df) + 1))
            
            print(f"✅ Loaded {len(self.df)} reviews")
            self.loaded = True
            
            return self.df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_reviews(self, limit: Optional[int] = None, **filters) -> List[Dict]:
        """Get reviews with filters"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or self.df.empty:
            return []
        
        filtered_df = self.df.copy()
        
        # Apply filters
        if 'category' in filters and filters['category']:
            filtered_df = filtered_df[filtered_df['category'].str.contains(filters['category'], case=False, na=False)]
        
        if 'product' in filters and filters['product']:
            filtered_df = filtered_df[filtered_df['product_name'].str.contains(filters['product'], case=False, na=False)]
        
        if 'min_rating' in filters and filters['min_rating']:
            filtered_df = filtered_df[filtered_df['rating'] >= filters['min_rating']]
        
        if 'max_rating' in filters and filters['max_rating']:
            filtered_df = filtered_df[filtered_df['rating'] <= filters['max_rating']]
        
        if 'verified' in filters and filters['verified'] is not None:
            if filters['verified']:
                filtered_df = filtered_df[filtered_df['verified'].str.lower().isin(['yes', 'true', '1'])]
            else:
                filtered_df = filtered_df[~filtered_df['verified'].str.lower().isin(['yes', 'true', '1'])]
        
        # Apply limit
        if limit:
            filtered_df = filtered_df.head(limit)
        
        return filtered_df.to_dict('records')
    
    def get_stats(self) -> Dict[str, Any]:
        """Calculate statistics"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or self.df.empty:
            return {}
        
        # Basic stats
        total_reviews = len(self.df)
        
        # Category stats
        categories = {}
        if 'category' in self.df.columns:
            categories = self.df['category'].value_counts().to_dict()
        
        # Rating stats
        ratings = {}
        if 'rating' in self.df.columns:
            for rating in range(1, 6):
                count = (self.df['rating'] == rating).sum()
                ratings[str(rating)] = int(count)
        
        # Verified stats
        verified = 0
        if 'verified' in self.df.columns:
            verified = int(self.df['verified'].str.lower().isin(['yes', 'true', '1']).sum())
        
        # Product count
        products = 0
        if 'product_name' in self.df.columns:
            products = self.df['product_name'].nunique()
        
        return {
            'total_reviews': total_reviews,
            'total_products': products,
            'categories': categories,
            'ratings': ratings,
            'verified_reviews': verified
        }
    
    def search_reviews(self, query: str, limit: int = 20) -> List[Dict]:
        """Search reviews by text"""
        if not self.loaded:
            self.load_data()
        
        if self.df is None or self.df.empty:
            return []
        
        if 'review_text' not in self.df.columns:
            return []
        
        # Search in review text
        mask = self.df['review_text'].str.contains(query, case=False, na=False)
        results_df = self.df[mask].head(limit)
        
        return results_df.to_dict('records')

# Global instance
data_loader = DataLoader()