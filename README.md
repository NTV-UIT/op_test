# Product Retrieval System

A powerful semantic search system for product discovery using advanced AI embeddings and vector similarity search. This system enables intelligent product search based on natural language queries, ingredients, brands, and product characteristics.

## 🎯 Overview

The Product Retrieval System is designed to provide accurate and relevant product search results using state-of-the-art natural language processing and machine learning techniques. It combines traditional keyword matching with semantic understanding to deliver superior search experiences.

## ✨ Key Features

- **🔍 Semantic Search**: Advanced AI-powered search using sentence transformers
- **⚡ Vector Similarity**: FAISS-powered fast similarity search with 1024-dimensional embeddings
- **🎯 Hybrid Approach**: Combines Bi-Encoder and Cross-Encoder models for optimal results
- **📊 Real-time Analytics**: Performance metrics and search analytics dashboard
- **🌐 Web Interface**: Modern, responsive UI built with Bootstrap 5
- **🔗 REST API**: Complete API for integration with other systems
- **📈 Product Management**: Add, edit, and delete products with live index updates

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python 3.8+)
- **Search Engine**: FAISS (Facebook AI Similarity Search)
- **ML Models**: 
  - Bi-Encoder: `BAAI/bge-large-en-v1.5` (1024-dim embeddings)
  - Cross-Encoder: `BAAI/bge-reranker-base` (for reranking)
- **Data Processing**: Pandas, NumPy
- **API**: Flask-CORS for cross-origin requests

### Frontend
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js for analytics visualization
- **Icons**: Font Awesome
- **Styling**: Custom CSS with responsive design

### Data Storage
- **Metadata**: CSV format for product information
- **Embeddings**: NumPy arrays (.npy files)
- **Vector Index**: FAISS index files for fast similarity search

## 📁 Project Structure

```
product_retrieval_system/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── run.py                             # Application entry point
├── gt.csv                             # Ground truth queries for evaluation
├── ingredients v1.csv                 # Food Ingredient Lists data
├── product_metadata.csv               # Main product database
├── embeddings.npy                     # Precomputed embeddings
├── faiss_index.index                  # FAISS vector index
├── evaluation_results.json            # System evaluation metrics
├── dataprocess.ipynb                  # Data processing notebook
├── product_retrieval_system.ipynb     # System development notebook
│
├── product_retrieval_app/             # Main application
│   ├── README.md                      # App-specific documentation
│   ├── requirements.txt               # App dependencies
│   ├── run.py                         # Flask app runner
│   ├── test_api.py                    # API testing script
│   │
│   ├── backend/                       # Backend components
│   │   ├── app.py                     # Main Flask application
│   │   ├── database/
│   │   │   ├── search_engine.py       # Core search functionality
│   │   │   └── crud_operations.py     # Product management
│   │   └── utils/
│   │       └── validation.py          # Data validation
│   │
│   ├── frontend/                      # Frontend components
│   │   ├── templates/                 # Jinja2 templates
│   │   │   ├── base.html             # Base template
│   │   │   ├── dashboard.html        # Analytics dashboard
│   │   │   ├── search.html           # Search interface
│   │   │   └── admin.html            # Admin panel
│   │   └── static/                   # Static assets
│   │       ├── css/style.css         # Custom styles
│   │       └── js/                   # JavaScript files
│   │
│   ├── config/                       # Configuration
│   │   └── settings.py               # App settings
│   │
│   ├── data/                         # Application data
│   │   ├── product_metadata.csv      # Product database
│   │   ├── embeddings.npy            # Vector embeddings
│   │   ├── faiss_index.index         # Search index
│   │   └── uploads/                  # File uploads
│   │
│   ├── logs/                         # Application logs
│   └── tests/                        # Test files
```

## 📊 Data Sources

### Core Dataset
- **`product_metadata.csv`**: Main product database containing:
  - Product ID, name, brand
  - Categories and classifications  
  - Detailed ingredient lists
  - Manufacturer information
  - Text corpus for semantic search

