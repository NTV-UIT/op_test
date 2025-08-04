# Product Retrieval System

Hệ thống truy vấn sản phẩm sử dụng Bi-Encoder và Hybrid Search với Cross-Encoder re-ranking.

## Cấu trúc Project

```
demo/
├── data/
│   ├── ingredients v1.csv      # Dữ liệu gốc### Target Performance
- **Hit@3**: ≥ 95%
- **MRR**: ≥ 50%
- **Response Time### Trường dữ liệu:
- **Bắt buộc**: name, brand, ingredients
- **Tùy chọn**: categories, manufacturer, manufacturerNumber

## API Endpoints

### 🌐 **RESTful API** (`app.py`):
```bash
# Start API server
python app.py
# Server runs at http://localhost:5000
```

**Core Endpoints:**
- `POST /api/search` - Tìm kiếm sản phẩm
- `GET /api/products` - List sản phẩm (pagination)
- `POST /api/products` - Thêm sản phẩm
- `PUT /api/products/{id}` - Cập nhật sản phẩm
- `DELETE /api/products/{id}` - Xóa sản phẩm
- `GET /api/stats` - Thống kê hệ thống

**Features:**
- **RESTful design** với JSON requests/responses
- **CORS enabled** cho frontend integration
- **Pagination** cho danh sách sản phẩm
- **Real-time updates** - embedding ngay khi CRUD
- **Error handling** nhất quán
- **Health check** endpoint

👉 **Chi tiết**: Xem `API_DOCUMENTATION.md`

## 🌐 Frontend Demo

### **Web Interface** (`templates/index.html`):
```bash
# Quick start
python run_demo.py
# Tự động mở: http://localhost:5000
```

**Demo Features:**
- **🔍 Search Tab**: Interactive product search với bi-encoder/hybrid
- **➕ Add Tab**: Form thêm sản phẩm với validation  
- **🛠️ Manage Tab**: Danh sách, edit, delete với pagination
- **📊 Stats Tab**: Real-time system statistics
- **🎨 Modern UI**: Responsive design, animations, toast notifications

**Tech Stack:**
- HTML5 + CSS3 + Vanilla JavaScript
- Flask templates & static files
- Real-time API integration
- Mobile-responsive design

👉 **Chi tiết**: Xem `FRONTEND_DEMO.md`

### Target Performance 200ms

## Cách sử dụng

### 1. Khởi tạo và tạo embeddings:
```bash
# Khởi tạo dữ liệu và tạo embeddings ban đầu
python src/preprocess.py
python src/embedding.py
```

### 2. Tìm kiếm sản phẩm:
```bash
# Tìm kiếm interactive
python src/search.py
```

### 3. Đánh giá hệ thống:
```bash
# Chạy evaluation
python src/evaluation.py
```

### 4. Quản lý database:
```bash
# Thêm sản phẩm mới
python src/add_row.py

# Cập nhật sản phẩm
python src/update_row.py

# Xóa sản phẩm
python src/delete_row.py

# Giao diện quản lý tổng hợp
python src/database_manager.py
```

### 5. Test chức năng:
```bash
# Test thêm sản phẩm
python test_add_product.py

# Test cập nhật sản phẩm
python test_update_product.py

# Test xóa sản phẩm  
python test_delete_product.py
```

### 6. Chạy API Server:
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy API server
python app.py

# Test API
python test_api.py
```

