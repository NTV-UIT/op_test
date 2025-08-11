"""
Chức năng thêm sản phẩm mới vào cơ sở dữ liệu
- Nhập thông tin sản phẩm từ bàn phím
- Tạo text corpus và embedding
- Cập nhật metadata và FAISS index
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
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_config import (
    EMBEDDING_MODEL_NAME, DATA_PATHS, BATCH_SIZE, MAX_LENGTH, get_device,
    get_global_embedding_model, monitor_gpu_memory
)
from src.preprocess import create_text_corpus_for_product
from src.embedding import embed_text_with_attention, load_embedding_model

class ProductManager:
    """Quản lý thêm/sửa/xóa sản phẩm"""
    
    def __init__(self):
        """Khởi tạo ProductManager"""
        self.device = get_device()
        self.model = None
        self.tokenizer = None
        self.index = None
        self.metadata_df = None
        self.embeddings = None  # Thêm embeddings array
        self._load_models_and_data()
    
    def _load_models_and_data(self):
        """Load models và dữ liệu hiện tại"""
        try:
            print("🔄 Loading models and data...")
            
            # ✅ Sử dụng global model thay vì load mới
            self.model, self.tokenizer = get_global_embedding_model()
            
            self._load_data()
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    def _load_data(self):
        """Load/reload index, embeddings và metadata"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(DATA_PATHS['faiss_index'])
            
            # Load embeddings array
            self.embeddings = np.load(DATA_PATHS['embeddings'])
            
            # Load metadata
            self.metadata_df = pd.read_csv(DATA_PATHS['metadata'])
            
            print(f"✅ Loaded {len(self.metadata_df)} products")
            print(f"✅ Loaded embeddings: {self.embeddings.shape}")
            print(f"✅ Index has {self.index.ntotal} vectors")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading files: {e}")
            print("Please run preprocess.py and embedding.py first")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _create_text_corpus(self, product_data: Dict[str, str]) -> str:
        """Tạo text corpus từ thông tin sản phẩm - sử dụng logic từ preprocess.py"""
        return create_text_corpus_for_product(
            name=product_data.get('name', ''),
            brand=product_data.get('brand', ''),
            ingredients=product_data.get('ingredients', ''),
            categories=product_data.get('categories', ''),
            manufacturer=product_data.get('manufacturer', ''),
            manufacturerNumber=product_data.get('manufacturerNumber', '')
        )
    
    def _create_embedding(self, text: str) -> np.ndarray:
        """Tạo embedding cho text"""
        try:
            # Kiểm tra độ dài text
            tokens = self.tokenizer.tokenize(text)
            
            if len(tokens) <= MAX_LENGTH:
                # Text ngắn - embed bình thường
                embedding = self.model.encode(
                    text,
                    batch_size=BATCH_SIZE,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                    max_length=MAX_LENGTH,
                    device=self.device,
                    convert_to_tensor=True
                )
            else:
                # Text dài - sử dụng attention pooling
                embedding = embed_text_with_attention(
                    text, self.model, self.tokenizer, MAX_LENGTH, self.device, BATCH_SIZE
                )
            
            return embedding.detach().cpu().numpy()
            
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return None
    
    def input_product_info(self) -> Optional[Dict[str, str]]:
        """Nhập thông tin sản phẩm từ bàn phím"""
        print("\n📝 NHẬP THÔNG TIN SẢN PHẨM MỚI")
        print("="*50)
        print("Nhập thông tin sản phẩm (Enter để bỏ qua trường không bắt buộc)")
        print("Gõ 'cancel' để hủy bỏ")
        print("="*50)
        
        fields = {
            'name': "Tên sản phẩm (*bắt buộc): ",
            'brand': "Thương hiệu (*bắt buộc): ",
            'categories': "Danh mục (vd: food, beverage): ",
            'ingredients': "Thành phần (*bắt buộc): ",
            'manufacturer': "Nhà sản xuất: ",
            'manufacturerNumber': "Mã nhà sản xuất: "
        }
        
        product_data = {}
        
        for field, prompt in fields.items():
            while True:
                value = input(f"{prompt}").strip()
                
                if value.lower() == 'cancel':
                    print("❌ Hủy bỏ thêm sản phẩm")
                    return None
                
                # Kiểm tra trường bắt buộc
                if field in ['name', 'brand', 'ingredients'] and not value:
                    print(f"⚠️  {field} là trường bắt buộc!")
                    continue
                
                product_data[field] = value
                break
        
        # Xác nhận thông tin
        print(f"\n📋 XÁC NHẬN THÔNG TIN SẢN PHẨM:")
        print("-" * 40)
        for field, value in product_data.items():
            display_name = {
                'name': 'Tên sản phẩm',
                'brand': 'Thương hiệu', 
                'categories': 'Danh mục',
                'ingredients': 'Thành phần',
                'manufacturer': 'Nhà sản xuất',
                'manufacturerNumber': 'Mã nhà sản xuất'
            }
            print(f"{display_name[field]}: {value}")
        
        confirm = input(f"\n✅ Xác nhận thêm sản phẩm? (y/n) [default: y]: ").strip().lower()
        if confirm == 'n':
            print("❌ Hủy bỏ thêm sản phẩm")
            return None
            
        return product_data
    
    def add_product_programmatic(self, name: str, brand: str, ingredients: str,
                               categories: str = "", manufacturer: str = "", 
                               manufacturerNumber: str = "") -> bool:
        """Thêm sản phẩm programmatically (cho API)"""
        product_data = {
            'name': name.strip(),
            'brand': brand.strip(),
            'ingredients': ingredients.strip(),
            'categories': categories.strip(),
            'manufacturer': manufacturer.strip(),
            'manufacturerNumber': manufacturerNumber.strip()
        }
        return self.add_product(product_data)
    
    def add_product_from_data(self, product_data: Dict[str, str]) -> bool:
        """Thêm sản phẩm mới từ dữ liệu API"""
        return self.add_product(product_data)
    
    def add_product(self, product_data: Optional[Dict[str, str]] = None) -> bool:
        """Thêm sản phẩm mới vào cơ sở dữ liệu"""
        if self.model is None or self.index is None or self.metadata_df is None or self.embeddings is None:
            print("❌ Models hoặc data chưa được load")
            return False
        
        # Nhập thông tin nếu chưa có
        if product_data is None:
            product_data = self.input_product_info()
            if product_data is None:
                return False
        
        try:
            print("\n🔄 Processing new product...")
            
            # 1. Tạo ID mới
            new_id = self.metadata_df['id'].max() + 1 if len(self.metadata_df) > 0 else 0
            
            # 2. Tạo text corpus
            text_corpus = self._create_text_corpus(product_data)
            print(f"📝 Text corpus: {text_corpus[:100]}...")
            
            # 3. Tạo embedding
            start_time = time.time()
            embedding = self._create_embedding(text_corpus)
            embedding_time = (time.time() - start_time) * 1000
            
            if embedding is None:
                print("❌ Không thể tạo embedding")
                return False
                
            print(f"🔗 Created embedding in {embedding_time:.1f}ms")
            
            # 4. Thêm vào metadata
            new_row = {
                'id': new_id,
                'name': product_data['name'],
                'brand': product_data['brand'],
                'categories': product_data.get('categories', ''),
                'ingredients': product_data.get('ingredients', ''),
                'manufacturer': product_data.get('manufacturer', ''),
                'manufacturerNumber': product_data.get('manufacturerNumber', ''),
                'text_corpus': text_corpus
            }
            
            # Thêm vào DataFrame
            self.metadata_df = pd.concat([
                self.metadata_df, 
                pd.DataFrame([new_row])
            ], ignore_index=True)
            
            # 5. Thêm vào embeddings array
            self.embeddings = np.vstack([self.embeddings, embedding.reshape(1, -1)])
            
            # 6. Thêm vào FAISS index
            embedding_2d = embedding.reshape(1, -1)  # Reshape to (1, dimension)
            self.index.add_with_ids(embedding_2d, np.array([new_id], dtype=np.int64))
            
            # 7. Lưu file
            self._save_data()
            
            print(f"✅ Đã thêm sản phẩm thành công!")
            print(f"   • ID: {new_id}")
            print(f"   • Tên: {product_data['name']}")
            print(f"   • Thương hiệu: {product_data['brand']}")
            print(f"   • Total products: {len(self.metadata_df)}")
            print(f"   • Total embeddings: {self.embeddings.shape[0]}")
            print(f"   • Total vectors: {self.index.ntotal}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi thêm sản phẩm: {e}")
            return False
    
    def _save_data(self):
        """Lưu metadata, embeddings và FAISS index"""
        try:
            # Lưu metadata
            self.metadata_df.to_csv(DATA_PATHS['metadata'], index=False)
            
            # Lưu embeddings array
            np.save(DATA_PATHS['embeddings'], self.embeddings)
            
            # Lưu FAISS index
            faiss.write_index(self.index, DATA_PATHS['faiss_index'])
            
            print("💾 Đã lưu tất cả dữ liệu")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu dữ liệu: {e}")
    
    def batch_add_products(self, products_list):
        """Thêm nhiều sản phẩm cùng lúc"""
        print(f"\n🔄 Thêm {len(products_list)} sản phẩm...")
        
        success_count = 0
        for i, product_data in enumerate(products_list, 1):
            print(f"\nThêm sản phẩm {i}/{len(products_list)}:")
            if self.add_product(product_data):
                success_count += 1
        
        print(f"\n✅ Đã thêm thành công {success_count}/{len(products_list)} sản phẩm")
        return success_count
    
    def search_test(self, query: str, top_k: int = 3):
        """Test search với sản phẩm mới"""
        if self.model is None or self.index is None:
            print("❌ Models chưa được load")
            return
            
        try:
            # Tạo query embedding
            query_embedding = self.model.encode(
                [query],
                normalize_embeddings=True,
                device=self.device
            )
            
            # Search
            distances, indices = self.index.search(query_embedding, top_k)
            
            print(f"\n🔍 Kết quả tìm kiếm cho: '{query}'")
            print("="*60)
            
            for i, (idx, score) in enumerate(zip(indices[0], distances[0]), 1):
                product_row = self.metadata_df[self.metadata_df['id'] == idx]
                if not product_row.empty:
                    row = product_row.iloc[0]
                    print(f"{i}. {row['name']} - {row['brand']}")
                    print(f"   Score: {score:.4f}")
                    print(f"   ID: {row['id']}")
                    
        except Exception as e:
            print(f"❌ Lỗi khi search: {e}")

