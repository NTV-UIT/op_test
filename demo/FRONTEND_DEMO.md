# 🌐 Product Retrieval System - Frontend Demo

Giao diện web đơn giản để demo các chức năng của hệ thống Product Retrieval với AI.

## 🎯 Chức năng chính

### 🔍 **Tab Tìm kiếm**
- **Search Input**: Nhập từ khóa (ví dụ: "chocolate milk", "protein", "vitamin")
- **Search Methods**: 
  - `Hybrid` (Bi-encoder + Cross-encoder) - Khuyến nghị
  - `Bi-encoder only` - Nhanh hơn
- **Top-K Results**: Số lượng kết quả trả về (1-20)
- **Real-time Scoring**: Hiển thị độ tương tự (%)

### ➕ **Tab Thêm sản phẩm**
- **Form Fields**:
  - `Tên sản phẩm` * (bắt buộc)
  - `Thương hiệu` * (bắt buộc)  
  - `Thành phần` * (bắt buộc)
  - `Danh mục` (tùy chọn)
  - `Nhà sản xuất` (tùy chọn)
  - `Mã sản xuất` (tùy chọn)
- **Auto-embedding**: Tự động tạo embedding và cập nhật index
- **Validation**: Kiểm tra dữ liệu đầu vào

### 🛠️ **Tab Quản lý**
- **Product List**: Danh sách sản phẩm với pagination
- **Search Filter**: Tìm kiếm trong danh sách
- **Edit Product**: Modal popup để chỉnh sửa
- **Delete Product**: Xóa với xác nhận
- **Real-time Updates**: Tự động refresh sau thao tác

### 📊 **Tab Thống kê**
- **System Stats**: Tổng sản phẩm, vectors, dimensions
- **Top Brands**: Thương hiệu phổ biến nhất
- **Performance Metrics**: Độ dài text trung bình
- **Real-time Data**: Cập nhật theo thời gian thực

## 🚀 Cách chạy Demo

### Option 1: Quick Start (Khuyến nghị)
```bash
python run_demo.py
```
- Tự động kiểm tra dependencies
- Tự động kiểm tra data files
- Tự động mở browser
- Server: http://localhost:5000

### Option 2: Manual Start
```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Chạy API server
python app.py

# 3. Mở browser
# http://localhost:5000
```

## 🔧 API Endpoints được sử dụng

| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET | `/` | Serve frontend |
| GET | `/api/health` | Check API status |
| POST | `/api/search` | Tìm kiếm sản phẩm |
| GET | `/api/products` | List sản phẩm (pagination) |
| POST | `/api/products` | Thêm sản phẩm |
| GET | `/api/products/{id}` | Chi tiết sản phẩm |
| PUT | `/api/products/{id}` | Cập nhật sản phẩm |
| DELETE | `/api/products/{id}` | Xóa sản phẩm |
| GET | `/api/stats` | Thống kê hệ thống |

## 🎨 Frontend Stack

- **HTML5**: Semantic structure
- **CSS3**: Modern styling với animations
- **Vanilla JavaScript**: No frameworks, pure JS
- **Font Awesome**: Icons
- **Responsive Design**: Mobile-friendly

## 📱 UI Features

### 🎨 **Styling**
- **Modern Design**: Gradient backgrounds, glass morphism
- **Responsive Layout**: Mobile-first design
- **Smooth Animations**: Hover effects, transitions
- **Status Indicators**: Real-time API status
- **Toast Notifications**: Success/Error messages

### 🔄 **UX Features**
- **Tab Navigation**: Intuitive interface
- **Loading States**: Spinners and overlays
- **Error Handling**: User-friendly error messages  
- **Form Validation**: Client-side validation
- **Modal Dialogs**: Edit product popup
- **Pagination**: Navigate large datasets
- **Auto-refresh**: Real-time data updates

### 📊 **Data Display**
- **Search Results**: Score-based ranking
- **Product Cards**: Clean information layout
- **Statistics Dashboard**: Visual metrics
- **Pagination Controls**: Easy navigation
- **Filter/Search**: Real-time filtering

## 🧪 Demo Scenarios

### 1. **Search Demo**
```
Query: "chocolate milk"
Method: Hybrid
Top-K: 5
Expected: Products with chocolate/milk in name/ingredients
```

### 2. **Add Product Demo**
```
Name: "Demo Protein Powder"
Brand: "Demo Brand"
Ingredients: "Whey protein, Natural flavors"
Categories: "Sports Nutrition"
```

### 3. **Edit Product Demo**
- Find product in Manage tab
- Click "Sửa" button
- Update information in modal
- See real-time updates

### 4. **Delete Product Demo**
- Find product in Manage tab
- Click "Xóa" button
- Confirm deletion
- See updated list

## 🚨 Troubleshooting

### API Offline
- Check if `python app.py` is running
- Verify dependencies are installed
- Check data files exist

### No Search Results
- Try different keywords
- Check if embeddings are loaded
- Verify FAISS index exists

### Add/Edit Fails
- Check required fields are filled
- Verify API is accessible
- Check browser console for errors

### UI Issues
- Refresh browser page
- Check browser console
- Verify static files are served

## 🔗 Related Files

```
demo/
├── app.py                    # Flask API server
├── run_demo.py              # Demo runner script
├── templates/
│   └── index.html           # Frontend HTML
├── static/
│   ├── style.css            # Styling
│   └── script.js            # JavaScript logic
├── test_api.py              # API testing
└── requirements.txt         # Dependencies
```

## 💡 Tips

- **Performance**: Hybrid search cho kết quả tốt nhất
- **Data**: Test với keywords có trong dataset
- **Responsive**: Works on mobile devices
- **Keyboard**: Enter key works in search
- **Auto-save**: Changes are immediate
- **Real-time**: No need to refresh manually

## 🎉 Demo Success Criteria

✅ **API Status**: Green "API Online" indicator  
✅ **Search**: Returns relevant results with scores  
✅ **Add**: Successfully adds new product  
✅ **Edit**: Updates product information  
✅ **Delete**: Removes product from system  
✅ **Stats**: Shows current system metrics  
✅ **UI/UX**: Smooth, responsive interface
