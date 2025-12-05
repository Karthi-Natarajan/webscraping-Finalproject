# combine_datasets_fixed.py
import pandas as pd
import glob
import os
from datetime import datetime
import json

def combine_all_reviews():
    """Combine all scraped CSV files into one master dataset"""
    print("=" * 70)
    print("🔄 COMBINING ALL DATASETS")
    print("=" * 70)
    
    # Find all CSV files
    csv_files = glob.glob("flipkart_*.csv")
    
    # Remove master datasets from list
    csv_files = [f for f in csv_files if "MASTER_DATASET" not in f]
    
    if not csv_files:
        print("❌ No CSV files found!")
        print("Please run scrapers first.")
        return None
    
    print(f"📂 Found {len(csv_files)} CSV files:")
    for file in csv_files:
        size_kb = os.path.getsize(file) / 1024
        print(f"   - {os.path.basename(file)} ({size_kb:.1f} KB)")
    
    # Load and combine all files
    all_dfs = []
    
    for file in csv_files:
        try:
            print(f"\n📥 Loading: {os.path.basename(file)}")
            
            # Try different encodings
            try:
                df = pd.read_csv(file, encoding='utf-8-sig')
            except:
                try:
                    df = pd.read_csv(file, encoding='latin1')
                except:
                    df = pd.read_csv(file)
            
            print(f"   Original shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            
            # Check if review_id exists
            if 'review_id' in df.columns:
                print(f"   ✓ Has review_id column")
                # Remove existing review_id, we'll create new one
                df = df.drop(columns=['review_id'])
            
            # Standardize column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Add source info
            df['source_file'] = os.path.basename(file)
            
            # Determine category
            filename = file.lower()
            if 'phase2' in filename or 'home' in filename or 'appliance' in filename or 'shoe' in filename:
                df['scrape_phase'] = 'Phase 2'
                # Auto-assign category if missing
                if 'category' not in df.columns:
                    if 'shoe' in filename:
                        df['category'] = 'Shoes'
                    else:
                        df['category'] = 'Home Appliances'
            else:
                df['scrape_phase'] = 'Phase 1'
                if 'category' not in df.columns:
                    df['category'] = 'Electronics'
            
            # Fix rating column
            if 'rating' in df.columns:
                df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
                df['rating'] = df['rating'].fillna(0).astype(int).clip(1, 5)
            
            all_dfs.append(df)
            print(f"   ✅ Loaded {len(df)} rows")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            continue
    
    if not all_dfs:
        print("\n❌ No data loaded!")
        return None
    
    # Combine all dataframes
    print(f"\n🔗 Combining {len(all_dfs)} dataframes...")
    combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)
    
    # Create new review_id
    combined_df.insert(0, 'review_id', range(1, len(combined_df) + 1))
    
    # Clean data
    if 'verified' in combined_df.columns:
        combined_df['verified'] = combined_df['verified'].astype(str).str.lower()
        combined_df['verified'] = combined_df['verified'].apply(
            lambda x: 'Yes' if x in ['yes', 'true', '1', 'verified'] else 'No'
        )
    
    # Remove duplicates based on review text
    if 'review_text' in combined_df.columns:
        before = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['review_text'], keep='first')
        after = len(combined_df)
        print(f"   Removed {before - after} duplicate reviews")
    
    # Save master dataset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    master_file = f"flipkart_MASTER_DATASET_{timestamp}.csv"
    
    # Define column order
    column_order = ['review_id', 'category', 'product_name', 'rating', 
                   'review_text', 'reviewer', 'date', 'verified',
                   'product_url', 'scraped_date', 'scrape_phase', 'source_file']
    
    # Select only existing columns
    existing_cols = [col for col in column_order if col in combined_df.columns]
    combined_df = combined_df[existing_cols]
    
    combined_df.to_csv(master_file, index=False, encoding='utf-8-sig')
    
    print(f"\n🎉 MASTER DATASET CREATED!")
    print(f"📊 Total reviews: {len(combined_df):,}")
    print(f"📁 File: {master_file}")
    print(f"📏 Size: {os.path.getsize(master_file)/1024/1024:.2f} MB")
    
    # Generate statistics
    print(f"\n📈 DATASET STATISTICS:")
    print(f"   Total unique reviews: {len(combined_df):,}")
    
    # Category stats
    if 'category' in combined_df.columns:
        print(f"\n   📦 CATEGORIES:")
        cat_stats = combined_df['category'].value_counts()
        for cat, count in cat_stats.items():
            percent = (count / len(combined_df)) * 100
            print(f"     {cat}: {count:,} ({percent:.1f}%)")
    
    # Rating stats
    if 'rating' in combined_df.columns:
        print(f"\n   ⭐ RATINGS:")
        for rating in range(1, 6):
            count = (combined_df['rating'] == rating).sum()
            percent = (count / len(combined_df)) * 100
            stars = '★' * rating
            print(f"     {stars} ({rating}): {count:,} ({percent:.1f}%)")
    
    # Scrape phase stats
    if 'scrape_phase' in combined_df.columns:
        print(f"\n   📋 SCRAPE PHASES:")
        phase_stats = combined_df['scrape_phase'].value_counts()
        for phase, count in phase_stats.items():
            print(f"     {phase}: {count:,}")
    
    # Save summary
    summary_file = f"dataset_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("FLIPKART REVIEWS MASTER DATASET SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Reviews: {len(combined_df):,}\n")
        f.write(f"Source Files: {len(csv_files)}\n")
        f.write(f"Master File: {master_file}\n\n")
        
        f.write("CATEGORIES:\n")
        if 'category' in combined_df.columns:
            for cat, count in cat_stats.items():
                f.write(f"  {cat}: {count:,}\n")
        
        f.write("\nRATINGS:\n")
        if 'rating' in combined_df.columns:
            for rating in range(1, 6):
                count = (combined_df['rating'] == rating).sum()
                f.write(f"  {rating} stars: {count:,}\n")
    
    print(f"\n📝 Summary saved: {summary_file}")
    
    # Export other formats
    print(f"\n🚀 EXPORTING OTHER FORMATS:")
    
    # JSON
    json_file = master_file.replace('.csv', '.json')
    combined_df.to_json(json_file, orient='records', indent=2)
    print(f"   ✅ JSON: {json_file}")
    
    # Clean version
    clean_cols = ['review_id', 'category', 'product_name', 'rating', 
                 'review_text', 'reviewer', 'date', 'verified']
    clean_df = combined_df[[c for c in clean_cols if c in combined_df.columns]]
    clean_file = f"clean_reviews_{timestamp}.csv"
    clean_df.to_csv(clean_file, index=False)
    print(f"   ✅ Clean CSV: {clean_file}")
    
    # Sample
    sample_size = min(100, len(combined_df))
    sample_df = combined_df.sample(n=sample_size, random_state=42)
    sample_file = f"sample_{timestamp}.csv"
    sample_df.to_csv(sample_file, index=False)
    print(f"   ✅ Sample ({sample_size}): {sample_file}")
    
    print(f"\n📂 All files saved in: {os.getcwd()}")
    
    return combined_df

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔄 FLIPKART REVIEWS DATA COMBINER")
    print("=" * 70)
    print("This script combines Phase 1 and Phase 2 data.")
    print("Make sure you have CSV files from both phases.\n")
    
    master_df = combine_all_reviews()
    
    if master_df is not None:
        print(f"\n✅ DATASET READY FOR BACKEND!")
        print(f"📦 Total Reviews: {len(master_df):,}")
        print(f"📊 Categories: {master_df['category'].nunique() if 'category' in master_df.columns else 0}")
        print(f"\n🚀 Next: Deploy to Render with FastAPI")