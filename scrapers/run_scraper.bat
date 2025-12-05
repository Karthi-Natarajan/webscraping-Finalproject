@echo off
echo ========================================
echo 📁 FLIPKART BULK SCRAPER - FROM FILE
echo ========================================
echo.
echo This will:
echo 1. Read products from products_list.txt
echo 2. Search Flipkart for each product
echo 3. Scrape reviews from found products
echo 4. Save to CSV and MongoDB
echo.
echo Press any key to start...
pause > nul

python bulk_scraper_from_file.py

echo.
echo ========================================
echo 🎉 SCRAPING COMPLETED!
echo ========================================
echo.
echo Files created:
echo - flipkart_all_reviews_*.csv
echo - flipkart_all_reviews_*.xlsx
echo.
echo To add more products, run:
echo python add_products.py
echo.
pause