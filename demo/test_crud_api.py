#!/usr/bin/env python3
"""
Test CRUD API endpoints
Kiểm tra các chức năng thêm, sửa, xóa sản phẩm qua API
"""

import requests
import json
import time
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:5000/api"

def test_api_health():
    """Test health check"""
    print("\n🔍 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health check passed")
            return True
        else:
            print(f"❌ API Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_add_product(product_data: Dict[str, str]):
    """Test add product"""
    print(f"\n📝 Testing Add Product: {product_data['name']}")
    try:
        response = requests.post(
            f"{BASE_URL}/products",
            json=product_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Product added successfully")
            print(f"   Product: {result['product']['name']} - {result['product']['brand']}")
            return True
        else:
            print(f"❌ Add product failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Add product error: {e}")
        return False

def test_search_products(query: str):
    """Test search products"""
    print(f"\n🔍 Testing Search: '{query}'")
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json={
                "query": query,
                "method": "bi_encoder",
                "top_k": 3
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search successful, found {len(result['results'])} results")
            for i, product in enumerate(result['results'][:2], 1):
                print(f"   {i}. {product['name']} - {product['brand']} (Score: {product['score']:.4f})")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def test_get_products():
    """Test get products list"""
    print(f"\n📋 Testing Get Products List...")
    try:
        response = requests.get(f"{BASE_URL}/products?limit=3")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Get products successful, total: {result['pagination']['total_count']}")
            for product in result['products'][:2]:
                print(f"   ID {product['id']}: {product['name']} - {product['brand']}")
            return result['products'][0]['id'] if result['products'] else None
        else:
            print(f"❌ Get products failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Get products error: {e}")
        return None

def test_update_product(product_id: int, update_data: Dict[str, str]):
    """Test update product"""
    print(f"\n✏️ Testing Update Product ID {product_id}")
    try:
        response = requests.put(
            f"{BASE_URL}/products/{product_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Product updated successfully")
            print(f"   Updated fields: {result['updated_fields']}")
            print(f"   Product: {result['product']['name']} - {result['product']['brand']}")
            return True
        else:
            print(f"❌ Update product failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Update product error: {e}")
        return False

def test_delete_product(product_id: int):
    """Test delete product"""
    print(f"\n🗑️ Testing Delete Product ID {product_id}")
    try:
        response = requests.delete(f"{BASE_URL}/products/{product_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Product deleted successfully")
            print(f"   Deleted: {result['deleted_product']['name']} - {result['deleted_product']['brand']}")
            return True
        else:
            print(f"❌ Delete product failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Delete product error: {e}")
        return False

def run_crud_tests():
    """Run complete CRUD tests"""
    print("🎯 TESTING CRUD API ENDPOINTS")
    print("="*60)
    
    # 1. Health check
    if not test_api_health():
        print("❌ API is not available. Make sure the server is running.")
        return
    
    # 2. Get existing products to check baseline
    existing_product_id = test_get_products()
    
    # 3. Add new test product
    test_product = {
        "name": "API Test Product",
        "brand": "Test Brand", 
        "ingredients": "Test ingredient 1, Test ingredient 2",
        "categories": "Test Category",
        "manufacturer": "Test Manufacturer",
        "manufacturerNumber": "TEST123"
    }
    
    add_success = test_add_product(test_product)
    
    # 4. Search for the new product
    if add_success:
        time.sleep(1)  # Wait for indexing
        test_search_products("API Test Product")
    
    # 5. Get updated products list
    updated_product_id = test_get_products()
    
    # 6. Update existing product (if available)
    if existing_product_id:
        update_data = {
            "name": "Updated Product Name",
            "manufacturer": "Updated Manufacturer"
        }
        test_update_product(existing_product_id, update_data)
    
    # 7. Search again to verify update
    if existing_product_id:
        time.sleep(1)  # Wait for indexing
        test_search_products("Updated Product")
    
    # Clean up - delete test product if we can find it
    # Note: In a real test, you'd want to track the added product ID
    
    print(f"\n🎉 CRUD API Tests Completed!")
    print("="*60)

if __name__ == "__main__":
    run_crud_tests()
