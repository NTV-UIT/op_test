"""
Database Manager - Quản lý tổng hợp cơ sở dữ liệu sản phẩm
Tích hợp chức năng thêm, xóa, tìm kiếm, và thống kê
"""

import os
import sys
from src.add_row import ProductManager
from src.delete_row import ProductDeleter
from src.update_row import ProductUpdater

# Add config path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from config.simple_config import print_config

class DatabaseManager:
    """Quản lý tổng hợp database sản phẩm"""
    
    def __init__(self):
        """Khởi tạo Database Manager"""
        self.product_manager = ProductManager()
        self.product_deleter = ProductDeleter()
        self.product_updater = ProductUpdater()
        
    def show_statistics(self):
        """Hiển thị thống kê database"""
        if self.product_manager.metadata_df is None:
            print("❌ Database chưa được load")
            return
            
        df = self.product_manager.metadata_df
        index = self.product_manager.index
        
        print(f"\n📊 THỐNG KÊ CƠ SỞ DỮ LIỆU")
        print("="*60)
        print(f"📦 Tổng số sản phẩm: {len(df)}")
        print(f"🔗 Tổng số vectors: {index.ntotal if index else 0}")
        print(f"📐 Vector dimension: {index.d if index else 0}")
        
        if len(df) > 0:
            # Thống kê theo thương hiệu
            brand_counts = df['brand'].value_counts().head(10)
            print(f"\n🏷️  Top 10 thương hiệu:")
            for i, (brand, count) in enumerate(brand_counts.items(), 1):
                print(f"   {i:2d}. {brand}: {count} sản phẩm")
            
            # Thống kê độ dài text corpus
            text_lengths = df['text_corpus'].str.len()
            print(f"\n📝 Thống kê text corpus:")
            print(f"   • Độ dài trung bình: {text_lengths.mean():.0f} ký tự")
            print(f"   • Độ dài ngắn nhất: {text_lengths.min()} ký tự")
            print(f"   • Độ dài dài nhất: {text_lengths.max()} ký tự")
            
            # Sản phẩm mới nhất
            latest_products = df.nlargest(5, 'id')
            print(f"\n🆕 5 sản phẩm mới nhất:")
            for _, row in latest_products.iterrows():
                print(f"   • ID {row['id']}: {row['name']} - {row['brand']}")
    
    def search_products(self, query: str, method: str = 'hybrid', top_k: int = 5):
        """Tìm kiếm sản phẩm"""
        print(f"\n🔍 Tìm kiếm: '{query}' (method: {method})")
        print("="*60)
        
        try:
            if method == 'hybrid':
                # Import search functions
                from search import hybrid_search
                results = hybrid_search(query, top_k=top_k)
            else:
                from search import bi_encoder_search
                results = bi_encoder_search(query, top_k=top_k)
            
            if results:
                print(f"Tìm thấy {len(results)} kết quả:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['name']} - {result['brand']}")
                    print(f"   ID: {result['id']}")
                    print(f"   Score: {result['score']:.4f}")
                    print(f"   Method: {result['method']}")
                    if 'cross_encoder_score' in result:
                        print(f"   Cross-Encoder Score: {result['cross_encoder_score']:.4f}")
            else:
                print("❌ Không tìm thấy kết quả nào")
                
        except Exception as e:
            print(f"❌ Lỗi khi tìm kiếm: {e}")
    
    def backup_database(self):
        """Backup database"""
        import shutil
        import datetime
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"../data/backup_{timestamp}"
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup files
            files_to_backup = [
                'metadata', 'embeddings', 'faiss_index'
            ]
            
            backed_up_files = []
            
            for file_key in files_to_backup:
                from config.simple_config import DATA_PATHS
                source_file = DATA_PATHS[file_key]
                
                if os.path.exists(source_file):
                    filename = os.path.basename(source_file)
                    backup_file = os.path.join(backup_dir, filename)
                    shutil.copy2(source_file, backup_file)
                    backed_up_files.append(filename)
            
            print(f"✅ Backup thành công!")
            print(f"   📁 Thư mục: {backup_dir}")
            print(f"   📄 Files: {', '.join(backed_up_files)}")
            
            return backup_dir
            
        except Exception as e:
            print(f"❌ Lỗi khi backup: {e}")
            return None

