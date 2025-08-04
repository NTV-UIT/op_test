#!/usr/bin/env python3
"""
Test script cho Product Retrieval API
"""

import requests
import json
import time
from datetime import datetime


# API Base URL
BASE_URL = "http://localhost:5000/api"


def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_search():
    """Test search functionality"""
    print("\n🔍 Testing search...")
    
    search_requests = [
        {"query": "milk chocolate", "method": "hybrid", "top_k": 5},
        {"query": "organic protein", "method": "bi_encoder", "top_k": 3},
        {"query": "vitamin", "top_k": 7}  # Default method
    ]
    
    for i, search_data in enumerate(search_requests, 1):
        print(f"\n  Test {i}: {search_data}")
        try:
            response = requests.post(
                f"{BASE_URL}/search",
                json=search_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Found {data['total_results']} results")
                
                # Show top 2 results
                for j, result in enumerate(data['results'][:2], 1):
                    print(f"    {j}. {result['name']} - {result['brand']} (Score: {result['score']:.3f})")
            else:
                print(f"  ❌ Search failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Search error: {e}")


def test_add_product():
    """Test add product functionality"""
    print("\n➕ Testing add product...")
    
    new_product = {
        "name": "Test Product API",
        "brand": "Test Brand",
        "ingredients": "Water, Sugar, Test Ingredient",
        "categories": "Test Category",
        "manufacturer": "Test Manufacturer",
        "manufacturerNumber": "TEST-API-001"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/products",
            json=new_product,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            product_id = data['product_id']
            print(f"✅ Product added successfully with ID: {product_id}")
            return product_id
        else:
            print(f"❌ Add product failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Add product error: {e}")
        return None


def test_get_product(product_id):
    """Test get product by ID"""
    print(f"\n📋 Testing get product ID: {product_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}")
        
        if response.status_code == 200:
            data = response.json()
            product = data['product']
            print(f"✅ Product retrieved: {product['name']} - {product['brand']}")
            return product
        else:
            print(f"❌ Get product failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Get product error: {e}")
        return None


def test_update_product(product_id):
    """Test update product"""
    print(f"\n✏️ Testing update product ID: {product_id}...")
    
    updated_data = {
        "name": "Test Product API - Updated",
        "brand": "Test Brand Updated",
        "ingredients": "Water, Sugar, Test Ingredient, Updated Ingredient",
        "categories": "Test Category, Updated Category",
        "manufacturer": "Test Manufacturer Updated",
        "manufacturerNumber": "TEST-API-001-UPDATED"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/products/{product_id}",
            json=updated_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product updated successfully: {data['message']}")
            return True
        else:
            print(f"❌ Update product failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Update product error: {e}")
        return False


def test_list_products():
    """Test list products with pagination"""
    print("\n📋 Testing list products...")
    
    try:
        # Test basic listing
        response = requests.get(f"{BASE_URL}/products?page=1&limit=5")
        
        if response.status_code == 200:
            data = response.json()
            pagination = data['pagination']
            print(f"✅ Listed {len(data['products'])} products")
            print(f"   Total: {pagination['total_count']}, Pages: {pagination['total_pages']}")
            
            # Test search within listing
            response = requests.get(f"{BASE_URL}/products?search=test&limit=3")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Search listing found {len(data['products'])} products")
            
            return True
        else:
            print(f"❌ List products failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ List products error: {e}")
        return False


def test_statistics():
    """Test statistics endpoint"""
    print("\n📊 Testing statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data['statistics']
            print(f"✅ Statistics retrieved:")
            print(f"   Total products: {stats['total_products']}")
            print(f"   Total vectors: {stats['total_vectors']}")
            print(f"   Vector dimension: {stats['vector_dimension']}")
            return True
        else:
            print(f"❌ Statistics failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return False


def test_delete_product(product_id):
    """Test delete product"""
    print(f"\n🗑️ Testing delete product ID: {product_id}...")
    
    try:
        response = requests.delete(f"{BASE_URL}/products/{product_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product deleted successfully: {data['message']}")
            return True
        else:
            print(f"❌ Delete product failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Delete product error: {e}")
        return False


def test_search_after_operations():
    """Test search after CRUD operations"""
    print("\n🔍 Testing search after CRUD operations...")
    
    try:
        # Search for the updated product
        response = requests.post(
            f"{BASE_URL}/search",
            json={"query": "Updated", "top_k": 5},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search after operations found {data['total_results']} results")
            return True
        else:
            print(f"❌ Search after operations failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Search after operations error: {e}")
        return False


def run_comprehensive_test():
    """Run comprehensive API test"""
    print("🚀 STARTING COMPREHENSIVE API TEST")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Health check failed. API may not be running.")
        return
    
    # Test 2: Initial statistics
    test_statistics()
    
    # Test 3: List products
    test_list_products()
    
    # Test 4: Search functionality
    test_search()
    
    # Test 5: Add product
    product_id = test_add_product()
    if product_id is None:
        print("❌ Cannot continue without adding a product")
        return
    
    # Test 6: Get product
    product = test_get_product(product_id)
    
    # Test 7: Update product
    test_update_product(product_id)
    
    # Test 8: Get updated product
    test_get_product(product_id)
    
    # Test 9: Search after operations
    test_search_after_operations()
    
    # Test 10: Delete product
    test_delete_product(product_id)
    
    # Test 11: Final statistics
    test_statistics()
    
    print("\n" + "=" * 60)
    print("🏁 COMPREHENSIVE API TEST COMPLETED")


if __name__ == "__main__":
    print("🧪 Product Retrieval API Test Suite")
    print("Make sure the API server is running: python app.py")
    print()
    
    # Wait a moment for user to confirm
    input("Press Enter to start testing...")
    
    run_comprehensive_test()
