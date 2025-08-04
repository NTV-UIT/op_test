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

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.simple_config import config
from src.embedding import embed_text_with_attention, load_embedding_model
from src.preprocess import create_text_corpus_for_product


class ProductUpdater:
    """Class để cập nhật thông tin sản phẩm trong database"""
    
    def __init__(self):
        """Khởi tạo ProductUpdater"""
        self.config = config
        self.model = None
        self.tokenizer = None
        self.data_df = None
        self.embeddings = None
        self.index = None
        self.load_existing_data()
        
    def load_existing_data(self):
        """Load dữ liệu hiện có"""
        try:
            # Load CSV data
            if os.path.exists(self.config['data']['output_csv_path']):
                self.data_df = pd.read_csv(self.config['data']['output_csv_path'])
                print(f"✅ Loaded {len(self.data_df)} products from CSV")
            else:
                raise FileNotFoundError("CSV file not found")
                
            # Load embeddings
            if os.path.exists(self.config['embedding']['output_path']):
                self.embeddings = np.load(self.config['embedding']['output_path'])
                print(f"✅ Loaded embeddings: {self.embeddings.shape}")
            else:
                raise FileNotFoundError("Embeddings file not found")
                
            # Load FAISS index
            if os.path.exists(self.config['embedding']['index_path']):
                self.index = faiss.read_index(self.config['embedding']['index_path'])
                print(f"✅ Loaded FAISS index: {self.index.ntotal} vectors")
            else:
                raise FileNotFoundError("FAISS index not found")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            sys.exit(1)
    
    def display_products(self, limit: int = 20) -> None:
        """Hiển thị danh sách sản phẩm"""
        print(f"\n📋 Danh sách sản phẩm (hiển thị {min(limit, len(self.data_df))} sản phẩm):")
        print("-" * 100)
        
        for idx, row in self.data_df.head(limit).iterrows():
            print(f"ID: {idx:3d} | {row['name'][:50]:<50} | {row['brand'][:20]:<20}")
        
        if len(self.data_df) > limit:
            print(f"... và {len(self.data_df) - limit} sản phẩm khác")
    
    def search_products(self, query: str) -> List[int]:
        """Tìm kiếm sản phẩm theo keyword"""
        if not self.model:
            self.model, self.tokenizer = load_embedding_model()
            
        # Search in name, brand, ingredients
        results = []
        query_lower = query.lower()
        
        for idx, row in self.data_df.iterrows():
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
            product_id = int(input(f"Nhập ID sản phẩm (0-{len(self.data_df)-1}): "))
            if 0 <= product_id < len(self.data_df):
                self._display_product_details(product_id)
                if input("Xác nhận cập nhật sản phẩm này? (y/n): ").lower() == 'y':
                    return product_id
            else:
                print(f"❌ ID không hợp lệ! Phải từ 0 đến {len(self.data_df)-1}")
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
            row = self.data_df.iloc[idx]
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
        total_pages = (len(self.data_df) - 1) // page_size + 1
        current_page = 0
        
        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(self.data_df))
            
            print(f"\n📋 Danh sách sản phẩm (Trang {current_page + 1}/{total_pages}):")
            print("-" * 80)
            
            for i in range(start_idx, end_idx):
                row = self.data_df.iloc[i]
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
        row = self.data_df.iloc[product_id]
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
            max_length=self.config['embedding']['max_length']
        )
        
        return embedding.reshape(1, -1)
    
    def update_product(self, product_id: int, updated_info: Dict[str, Any]) -> bool:
        """Cập nhật sản phẩm trong database"""
        try:
            print(f"\n🔄 Đang cập nhật sản phẩm ID: {product_id}...")
            
            # 1. Tạo embedding mới
            print("📊 Tạo embedding mới...")
            new_embedding = self._create_embedding(updated_info)
            
            # 2. Cập nhật metadata trong DataFrame
            print("📝 Cập nhật metadata...")
            for field, value in updated_info.items():
                self.data_df.at[product_id, field] = value
            
            # 3. Cập nhật embedding trong array
            print("🔢 Cập nhật embedding...")
            self.embeddings[product_id] = new_embedding.flatten()
            
            # 4. Cập nhật FAISS index
            print("📚 Cập nhật FAISS index...")
            if hasattr(self.index, 'remove_ids'):
                # Nếu là IndexIDMap, remove và add lại
                self.index.remove_ids(np.array([product_id], dtype=np.int64))
                self.index.add_with_ids(new_embedding, np.array([product_id], dtype=np.int64))
            else:
                # Nếu không phải IndexIDMap, rebuild toàn bộ index
                print("⚠️ Rebuilding entire index...")
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
    
    def _save_data(self):
        """Lưu dữ liệu ra file"""
        # Lưu CSV
        self.data_df.to_csv(self.config['data']['output_csv_path'], index=False)
        
        # Lưu embeddings
        np.save(self.config['embedding']['output_path'], self.embeddings)
        
        # Lưu FAISS index
        faiss.write_index(self.index, self.config['embedding']['index_path'])
        
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
            current_product = self.data_df.iloc[product_id]
            
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
