# backend/routes/analyze_route.py
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import json

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

# Load dataset
def load_dataset():
    try:
        df = pd.read_csv("data/flipkart_MASTER_DATASET_20251205_161226.csv", encoding='utf-8-sig')
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()

@router.get("/stats")
async def get_detailed_stats():
    """Get comprehensive dataset statistics"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    total_reviews = len(df)
    total_products = df['product_name'].nunique()
    
    # Category statistics
    category_stats = {}
    if 'category' in df.columns:
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            category_stats[str(category)] = {
                "review_count": len(category_df),
                "product_count": category_df['product_name'].nunique(),
                "avg_rating": float(category_df['rating'].mean()) if not pd.isna(category_df['rating'].mean()) else 0,
                "verified_reviews": int((category_df['verified'].str.lower() == 'yes').sum())
            }
    
    # Rating statistics
    rating_stats = {}
    if 'rating' in df.columns:
        for rating in range(1, 6):
            count = (df['rating'] == rating).sum()
            percentage = (count / total_reviews) * 100
            rating_stats[str(rating)] = {
                "count": int(count),
                "percentage": float(percentage)
            }
    
    # Verified reviews
    verified_count = 0
    if 'verified' in df.columns:
        verified_count = int((df['verified'].str.lower() == 'yes').sum())
    
    # Text analysis
    text_stats = {}
    if 'review_text' in df.columns:
        df['review_length'] = df['review_text'].astype(str).str.len()
        text_stats = {
            "avg_length": float(df['review_length'].mean()),
            "min_length": int(df['review_length'].min()),
            "max_length": int(df['review_length'].max()),
            "total_words": int(df['review_text'].astype(str).str.split().str.len().sum())
        }
    
    # Top products by review count
    top_products = []
    if 'product_name' in df.columns:
        product_counts = df['product_name'].value_counts().head(10)
        for product, count in product_counts.items():
            product_df = df[df['product_name'] == product]
            avg_rating = product_df['rating'].mean()
            top_products.append({
                "product_name": str(product),
                "review_count": int(count),
                "avg_rating": float(avg_rating) if not pd.isna(avg_rating) else 0,
                "category": str(product_df.iloc[0].get('category', 'Unknown'))
            })
    
    return {
        "summary": {
            "total_reviews": total_reviews,
            "total_products": total_products,
            "verified_reviews": verified_count,
            "verified_percentage": float((verified_count / total_reviews) * 100) if total_reviews > 0 else 0,
            "overall_avg_rating": float(df['rating'].mean()) if 'rating' in df.columns else 0,
            "categories_count": len(category_stats)
        },
        "categories": category_stats,
        "ratings": rating_stats,
        "text_analysis": text_stats,
        "top_products": top_products,
        "dataset_info": {
            "last_updated": datetime.now().isoformat(),
            "file_size_mb": 0.1,  # Approximate
            "scrape_phases": list(df['scrape_phase'].unique()) if 'scrape_phase' in df.columns else ["Unknown"]
        }
    }

@router.get("/category/{category_name}/insights")
async def get_category_insights(category_name: str):
    """Get detailed insights for a specific category"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    if 'category' not in df.columns:
        raise HTTPException(status_code=400, detail="Category data not available")
    
    # Get category data
    category_df = df[df['category'].str.contains(category_name, case=False, na=False)]
    
    if category_df.empty:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Basic stats
    total_reviews = len(category_df)
    total_products = category_df['product_name'].nunique()
    avg_rating = category_df['rating'].mean()
    
    # Rating distribution
    rating_dist = {}
    for rating in range(1, 6):
        count = (category_df['rating'] == rating).sum()
        percentage = (count / total_reviews) * 100
        rating_dist[str(rating)] = {
            "count": int(count),
            "percentage": float(percentage)
        }
    
    # Top products in this category
    top_products = []
    product_counts = category_df['product_name'].value_counts().head(5)
    for product, count in product_counts.items():
        product_df = category_df[category_df['product_name'] == product]
        top_products.append({
            "product_name": str(product),
            "review_count": int(count),
            "avg_rating": float(product_df['rating'].mean()),
            "verified_count": int((product_df['verified'].str.lower() == 'yes').sum())
        })
    
    # Sentiment-like analysis (based on rating)
    sentiment = {
        "positive": int((category_df['rating'] >= 4).sum()),
        "neutral": int((category_df['rating'] == 3).sum()),
        "negative": int((category_df['rating'] <= 2).sum())
    }
    
    return {
        "category": category_name,
        "overview": {
            "total_reviews": total_reviews,
            "total_products": total_products,
            "average_rating": float(avg_rating) if not pd.isna(avg_rating) else 0,
            "verified_reviews": int((category_df['verified'].str.lower() == 'yes').sum())
        },
        "rating_distribution": rating_dist,
        "sentiment_analysis": sentiment,
        "top_products": top_products,
        "review_trends": {
            "most_common_words": ["good", "product", "quality", "value", "price"],  # Placeholder
            "avg_review_length": float(category_df['review_text'].astype(str).str.len().mean()) if 'review_text' in category_df.columns else 0
        }
    }

