# add_products.py - Add products to the list
import os
from datetime import datetime

def add_products():
    """Add products to the list file"""
    print("📝 ADD PRODUCTS TO LIST")
    print("=" * 60)
    
    filename = "products_list.txt"
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found. Creating new file...")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Products List\n# Format: category | product_name\n\n")
    
    print(f"\nCurrent file: {filename}")
    print("Format: category | product_name")
    print("Example: smartphone | iPhone 15\n")
    
    # Show current content
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            if len(lines) > 0:
                print("📄 CURRENT CONTENT:")
                print("-" * 40)
                for line in lines[-10:]:  # Show last 10 lines
                    print(line)
                print("-" * 40)
    except:
        pass
    
    # Get new products
    print("\n➕ ADD NEW PRODUCTS (Enter blank line to finish):")
    
    new_products = []
    while True:
        category = input("\nCategory (e.g., smartphone, laptop, home): ").strip()
        if not category:
            break
        
        product_name = input("Product Name/Search Term: ").strip()
        if not product_name:
            break
        
        new_products.append(f"{category} | {product_name}")
        
        more = input("Add another product? (y/n): ").strip().lower()
        if more != 'y':
            break
    
    if new_products:
        # Add to file
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"\n# Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for product in new_products:
                f.write(f"{product}\n")
        
        print(f"\n✅ Added {len(new_products)} products to {filename}")
        
        # Show added products
        print("\n📋 ADDED PRODUCTS:")
        for product in new_products:
            print(f"   {product}")
    
    print(f"\n🎯 NEXT: Run 'python bulk_scraper_from_file.py' to scrape these products!")

def view_products():
    """View all products in the file"""
    print("👀 VIEW PRODUCTS LIST")
    print("=" * 60)
    
    filename = "products_list.txt"
    
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\nFile: {filename}")
    print("=" * 40)
    print(content)
    print("=" * 40)
    
    # Count products
    lines = content.strip().split('\n')
    product_count = 0
    categories = {}
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '|' in line:
                product_count += 1
                category = line.split('|')[0].strip()
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
    
    print(f"\n📊 STATS:")
    print(f"   Total products: {product_count}")
    print(f"   Categories: {len(categories)}")
    for cat, count in categories.items():
        print(f"      {cat}: {count} products")

def main():
    """Main menu"""
    print("📁 PRODUCT LIST MANAGER")
    print("=" * 60)
    
    while True:
        print("\n📋 MENU:")
        print("1. 📝 Add new products")
        print("2. 👀 View current products")
        print("3. 🚀 Start scraping")
        print("4. ❌ Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            add_products()
        elif choice == "2":
            view_products()
        elif choice == "3":
            print("\n🚀 Starting scraper...")
            os.system("python bulk_scraper_from_file.py")
            break
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()