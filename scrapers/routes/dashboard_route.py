# backend/routes/dashboard_route.py
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import pandas as pd
import json
from datetime import datetime

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

def load_dataset():
    try:
        df = pd.read_csv("data/flipkart_MASTER_DATASET_20251205_161226.csv", encoding='utf-8-sig')
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()

@router.get("/overview")
async def get_dashboard_overview():
    """Get overview data for dashboard"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    total_reviews = len(df)
    total_products = df['product_name'].nunique()
    
    # Category stats
    category_stats = []
    if 'category' in df.columns:
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            category_stats.append({
                "name": str(category),
                "reviews": len(category_df),
                "products": category_df['product_name'].nunique(),
                "avg_rating": float(category_df['rating'].mean()),
                "verified_reviews": int((category_df['verified'].str.lower() == 'yes').sum())
            })
    
    # Recent reviews
    recent_reviews = []
    if 'scraped_date' in df.columns:
        try:
            df['scraped_date_parsed'] = pd.to_datetime(df['scraped_date'], errors='coerce')
            recent_df = df.sort_values('scraped_date_parsed', ascending=False).head(10)
            
            for _, row in recent_df.iterrows():
                recent_reviews.append({
                    "product": str(row.get('product_name', '')),
                    "category": str(row.get('category', '')),
                    "rating": int(row.get('rating', 0)),
                    "review": str(row.get('review_text', ''))[:100] + "..." if len(str(row.get('review_text', ''))) > 100 else str(row.get('review_text', '')),
                    "reviewer": str(row.get('reviewer', '')),
                    "date": str(row.get('scraped_date', ''))
                })
        except:
            recent_reviews = []
    
    # Top rated products
    top_rated = []
    if 'product_name' in df.columns and 'rating' in df.columns:
        product_ratings = df.groupby('product_name')['rating'].agg(['mean', 'count']).reset_index()
        top_rated_df = product_ratings[product_ratings['count'] >= 3].sort_values('mean', ascending=False).head(10)
        
        for _, row in top_rated_df.iterrows():
            top_rated.append({
                "product": str(row['product_name']),
                "avg_rating": float(row['mean']),
                "review_count": int(row['count'])
            })
    
    return {
        "overview": {
            "total_reviews": total_reviews,
            "total_products": total_products,
            "categories": len(category_stats),
            "overall_rating": float(df['rating'].mean()),
            "verified_percentage": float((df['verified'].str.lower() == 'yes').sum() / total_reviews * 100)
        },
        "category_stats": category_stats,
        "recent_reviews": recent_reviews,
        "top_rated": top_rated,
        "updated_at": datetime.now().isoformat()
    }