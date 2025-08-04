# Product Retrieval API Documentation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start API Server
```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

### 3. Test API
```bash
python test_api.py
```

## 📚 API Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-03T10:30:00",
  "services": {
    "searcher": true,
    "product_manager": true,
    "product_updater": true,
    "product_deleter": true
  }
}
```

### Search Products
```http
POST /api/search
Content-Type: application/json

{
  "query": "milk chocolate",
  "method": "hybrid",  // "bi_encoder" | "hybrid"
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "milk chocolate",
  "method": "hybrid",
  "total_results": 5,
  "results": [
    {
      "id": 123,
      "name": "Chocolate Milk Powder",
      "brand": "Brand Name",
      "ingredients": "Milk, Cocoa, Sugar",
      "categories": "Beverages",
      "manufacturer": "Company",
      "manufacturerNumber": "CM001",
      "score": 0.95
    }
  ],
  "timestamp": "2025-08-03T10:30:00"
}
```

### Add Product
```http
POST /api/products
Content-Type: application/json

{
  "name": "New Product Name",
  "brand": "Brand Name",
  "ingredients": "Ingredient 1, Ingredient 2",
  "categories": "Category 1, Category 2",
  "manufacturer": "Manufacturer Name",
  "manufacturerNumber": "MN001"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Product added successfully",
  "product_id": 500,
  "timestamp": "2025-08-03T10:30:00"
}
```

### Get Product by ID
```http
GET /api/products/{id}
```

**Response:**
```json
{
  "success": true,
  "product": {
    "id": 123,
    "name": "Product Name",
    "brand": "Brand Name",
    "ingredients": "Ingredients",
    "categories": "Categories",
    "manufacturer": "Manufacturer",
    "manufacturerNumber": "MN001"
  },
  "timestamp": "2025-08-03T10:30:00"
}
```

### Update Product
```http
PUT /api/products/{id}
Content-Type: application/json

{
  "name": "Updated Product Name",
  "brand": "Updated Brand",
  "ingredients": "Updated Ingredients",
  "categories": "Updated Categories",
  "manufacturer": "Updated Manufacturer",
  "manufacturerNumber": "UMN001"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Product updated successfully",
  "product_id": 123,
  "timestamp": "2025-08-03T10:30:00"
}
```

### Delete Product
```http
DELETE /api/products/{id}
```

**Response:**
```json
{
  "success": true,
  "message": "Product deleted successfully",
  "product_id": 123,
  "timestamp": "2025-08-03T10:30:00"
}
```

### Delete Multiple Products
```http
DELETE /api/products
Content-Type: application/json

{
  "product_ids": [123, 124, 125]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully deleted 3 products",
  "product_ids": [123, 124, 125],
  "timestamp": "2025-08-03T10:30:00"
}
```

### List Products (with Pagination)
```http
GET /api/products?page=1&limit=20&search=chocolate
```

**Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `search`: Search keyword (optional)

**Response:**
```json
{
  "success": true,
  "products": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_count": 500,
    "total_pages": 25,
    "has_next": true,
    "has_prev": false
  },
  "search_query": "chocolate",
  "timestamp": "2025-08-03T10:30:00"
}
```

### Get Statistics
```http
GET /api/stats
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_products": 500,
    "total_vectors": 500,
    "vector_dimension": 1024,
    "top_brands": {
      "Brand A": 50,
      "Brand B": 45
    },
    "text_corpus_stats": {
      "avg_length": 150,
      "min_length": 50,
      "max_length": 500
    }
  },
  "timestamp": "2025-08-03T10:30:00"
}
```

## 🔧 Configuration

API settings trong `config/simple_config.py`:

```python
API_SETTINGS = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'cors_enabled': True,
    'max_page_size': 100,
    'default_page_size': 20
}
```

## 🧪 Testing

### Manual Testing
```bash
# Start API server
python app.py

# In another terminal, run tests
python test_api.py
```

### Using curl
```bash
# Health check
curl http://localhost:5000/api/health

# Search
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "chocolate", "top_k": 3}'

# Add product
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "brand": "Test Brand", 
    "ingredients": "Test Ingredients"
  }'
```

## 🚨 Error Handling

All endpoints return consistent error formats:

```json
{
  "error": "Error description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created (for add operations)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## 🎯 Performance

- **Search Response Time**: < 200ms
- **CRUD Operations**: < 500ms
- **Concurrent Requests**: Supported
- **Real-time Updates**: Embeddings updated immediately

## 🔒 Security Notes

- API runs in development mode by default
- For production, consider:
  - Rate limiting
  - Authentication
  - Input sanitization
  - HTTPS
  - Database connection pooling