### 7. Frontend Demo:
```bash
# Quick demo (khuyến nghị)
python run_demo.py

# Hoặc manual start
python app.py
# Mở browser: http://localhost:5000
``` ├── gt.csv                  # Ground truth cho evaluation
│   ├── product_metadata.csv    # Metadata đã xử lý
│   ├── embeddings_attention.npy # Vector embeddings
│   ├── faiss_index.index      # FAISS index
│   └── evaluation_results.json # Kết quả đánh giá
├── src/
│   ├── preprocess.py          # Tiền xử lý dữ liệu
│   ├── embedding.py           # Tạo embeddings và FAISS index
│   ├── search.py              # Tìm kiếm Bi-Encoder và Hybrid
│   ├── evaluation.py          # Đánh giá hiệu suất
│   ├── add_row.py            # Thêm sản phẩm mới vào database
│   ├── delete_row.py         # Xóa sản phẩm khỏi database
│   ├── database_manager.py   # Quản lý database tổng hợp
│   ├── test_add_product.py   # Test chức năng thêm sản phẩm
│   └── test_delete_product.py # Test chức năng xóa sản phẩm
├── notebook/
│   └── product_retrieval_system.ipynb
└── README.md
```

## Quy trình Chạy Hệ thống

### 1. Tiền xử lý dữ liệu (`preprocess.py`)
```bash
cd src
python preprocess.py
```

Chức năng:
- Load và clean dữ liệu từ `ingredients v1.csv`
- Tạo text corpus tổng hợp từ name, brand, categories, ingredients
- Lưu metadata vào `product_metadata.csv`

### 2. Tạo Embeddings (`embedding.py`)
```bash
python embedding.py
```

Chức năng:
- Load model BGE-large-en-v1.5
- Tạo embeddings với attention pooling cho text dài
- Xây dựng FAISS IndexIDMap cho tìm kiếm hiệu quả
- Lưu embeddings và index

### 3. Tìm kiếm (`search.py`)
```bash
python search.py
```

Chức năng:
- Bi-Encoder search với BGE model
- Hybrid search (Bi-Encoder + Cross-Encoder re-ranking)
- Hỗ trợ tìm kiếm real-time

### 4. Đánh giá (`evaluation.py`)
```bash
python evaluation.py
```

Chức năng:
- Tính toán Hit@3, MRR, Precision@3
- So sánh hiệu suất Bi-Encoder vs Hybrid
- Xuất báo cáo chi tiết

### 5. Quản lý Database (`add_row.py`, `update_row.py`, `delete_row.py`)
```bash
# Thêm sản phẩm
python add_row.py

# Cập nhật sản phẩm
python update_row.py

# Xóa sản phẩm  
python delete_row.py

# Quản lý tổng hợp
python database_manager.py
```

Chức năng:
- **Thêm**: Sản phẩm mới vào database với embedding tự động
- **Cập nhật**: Thông tin sản phẩm với re-embedding và index update
- **Xóa**: Sản phẩm theo ID với rebuild index tự động  
- **Tìm kiếm**: Các phương thức khác nhau (ID, keyword, danh sách)
- **Quản lý**: Giao diện tổng hợp với thống kê và backup

## Kiến trúc Hệ thống

### Models sử dụng:
- **Bi-Encoder**: BAAI/bge-large-en-v1.5
- **Cross-Encoder**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Vector Database**: FAISS IndexIDMap

### Pipeline Tìm kiếm:
1. **Bi-Encoder**: Retrieve top-K candidates (K=20)
2. **Cross-Encoder**: Re-rank candidates
3. **Return**: Top-3 kết quả tốt nhất

### Metrics Đánh giá:
- **Hit@3**: Tỷ lệ query có ít nhất 1 kết quả đúng trong top-3
- **MRR**: Mean Reciprocal Rank
- **Precision@3**: Độ chính xác trung bình trong top-3
- **Response Time**: Thời gian phản hồi (ms)

## Cách sử dụng

### Import và sử dụng Search:
```python
from search import bi_encoder_search, hybrid_search

# Tìm kiếm đơn giản
results = bi_encoder_search("organic chocolate", top_k=3)

# Tìm kiếm hybrid (tốt hơn)
results = hybrid_search("organic chocolate", top_k=3)

# Hiển thị kết quả
for result in results:
    print(f"{result['name']} - {result['brand']}")
    print(f"Score: {result['score']:.4f}")
