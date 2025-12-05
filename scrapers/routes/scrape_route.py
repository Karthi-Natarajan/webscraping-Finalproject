# backend/routes/scrape_route.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
import pandas as pd
from datetime import datetime
import json
import os

router = APIRouter(prefix="/api/scrape", tags=["Scraping"])

@router.get("/status")
async def get_scraping_status():
    """Get information about current dataset"""
    try:
        # Find latest dataset
        data_dir = "data"
        if not os.path.exists(data_dir):
            return {
                "status": "no_data",
                "message": "No dataset found",
                "dataset_loaded": False
            }
        
        csv_files = [f for f in os.listdir(data_dir) if f.startswith('flipkart_MASTER_DATASET_') and f.endswith('.csv')]
        
        if not csv_files:
            return {
                "status": "no_data",
                "message": "No master dataset found",
                "dataset_loaded": False
            }
        
        # Get latest file
        latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
        file_path = os.path.join(data_dir, latest_file)
        
        # Load dataset for stats
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        return {
            "status": "loaded",
            "dataset_loaded": True,
            "dataset_info": {
                "file_name": latest_file,
                "total_reviews": len(df),
                "total_products": df['product_name'].nunique(),
                "categories": df['category'].nunique() if 'category' in df.columns else 0,
                "file_size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            },
            "summary": {
                "electronics_reviews": len(df[df['category'] == 'Electronics']) if 'category' in df.columns else 0,
                "home_appliance_reviews": len(df[df['category'] == 'Home Appliance']) if 'category' in df.columns else 0,
                "shoes_reviews": len(df[df['category'] == 'Shoes']) if 'category' in df.columns else 0,
                "average_rating": float(df['rating'].mean()) if 'rating' in df.columns else 0,
                "verified_reviews": int((df['verified'].str.lower() == 'yes').sum()) if 'verified' in df.columns else 0
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "dataset_loaded": False
        }

@router.get("/metadata")
async def get_scraping_metadata():
    """Get metadata about scraping process"""
    try:
        metadata_file = "scraping_metadata.json"
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        else:
            # Create default metadata
            metadata = {
                "scraping_sessions": [
                    {
                        "phase": "Phase 1",
                        "date": "2025-12-05",
                        "products_scraped": 19,
                        "reviews_collected": 186,
                        "categories": ["Electronics"]
                    },
                    {
                        "phase": "Phase 2",
                        "date": "2025-12-05",
                        "products_scraped": 20,
                        "reviews_collected": 31,
                        "categories": ["Home Appliances", "Shoes"]
                    }
                ],
                "total_reviews": 217,
                "total_products": 39,
                "last_updated": datetime.now().isoformat()
            }
        
        return metadata
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_dataset(format: str = "csv"):
    """Export dataset in different formats"""
    try:
        # Find latest dataset
        data_dir = "data"
        csv_files = [f for f in os.listdir(data_dir) if f.startswith('flipkart_MASTER_DATASET_') and f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No dataset found")
        
        latest_file = max(csv_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
        file_path = os.path.join(data_dir, latest_file)
        
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        if format.lower() == "json":
            return {
                "filename": latest_file.replace('.csv', '.json'),
                "data": df.to_dict(orient='records'),
                "count": len(df)
            }
        elif format.lower() == "csv":
            # Return CSV download info
            return {
                "filename": latest_file,
                "download_url": f"/api/scrape/download/{latest_file}",
                "row_count": len(df),
                "columns": list(df.columns)
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv' or 'json'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_dataset_summary():
    """Get comprehensive dataset summary"""
    try:
        # Load dataset
        df = pd.read_csv("data/flipkart_MASTER_DATASET_20251205_161226.csv", encoding='utf-8-sig')
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Dataset empty")
        
        # Calculate various statistics
        total_reviews = len(df)
        total_products = df['product_name'].nunique()
        
        # Category breakdown
        category_breakdown = {}
        if 'category' in df.columns:
            for category in df['category'].unique():
                category_df = df[df['category'] == category]
                category_breakdown[str(category)] = {
                    "reviews": len(category_df),
                    "products": category_df['product_name'].nunique(),
                    "avg_rating": float(category_df['rating'].mean()),
                    "verified_reviews": int((category_df['verified'].str.lower() == 'yes').sum())
                }
        
        # Rating analysis
        rating_analysis = {}
        if 'rating' in df.columns:
            for rating in range(1, 6):
                count = (df['rating'] == rating).sum()
                percentage = (count / total_reviews) * 100
                rating_analysis[str(rating)] = {
                    "count": int(count),
                    "percentage": float(percentage),
                    "stars": "★" * rating
                }
        
        # Top products
        top_products = []
        if 'product_name' in df.columns:
            product_counts = df['product_name'].value_counts().head(10)
            for product, count in product_counts.items():
                product_df = df[df['product_name'] == product]
                top_products.append({
                    "product": str(product),
                    "reviews": int(count),
                    "avg_rating": float(product_df['rating'].mean()),
                    "category": str(product_df.iloc[0].get('category', 'Unknown'))
                })
        
        # Verified analysis
        verified_stats = {}
        if 'verified' in df.columns:
            verified_count = (df['verified'].str.lower() == 'yes').sum()
            verified_stats = {
                "verified": int(verified_count),
                "non_verified": int(total_reviews - verified_count),
                "percentage": float((verified_count / total_reviews) * 100)
            }
        
        return {
            "dataset_summary": {
                "total_reviews": total_reviews,
                "total_products": total_products,
                "categories_count": len(category_breakdown),
                "overall_avg_rating": float(df['rating'].mean()),
                "data_collection_period": "December 2025",
                "scrape_phases": list(df['scrape_phase'].unique()) if 'scrape_phase' in df.columns else ["Unknown"]
            },
            "category_breakdown": category_breakdown,
            "rating_analysis": rating_analysis,
            "top_products": top_products,
            "verified_stats": verified_stats,
            "data_quality": {
                "missing_ratings": int(df['rating'].isnull().sum()),
                "missing_reviews": int(df['review_text'].isnull().sum()),
                "duplicate_reviews": int(df.duplicated(subset=['review_text']).sum()) if 'review_text' in df.columns else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))