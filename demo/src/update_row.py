#!/usr/bin/env python3
"""
Product Update Module
Chức năng cập nhật sản phẩm trong database với re-embedding và index update
"""

import os
import sys
import pandas as pd
import numpy as np
import faiss
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config'))

from simple_config import (
    EMBEDDING_MODEL_NAME, DATA_PATHS, BATCH_SIZE, MAX_LENGTH, get_device
)
from src.embedding import embed_text_with_attention, load_embedding_model
from src.preprocess import create_text_corpus_for_product


class ProductUpdater:
    """Class để cập nhật thông tin sản phẩm trong database"""
    
    def __init__(self):
        """Khởi tạo ProductUpdater"""
        self.device = get_device()
        self.model = None
        self.tokenizer = None
        self.metadata_df = None
        self.embeddings = None
        self.index = None
        self.load_existing_data()
        
    def load_existing_data(self):
        """Load dữ liệu hiện có"""
        try:
            # Load model
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            self.tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
            print("✅ Loaded embedding model")
            
            self._load_data()
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.metadata_df = None
            self.embeddings = None
            self.index = None
    
    def _load_data(self):
        """Load/reload dữ liệu database"""
        try:
            # Load CSV metadata
            if os.path.exists(DATA_PATHS['metadata']):
                self.metadata_df = pd.read_csv(DATA_PATHS['metadata'])
                print(f"✅ Loaded {len(self.metadata_df)} products from metadata")
            else:
                raise FileNotFoundError("Metadata file not found")
                
            # Load embeddings
            if os.path.exists(DATA_PATHS['embeddings']):
                self.embeddings = np.load(DATA_PATHS['embeddings'])
                print(f"✅ Loaded embeddings: {self.embeddings.shape}")
            else:
                raise FileNotFoundError("Embeddings file not found")
                
            # Load FAISS index
            if os.path.exists(DATA_PATHS['faiss_index']):
                self.index = faiss.read_index(DATA_PATHS['faiss_index'])
                print(f"✅ Loaded FAISS index: {self.index.ntotal} vectors")
            else:
                raise FileNotFoundError("FAISS index not found")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise e
    
    def display_products(self, limit: int = 20) -> None:
        """Hiển thị danh sách sản phẩm"""
        print(f"\n📋 Danh sách sản phẩm (hiển thị {min(limit, len(self.metadata_df))} sản phẩm):")
        print("-" * 100)
        
        for idx, row in self.metadata_df.head(limit).iterrows():
            print(f"ID: {idx:3d} | {row['name'][:50]:<50} | {row['brand'][:20]:<20}")
        
        if len(self.metadata_df) > limit:
            print(f"... và {len(self.metadata_df) - limit} sản phẩm khác")
    
    def search_products(self, query: str) -> List[int]:
        """Tìm kiếm sản phẩm theo keyword"""
        if not self.model:
            self.model, self.tokenizer = load_embedding_model()
            
        # Search in name, brand, ingredients
        results = []
        query_lower = query.lower()
        
        for idx, row in self.metadata_df.iterrows():
            search_text = f"{row['name']} {row['brand']} {row.get('ingredients', '')}".lower()
            if query_lower in search_text:
                results.append(idx)
                
        return results
    
    def select_product_to_update(self) -> Optional[int]:
        """Chọn sản phẩm để cập nhật với nhiều phương thức"""
        while True:
            print("\n🎯 Chọn phương thức tìm sản phẩm cần cập nhật:")
            print("1. Nhập ID trực tiếp")
            print("2. Tìm kiếm theo keyword")
            print("3. Xem danh sách sản phẩm")
            print("0. Quay lại")
            
            choice = input("\nNhập lựa chọn (0-3): ").strip()
            
            if choice == "0":
                return None
            elif choice == "1":
                return self._select_by_id()
            elif choice == "2":
                return self._select_by_search()
            elif choice == "3":
                return self._select_from_list()
            else:
                print("❌ Lựa chọn không hợp lệ!")
    
    def _select_by_id(self) -> Optional[int]:
        """Chọn sản phẩm theo ID"""
        try:
            product_id = int(input(f"Nhập ID sản phẩm (0-{len(self.metadata_df)-1}): "))
            if 0 <= product_id < len(self.metadata_df):
                self._display_product_details(product_id)
                if input("Xác nhận cập nhật sản phẩm này? (y/n): ").lower() == 'y':
                    return product_id
            else:
                print(f"❌ ID không hợp lệ! Phải từ 0 đến {len(self.metadata_df)-1}")
        except ValueError:
            print("❌ ID phải là số nguyên!")
        return None
    
    def _select_by_search(self) -> Optional[int]:
        """Chọn sản phẩm qua tìm kiếm"""
        query = input("Nhập keyword tìm kiếm: ").strip()
        if not query:
            return None
            
        results = self.search_products(query)
        if not results:
            print("❌ Không tìm thấy sản phẩm nào!")
            return None
            
        print(f"\n🔍 Tìm thấy {len(results)} sản phẩm:")
        print("-" * 80)
        
        for i, idx in enumerate(results[:10], 1):
            row = self.metadata_df.iloc[idx]
            print(f"{i:2d}. ID:{idx:3d} | {row['name'][:40]:<40} | {row['brand'][:15]}")
            
        try:
            choice = int(input(f"\nChọn sản phẩm (1-{min(len(results), 10)}): ")) - 1
            if 0 <= choice < min(len(results), 10):
                product_id = results[choice]
                self._display_product_details(product_id)
                if input("Xác nhận cập nhật sản phẩm này? (y/n): ").lower() == 'y':
                    return product_id
        except ValueError:
            print("❌ Lựa chọn không hợp lệ!")
        return None
    
    def _select_from_list(self) -> Optional[int]:
        """Chọn sản phẩm từ danh sách"""
        page_size = 20
        total_pages = (len(self.metadata_df) - 1) // page_size + 1
        current_page = 0
        
        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(self.metadata_df))
            
            print(f"\n📋 Danh sách sản phẩm (Trang {current_page + 1}/{total_pages}):")
            print("-" * 80)
            
            for i in range(start_idx, end_idx):
                row = self.metadata_df.iloc[i]
                print(f"{i:3d}. {row['name'][:40]:<40} | {row['brand'][:15]}")
            
            print(f"\n[n]ext | [p]rev | [s]elect | [q]uit")
            choice = input("Lựa chọn: ").strip().lower()
            
            if choice == 'n' and current_page < total_pages - 1:
                current_page += 1
            elif choice == 'p' and current_page > 0:
                current_page -= 1
            elif choice == 's':
                try:
                    product_id = int(input(f"Nhập ID sản phẩm ({start_idx}-{end_idx-1}): "))
                    if start_idx <= product_id < end_idx:
                        self._display_product_details(product_id)
                        if input("Xác nhận cập nhật sản phẩm này? (y/n): ").lower() == 'y':
                            return product_id
                    else:
                        print(f"❌ ID phải từ {start_idx} đến {end_idx-1}")
                except ValueError:
                    print("❌ ID phải là số nguyên!")
            elif choice == 'q':
                return None
    
    def _display_product_details(self, product_id: int) -> None:
        """Hiển thị chi tiết sản phẩm"""
        row = self.metadata_df.iloc[product_id]
        print(f"\n📦 Chi tiết sản phẩm ID: {product_id}")
        print("-" * 60)
        print(f"Tên: {row['name']}")
        print(f"Thương hiệu: {row['brand']}")
        print(f"Thành phần: {row.get('ingredients', 'N/A')}")
        print(f"Danh mục: {row.get('categories', 'N/A')}")
        print(f"Nhà sản xuất: {row.get('manufacturer', 'N/A')}")
        print(f"Mã sản xuất: {row.get('manufacturerNumber', 'N/A')}")
    
    def get_updated_product_info(self, current_product: pd.Series) -> Dict[str, Any]:
        """Thu thập thông tin cập nhật từ user"""
        print("\n✏️ Nhập thông tin mới (nhấn Enter để giữ nguyên):")
        print("-" * 50)
        
        updated_info = {}
        
        # Các trường bắt buộc
        required_fields = ['name', 'brand', 'ingredients']
        for field in required_fields:
            current_value = current_product.get(field, '')
            print(f"Hiện tại - {field}: {current_value}")
            new_value = input(f"Mới - {field}: ").strip()
            updated_info[field] = new_value if new_value else current_value
        
        # Các trường tùy chọn
        optional_fields = ['categories', 'manufacturer', 'manufacturerNumber']
        for field in optional_fields:
            current_value = current_product.get(field, '')
            print(f"Hiện tại - {field}: {current_value}")
            new_value = input(f"Mới - {field}: ").strip()
            updated_info[field] = new_value if new_value else current_value
        
        return updated_info
    
    def _create_embedding(self, product_info: Dict[str, Any]) -> np.ndarray:
        """Tạo embedding cho sản phẩm"""
        if not self.model:
            self.model, self.tokenizer = load_embedding_model()
        
        # Tạo text corpus
        text_corpus = create_text_corpus_for_product(
            name=product_info['name'],
            brand=product_info['brand'], 
            ingredients=product_info.get('ingredients', ''),
            categories=product_info.get('categories', ''),
            manufacturer=product_info.get('manufacturer', ''),
            manufacturerNumber=product_info.get('manufacturerNumber', '')
        )
        
        # Tạo embedding
        embedding = embed_text_with_attention(
            text_corpus,
            self.model,
            self.tokenizer,
            max_length=MAX_LENGTH,
            device=self.device
        )
        
        # Convert to CPU and numpy before reshape
        embedding_numpy = embedding.detach().cpu().numpy()
        return embedding_numpy.reshape(1, -1)
    
    def update_product(self, product_id: int, updated_info: Dict[str, Any]) -> bool:
        """Cập nhật sản phẩm trong database"""
        try:
            print(f"\n🔄 Đang cập nhật sản phẩm ID: {product_id}...")
            
            # 0. Tìm index của product_id trong DataFrame
            if product_id not in self.metadata_df['id'].values:
                print(f"❌ Product ID {product_id} không tồn tại!")
                return False
            
            # Lấy index thực tế của product_id
            product_index = self.metadata_df[self.metadata_df['id'] == product_id].index[0]
            
            # Debug: Kiểm tra consistency
            print(f"🔍 Debug info:")
            print(f"   Product ID: {product_id}")
            print(f"   Product index in DataFrame: {product_index}")
            print(f"   Metadata shape: {self.metadata_df.shape}")
            print(f"   Embeddings shape: {self.embeddings.shape}")
            print(f"   FAISS index size: {self.index.ntotal}")
            
            # Validation: Đảm bảo index không vượt quá bounds
            if product_index >= len(self.embeddings):
                print(f"❌ Error: product_index {product_index} >= embeddings size {len(self.embeddings)}")
                print("🔄 Rebuilding embeddings to match metadata...")
                self._rebuild_all_embeddings()
                # Sau khi rebuild, kiểm tra lại
                if product_index >= len(self.embeddings):
                    print(f"❌ Still out of bounds after rebuild!")
                    return False
            
            # 1. Tạo embedding mới
            print("📊 Tạo embedding mới...")
            new_embedding = self._create_embedding(updated_info)
            
            # 2. Cập nhật metadata trong DataFrame (sử dụng index, không phải ID)
            print("📝 Cập nhật metadata...")
            for field, value in updated_info.items():
                self.metadata_df.at[product_index, field] = value
            
            # Cập nhật text_corpus với thông tin mới
            new_text_corpus = create_text_corpus_for_product(
                name=updated_info['name'],
                brand=updated_info['brand'], 
                ingredients=updated_info.get('ingredients', ''),
                categories=updated_info.get('categories', ''),
                manufacturer=updated_info.get('manufacturer', ''),
                manufacturerNumber=updated_info.get('manufacturerNumber', '')
            )
            self.metadata_df.at[product_index, 'text_corpus'] = new_text_corpus
            
            # 3. Cập nhật embedding trong array (sử dụng index)
            print("🔢 Cập nhật embedding...")
            self.embeddings[product_index] = new_embedding.flatten()
            
            # 4. Cập nhật FAISS index (QUICK UPDATE)
            print("📚 Cập nhật FAISS index...")
            
            # Normalize embedding cho cosine similarity
            normalized_embedding = new_embedding.copy()
            faiss.normalize_L2(normalized_embedding)
            
            # Quick update: Chỉ remove và add lại vector này
            try:
                self.index.remove_ids(np.array([product_index], dtype=np.int64))
                self.index.add_with_ids(normalized_embedding, np.array([product_index], dtype=np.int64))
                print(f"⚡ Quick update vector at index {product_index}")
                
            except Exception as idx_error:
                print(f"⚠️ Quick update failed: {idx_error}")
                print("🔄 Rebuilding index...")
                self._rebuild_faiss_index()
            
            # 5. Lưu dữ liệu
            print("💾 Lưu dữ liệu...")
            self._save_data()
            
            print(f"✅ Cập nhật thành công sản phẩm ID: {product_id}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật sản phẩm: {e}")
            return False
    
    def _rebuild_faiss_index(self):
        """Rebuild toàn bộ FAISS index"""
        embedding_dim = self.embeddings.shape[1]
        
        # Tạo IndexIDMap mới
        base_index = faiss.IndexFlatIP(embedding_dim)
        self.index = faiss.IndexIDMap(base_index)
        
        # Normalize embeddings cho cosine similarity
        normalized_embeddings = self.embeddings.copy()
        faiss.normalize_L2(normalized_embeddings)
        
        # Thêm tất cả embeddings với ID
        ids = np.arange(len(self.embeddings), dtype=np.int64)
        self.index.add_with_ids(normalized_embeddings, ids)
        
        print(f"✅ Rebuilt FAISS index với {self.index.ntotal} vectors")
    
    def _rebuild_all_embeddings(self):
        """Rebuild toàn bộ embeddings từ metadata"""
        try:
            print("🔄 Rebuilding all embeddings from metadata...")
            
            embeddings_list = []
            
            for idx, row in self.metadata_df.iterrows():
                # Tạo embedding từ text_corpus hoặc từ các field
                if 'text_corpus' in row and pd.notna(row['text_corpus']):
                    text = row['text_corpus']
                else:
                    # Tạo text_corpus từ các field
                    text = create_text_corpus_for_product(
                        name=row.get('name', ''),
                        brand=row.get('brand', ''),
                        ingredients=row.get('ingredients', ''),
                        categories=row.get('categories', ''),
                        manufacturer=row.get('manufacturer', ''),
                        manufacturerNumber=row.get('manufacturerNumber', '')
                    )
                
                # Tạo embedding
                embedding = embed_text_with_attention(
                    text,
                    self.model,
                    self.tokenizer,
                    max_length=MAX_LENGTH,
                    device=self.device
                )
                
                embeddings_list.append(embedding.detach().cpu().numpy())
                
                if (idx + 1) % 50 == 0:
                    print(f"   Processed {idx + 1}/{len(self.metadata_df)} products...")
            
            # Convert to numpy array
            self.embeddings = np.array(embeddings_list)
            
            # Rebuild FAISS index
            self._rebuild_faiss_index()
            
            print(f"✅ Rebuilt all embeddings: {self.embeddings.shape}")
            
        except Exception as e:
            print(f"❌ Lỗi khi rebuild embeddings: {e}")
            raise e
    
    def _save_data(self):
        """Lưu dữ liệu ra file"""
        # Lưu CSV metadata
        self.metadata_df.to_csv(DATA_PATHS['metadata'], index=False)
        
        # Lưu embeddings
        np.save(DATA_PATHS['embeddings'], self.embeddings)
        
        # Lưu FAISS index
        faiss.write_index(self.index, DATA_PATHS['faiss_index'])
        
        print("💾 Đã lưu tất cả dữ liệu")
    
    def interactive_update(self):
        """Giao diện tương tác để cập nhật sản phẩm"""
        print("🔧 CHỨC NĂNG CẬP NHẬT SẢN PHẨM")
        print("=" * 50)
        
        while True:
            # Chọn sản phẩm cần cập nhật
            product_id = self.select_product_to_update()
            if product_id is None:
                break
                
            # Lấy thông tin hiện tại
            current_product = self.metadata_df.iloc[product_id]
            
            # Thu thập thông tin mới
            updated_info = self.get_updated_product_info(current_product)
            
            # Hiển thị preview
            print("\n👀 Preview thông tin mới:")
            print("-" * 40)
            for field, value in updated_info.items():
                print(f"{field}: {value}")
            
            # Xác nhận cập nhật
            if input("\nXác nhận cập nhật? (y/n): ").lower() == 'y':
                success = self.update_product(product_id, updated_info)
                if success:
                    print("🎉 Cập nhật thành công!")
                else:
                    print("💥 Cập nhật thất bại!")
            
            # Tiếp tục?
            if input("\nCập nhật sản phẩm khác? (y/n): ").lower() != 'y':
                break
        
        print("👋 Cảm ơn bạn đã sử dụng chức năng cập nhật!")


def main():
    """Main function"""
    try:
        updater = ProductUpdater()
        updater.interactive_update()
    except KeyboardInterrupt:
        print("\n\n👋 Đã thoát chương trình")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
