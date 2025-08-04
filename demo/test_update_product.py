#!/usr/bin/env python3
"""
Test script cho chức năng update sản phẩm
"""

import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.update_row import ProductUpdater


def test_update_product():
    """Test cập nhật sản phẩm"""
    print("🧪 TEST CHỨC NĂNG CẬP NHẬT SẢN PHẨM")
    print("=" * 50)
    
    try:
        # Khởi tạo updater
        updater = ProductUpdater()
        
        # Hiển thị một số sản phẩm mẫu
        print("\n📋 Danh sách sản phẩm hiện có:")
        updater.display_products(10)
        
        # Test update sản phẩm đầu tiên
        product_id = 0
        print(f"\n🎯 Test cập nhật sản phẩm ID: {product_id}")
        
        # Lấy thông tin hiện tại
        current_product = updater.data_df.iloc[product_id]
        print(f"\n📦 Thông tin hiện tại:")
        updater._display_product_details(product_id)
        
        # Tạo thông tin cập nhật mẫu
        updated_info = {
            'name': current_product['name'] + " - Updated",
            'brand': current_product['brand'],
            'ingredients': current_product.get('ingredients', '') + ", TEST_INGREDIENT",
            'categories': current_product.get('categories', '') + ", TEST_CATEGORY",
            'manufacturer': current_product.get('manufacturer', 'TEST_MANUFACTURER'),
            'manufacturerNumber': current_product.get('manufacturerNumber', 'TEST_001')
        }
        
        print(f"\n📝 Thông tin cập nhật:")
        for field, value in updated_info.items():
            print(f"{field}: {value}")
        
        # Thực hiện cập nhật
        success = updater.update_product(product_id, updated_info)
        
        if success:
            print("\n✅ Test cập nhật thành công!")
            
            # Hiển thị thông tin sau khi cập nhật
            print(f"\n📦 Thông tin sau khi cập nhật:")
            updater._display_product_details(product_id)
            
            # Test tìm kiếm với thông tin mới
            print(f"\n🔍 Test tìm kiếm với từ khóa 'Updated':")
            results = updater.search_products("Updated")
            if results:
                print(f"Tìm thấy {len(results)} sản phẩm có chứa 'Updated'")
                for idx in results[:3]:
                    row = updater.data_df.iloc[idx]
                    print(f"  ID: {idx} - {row['name']}")
            else:
                print("Không tìm thấy sản phẩm nào")
        else:
            print("\n❌ Test cập nhật thất bại!")
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {e}")
        import traceback
        traceback.print_exc()


def test_search_functionality():
    """Test chức năng tìm kiếm"""
    print("\n🔍 TEST CHỨC NĂNG TÌM KIẾM")
    print("=" * 40)
    
    try:
        updater = ProductUpdater()
        
        # Test tìm kiếm với một số từ khóa
        test_queries = ["milk", "chocolate", "organic", "protein"]
        
        for query in test_queries:
            print(f"\n🎯 Tìm kiếm: '{query}'")
            results = updater.search_products(query)
            print(f"Kết quả: {len(results)} sản phẩm")
            
            for idx in results[:3]:  # Hiển thị 3 kết quả đầu
                row = updater.data_df.iloc[idx]
                print(f"  ID: {idx} - {row['name'][:50]}")
                
    except Exception as e:
        print(f"❌ Lỗi test tìm kiếm: {e}")


def test_embedding_consistency():
    """Test tính nhất quán của embedding"""
    print("\n🔬 TEST TÍNH NHẤT QUÁN EMBEDDING")
    print("=" * 40)
    
    try:
        updater = ProductUpdater()
        
        # Kiểm tra shape của embeddings và index
        print(f"📊 Shape embeddings: {updater.embeddings.shape}")
        print(f"📚 Số vectors trong index: {updater.index.ntotal}")
        print(f"📋 Số sản phẩm trong CSV: {len(updater.data_df)}")
        
        # Kiểm tra consistency
        if (updater.embeddings.shape[0] == updater.index.ntotal == len(updater.data_df)):
            print("✅ Dữ liệu nhất quán!")
        else:
            print("❌ Dữ liệu không nhất quán!")
            
        # Test embedding dimension
        expected_dim = 1024  # BGE-large dimension
        if updater.embeddings.shape[1] == expected_dim:
            print(f"✅ Embedding dimension đúng: {expected_dim}")
        else:
            print(f"❌ Embedding dimension sai: {updater.embeddings.shape[1]} (expected: {expected_dim})")
            
    except Exception as e:
        print(f"❌ Lỗi test consistency: {e}")


if __name__ == "__main__":
    print("🚀 BẮT ĐẦU TEST CHỨC NĂNG UPDATE")
    print("=" * 60)
    
    # Test các chức năng
    test_embedding_consistency()
    test_search_functionality() 
    test_update_product()
    
    print("\n" + "=" * 60)
    print("🏁 HOÀN THÀNH TẤT CẢ TEST")
