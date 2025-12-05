# setup_environment.py - Setup environment for scraping
import subprocess
import sys
import os

print("🛠️ SETTING UP SCRAPING ENVIRONMENT")
print("=" * 60)

def install_packages():
    """Install required packages"""
    packages = [
        'selenium',
        'webdriver-manager', 
        'pymongo',
        'textblob',
        'pandas',
        'openpyxl',
        'certifi'
    ]
    
    print("📦 Installing packages...")
    for package in packages:
        print(f"   Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
    
    print("\n✅ All packages installed!")

def download_nltk_data():
    """Download NLTK data for TextBlob"""
    print("\n📚 Downloading NLTK data for sentiment analysis...")
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('brown')
        print("✅ NLTK data downloaded")
    except Exception as e:
        print(f"⚠️ NLTK download skipped: {e}")

def create_folders():
    """Create necessary folders"""
    print("\n📁 Creating folders...")
    folders = ['data', 'exports', 'screenshots', 'logs']
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"   Created: {folder}/")
        else:
            print(f"   Exists: {folder}/")
    
    print("✅ Folders created")

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🌐 Checking Chrome browser...")
    try:
        import webbrowser
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome"
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"   ✅ Chrome found at: {path}")
                chrome_found = True
                break
        
        if not chrome_found:
            print("   ⚠️ Chrome not found in standard locations")
            print("   ℹ️ Make sure Chrome is installed for Selenium to work")
        else:
            print("   ✅ Chrome is ready")
            
    except Exception as e:
        print(f"   ⚠️ Chrome check failed: {e}")

def test_mongodb():
    """Test MongoDB connection"""
    print("\n🗄️ Testing MongoDB connection...")
    try:
        from pymongo import MongoClient
        import certifi
        
        MONGO_URL = "mongodb+srv://skarthinatarajan21_db_user:skn212005@cluster0.ebtw7zu.mongodb.net/sentimentDB"
        client = MongoClient(MONGO_URL, tls=True, tlsCAFile=certifi.where())
        
        # Test connection
        client.admin.command('ping')
        print("   ✅ MongoDB connection successful!")
        
        # Show database info
        db = client["sentiment_analysis_db"]
        collections = db.list_collection_names()
        print(f"   📊 Database: sentiment_analysis_db")
        print(f"   📁 Collections: {', '.join(collections)}")
        
        client.close()
        
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {e}")
        print("   ℹ️ Make sure the connection string is correct")

def main():
    """Main setup function"""
    print("🎯 FLIPKART SCRAPER SETUP")
    print("=" * 60)
    
    print("\n1. Installing packages...")
    install_packages()
    
    print("\n2. Downloading NLTK data...")
    download_nltk_data()
    
    print("\n3. Creating folders...")
    create_folders()
    
    print("\n4. Checking Chrome...")
    check_chrome()
    
    print("\n5. Testing MongoDB...")
    test_mongodb()
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Run: python bulk_scraper.py")
    print("2. Enter 'iPhone 15' when prompted")
    print("3. Choose default options")
    print("4. Check the CSV files created")
    print("\n💡 TIP: If scraping fails, try:")
    print("   - Using a VPN")
    print("   - Running test_scraper.py first")
    print("   - Checking your internet connection")

if __name__ == "__main__":
    main()