### Food Ingredients Data
- **`ingredients v1.csv`**: Comprehensive ingredient database sourced from **Food Ingredient Lists**
  - Standardized ingredient names and classifications
  - Ingredient-based queries (garlic powder, cinnamon, etc.)
  - Category searches (fresh food, coffee products, etc.)
### Prerequisites
- Python 3.8 or higher

   git clone <your-repository-url>
2. **Install dependencies**
   ```bash
   pip install -r product_retrieval_app/requirements.txt
   ```

3. **Verify data files**
   ```bash
   ls product_retrieval_app/data/
   # Should show: embeddings.npy, faiss_index.index, product_metadata.csv
   ```

4. **Run the application**
   ```bash
   cd product_retrieval_app
   python run.py
   ```

5. **Access the application**
   - Web Interface: http://localhost:5001
   - API Base URL: http://localhost:5001/api

## 🔧 Configuration

### Environment Variables
```bash
# Application settings
DEBUG=True                    # Enable debug mode
HOST=0.0.0.0                 # Server host
PORT=5001                    # Server port

# Model settings  
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
CROSS_ENCODER_MODEL=BAAI/bge-reranker-base
```

### Model Configuration
- **Embedding Dimension**: 1024 (BGE-large)
- **Max Sequence Length**: 512 tokens
- **Batch Size**: 32
- **Device**: CPU (configurable)

## 🌐 API Documentation

### Search Endpoint
```http
POST /api/search
Content-Type: application/json

{
  "query": "organic juice with vitamin C",
  "method": "hybrid",
  "top_k": 10
Semantic product search using AI embeddings and vector similarity. Search by natural language, ingredients, brands, and product features.

Accurate product search using NLP and ML. Combines keyword and semantic matching for better results.

**Semantic Search** (AI-powered), **Vector Similarity** (FAISS, 1024-dim), **Hybrid Model** (Bi-Encoder + Cross-Encoder), **Analytics Dashboard**, **Web UI** (Bootstrap 5), **REST API**, **Product Management** (CRUD, live index).

Backend: Flask, FAISS, Pandas, NumPy, Flask-CORS. ML: Bi-Encoder (BAAI/bge-large-en-v1.5), Cross-Encoder (BAAI/bge-reranker-base). Frontend: Bootstrap 5, Chart.js, Font Awesome. Data: CSV, .npy, FAISS index.

product_retrieval_system/
├── README.md
├── requirements.txt
├── run.py
├── gt.csv
├── ingredients v1.csv
├── product_metadata.csv
├── embeddings.npy
├── faiss_index.index
├── evaluation_results.json
├── dataprocess.ipynb
├── product_retrieval_system.ipynb
├── product_retrieval_app/
│   ├── backend/
│   ├── frontend/
│   ├── config/
│   ├── data/
│   ├── logs/
│   └── tests/

1. Clone repo & install dependencies:
   ```bash
   git clone <your-repository-url>
   cd product_retrieval_system
   pip install -r product_retrieval_app/requirements.txt
   ```
2. Verify data files:
   ```bash
   ls product_retrieval_app/data/
   # Should show: embeddings.npy, faiss_index.index, product_metadata.csv
   ```
3. Run app:
   ```bash
   cd product_retrieval_app
   python run.py
   ```
4. Access: http://localhost:5001

Environment variables:
```bash
DEBUG=True
HOST=0.0.0.0
PORT=5001
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
CROSS_ENCODER_MODEL=BAAI/bge-reranker-base
```

API endpoints:
- `/api/search` (POST): Search products
- `/api/products` (CRUD): Manage products
- `/api/stats` (GET): System stats

### PERFORMANCE COMPARISON
```
Metric      Bi-Encoder   Hybrid     Improvement
----------------------------------------------
Hit@3 (%)   90.9        100.0      +9.1
MRR (%)     79.1        94.7       +15.6
P@3 (%)     65.2        83.3       +18.2
Time (ms)   17.2        138.4      +121.2
```

🏆 BEST METHOD: Hybrid (Score: 93.4)

---
**Quick Start:** Clone, install, run, and access at http://localhost:5001

**Best for:** Fast, accurate product search using hybrid semantic methods.

**Contact:** Issues, docs, or test suite for support.
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": 123,
      "name": "Organic Apple Juice",
      "brand": "Healthy Brand",
      "score": 0.85,
      "text_corpus": "..."
    }
  ],
  "total": 10
}
```

