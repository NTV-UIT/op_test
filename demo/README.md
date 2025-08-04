# Product Retrieval System

Hệ thống tìm kiếm và quản lý sản phẩm sử dụng AI với Bi-Encoder và Cross-Encoder re-ranking.

## 🚀 Khởi chạy nhanh

### 1. Cài đặt dependencies

```bash
# Clone/download project
cd demo

# Cài đặt Python packages
pip install -r requirements.txt
```

### 2. Khởi tạo dữ liệu (Chỉ chạy lần đầu)

```bash
# Tiền xử lý dữ liệu
python src/preprocess.py

# Tạo embeddings và FAISS index
python src/embedding.py
```

### 3. Chạy ứng dụng


```bash
python app.py
```
→ Mở browser thủ công tại `http://localhost:5000`

## 📋 Cấu trúc Project

```
demo/
├── app.py                      # 🌐 Flask API server
├── run_demo.py                 # 🚀 Quick start script
├── requirements.txt            # 📦 Dependencies
├── config/
│   └── simple_config.py        # ⚙️ Configuration
├── data/
│   ├── ingredients v1.csv      # 📊 Dữ liệu gốc
│   ├── product_metadata.csv    # 🗃️ Metadata đã xử lý
│   ├── embeddings_attention.npy # 🧠 Vector embeddings
│   └── faiss_index.index      # 🔍 FAISS search index
├── src/
│   ├── preprocess.py          # 🔧 Tiền xử lý dữ liệu
│   ├── embedding.py           # 🧠 Tạo embeddings
│   ├── search.py              # 🔍 Tìm kiếm
│   ├── add_row.py            # ➕ Thêm sản phẩm
│   ├── update_row.py         # ✏️ Cập nhật sản phẩm
│   └── delete_row.py         # 🗑️ Xóa sản phẩm
├── templates/
│   └── index.html            # 🎨 Web interface
└── static/
    ├── style.css             # 💅 Styling
    └── script.js             # ⚡ Frontend logic
```

## 🎯 Tính năng chính

### 🌐 Web Interface
- **🔍 Search Tab**: Tìm kiếm sản phẩm thông minh
- **➕ Add Tab**: Thêm sản phẩm mới với form validation
- **🛠️ Manage Tab**: Quản lý sản phẩm (edit/delete/browse)
- **📊 Stats Tab**: Thống kê hệ thống real-time

### 🔧 API Endpoints
- `POST /api/search` - Tìm kiếm sản phẩm
- `GET /api/products` - Danh sách sản phẩm (có pagination)
- `POST /api/products` - Thêm sản phẩm mới
- `PUT /api/products/{id}` - Cập nhật sản phẩm
- `DELETE /api/products/{id}` - Xóa sản phẩm
- `GET /api/stats` - Thống kê hệ thống

## 🛠️ Quản lý Database

### Thêm sản phẩm
```bash
python src/add_row.py
```

### Cập nhật sản phẩm
```bash
python src/update_row.py
```

### Xóa sản phẩm
```bash
python src/delete_row.py
```

### Quản lý tổng hợp
```bash
python src/database_manager.py
```

## 🧪 Testing

### Test API
```bash
python test_api.py
```

### Test CRUD operations
```bash
python test_add_product.py
python test_update_product.py
python test_delete_product.py
```

## ⚙️ Cấu hình

### Models sử dụng:
- **Bi-Encoder**: `BAAI/bge-large-en-v1.5`
- **Cross-Encoder**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Vector Database**: FAISS IndexIDMap

### Trường dữ liệu:
- **Bắt buộc**: name, brand, ingredients
- **Tùy chọn**: categories, manufacturer, manufacturerNumber

### Performance Target:
- **Hit@3**: ≥ 95%
- **MRR**: ≥ 50%
- **Response Time**: ≤ 200ms

## 🚨 Troubleshooting

### Lỗi thiếu dữ liệu:
```bash
# Tạo lại embeddings
python src/embedding.py
```

### Lỗi CUDA/GPU:
```bash
# Sửa trong config/simple_config.py
DEVICE = "cpu"  # Thay vì "cuda"
```

### Lỗi port đã sử dụng:
```bash
# Đổi port trong app.py hoặc run_demo.py
app.run(port=5001)  # Thay vì 5000
```

### Reset hệ thống:
```bash
# Xóa dữ liệu đã tạo
rm data/product_metadata.csv
rm data/embeddings_attention.npy
rm data/faiss_index.index

# Tạo lại từ đầu
python src/preprocess.py
python src/embedding.py
```

## 📖 Hướng dẫn sử dụng chi tiết

### 1. Tìm kiếm sản phẩm
- Mở tab **Search**
- Nhập từ khóa tìm kiếm (VD: "organic chocolate")
- Chọn phương thức: Bi-Encoder hoặc Hybrid (khuyến nghị)
- Xem kết quả với điểm số relevance

### 2. Thêm sản phẩm mới
- Mở tab **Add Product**
- Điền thông tin bắt buộc: Name, Brand, Ingredients
- Điền thông tin tùy chọn: Categories, Manufacturer, etc.
- Click **Add Product**

### 3. Quản lý sản phẩm
- Mở tab **Manage Products**
- **Browse**: Xem danh sách với filter và pagination
- **Edit**: Click nút Edit để chỉnh sửa
- **Delete**: Click nút Delete để xóa (có xác nhận)

### 4. Xem thống kê
- Mở tab **Statistics**
- Xem tổng số sản phẩm, thời gian response, etc.

## 🔌 API Usage Examples

### Search Products
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "organic chocolate", "method": "hybrid", "top_k": 3}'
```

### Add Product
```bash
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Organic Dark Chocolate",
    "brand": "Green Valley",
    "ingredients": "cocoa beans, cocoa butter, sugar"
  }'
```

### Get Products List
```bash
curl "http://localhost:5000/api/products?page=1&per_page=10&filter=chocolate"
```

## 📝 Notes

- Hệ thống tự động tạo embeddings khi thêm/sửa sản phẩm
- FAISS index được rebuild khi xóa sản phẩm
- Tất cả thay đổi được persist vào files
- Frontend có real-time updates và loading states

## 📄 License

MIT License - See LICENSE file for details.