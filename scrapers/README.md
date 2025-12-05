# Flipkart Reviews API

A FastAPI backend for accessing scraped Flipkart product reviews.

## Features
- 217+ product reviews across Electronics, Home Appliances, and Shoes
- RESTful API endpoints
- Filtering and pagination
- Search functionality
- Dataset statistics

## API Endpoints
- `GET /` - API documentation
- `GET /reviews` - Get reviews with filters
- `GET /reviews/{id}` - Get specific review
- `GET /stats` - Dataset statistics
- `GET /products` - List all products
- `GET /categories` - List all categories
- `GET /search` - Search reviews
- `GET /health` - Health check

## Local Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload"# backend" 
