# backend/app.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import time
import os
import pandas as pd
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

# Global variables for cold start handling
app_start_time = time.time()
is_warm = False

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

def show_loading_page():
    """Show loading page during cold start"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipkart Reviews API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .loader-container {
                margin: 30px 0;
            }
            .loader {
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                margin: 20px 0;
                overflow: hidden;
            }
            .progress {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #8BC34A);
                animation: progress-animation 2s ease-in-out infinite alternate;
            }
            @keyframes progress-animation {
                0% { width: 0%; }
                100% { width: 100%; }
            }
            .info-box {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: left;
            }
            .endpoints {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-top: 20px;
            }
            .endpoint {
                background: rgba(255, 255, 255, 0.1);
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Flipkart Reviews API</h1>
            <div class="loader-container">
                <div class="loader"></div>
            </div>
            <div class="progress-bar">
                <div class="progress"></div>
            </div>
            
            <div class="info-box">
                <p><strong>⏰ Service is waking up...</strong></p>
                <p>Free tier services on Render sleep after 15 minutes of inactivity.</p>
                <p>First request takes 30-60 seconds to wake up.</p>
                <p>Page will auto-refresh when ready.</p>
            </div>
            
            <h3>📡 Live Endpoints:</h3>
            <div class="endpoints">
                <div class="endpoint">GET /health</div>
                <div class="endpoint">GET /docs</div>
                <div class="endpoint">GET /reviews</div>
                <div class="endpoint">GET /stats</div>
            </div>
            
            <script>
                // Show loading progress
                let timeElapsed = 0;
                const progressElement = document.querySelector('.progress');
                
                const updateProgress = () => {
                    timeElapsed += 1;
                    const progress = Math.min((timeElapsed / 30) * 100, 100);
                    
                    if (timeElapsed >= 30) {
                        // Try to load the API after 30 seconds
                        fetch('/health')
                            .then(response => {
                                if (response.ok) {
                                    window.location.reload();
                                }
                            })
                            .catch(() => {
                                // Continue trying
                                setTimeout(() => window.location.reload(), 5000);
                            });
                    }
                };
                
                // Update every second
                setInterval(updateProgress, 1000);
                
                // Auto-refresh as backup
                setTimeout(() => {
                    window.location.reload();
                }, 35000);
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with cold start handling"""
    global is_warm
    
    # Check if we're in cold start phase (first 45 seconds)
    if not is_warm and time.time() - app_start_time < 45:
        return show_loading_page()
    
    # Mark as warm after first successful load
    is_warm = True
    
    # Load data if not loaded
    if not data_loader.loaded:
        data_loader.load_data()
    
    # Show API info page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipkart Reviews API</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }}
            .header {{
                text-align: center;
                padding: 40px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            }}
            h1 {{
                font-size: 3em;
                margin: 0;
            }}
            .tagline {{
                font-size: 1.2em;
                opacity: 0.9;
                margin-top: 10px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }}
            .endpoints-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            .endpoint-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
                border-left: 5px solid #667eea;
            }}
            .method {{
                display: inline-block;
                padding: 5px 10px;
                background: #667eea;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 10px;
            }}
            .path {{
                font-family: monospace;
                background: #f5f5f5;
                padding: 5px 10px;
                border-radius: 5px;
                display: block;
                margin: 10px 0;
            }}
            .buttons {{
                text-align: center;
                margin: 40px 0;
            }}
            .btn {{
                display: inline-block;
                padding: 15px 30px;
                margin: 0 10px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            .btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }}
            .btn-docs {{
                background: #764ba2;
            }}
            .status-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #4CAF50;
                border-radius: 50%;
                margin-right: 8px;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Flipkart Reviews API</h1>
            <p class="tagline">Access 217+ Flipkart product reviews across 39+ products</p>
            <div style="margin-top: 20px;">
                <span class="status-indicator"></span>
                <strong>Status: </strong>
                <span id="status">Checking...</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div>📊 Total Reviews</div>
                <div class="stat-number" id="total-reviews">Loading...</div>
                <div>from 217+ dataset</div>
            </div>
            <div class="stat-card">
                <div>📦 Total Products</div>
                <div class="stat-number" id="total-products">Loading...</div>
                <div>39+ products</div>
            </div>
            <div class="stat-card">
                <div>🏷️ Categories</div>
                <div class="stat-number" id="categories">3</div>
                <div>Electronics, Home Appliances, Shoes</div>
            </div>
        </div>
        
        <div class="buttons">
            <a href="/docs" class="btn btn-docs">📚 Interactive API Docs</a>
            <a href="/reviews" class="btn">📋 View All Reviews</a>
            <a href="https://github.com/Karthi-Natarajan/FinalProject-Webscraping" class="btn" target="_blank">💻 GitHub Repository</a>
        </div>
        
        <h2>📡 Available Endpoints</h2>
        <div class="endpoints-grid">
            <div class="endpoint-card">
                <span class="method">GET</span>
                <strong>Health Check</strong>
                <div class="path">/health</div>
                <p>Check API health status</p>
            </div>
            <div class="endpoint-card">
                <span class="method">GET</span>
                <strong>Dataset Statistics</strong>
                <div class="path">/stats</div>
                <p>Get dataset stats and metrics</p>
            </div>
            <div class="endpoint-card">
                <span class="method">GET</span>
                <strong>All Reviews</strong>
                <div class="path">/reviews</div>
                <p>Get all reviews with pagination</p>
            </div>
            <div class="endpoint-card">
                <span class="method">GET</span>
                <strong>Search Reviews</strong>
                <div class="path">/search?q=query</div>
                <p>Search reviews by text</p>
            </div>
            <div class="endpoint-card">
                <span class="method">GET</span>
                <strong>Get Product</strong>
                <div class="path">/products</div>
                <p>List all unique products</p>
            </div>
            <div class="endpoint-card">
                <span class="method">GET</span>
                <strong>Filter Reviews</strong>
                <div class="path">/reviews?category=electronics</div>
                <p>Filter by category, rating, etc.</p>
            </div>
        </div>
        
        <div class="buttons" style="margin-top: 40px;">
            <a href="/" class="btn">🔄 Test Now</a>
        </div>
        
        <script>
            // Fetch real-time stats on page load
            async function loadStats() {{
                try {{
                    // Check health
                    const healthResponse = await fetch('/health');
                    if (healthResponse.ok) {{
                        document.getElementById('status').innerHTML = '<strong style="color: #4CAF50;">✓ Online & Healthy</strong>';
                    }}
                    
                    // Load stats
                    const statsResponse = await fetch('/stats');
                    if (statsResponse.ok) {{
                        const stats = await statsResponse.json();
                        document.getElementById('total-reviews').textContent = stats.total_reviews;
                        document.getElementById('total-products').textContent = stats.total_products;
                        document.getElementById('categories').textContent = Object.keys(stats.categories).length;
                    }}
                }} catch (error) {{
                    console.error('Error loading stats:', error);
                    document.getElementById('status').innerHTML = '<strong style="color: #f44336;">✗ Connection Error</strong>';
                }}
            }}
            
            // Load stats when page loads
            loadStats();
            
            // Auto-refresh stats every 30 seconds
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint - also keeps service awake"""
    global is_warm
    is_warm = True
    
    try:
        # Try to load data to verify everything works
        if not data_loader.loaded:
            data_loader.load_data()
        
        loaded = data_loader.loaded
        review_count = len(data_loader.df) if loaded else 0
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "dataset_loaded": loaded,
            "reviews_count": review_count,
            "service": "Flipkart Reviews API",
            "version": "2.0.0",
            "uptime": time.time() - app_start_time
        }
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "service": "Flipkart Reviews API"
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
    # Mark service as warm
    global is_warm
    is_warm = True
    
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
    # Mark service as warm
    global is_warm
    is_warm = True
    
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
    # Mark service as warm
    global is_warm
    is_warm = True
    
    if not data_loader.loaded:
        data_loader.load_data()
    
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
    # Mark service as warm
    global is_warm
    is_warm = True
    
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
    # Mark service as warm
    global is_warm
    is_warm = True
    
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
    # Mark service as warm
    global is_warm
    is_warm = True
    
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

# Pre-load data when app starts (but don't block startup)
@app.on_event("startup")
async def startup_event():
    """Pre-load data in background on startup"""
    global app_start_time
    app_start_time = time.time()
    
    # Load data in background to avoid blocking startup
    import threading
    def load_data_background():
        try:
            data_loader.load_data()
            print(f"✅ Dataset loaded successfully: {len(data_loader.df)} reviews")
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
    
    thread = threading.Thread(target=load_data_background)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    import uvicorn
    # Pre-load data on startup
    data_loader.load_data()
    uvicorn.run(app, host="0.0.0.0", port=8000)