"""
Test script cho chức năng xóa sản phẩm
Demo xóa sản phẩm và test tính năng
"""

from delete_row import ProductDeleter
from add_row import ProductManager

def test_delete_product():
    """Test chức năng xóa sản phẩm"""
    print("🧪 TESTING PRODUCT DELETION")
    print("="*50)
    
    # Tạo deleter
    deleter = ProductDeleter()
    
    if deleter.model is None:
        print("❌ Cannot test - models not loaded")
        return
    
    initial_count = len(deleter.metadata_df)
    print(f"📊 Initial product count: {initial_count}")
    
    if initial_count == 0:
        print("❌ No products to delete. Please add some products first.")
        return
    
    # Hiển thị một số sản phẩm
    print(f"\n📋 First 5 products:")
    for i in range(min(5, len(deleter.metadata_df))):
        row = deleter.metadata_df.iloc[i]
        print(f"   • ID {row['id']}: {row['name']} - {row['brand']}")
    
    # Test xóa bằng ID (xóa sản phẩm đầu tiên)
    if len(deleter.metadata_df) > 0:
        first_product_id = deleter.metadata_df.iloc[0]['id']
        first_product_name = deleter.metadata_df.iloc[0]['name']
        
        print(f"\n🗑️  Testing deletion of product ID {first_product_id}: {first_product_name}")
        
        # Confirm deletion
        confirm = input(f"Delete product ID {first_product_id}? (y/n) [default: n]: ").strip().lower()
        
        if confirm == 'y':
            success = deleter.delete_products([first_product_id])
            
            if success:
                print(f"✅ Successfully deleted product ID {first_product_id}")
                print(f"📊 Products remaining: {len(deleter.metadata_df)}")
                
                # Test search to verify deletion
                print(f"\n🔍 Testing search after deletion...")
                
                # Search for deleted product (should not be found)
                if deleter.model:
                    try:
                        query_embedding = deleter.model.encode(
                            [first_product_name],
                            normalize_embeddings=True,
                            device=deleter.device
                        )
                        
                        distances, indices = deleter.index.search(query_embedding, 3)
                        
                        print(f"Search results for '{first_product_name}':")
                        found_deleted = False
                        
                        for i, (idx, score) in enumerate(zip(indices[0], distances[0]), 1):
                            if idx == first_product_id:
                                found_deleted = True
                                print(f"❌ ERROR: Deleted product still found in index!")
                            else:
                                product_row = deleter.metadata_df[deleter.metadata_df['id'] == idx]
                                if not product_row.empty:
                                    row = product_row.iloc[0]
                                    print(f"   {i}. ID {idx}: {row['name']} - Score: {score:.4f}")
                        
                        if not found_deleted:
                            print("✅ Deleted product not found in search results (correct)")
                            
                    except Exception as e:
                        print(f"❌ Error during search test: {e}")
            
            else:
                print(f"❌ Failed to delete product ID {first_product_id}")
        else:
            print("❌ Deletion cancelled")
    
    print(f"\n✅ Test completed!")

def test_batch_delete():
    """Test xóa nhiều sản phẩm cùng lúc"""
    print("\n🧪 TESTING BATCH DELETION")
    print("="*50)
    
    deleter = ProductDeleter()
    
    if deleter.model is None or len(deleter.metadata_df) < 3:
        print("❌ Cannot test batch deletion - need at least 3 products")
        return
    
    # Lấy 2 sản phẩm đầu để test
    test_ids = deleter.metadata_df.head(2)['id'].tolist()
    
    print(f"Testing batch deletion of products: {test_ids}")
    for product_id in test_ids:
        row = deleter.metadata_df[deleter.metadata_df['id'] == product_id].iloc[0]
        print(f"   • ID {product_id}: {row['name']} - {row['brand']}")
    
    confirm = input(f"\nDelete {len(test_ids)} products? (y/n) [default: n]: ").strip().lower()
    
    if confirm == 'y':
        initial_count = len(deleter.metadata_df)
        success = deleter.delete_products(test_ids)
        
        if success:
            final_count = len(deleter.metadata_df)
            deleted_count = initial_count - final_count
            
            print(f"✅ Batch deletion successful!")
            print(f"   • Products deleted: {deleted_count}")
            print(f"   • Products remaining: {final_count}")
            print(f"   • Index vectors: {deleter.index.ntotal}")
            
            if final_count == deleter.index.ntotal:
                print("✅ Metadata and index counts match")
            else:
                print("❌ Metadata and index counts mismatch!")
        else:
            print("❌ Batch deletion failed")
    else:
        print("❌ Batch deletion cancelled")

if __name__ == "__main__":
    # Test individual deletion
    test_delete_product()
    
    # Test batch deletion
    test_batch_delete()