```

### Thêm/Xóa sản phẩm:
```python
from add_row import ProductManager
from delete_row import ProductDeleter

# Thêm sản phẩm
manager = ProductManager()
product_data = {
    'name': 'Organic Dark Chocolate',
    'brand': 'Green Valley', 
    'categories': 'chocolate, organic',
    'ingredients': 'cocoa beans, cocoa butter, sugar',
    'manufacturer': 'green valley foods',
    'manufacturerNumber': 'GV-001'
}
manager.add_product(product_data)

# Xóa sản phẩm
deleter = ProductDeleter()
deleter.delete_products([1, 2, 3])  # Xóa theo ID list

# Quản lý tổng hợp
from database_manager import DatabaseManager
db_manager = DatabaseManager()
db_manager.show_statistics()
```

### Chạy Evaluation:
```python
from evaluation import run_complete_evaluation

# Chạy evaluation đầy đủ
results = run_complete_evaluation()
```

## Tối ưu hóa

### Attention Pooling cho Text dài:
- Chia text thành chunks nhỏ
- Embedding từng chunk
- Kết hợp bằng Attention mechanism

### FAISS IndexIDMap:
- Hỗ trợ update vector individual
- Tối ưu cho real-time applications
- Memory-efficient cosine similarity search
- Dynamic product addition/removal

## Chức năng Quản lý Database

### Thêm sản phẩm mới:
1. **Interactive Mode**: Nhập thông tin từ bàn phím
2. **Batch Mode**: Thêm nhiều sản phẩm cùng lúc
3. **Programmatic**: API để tích hợp vào hệ thống khác

### Xóa sản phẩm:
1. **Xóa theo ID**: Nhập trực tiếp ID sản phẩm
2. **Xóa theo tìm kiếm**: Tìm kiếm rồi chọn xóa
3. **Xóa theo danh sách**: Xem danh sách và chọn
4. **Batch delete**: Xóa nhiều sản phẩm cùng lúc

### Cập nhật sản phẩm:
1. **Cập nhật theo ID**: Nhập trực tiếp ID sản phẩm
2. **Cập nhật theo tìm kiếm**: Tìm kiếm rồi chọn cập nhật
3. **Cập nhật theo danh sách**: Xem danh sách và chọn
4. **Real-time update**: Embedding và index được cập nhật ngay

### Quy trình thêm sản phẩm:
1. **Input validation**: Kiểm tra dữ liệu đầu vào
2. **Text corpus generation**: Tạo text corpus từ các trường
3. **Embedding creation**: Tạo vector embedding
4. **Index update**: Cập nhật FAISS index với ID mapping
5. **Metadata update**: Cập nhật file CSV metadata
6. **Real-time search**: Sản phẩm mới có thể search ngay

### Quy trình xóa sản phẩm:
1. **Product selection**: Chọn sản phẩm cần xóa (nhiều phương thức)
2. **Metadata cleanup**: Xóa khỏi CSV metadata
3. **Index rebuild**: Rebuild FAISS index sau khi xóa
4. **ID remapping**: Cập nhật ID mapping trong index
5. **Data persistence**: Lưu lại metadata và index mới

### Quy trình cập nhật sản phẩm:
1. **Product selection**: Chọn sản phẩm cần cập nhật (ID, search, list)
2. **Field editing**: Chỉnh sửa từng trường thông tin
3. **Re-embedding**: Tạo lại embedding với thông tin mới
4. **Index update**: Cập nhật vector trong FAISS index
5. **Metadata update**: Cập nhật thông tin trong CSV
6. **Real-time availability**: Sản phẩm cập nhật có thể search ngay

### Trường dữ liệu:
- **Bắt buộc**: name, brand, ingredients
- **Tùy chọn**: categories, manufacturer, manufacturerNumber

## Target Performance
- **Hit@3**: ≥ 95%
- **MRR**: ≥ 50%
- **Response Time**: ≤ 200ms
