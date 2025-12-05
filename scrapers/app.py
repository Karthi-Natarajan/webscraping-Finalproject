# backend/app.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from data_loader import data_loader

app = FastAPI(
    title="Flipkart Reviews API",
    description="API for accessing Flipkart product reviews dataset",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models (compatible with pydantic 1.x)
class Review(BaseModel):
    review_id: int = Field(..., description="Review ID")
    category: str = Field(..., description="Product category")
    product_name: str = Field(..., description="Product name")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    review_text: str = Field(..., description="Review text")
    reviewer: str = Field(..., description="Reviewer name")
    date: Optional[str] = Field(None, description="Review date")
    verified: str = Field(..., description="Verified status")
    
    class Config:
        schema_extra = {
            "example": {
                "review_id": 1,
                "category": "Electronics",
                "product_name": "iPhone 15",
                "rating": 5,
                "review_text": "Excellent product!",
                "reviewer": "Customer",
                "date": "2024-01-01",
                "verified": "Yes"
            }
        }

class StatsResponse(BaseModel):
    total_reviews: int
    total_products: int
    categories: Dict[str, int]
    ratings: Dict[str, int]
    verified_reviews: int

@app.get("/")
async def root():
    return {
        "message": "Flipkart Reviews API",
        "version": "2.0.0",
        "status": "active",
        "dataset": {
            "total_reviews": len(data_loader.df) if data_loader.loaded else 0,
            "loaded": data_loader.loaded
        },
        "endpoints": {
            "/reviews": "Get all reviews (with pagination)",
            "/reviews/{id}": "Get specific review",
            "/stats": "Get dataset statistics",
            "/products": "Get all products",
            "/categories": "Get all categories",
            "/search": "Search reviews",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dataset_loaded": data_loader.loaded,
        "reviews_count": len(data_loader.df) if data_loader.loaded else 0
    }

@app.get("/reviews", response_model=List[Review])
async def get_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    product: Optional[str] = None,
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    verified: Optional[bool] = None
):
    """Get reviews with filtering"""
    # Load data if not loaded
    if not data_loader.loaded:
        data_loader.load_data()
    
    if data_loader.df is None or data_loader.df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    # Calculate pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    # Get filtered data
    filters = {
        'category': category,
        'product': product,
        'min_rating': min_rating,
        'max_rating': max_rating,
        'verified': verified
    }
    
    # Remove None filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Get all filtered data
    all_reviews = data_loader.get_reviews(**filters)
    
    # Apply pagination
    paginated_reviews = all_reviews[start_idx:end_idx]
    
    # Convert to Review models
    reviews = []
    for item in paginated_reviews:
        try:
            review = Review(
                review_id=int(item.get('review_id', 0)),
                category=str(item.get('category', 'Unknown')),
                product_name=str(item.get('product_name', 'Unknown')),
                rating=int(item.get('rating', 0)),
                review_text=str(item.get('review_text', '')),
                reviewer=str(item.get('reviewer', 'Customer')),
                date=str(item.get('date', '')) if item.get('date') else None,
                verified=str(item.get('verified', 'No'))
            )
            reviews.append(review)
        except (ValueError, KeyError) as e:
            print(f"Error converting review: {e}")
            continue
    
    return reviews

@app.get("/reviews/{review_id}", response_model=Review)
async def get_review(review_id: int):
    """Get a specific review"""
    if not data_loader.loaded:
        data_loader.load_data()
    
    if data_loader.df is None or data_loader.df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    # Find review by ID
    review_df = data_loader.df[data_loader.df['review_id'] == review_id]
    
    if review_df.empty:
        raise HTTPException(status_code=404, detail="Review not found")
    
    item = review_df.iloc[0].to_dict()
    
    return Review(
        review_id=int(item.get('review_id', 0)),
        category=str(item.get('category', 'Unknown')),
        product_name=str(item.get('product_name', 'Unknown')),
        rating=int(item.get('rating', 0)),
        review_text=str(item.get('review_text', '')),
        reviewer=str(item.get('reviewer', 'Customer')),
        date=str(item.get('date', '')) if item.get('date') else None,
        verified=str(item.get('verified', 'No'))
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get dataset statistics"""
    stats = data_loader.get_stats()
    
    if not stats:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    return StatsResponse(
        total_reviews=stats.get('total_reviews', 0),
        total_products=stats.get('total_products', 0),
        categories=stats.get('categories', {}),
        ratings=stats.get('ratings', {}),
        verified_reviews=stats.get('verified_reviews', 0)
    )

@app.get("/products")
async def get_products():
    """Get all unique products"""
    if not data_loader.loaded:
        data_loader.load_data()
    
    if data_loader.df is None or data_loader.df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    if 'product_name' not in data_loader.df.columns:
        return {"products": [], "count": 0}
    
    products = data_loader.df['product_name'].unique().tolist()
    
    return {
        "products": products,
        "count": len(products)
    }

@app.get("/categories")
async def get_categories():
    """Get all categories"""
    if not data_loader.loaded:
        data_loader.load_data()
    
    if data_loader.df is None or data_loader.df.empty:
        raise HTTPException(status_code=404, detail="Dataset not loaded")
    
    if 'category' not in data_loader.df.columns:
        return {"categories": [], "count": 0}
    
    categories = data_loader.df['category'].unique().tolist()
    
    return {
        "categories": categories,
        "count": len(categories)
    }

@app.get("/search")
async def search_reviews(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """Search reviews by text"""
    results = data_loader.search_reviews(query, limit)
    
    formatted_results = []
    for item in results:
        formatted_results.append({
            "review_id": int(item.get('review_id', 0)),
            "category": str(item.get('category', 'Unknown')),
            "product_name": str(item.get('product_name', 'Unknown')),
            "rating": int(item.get('rating', 0)),
            "review_text": str(item.get('review_text', '')),
            "reviewer": str(item.get('reviewer', 'Customer'))
        })
    
    return {
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results)
    }

if __name__ == "__main__":
    import uvicorn
    # Pre-load data on startup
    data_loader.load_data()
    uvicorn.run(app, host="0.0.0.0", port=8000)