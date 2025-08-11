"""
Chức năng xóa sản phẩm khỏi cơ sở dữ liệu
- Tương tác với product_metadata để chọn sản phẩm cần xóa
- Xóa vector tương ứng khỏi FAISS index
- Cập nhật lại index và ID mapping
"""

import os
import sys
import pandas as pd
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import time
from typing import List, Optional, Union

# Add config path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_config import (
    EMBEDDING_MODEL_NAME, DATA_PATHS, MAX_LENGTH, BATCH_SIZE, get_device,
    get_global_embedding_model, monitor_gpu_memory
)

class ProductDeleter:
    """Quản lý xóa sản phẩm khỏi database"""
    
    def __init__(self):
        """Khởi tạo ProductDeleter"""
        self.device = get_device()
        self.model = None
        self.tokenizer = None
        self.index = None
        self.metadata_df = None
        self._load_models_and_data()
    
    def reload_data(self):
        """Reload dữ liệu từ file (dùng khi có thay đổi từ module khác)"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(DATA_PATHS['faiss_index'])
            
            # Load metadata
            self.metadata_df = pd.read_csv(DATA_PATHS['metadata'])
            
            print(f"✅ Reloaded {len(self.metadata_df)} products")
            print(f"✅ Index has {self.index.ntotal} vectors")
            
        except Exception as e:
            print(f"❌ Error reloading data: {e}")
    
    def _load_models_and_data(self):
        """Load models và dữ liệu hiện tại"""
        try:
            print("🔄 Loading models and data...")
            
            # ✅ Sử dụng global model
            self.model, self.tokenizer = get_global_embedding_model()
            print("✅ Using global embedding model")
            
            # Load FAISS index
            self.index = faiss.read_index(DATA_PATHS['faiss_index'])
            
            # Load metadata
            self.metadata_df = pd.read_csv(DATA_PATHS['metadata'])
            
            print(f"✅ Loaded {len(self.metadata_df)} products")
            print(f"✅ Index has {self.index.ntotal} vectors")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading files: {e}")
            print("Please run preprocess.py and embedding.py first")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def display_products(self, page_size: int = 10, page: int = 0) -> bool:
        """Hiển thị danh sách sản phẩm với phân trang"""
        if self.metadata_df is None or len(self.metadata_df) == 0:
            print("❌ Không có sản phẩm nào trong database")
            return False
        
        total_products = len(self.metadata_df)
        total_pages = (total_products + page_size - 1) // page_size
        
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, total_products)
        
        print(f"\n📋 DANH SÁCH SẢN PHẨM (Trang {page + 1}/{total_pages})")
        print("="*80)
        print(f"{'ID':<5} {'Tên sản phẩm':<30} {'Thương hiệu':<20} {'Text corpus':<25}")
        print("-"*80)
        
        for idx in range(start_idx, end_idx):
            row = self.metadata_df.iloc[idx]
            text_preview = row['text_corpus'][:22] + "..." if len(row['text_corpus']) > 25 else row['text_corpus']
            print(f"{row['id']:<5} {row['name'][:27]+'...' if len(row['name']) > 30 else row['name']:<30} "
                  f"{row['brand'][:17]+'...' if len(row['brand']) > 20 else row['brand']:<20} {text_preview:<25}")
        
        print(f"\nHiển thị {start_idx + 1}-{end_idx} của {total_products} sản phẩm")
        return True
    
    def search_products(self, query: str) -> List[dict]:
        """Tìm kiếm sản phẩm theo từ khóa"""
        if self.metadata_df is None:
            return []
        
        # Tìm kiếm trong name, brand, text_corpus
        mask = (
            self.metadata_df['name'].str.contains(query, case=False, na=False) |
            self.metadata_df['brand'].str.contains(query, case=False, na=False) |
            self.metadata_df['text_corpus'].str.contains(query, case=False, na=False)
        )
        
        results = self.metadata_df[mask].to_dict('records')
        return results
    
    def select_products_to_delete(self) -> Optional[List[int]]:
        """Tương tác để chọn sản phẩm cần xóa"""
        print("\n🗑️  CHỌN SẢN PHẨM CẦN XÓA")
        print("="*50)
        print("Chọn phương thức:")
        print("1. Xóa theo ID")
        print("2. Tìm kiếm và chọn")
        print("3. Xem danh sách và chọn")
        print("4. Hủy bỏ")
        
        choice = input("\nNhập lựa chọn (1-4): ").strip()
        
        if choice == '1':
            return self._delete_by_id()
        elif choice == '2':
            return self._delete_by_search()
        elif choice == '3':
            return self._delete_by_list()
        elif choice == '4':
            print("❌ Hủy bỏ xóa sản phẩm")
            return None
        else:
            print("❌ Lựa chọn không hợp lệ")
            return None
    
    def _delete_by_id(self) -> Optional[List[int]]:
        """Xóa theo ID"""
        try:
            id_input = input("Nhập ID sản phẩm cần xóa (có thể nhập nhiều ID cách nhau bằng dấu phẩy): ").strip()
            
            if not id_input:
                return None
            
            # Parse IDs
            id_list = [int(x.strip()) for x in id_input.split(',') if x.strip().isdigit()]
            
            if not id_list:
                print("❌ Không có ID hợp lệ")
                return None
            
            # Kiểm tra ID có tồn tại không
            existing_ids = self.metadata_df['id'].tolist()
            valid_ids = [id for id in id_list if id in existing_ids]
            invalid_ids = [id for id in id_list if id not in existing_ids]
            
            if invalid_ids:
                print(f"⚠️  ID không tồn tại: {invalid_ids}")
            
            if not valid_ids:
                print("❌ Không có ID hợp lệ để xóa")
                return None
            
            # Hiển thị sản phẩm sẽ bị xóa
            print(f"\n📋 Sản phẩm sẽ bị xóa:")
            for product_id in valid_ids:
                row = self.metadata_df[self.metadata_df['id'] == product_id].iloc[0]
                print(f"   • ID {product_id}: {row['name']} - {row['brand']}")
            
            confirm = input(f"\n⚠️  Xác nhận xóa {len(valid_ids)} sản phẩm? (y/n) [default: n]: ").strip().lower()
            if confirm == 'y':
                return valid_ids
            else:
                print("❌ Hủy bỏ xóa sản phẩm")
                return None
                
        except ValueError:
            print("❌ ID phải là số nguyên")
            return None
    
    def _delete_by_search(self) -> Optional[List[int]]:
        """Xóa thông qua tìm kiếm"""
        query = input("Nhập từ khóa tìm kiếm: ").strip()
        
        if not query:
            return None
        
        results = self.search_products(query)
        
        if not results:
            print("❌ Không tìm thấy sản phẩm nào")
            return None
        
        print(f"\n🔍 Tìm thấy {len(results)} sản phẩm:")
        print("-"*70)
        for i, product in enumerate(results, 1):
            print(f"{i}. ID {product['id']}: {product['name']} - {product['brand']}")
        
        # Chọn sản phẩm để xóa
        selection = input(f"\nNhập số thứ tự cần xóa (1-{len(results)}, có thể nhập nhiều số cách nhau bằng dấu phẩy): ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip().isdigit()]
            valid_indices = [i for i in indices if 0 <= i < len(results)]
            
            if not valid_indices:
                print("❌ Không có lựa chọn hợp lệ")
                return None
            
            selected_ids = [results[i]['id'] for i in valid_indices]
            
            print(f"\n📋 Sản phẩm sẽ bị xóa:")
            for i in valid_indices:
                product = results[i]
                print(f"   • ID {product['id']}: {product['name']} - {product['brand']}")
            
            confirm = input(f"\n⚠️  Xác nhận xóa {len(selected_ids)} sản phẩm? (y/n) [default: n]: ").strip().lower()
            if confirm == 'y':
                return selected_ids
            else:
                print("❌ Hủy bỏ xóa sản phẩm")
                return None
                
        except ValueError:
            print("❌ Lựa chọn không hợp lệ")
            return None
    
    def _delete_by_list(self) -> Optional[List[int]]:
        """Xóa thông qua xem danh sách"""
        page = 0
        page_size = 10
        
        while True:
            if not self.display_products(page_size, page):
                return None
            
            total_pages = (len(self.metadata_df) + page_size - 1) // page_size
            
            print(f"\nLựa chọn:")
            print("• Nhập ID cần xóa (có thể nhập nhiều ID cách nhau bằng dấu phẩy)")
            if page > 0:
                print("• 'prev' để xem trang trước")
            if page < total_pages - 1:
                print("• 'next' để xem trang tiếp")
            print("• 'cancel' để hủy bỏ")
            
            choice = input("\nNhập lựa chọn: ").strip().lower()
            
            if choice == 'cancel':
                return None
            elif choice == 'prev' and page > 0:
                page -= 1
            elif choice == 'next' and page < total_pages - 1:
                page += 1
            else:
                # Thử parse như ID
                try:
                    id_list = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                    
                    if id_list:
                        existing_ids = self.metadata_df['id'].tolist()
                        valid_ids = [id for id in id_list if id in existing_ids]
                        
                        if valid_ids:
                            print(f"\n📋 Sản phẩm sẽ bị xóa:")
                            for product_id in valid_ids:
                                row = self.metadata_df[self.metadata_df['id'] == product_id].iloc[0]
                                print(f"   • ID {product_id}: {row['name']} - {row['brand']}")
                            
                            confirm = input(f"\n⚠️  Xác nhận xóa {len(valid_ids)} sản phẩm? (y/n) [default: n]: ").strip().lower()
                            if confirm == 'y':
                                return valid_ids
                        else:
                            print("❌ ID không hợp lệ")
                    else:
                        print("❌ Lựa chọn không hợp lệ")
                except ValueError:
                    print("❌ Lựa chọn không hợp lệ")
    
    def delete_products(self, product_ids: List[int]) -> bool:
        """Xóa sản phẩm khỏi database và vector index"""
        if self.metadata_df is None or self.index is None:
            print("❌ Database chưa được load")
            return False
        
        try:
            print(f"\n🔄 Đang xóa {len(product_ids)} sản phẩm...")
            
            # 1. Kiểm tra ID có tồn tại không và chuyển từ ID sang index
            existing_ids = self.metadata_df['id'].tolist()
            valid_ids = [id for id in product_ids if id in existing_ids]
            
            if not valid_ids:
                print("❌ Không có ID hợp lệ để xóa")
                return False
            
            # 2. Chuyển từ ID sang index để xóa
            indices_to_delete = []
            deleted_products = []
            
            for product_id in valid_ids:
                # Tìm index của product_id trong DataFrame
                idx = self.metadata_df[self.metadata_df['id'] == product_id].index[0]
                indices_to_delete.append(idx)
                
                # Lưu thông tin sản phẩm bị xóa (để log)
                row = self.metadata_df.iloc[idx]
                deleted_products.append({
                    'id': product_id,
                    'name': row['name'],
                    'brand': row['brand']
                })
            
            # 3. Load embeddings hiện tại
            embeddings_file = DATA_PATHS['embeddings']
            if os.path.exists(embeddings_file):
                old_embeddings = np.load(embeddings_file)
            else:
                print("❌ Không tìm thấy file embeddings")
                return False
            
            # 4. Kiểm tra consistency và tạo mask
            print(f"🔍 Debug info:")
            print(f"   Metadata rows: {len(self.metadata_df)}")
            print(f"   Embeddings rows: {len(old_embeddings)}")
            print(f"   Indices to delete: {indices_to_delete}")
            
            # Sử dụng kích thước nhỏ hơn để đảm bảo không có lỗi index
            effective_size = min(len(self.metadata_df), len(old_embeddings))
            
            # Tạo mask để giữ lại các hàng không bị xóa
            keep_mask = np.ones(effective_size, dtype=bool)
            valid_indices = [idx for idx in indices_to_delete if idx < effective_size]
            
            if len(valid_indices) != len(indices_to_delete):
                print(f"⚠️ Warning: Some indices are out of bounds. Valid: {valid_indices}")
            
            for idx in valid_indices:
                keep_mask[idx] = False
            
            # 5. Xóa khỏi metadata và reset ID
            # Đảm bảo chỉ giữ các hàng trong phạm vi hợp lệ
            self.metadata_df = self.metadata_df.iloc[:effective_size][keep_mask].reset_index(drop=True)
            # Cập nhật cột ID để khớp với index mới
            self.metadata_df['id'] = range(len(self.metadata_df))
            
            # 6. Xóa khỏi embeddings
            remaining_embeddings = old_embeddings[:effective_size][keep_mask]
            
            # 7. Rebuild FAISS index với embeddings mới
            print("🔄 Rebuilding FAISS index...")
            self._rebuild_faiss_index(remaining_embeddings)
            
            # 8. Lưu dữ liệu
            self._save_data(remaining_embeddings)
            
            # 9. Report kết quả
            print(f"✅ Đã xóa thành công {len(valid_ids)} sản phẩm:")
            for product in deleted_products:
                print(f"   • ID {product['id']}: {product['name']} - {product['brand']}")
            
            print(f"📊 Database statistics:")
            print(f"   • Sản phẩm còn lại: {len(self.metadata_df)}")
            print(f"   • Vectors còn lại: {self.index.ntotal}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi xóa sản phẩm: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _rebuild_faiss_index(self, embeddings: np.ndarray):
        """Rebuild FAISS index với embeddings mới"""
        try:
            if len(embeddings) == 0:
                # Tạo index rỗng
                dimension = self.index.d if self.index else 768  # Default dimension
                base_index = faiss.IndexFlatIP(dimension)
                self.index = faiss.IndexIDMap(base_index)
                return
            
            # Normalize embeddings cho cosine similarity
            normalized_embeddings = embeddings.copy()
            faiss.normalize_L2(normalized_embeddings)
            
            # Tạo index mới
            dimension = embeddings.shape[1]
            base_index = faiss.IndexFlatIP(dimension)
            new_index = faiss.IndexIDMap(base_index)
            
            # Thêm embeddings với ID mới (từ 0 đến n-1)
            ids = np.arange(len(embeddings), dtype=np.int64)
            new_index.add_with_ids(normalized_embeddings, ids)
            
            self.index = new_index
            print(f"✅ Rebuilt FAISS index với {self.index.ntotal} vectors")
                
        except Exception as e:
            print(f"❌ Lỗi khi rebuild index: {e}")
            import traceback
            traceback.print_exc()
    
    def _recreate_embeddings(self):
        """Tạo lại embeddings cho tất cả sản phẩm còn lại"""
        try:
            print("🔄 Recreating embeddings for remaining products...")
            
            if len(self.metadata_df) == 0:
                return
            
            embeddings_list = []
            
            for idx, row in self.metadata_df.iterrows():
                text = row['text_corpus']
                
                # Tạo embedding
                embedding = self.model.encode(
                    text,
                    batch_size=BATCH_SIZE,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                    max_length=MAX_LENGTH,
                    device=self.device,
                    convert_to_tensor=True
                )
                
                embeddings_list.append(embedding.detach().cpu().numpy())
                
                if (idx + 1) % 50 == 0:
                    print(f"   Processed {idx + 1}/{len(self.metadata_df)} products...")
            
            # Convert to numpy array
            new_embeddings = np.array(embeddings_list)
            
            # Tạo index mới
            dimension = new_embeddings.shape[1]
            base_index = faiss.IndexFlatIP(dimension)
            new_index = faiss.IndexIDMap(base_index)
            
            # Thêm embeddings với ID
            product_ids = self.metadata_df['id'].values
            new_index.add_with_ids(new_embeddings, product_ids)
            
            self.index = new_index
            
            # Lưu embeddings mới
            np.save(DATA_PATHS['embeddings'], new_embeddings)
            
            print("✅ Embeddings recreated successfully")
            
        except Exception as e:
            print(f"❌ Lỗi khi recreate embeddings: {e}")
    
    def _save_data(self, embeddings: np.ndarray = None):
        """Lưu metadata, embeddings và FAISS index"""
        try:
            # Lưu metadata
            self.metadata_df.to_csv(DATA_PATHS['metadata'], index=False)
            
            # Lưu embeddings nếu có
            if embeddings is not None:
                np.save(DATA_PATHS['embeddings'], embeddings)
            
            # Lưu FAISS index
            faiss.write_index(self.index, DATA_PATHS['faiss_index'])
            
            print("💾 Đã lưu dữ liệu")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu dữ liệu: {e}")

def interactive_delete_product():
    """Giao diện tương tác để xóa sản phẩm"""
    print("🗑️  XÓA SẢN PHẨM KHỎI CƠ SỞ DỮ LIỆU")
    print("="*50)
    
    deleter = ProductDeleter()
    
    if deleter.model is None or deleter.metadata_df is None:
        print("❌ Không thể load database")
        return
    
    if len(deleter.metadata_df) == 0:
        print("❌ Database trống, không có sản phẩm để xóa")
        return
    
    print(f"📊 Hiện tại có {len(deleter.metadata_df)} sản phẩm trong database")
    
    # Chọn sản phẩm cần xóa
    product_ids = deleter.select_products_to_delete()
    
    if product_ids:
        # Thực hiện xóa
        success = deleter.delete_products(product_ids)
        
        if success:
            print("\n🎉 Xóa sản phẩm thành công!")
        else:
            print("\n❌ Xóa sản phẩm thất bại!")
    else:
        print("\n👋 Hủy bỏ xóa sản phẩm")

if __name__ == "__main__":
    interactive_delete_product()