def interactive_database_manager():
    """Giao diện quản lý database tổng hợp"""
    print("🎯 QUẢN LÝ CƠ SỞ DỮ LIỆU SẢN PHẨM")
    print("="*60)
    
    # Hiển thị config
    print_config()
    
    manager = DatabaseManager()
    
    if manager.product_manager.model is None:
        print("❌ Không thể khởi tạo database manager")
        return
    
    while True:
        print(f"\n" + "="*60)
        manager.show_statistics()
        
        print(f"\n🎛️  MENU QUẢN LÝ:")
        print("1. 📝 Thêm sản phẩm mới")
        print("2. ✏️  Cập nhật sản phẩm")
        print("3. 🗑️  Xóa sản phẩm") 
        print("4. 🔍 Tìm kiếm sản phẩm")
        print("5. 📊 Hiển thị thống kê chi tiết")
        print("6. 💾 Backup database")
        print("7. 🔧 Kiểm tra tính nhất quán")
        print("8. 👋 Thoát")
        
        choice = input(f"\nNhập lựa chọn (1-8): ").strip()
        
        if choice == '1':
            print("\n" + "="*50)
            manager.product_manager.add_product()
            
        elif choice == '2':
            print("\n" + "="*50)
            manager.product_updater.interactive_update()
            # Reload manager để cập nhật dữ liệu
            manager.product_manager._load_models_and_data()
            
        elif choice == '3':
            print("\n" + "="*50)
            if len(manager.product_deleter.metadata_df) == 0:
                print("❌ Database trống, không có sản phẩm để xóa")
            else:
                product_ids = manager.product_deleter.select_products_to_delete()
                if product_ids:
                    success = manager.product_deleter.delete_products(product_ids)
                    if success:
                        # Reload manager để cập nhật dữ liệu
                        manager.product_manager._load_models_and_data()
            
        elif choice == '4':
            print("\n" + "="*50)
            query = input("🔍 Nhập từ khóa tìm kiếm: ").strip()
            if query:
                method = input("Chọn phương pháp (1=bi-encoder, 2=hybrid) [default: 2]: ").strip()
                method = 'bi_encoder' if method == '1' else 'hybrid'
                
                try:
                    top_k = int(input("Số kết quả [default: 5]: ").strip() or "5")
                    top_k = max(1, min(top_k, 20))
                except ValueError:
                    top_k = 5
                
                manager.search_products(query, method, top_k)
            
        elif choice == '5':
            print("\n" + "="*50)
            manager.show_statistics()
            
        elif choice == '6':
            print("\n" + "="*50)
            backup_dir = manager.backup_database()
            
        elif choice == '7':
            print("\n" + "="*50)
            print("🔧 KIỂM TRA TÍNH NHẤT QUÁN")
            print("-"*30)
            
            # Kiểm tra metadata vs index
            metadata_count = len(manager.product_manager.metadata_df)
            index_count = manager.product_manager.index.ntotal
            
            print(f"Metadata products: {metadata_count}")
            print(f"Index vectors: {index_count}")
            
            if metadata_count == index_count:
                print("✅ Metadata và index nhất quán")
            else:
                print("❌ Metadata và index không nhất quán!")
                
            # Kiểm tra file tồn tại
            from config.simple_config import DATA_PATHS
            print(f"\n📄 Kiểm tra files:")
            for name, path in DATA_PATHS.items():
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"✅ {name}: {path} ({size:,} bytes)")
                else:
                    print(f"❌ {name}: {path} (không tồn tại)")
            
        elif choice == '8':
            print("\n👋 Tạm biệt!")
            break
            
        else:
            print("❌ Lựa chọn không hợp lệ")
        
        input("\nNhấn Enter để tiếp tục...")

if __name__ == "__main__":
    interactive_database_manager()