def interactive_add_product():
    """Giao diện tương tác để thêm sản phẩm"""
    print("🎯 QUẢN LÝ CƠ SỞ DỮ LIỆU SẢN PHẨM")
    print("="*50)
    
    manager = ProductManager()
    
    if manager.model is None:
        return
    
    while True:
        print(f"\n📊 Hiện tại có {len(manager.metadata_df)} sản phẩm trong database")
        print("\nChọn hành động:")
        print("1. Thêm sản phẩm mới")
        print("2. Test search")
        print("3. Hiển thị thống kê")
        print("4. Thoát")
        
        choice = input("\nNhập lựa chọn (1-4): ").strip()
        
        if choice == '1':
            manager.add_product()
            
        elif choice == '2':
            query = input("Nhập từ khóa tìm kiếm: ").strip()
            if query:
                manager.search_test(query)
                
        elif choice == '3':
            print(f"\n📊 THỐNG KÊ DATABASE:")
            print(f"   • Tổng số sản phẩm: {len(manager.metadata_df)}")
            print(f"   • Tổng số vectors: {manager.index.ntotal}")
            print(f"   • Vector dimension: {manager.index.d}")
            
            # Top brands
            brand_counts = manager.metadata_df['brand'].value_counts().head(5)
            print(f"\n🏷️  Top 5 thương hiệu:")
            for brand, count in brand_counts.items():
                print(f"   • {brand}: {count} sản phẩm")
                
        elif choice == '4':
            print("👋 Tạm biệt!")
            break
            
        else:
            print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    interactive_add_product()