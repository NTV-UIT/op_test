"""
Test script cho chức năng thêm sản phẩm
Demo thêm sản phẩm mới và test search
"""

from add_row import ProductManager

def test_add_product():
    """Test thêm sản phẩm mới"""
    print("🧪 TESTING PRODUCT ADDITION")
    print("="*50)
    
    # Tạo ProductManager
    manager = ProductManager()
    
    if manager.model is None:
        print("❌ Cannot test - models not loaded")
        return
    
    # Test data - sản phẩm mẫu
    test_products = [
        {
            'name': 'Organic Dark Chocolate Bar 85%',
            'brand': 'Green Valley Organic',
            'categories': 'chocolate, organic food, confectionery',
            'ingredients': 'organic cocoa beans, organic cocoa butter, organic raw cane sugar, vanilla extract',
            'manufacturer': 'green valley foods inc',
            'manufacturerNumber': 'GV-CHOC-001'
        },
        {
            'name': 'Premium Protein Powder Vanilla',
            'brand': 'FitLife Pro',
            'categories': 'supplements, protein, fitness',
            'ingredients': 'whey protein isolate, natural vanilla flavor, stevia leaf extract, sunflower lecithin',
            'manufacturer': 'fitlife nutrition',
            'manufacturerNumber': 'FL-PROT-VAN-002'
        },
        {
            'name': 'Gluten-Free Quinoa Bread',
            'brand': 'Healthy Choice',
            'categories': 'bread, gluten-free, quinoa',
            'ingredients': 'quinoa flour, rice flour, tapioca starch, xanthan gum, yeast, salt, olive oil',
            'manufacturer': 'healthy foods co',
            'manufacturerNumber': 'HC-BREAD-003'
        }
    ]
    
    print(f"Thêm {len(test_products)} sản phẩm test...")
    
    # Thêm từng sản phẩm
    for i, product in enumerate(test_products, 1):
        print(f"\n📦 Thêm sản phẩm {i}: {product['name']}")
        success = manager.add_product(product)
        
        if success:
            print(f"✅ Thành công!")
        else:
            print(f"❌ Thất bại!")
    
    # Test search với sản phẩm mới
    test_queries = [
        "organic chocolate",
        "protein powder vanilla", 
        "gluten free bread",
        "quinoa flour",
        "green valley"
    ]
    
    print(f"\n🔍 TESTING SEARCH với {len(test_queries)} queries...")
    
    for query in test_queries:
        print(f"\n" + "="*60)
        manager.search_test(query, top_k=3)
    
    print(f"\n✅ Test completed!")
    print(f"Database now has {len(manager.metadata_df)} products")

if __name__ == "__main__":
    test_add_product()
