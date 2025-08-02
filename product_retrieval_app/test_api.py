#!/usr/bin/env python3
"""
Quick API Test Script for Product Retrieval System
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api():
    """Test basic API functionality"""
    print("🧪 Testing Product Retrieval System API...")
    print("="*50)
    
    # Test search endpoint
    print("1. Testing search endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/search", 
                               json={"query": "organic juice", "method": "hybrid", "top_k": 5})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search successful: {len(data.get('results', []))} results")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Search error: {e}")
    
    # Test add product endpoint
    print("\n2. Testing add product endpoint...")
    test_product = {
        "name": "Test Organic Juice",
        "brand": "TestBrand",
        "categories": "beverages",
        "ingredients": "organic apple juice, vitamin C",
        "manufacturer": "Test Manufacturer",
        "manufacturerNumber": "TEST001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/products", json=test_product)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Product added: ID {data.get('product_id')}")
            return data.get('product_id')
        else:
            print(f"   ❌ Add product failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Add product error: {e}")
    
    return None

def test_web_pages():
    """Test web page accessibility"""
    print("\n🌐 Testing web pages...")
    print("="*50)
    
    pages = [
        ("/", "Dashboard"),
        ("/search", "Search"),
        ("/admin", "Admin")
    ]
    
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}")
            if response.status_code == 200:
                print(f"   ✅ {name} page accessible")
            else:
                print(f"   ❌ {name} page failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name} page error: {e}")

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the application is running on http://localhost:5000")
    print("")
    
    # Wait for user confirmation
    input("Press Enter to continue with tests...")
    
    # Run tests
    product_id = test_api()
    test_web_pages()
    
    print("\n🎯 Test Summary:")
    print("If all tests passed, your Product Retrieval System is working correctly!")
    print("You can now use the web interface at http://localhost:5000")