@router.get("/rating-analysis")
async def rating_analysis():
    """Analyze rating patterns"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    if 'rating' not in df.columns:
        raise HTTPException(status_code=400, detail="Rating data not available")
    
    # Rating by category
    rating_by_category = {}
    if 'category' in df.columns:
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            rating_by_category[str(category)] = {
                "avg_rating": float(category_df['rating'].mean()),
                "median_rating": float(category_df['rating'].median()),
                "rating_distribution": category_df['rating'].value_counts().sort_index().to_dict()
            }
    
    # Rating trends (if date available)
    rating_trends = {}
    if 'date' in df.columns:
        try:
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            monthly_ratings = df.groupby(df['date_parsed'].dt.to_period('M'))['rating'].mean()
            rating_trends = {
                "monthly_avg": monthly_ratings.dropna().to_dict(),
                "overall_trend": "stable"  # Placeholder
            }
        except:
            rating_trends = {"error": "Date parsing failed"}
    
    # Verified vs Non-verified ratings
    verified_analysis = {}
    if 'verified' in df.columns:
        verified_df = df[df['verified'].str.lower() == 'yes']
        non_verified_df = df[df['verified'].str.lower() == 'no']
        
        verified_analysis = {
            "verified": {
                "count": len(verified_df),
                "avg_rating": float(verified_df['rating'].mean()) if len(verified_df) > 0 else 0,
                "rating_dist": verified_df['rating'].value_counts().sort_index().to_dict()
            },
            "non_verified": {
                "count": len(non_verified_df),
                "avg_rating": float(non_verified_df['rating'].mean()) if len(non_verified_df) > 0 else 0,
                "rating_dist": non_verified_df['rating'].value_counts().sort_index().to_dict()
            }
        }
    
    return {
        "overall_stats": {
            "average_rating": float(df['rating'].mean()),
            "median_rating": float(df['rating'].median()),
            "mode_rating": int(df['rating'].mode()[0]) if len(df['rating'].mode()) > 0 else 0,
            "rating_std": float(df['rating'].std())
        },
        "rating_by_category": rating_by_category,
        "verified_analysis": verified_analysis,
        "rating_trends": rating_trends,
        "rating_insights": {
            "most_common_rating": int(df['rating'].mode()[0]) if len(df['rating'].mode()) > 0 else 0,
            "percentage_5_star": float((df['rating'] == 5).sum() / len(df) * 100),
            "percentage_1_star": float((df['rating'] == 1).sum() / len(df) * 100)
        }
    }

@router.get("/comparison")
async def compare_categories(
    category1: str = Query(..., description="First category"),
    category2: str = Query(..., description="Second category")
):
    """Compare two categories"""
    df = load_dataset()
    if df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    # Get data for both categories
    cat1_df = df[df['category'].str.contains(category1, case=False, na=False)]
    cat2_df = df[df['category'].str.contains(category2, case=False, na=False)]
    
    if cat1_df.empty or cat2_df.empty:
        raise HTTPException(status_code=404, detail="One or both categories not found")
    
    comparison = {
        category1: {
            "total_reviews": len(cat1_df),
            "total_products": cat1_df['product_name'].nunique(),
            "avg_rating": float(cat1_df['rating'].mean()),
            "verified_percentage": float((cat1_df['verified'].str.lower() == 'yes').sum() / len(cat1_df) * 100),
            "top_product": cat1_df['product_name'].value_counts().index[0] if len(cat1_df) > 0 else "N/A"
        },
        category2: {
            "total_reviews": len(cat2_df),
            "total_products": cat2_df['product_name'].nunique(),
            "avg_rating": float(cat2_df['rating'].mean()),
            "verified_percentage": float((cat2_df['verified'].str.lower() == 'yes').sum() / len(cat2_df) * 100),
            "top_product": cat2_df['product_name'].value_counts().index[0] if len(cat2_df) > 0 else "N/A"
        },
        "differences": {
            "review_count_diff": len(cat1_df) - len(cat2_df),
            "rating_diff": float(cat1_df['rating'].mean() - cat2_df['rating'].mean()),
            "product_count_diff": cat1_df['product_name'].nunique() - cat2_df['product_name'].nunique()
        }
    }
    
    return comparison