# 🛒 Flipkart Reviews - Complete Project

A full-stack web application for scraping, analyzing, and visualizing Flipkart product reviews with 217+ reviews across 39+ products.

## 📁 Project Structure
FinalProjectCN/
├── backend/ # FastAPI backend (Deployed on Render)
├── frontend/ # React frontend
└── scrapers/ # Python scraping scripts

text

### 🚀 **Backend (FastAPI)**
- **Location**: `backend/`
- **Features**: REST API with filtering, pagination, search, statistics
- **Dataset**: 217+ reviews from 39+ Flipkart products
- **Live API**: https://flipkart-reviews-api.onrender.com
- **Docs**: https://flipkart-reviews-api.onrender.com/docs

### 🎨 **Frontend (React)**
- **Location**: `frontend/`
- **Features**: Interactive UI for searching/filtering reviews
- **Tech**: React, Vite, CSS

### 🕷️ **Scrapers (Python)**
- **Location**: `scrapers/`
- **Features**: Automated scraping from Flipkart
- **Tech**: Selenium, BeautifulSoup, Pandas
- **Categories**: Electronics, Home Appliances, Shoes

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload



API will be available at: http://localhost:8000

2. Frontend Setup
bash
cd frontend
npm install
npm run dev
Frontend will be available at: http://localhost:5173

📊 Dataset Statistics
Total Reviews: 217+

Total Products: 39+

Categories: Electronics, Home Appliances, Shoes

Data Collection: December 2025

🔧 Technologies Used
Backend: FastAPI, Pandas, Pydantic, Uvicorn

Frontend: React, Vite, CSS

Scraping: Selenium, BeautifulSoup, Pandas

Deployment: Render, Vercel

Version Control: Git, GitHub

📡 API Endpoints
text
GET  /health                    # Health check
GET  /stats                     # Dataset statistics
GET  /reviews                   # Get all reviews
GET  /reviews/{review_id}       # Get specific review
GET  /products                  # List all products
GET  /products/{product_id}     # Get specific product
GET  /search?query=...          # Search reviews
GET  /filter?category=...       # Filter by category
🚀 Deployment
Backend (Render)
Push to GitHub

Connect repo to Render.com

Set build command: cd backend && pip install -r requirements.txt

Set start command: cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT

Frontend (Vercel)
Connect frontend folder to Vercel

Automatic deployment from GitHub