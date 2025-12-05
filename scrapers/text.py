# backend/test_app.py
from fastapi import FastAPI
import pandas as pd
from pathlib import Path

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Flipkart Reviews API", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test-data")
async def test_data():
    """Test if data loading works"""
    try:
        # Try to load data
        data_dir = Path("data")
        csv_files = list(data_dir.glob("flipkart_MASTER_DATASET_*.csv"))
        
        if not csv_files:
            return {"error": "No dataset found"}
        
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        
        return {
            "status": "success",
            "file": str(latest_file),
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(3).to_dict('records')
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)