### Product Management
```http
# Add Product
POST /api/products
{
  "name": "New Product",
  "brand": "Brand Name",
  "categories": "food,beverages",
  "ingredients": "water, sugar, natural flavors"
}

# Update Product
PUT /api/products/{id}
{
  "name": "Updated Product Name"
}

# Delete Product
DELETE /api/products/{id}
```

### Statistics
```http
GET /api/stats
```

## 🎮 Usage Examples

### Web Interface

1. **Dashboard**: View system statistics and quick actions
   - Total products and embeddings count
   - Top brands distribution
   - System status indicators

2. **Search**: Perform intelligent product search
   - Natural language queries
   - Real-time results with relevance scores
   - Filter by search method (semantic, hybrid)

3. **Admin Panel**: Manage product database
   - Add new products
   - Edit existing entries
   - Delete products with automatic index updates

### Programmatic Usage

```python
import requests

# Search for products
response = requests.post('http://localhost:5001/api/search', json={
    'query': 'coffee beans with chocolate flavor',
    'method': 'hybrid',
    'top_k': 5
})

results = response.json()['results']
for product in results:
    print(f"{product['name']} - Score: {product['score']:.3f}")
```

## 🧪 Testing

### Run API Tests
```bash
cd product_retrieval_app
python test_api.py
```

### Test Coverage
- Search functionality (semantic, hybrid methods)
- Product CRUD operations
- Web page accessibility
- API endpoint validation

### Evaluation Metrics
The system is evaluated using the ground truth queries in `gt.csv`:
- **Precision@K**: Accuracy of top-K results
- **Recall@K**: Coverage of relevant documents
- **MRR**: Mean Reciprocal Rank
- **NDCG**: Normalized Discounted Cumulative Gain

## 📈 Performance

### Search Performance
- **Index Size**: ~500 products with 1024-dim vectors
- **Search Latency**: <100ms for typical queries
- **Memory Usage**: ~2GB (including ML models)
- **Throughput**: 50+ queries/second

### Model Performance
- **Bi-Encoder**: Fast initial retrieval (semantic similarity)
- **Cross-Encoder**: Precise reranking (contextual relevance)
- **Hybrid Approach**: Combines speed and accuracy

## 🔍 Search Methods

1. **Semantic Search**: Pure vector similarity using embeddings
2. **Hybrid Search**: Combines semantic and keyword matching
3. **Cross-Encoder Reranking**: Enhanced relevance scoring

## 🛡️ Data Validation

- Input sanitization for all API endpoints
- Product data validation (required fields, formats)
- Embedding dimension consistency checks
- FAISS index integrity validation

## 📝 Development Notes

### Adding New Products
When adding products, the system automatically:
1. Validates input data
2. Generates embeddings using the Bi-Encoder
3. Updates the FAISS index
4. Saves metadata to CSV
5. Persists embeddings to disk

### Model Updates
To update or retrain models:
1. Modify model paths in `config/settings.py`
2. Regenerate embeddings using `dataprocess.ipynb`
3. Rebuild FAISS index
4. Test with evaluation queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Food Ingredient Lists**: Data source for ingredient information
- **BAAI**: BGE embedding models
- **Facebook Research**: FAISS vector search
- **Hugging Face**: Transformers and model hosting
- **Flask Community**: Web framework and extensions

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Run the test suite for debugging

---

**Built with ❤️ for intelligent product discovery**
