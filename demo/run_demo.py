#!/usr/bin/env python3
"""
Demo Runner Script
Chạy toàn bộ hệ thống Product Retrieval với frontend demo
"""

import os
import sys
import time
import webbrowser
import subprocess
from threading import Timer

def print_banner():
    print("=" * 80)
    print("🚀 PRODUCT RETRIEVAL SYSTEM - DEMO")
    print("=" * 80)
    print()
    print("📋 Checklist trước khi chạy:")
    print("  ✅ Data files (CSV, embeddings, index) đã được tạo")
    print("  ✅ Dependencies đã được cài đặt")
    print("  ✅ Models đã được download")
    print()

def check_dependencies():
    """Kiểm tra dependencies"""
    print("🔍 Kiểm tra dependencies...")
    
    required_packages = [
        'flask', 'flask_cors', 'pandas', 'numpy', 
        'torch', 'transformers', 'sentence_transformers', 'faiss'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'faiss':
                import faiss
            elif package == 'flask_cors':
                import flask_cors
            elif package == 'sentence_transformers':
                import sentence_transformers
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Thiếu packages: {', '.join(missing_packages)}")
        print("💡 Cài đặt bằng: pip install -r requirements.txt")
        return False
    
    print("✅ Tất cả dependencies đã sẵn sàng!")
    return True

def check_data_files():
    """Kiểm tra data files"""
    print("\n📁 Kiểm tra data files...")
    
    required_files = [
        'data/product_metadata.csv',
        'data/embeddings_attention.npy', 
        'data/faiss_index.index'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({file_size:,} bytes)")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Thiếu files: {', '.join(missing_files)}")
        print("💡 Chạy preprocessing trước:")
        print("   python src/preprocess.py")
        print("   python src/embedding.py")
        return False
    
    print("✅ Tất cả data files đã sẵn sàng!")
    return True

def open_browser():
    """Mở browser sau delay"""
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Đã mở browser tại http://localhost:5000")
    except Exception as e:
        print(f"⚠️  Không thể mở browser tự động: {e}")
        print("💡 Vui lòng mở browser và truy cập http://localhost:5000")

def run_demo():
    """Chạy demo"""
    print_banner()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        return False
    
    # Kiểm tra data files  
    if not check_data_files():
        return False
    
    print("\n🎯 KHỞI ĐỘNG DEMO")
    print("-" * 40)
    
    try:
        print("📡 Starting Flask API server...")
        print("⏳ Đang khởi tạo models và load data...")
        print()
        
        # Import và chạy app
        from app import app, initialize_services
        
        # Khởi tạo services
        if not initialize_services():
            print("❌ Không thể khởi tạo services!")
            return False
        
        print("\n🎉 Demo đã sẵn sàng!")
        print("=" * 50)
        print("🌐 Frontend:  http://localhost:5000")
        print("🔧 API Base: http://localhost:5000/api")
        print("💡 Health:   http://localhost:5000/api/health")
        print("=" * 50)
        print()
        print("📋 Hướng dẫn sử dụng:")
        print("  1. Tab 'Tìm kiếm': Test search functionality")
        print("  2. Tab 'Thêm sản phẩm': Add new products")  
        print("  3. Tab 'Quản lý': Edit/Delete products")
        print("  4. Tab 'Thống kê': View system statistics")
        print()
        print("⌨️  Nhấn Ctrl+C để dừng server")
        print()
        
        # Mở browser sau 3 giây
        Timer(3.0, open_browser).start()
        
        # Chạy Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo đã được dừng!")
        return True
    except Exception as e:
        print(f"\n❌ Lỗi khi chạy demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_help():
    """Hiển thị help"""
    print("🆘 HƯỚNG DẪN SỬ DỤNG")
    print("=" * 40)
    print()
    print("📋 Chuẩn bị:")
    print("  1. Cài đặt dependencies:")
    print("     pip install -r requirements.txt")
    print()
    print("  2. Chạy preprocessing (nếu chưa có data):")
    print("     python src/preprocess.py")
    print("     python src/embedding.py")
    print()
    print("🚀 Chạy demo:")
    print("  python run_demo.py")
    print()
    print("🧪 Test API riêng lẻ:")
    print("  python test_api.py")
    print()
    print("💻 Chạy CLI interfaces:")
    print("  python src/search.py        # Search CLI")
    print("  python src/database_manager.py  # Management CLI")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
    else:
        success = run_demo()
        sys.exit(0 if success else 1)
