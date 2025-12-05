# backend/routes/product_route.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import pandas as pd
import json
from datetime import datetime

router = APIRouter(prefix="/api/products", tags=["Products"])

# Load dataset
def load_dataset():
    try:
        df = pd.read_csv("data/flipkart_MASTER_DATASET_20251205_161226.csv", encoding='utf-8-sig')
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()

@router.get("/")
async def get_all_products():
    """Get all unique products"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    products = df['product_name'].unique().tolist()
    return {
        "products": products,
        "count": len(products)
    }

@router.get("/categories")
async def get_categories():
    """Get all categories with counts"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    if 'category' not in df.columns:
        return {"categories": [], "count": 0}
    
    category_counts = df['category'].value_counts().to_dict()
    
    categories = []
    for category, count in category_counts.items():
        # Get unique products in this category
        category_products = df[df['category'] == category]['product_name'].unique().tolist()
        
        # Get average rating for category
        avg_rating = df[df['category'] == category]['rating'].mean()
        
        categories.append({
            "name": str(category),
            "product_count": len(category_products),
            "review_count": int(count),
            "avg_rating": float(avg_rating) if not pd.isna(avg_rating) else 0,
            "products": category_products[:10]  # First 10 products
        })
    
    return {
        "categories": categories,
        "total_categories": len(categories),
        "total_products": df['product_name'].nunique()
    }

@router.get("/{product_name}")
async def get_product_details(product_name: str):
    """Get detailed information about a specific product"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    # Find product (case-insensitive search)
    product_df = df[df['product_name'].str.contains(product_name, case=False, na=False)]
    
    if product_df.empty:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get first matching product
    first_product = product_df.iloc[0]
    
    # Calculate statistics
    total_reviews = len(product_df)
    avg_rating = product_df['rating'].mean()
    verified_reviews = (product_df['verified'].str.lower() == 'yes').sum()
    
    # Rating distribution
    rating_dist = {}
    for rating in range(1, 6):
        count = (product_df['rating'] == rating).sum()
        rating_dist[str(rating)] = int(count)
    
    # Get latest reviews
    latest_reviews = []
    for _, row in product_df.head(5).iterrows():
        latest_reviews.append({
            "review_id": int(row.get('review_id', 0)),
            "rating": int(row.get('rating', 0)),
            "review_text": str(row.get('review_text', ''))[:200] + "..." if len(str(row.get('review_text', ''))) > 200 else str(row.get('review_text', '')),
            "reviewer": str(row.get('reviewer', 'Customer')),
            "date": str(row.get('date', '')),
            "verified": str(row.get('verified', 'No'))
        })
    
    return {
        "product_name": str(first_product.get('product_name', '')),
        "category": str(first_product.get('category', 'Unknown')),
        "total_reviews": int(total_reviews),
        "average_rating": float(avg_rating) if not pd.isna(avg_rating) else 0,
        "verified_reviews": int(verified_reviews),
        "rating_distribution": rating_dist,
        "product_url": str(first_product.get('product_url', '')) if pd.notnull(first_product.get('product_url')) else None,
        "latest_reviews": latest_reviews,
        "first_scraped": str(first_product.get('scraped_date', '')) if pd.notnull(first_product.get('scraped_date')) else None
    }

@router.get("/category/{category_name}")
async def get_products_by_category(category_name: str):
    """Get all products in a specific category"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    if 'category' not in df.columns:
        raise HTTPException(status_code=404, detail="Category column not found")
    
    # Find category (case-insensitive)
    category_df = df[df['category'].str.contains(category_name, case=False, na=False)]
    
    if category_df.empty:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get unique products in this category
    products_list = []
    product_names = category_df['product_name'].unique()
    
    for product_name in product_names:
        product_reviews = category_df[category_df['product_name'] == product_name]
        avg_rating = product_reviews['rating'].mean()
        review_count = len(product_reviews)
        
        products_list.append({
            "product_name": str(product_name),
            "review_count": int(review_count),
            "average_rating": float(avg_rating) if not pd.isna(avg_rating) else 0,
            "verified_count": int((product_reviews['verified'].str.lower() == 'yes').sum())
        })
    
    # Sort by review count (descending)
    products_list.sort(key=lambda x: x["review_count"], reverse=True)
    
    return {
        "category": category_name,
        "total_products": len(products_list),
        "total_reviews": len(category_df),
        "average_category_rating": float(category_df['rating'].mean()) if not pd.isna(category_df['rating'].mean()) else 0,
        "products": products_list
    }

@router.get("/search/")
async def search_products(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """Search products by name"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    # Search in product names
    mask = df['product_name'].str.contains(query, case=False, na=False)
    matching_products = df[mask]['product_name'].unique()[:limit]
    
    results = []
    for product_name in matching_products:
        product_reviews = df[df['product_name'] == product_name]
        avg_rating = product_reviews['rating'].mean()
        
        results.append({
            "product_name": str(product_name),
            "category": str(product_reviews.iloc[0].get('category', 'Unknown')),
            "review_count": len(product_reviews),
            "average_rating": float(avg_rating) if not pd.isna(avg_rating) else 0
        })
    
    return {
        "query": query,
        "results": results,
        "count": len(results),
        "total_matches": len(df[mask]['product_name'].unique())
    }