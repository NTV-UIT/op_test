#!/usr/bin/env python3
"""
Product Retrieval API - Search Focus
Flask API cho hệ thống tìm kiếm sản phẩm
"""

import os
import sys
import json
import traceback
import socket
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

# Import our modules
from src.search import ProductSearcher
from src.add_row import ProductManager
from src.delete_row import ProductDeleter
from src.update_row import ProductUpdater
from simple_config import API_SETTINGS, get_global_embedding_model, monitor_gpu_memory

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # Enable CORS for frontend integration

# Global variables for search service and database managers
searcher = None
product_manager = None
product_deleter = None
product_updater = None


def find_available_port(start_port=5000, max_attempts=10):
    """Tìm port khả dụng bắt đầu từ start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise OSError(f"Không tìm thấy port khả dụng trong khoảng {start_port}-{start_port + max_attempts - 1}")


def initialize_search_service():
    """Khởi tạo search service và database managers"""
    global searcher, product_manager, product_deleter, product_updater
    
    try:
        print("🚀 Initializing search service...")
        
        # ✅ Khởi tạo global models trước - chỉ load 1 lần duy nhất
        print("🔄 Pre-loading global models...")
        model, tokenizer = get_global_embedding_model()
        print("✅ Global models loaded")
        monitor_gpu_memory("After loading global models")
        
        # Initialize searcher
        searcher = ProductSearcher()
        print("✅ ProductSearcher initialized")
        
        # Initialize database managers
        product_manager = ProductManager()
        print("✅ ProductManager initialized")
        
        product_deleter = ProductDeleter()
        print("✅ ProductDeleter initialized")
        
        product_updater = ProductUpdater()
        print("✅ ProductUpdater initialized")
        
        print("🎉 Search service and database managers initialized successfully!")
        monitor_gpu_memory("After all initialization")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing search service: {e}")
        traceback.print_exc()
        return False


def reload_all_managers():
    """Reload tất cả managers sau khi database thay đổi"""
    global searcher, product_manager, product_deleter, product_updater
    
    try:
        print("🔄 Reloading all managers...")
        
        # Reload searcher
        if searcher:
            searcher._load_data()
            print("✅ Searcher reloaded")
        
        # Reload database managers
        if product_manager:
            product_manager._load_data()
            print("✅ ProductManager reloaded")
            
        if product_deleter:
            product_deleter.reload_data()
            print("✅ ProductDeleter reloaded")
            
        if product_updater:
            product_updater._load_data()
            print("✅ ProductUpdater reloaded")
        
        print("🎉 All managers reloaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error reloading managers: {e}")
        return False


def safe_str(value):
    """Helper function to safely convert values to string, handling NaN"""
    if pd.isna(value):
        return ''
    return str(value)


def convert_numpy_types(obj):
    """Convert numpy types to Python native types"""
    if hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def format_search_results(results: List[Dict], scores: List[float] = None) -> List[Dict]:
    """Format search results for API response"""
    formatted_results = []
    
    for i, result in enumerate(results):
        # Convert all values to ensure JSON serializable
        result_id = convert_numpy_types(result.get('id', i))
        score = convert_numpy_types(scores[i] if scores and i < len(scores) else 0.0)
        
        formatted_result = {
            'id': int(result_id),
            'name': safe_str(result.get('name', '')),
            'brand': safe_str(result.get('brand', '')),
            'ingredients': safe_str(result.get('ingredients', '')),
            'categories': safe_str(result.get('categories', '')),
            'manufacturer': safe_str(result.get('manufacturer', '')),
            'manufacturerNumber': safe_str(result.get('manufacturerNumber', '')),
            'score': float(score)
        }
        formatted_results.append(formatted_result)
    
    return formatted_results


@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index_new.html')


@app.route('/test')
def test_api():
    """Serve API test page"""
    return render_template('test_api.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'searcher': searcher is not None
        }
    })


@app.route('/api/search', methods=['POST'])
def search_products():
    """
    Tìm kiếm sản phẩm
    
    Request body:
    {
        "query": "search query",
        "method": "bi_encoder" | "hybrid",
        "top_k": 5
    }
    """
    try:
        if not searcher:
            return jsonify({'error': 'Search service not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        method = data.get('method', 'hybrid')
        top_k = min(max(data.get('top_k', 5), 1), 50)  # Limit between 1-50
        
        # Perform search
        if method == 'bi_encoder':
            results, scores = searcher.bi_encoder_search(query, top_k)
        else:  # hybrid
            results, scores = searcher.hybrid_search(query, top_k)
        
        # Format results
        formatted_results = format_search_results(results, scores)
        
        return jsonify({
            'success': True,
            'query': query,
            'method': method,
            'total_results': len(formatted_results),
            'results': formatted_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/api/products', methods=['GET'])
def list_products():
    """
    Lấy danh sách sản phẩm với pagination
    
    Query parameters:
    - page: số trang (default: 1)
    - limit: số sản phẩm mỗi trang (default: 20, max: 100)
    - search: từ khóa tìm kiếm (optional)
    """
    try:
        if not searcher:
            return jsonify({'error': 'Search service not initialized'}), 500
        
        # Get query parameters
        page = max(int(request.args.get('page', 1)), 1)
        limit = min(max(int(request.args.get('limit', 20)), 1), 100)
        search_query = request.args.get('search', '').strip()
        
        # Get metadata from searcher
        df = searcher.metadata_df
        
        # Filter by search query if provided
        if search_query:
            mask = (
                df['name'].str.contains(search_query, case=False, na=False) |
                df['brand'].str.contains(search_query, case=False, na=False) |
                df.get('ingredients', pd.Series()).str.contains(search_query, case=False, na=False)
            )
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        # Calculate pagination
        total_count = len(filtered_df)
        total_pages = (total_count - 1) // limit + 1 if total_count > 0 else 0
        start_idx = (page - 1) * limit
        end_idx = min(start_idx + limit, total_count)
        
        # Get page data
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        products = []
        for idx, row in page_df.iterrows():
            products.append({
                'id': int(convert_numpy_types(row.get('id', idx))),
                'name': safe_str(row.get('name', '')),
                'brand': safe_str(row.get('brand', '')),
                'ingredients': safe_str(row.get('ingredients', '')),
                'categories': safe_str(row.get('categories', '')),
                'manufacturer': safe_str(row.get('manufacturer', '')),
                'manufacturerNumber': safe_str(row.get('manufacturerNumber', ''))
            })
        
        return jsonify({
            'success': True,
            'products': products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'search_query': search_query,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"List products error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'List products failed: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_database_stats():
    """Lấy thống kê database để debug"""
    try:
        if not searcher:
            return jsonify({'error': 'Search service not initialized'}), 500
            
        df = searcher.metadata_df
        stats = {
            'total_products': len(df),
            'id_range': {
                'min': int(df['id'].min()) if len(df) > 0 else None,
                'max': int(df['id'].max()) if len(df) > 0 else None
            },
            'sample_ids': df['id'].head(10).tolist() if len(df) > 0 else [],
            'faiss_vectors': searcher.index.ntotal if searcher.index else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': f'Stats failed: {str(e)}'}), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    """Lấy thông tin sản phẩm theo ID"""
    try:
        if not searcher:
            return jsonify({'error': 'Search service not initialized'}), 500
        
        # Check if product exists by ID value, not by index
        if product_id not in searcher.metadata_df['id'].values:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get product data using ID
        product = searcher.metadata_df[searcher.metadata_df['id'] == product_id].iloc[0]
        
        print(f"Debug - Product {product_id}:")
        print(f"  Name: {product.get('name', 'MISSING')}")
        print(f"  Brand: {product.get('brand', 'MISSING')}")
        print(f"  Categories: {product.get('categories', 'MISSING')}")
        print(f"  Manufacturer: {product.get('manufacturer', 'MISSING')}")
        print(f"  ManufacturerNumber: {product.get('manufacturerNumber', 'MISSING')}")
        
        # Handle NaN values for ingredients
        ingredients = product.get('ingredients', 'MISSING')
        if pd.isna(ingredients) or not isinstance(ingredients, str):
            ingredients_preview = "MISSING"
        else:
            ingredients_preview = ingredients[:50] + "..." if len(ingredients) > 50 else ingredients
        print(f"  Ingredients: {ingredients_preview}")
        
        product_data = {
            'id': int(product['id']),  # Use actual ID from metadata
            'name': safe_str(product.get('name', '')),
            'brand': safe_str(product.get('brand', '')),
            'ingredients': safe_str(product.get('ingredients', '')),
            'categories': safe_str(product.get('categories', '')),
            'manufacturer': safe_str(product.get('manufacturer', '')),
            'manufacturerNumber': safe_str(product.get('manufacturerNumber', ''))
        }
        
        return jsonify({
            'success': True,
            'product': product_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Get product error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Get product failed: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Lấy thống kê hệ thống"""
    try:
        if not searcher:
            return jsonify({'error': 'Search service not initialized'}), 500
        
        df = searcher.metadata_df
        index = searcher.index
        
        # Basic stats
        total_products = int(len(df))
        total_vectors = int(convert_numpy_types(index.ntotal)) if hasattr(index, 'ntotal') else 0
        vector_dimension = int(convert_numpy_types(index.d)) if hasattr(index, 'd') else 0
        
        # Brand statistics - convert to regular dict with string keys
        brand_counts = df['brand'].value_counts().head(10)
        brand_stats = {str(k): int(convert_numpy_types(v)) for k, v in brand_counts.items()}
        
        # Text length statistics
        if 'text_corpus' in df.columns:
            text_lengths = df['text_corpus'].str.len()
            text_stats = {
                'avg_length': float(convert_numpy_types(text_lengths.mean())),
                'min_length': int(convert_numpy_types(text_lengths.min())),
                'max_length': int(convert_numpy_types(text_lengths.max()))
            }
        else:
            text_stats = {'avg_length': 0, 'min_length': 0, 'max_length': 0}
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_products': total_products,
                'total_vectors': total_vectors,
                'vector_dimension': vector_dimension,
                'top_brands': brand_stats,
                'text_corpus_stats': text_stats
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Get statistics error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Get statistics failed: {str(e)}'}), 500


@app.route('/api/products', methods=['POST'])
def add_product():
    """
    Thêm sản phẩm mới
    
    Request body:
    {
        "name": "Product Name",
        "brand": "Brand Name",
        "ingredients": "Ingredient list",
        "categories": "Category list",
        "manufacturer": "Manufacturer",
        "manufacturerNumber": "MFG123"
    }
    """
    try:
        if not product_manager:
            return jsonify({'error': 'Product manager not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'brand']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create product data
        product_data = {
            'name': str(data.get('name', '')),
            'brand': str(data.get('brand', '')),
            'ingredients': str(data.get('ingredients', '')),
            'categories': str(data.get('categories', '')),
            'manufacturer': str(data.get('manufacturer', '')),
            'manufacturerNumber': str(data.get('manufacturerNumber', ''))
        }
        
        # Add product using ProductManager
        success = product_manager.add_product_from_data(product_data)
        
        if success:
            # Reload all managers to reflect changes
            reload_all_managers()
            
            return jsonify({
                'success': True,
                'message': 'Product added successfully',
                'product': product_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to add product'}), 500
        
    except Exception as e:
        print(f"Add product error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Add product failed: {str(e)}'}), 500


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Xóa sản phẩm theo ID
    """
    try:
        if not product_deleter:
            return jsonify({'error': 'Product deleter not initialized'}), 500
        
        # Reload data to ensure consistency
        product_deleter.reload_data()
        
        # Check if product exists
        df = product_deleter.metadata_df
        if product_id not in df['id'].values:
            return jsonify({'error': f'Product with ID {product_id} not found'}), 404
        
        # Get product info before deletion
        product_info = df[df['id'] == product_id].iloc[0].to_dict()
        
        # Delete product
        success = product_deleter.delete_products([product_id])
        
        if success:
            # Reload all managers to reflect changes
            reload_all_managers()
            
            return jsonify({
                'success': True,
                'message': f'Product {product_id} deleted successfully',
                'deleted_product': {
                    'id': int(product_id),
                    'name': safe_str(product_info.get('name', '')),
                    'brand': safe_str(product_info.get('brand', ''))
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to delete product'}), 500
        
    except Exception as e:
        print(f"Delete product error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Delete product failed: {str(e)}'}), 500


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Cập nhật sản phẩm theo ID
    
    Request body:
    {
        "name": "Updated Product Name",
        "brand": "Updated Brand Name",
        "ingredients": "Updated ingredients",
        "categories": "Updated categories",
        "manufacturer": "Updated Manufacturer",
        "manufacturerNumber": "Updated MFG123"
    }
    """
    try:
        if not product_updater:
            return jsonify({'error': 'Product updater not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Check if product exists
        df = product_updater.metadata_df
        if product_id not in df['id'].values:
            return jsonify({'error': f'Product with ID {product_id} not found'}), 404
        
        # Get current product info
        current_product = df[df['id'] == product_id].iloc[0].to_dict()
        
        # Prepare update data - only update provided fields
        update_data = {}
        updateable_fields = ['name', 'brand', 'ingredients', 'categories', 'manufacturer', 'manufacturerNumber']
        
        for field in updateable_fields:
            if field in data:
                update_data[field] = str(data[field])
        
        if not update_data:
            return jsonify({'error': 'No updateable fields provided'}), 400
        
        # Update product
        success = product_updater.update_product(product_id, update_data)
        
        if success:
            # Reload all managers to reflect changes
            reload_all_managers()
            
            # Get updated product info
            updated_df = searcher.metadata_df  # Use reloaded searcher data
            updated_product = updated_df[updated_df['id'] == product_id].iloc[0].to_dict()
            
            return jsonify({
                'success': True,
                'message': f'Product {product_id} updated successfully',
                'product': {
                    'id': int(product_id),
                    'name': safe_str(updated_product.get('name', '')),
                    'brand': safe_str(updated_product.get('brand', '')),
                    'ingredients': safe_str(updated_product.get('ingredients', '')),
                    'categories': safe_str(updated_product.get('categories', '')),
                    'manufacturer': safe_str(updated_product.get('manufacturer', '')),
                    'manufacturerNumber': safe_str(updated_product.get('manufacturerNumber', ''))
                },
                'updated_fields': list(update_data.keys()),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to update product'}), 500
        
    except Exception as e:
        print(f"Update product error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Update product failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Starting Product Retrieval API (Search Focus)...")
    
    # Initialize search service
    if not initialize_search_service():
        print("❌ Failed to initialize search service. Exiting.")
        sys.exit(1)
    
    print("🌐 API Endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/search - Search products")
    print("  GET  /api/products - List products (with pagination)")
    print("  POST /api/products - Add new product")
    print("  GET  /api/products/<id> - Get product by ID")
    print("  PUT  /api/products/<id> - Update product by ID")
    print("  DELETE /api/products/<id> - Delete product by ID")
    print("  GET  /api/stats - Get system statistics")
    
    # Find available port
    try:
        default_port = API_SETTINGS.get('port', 5000)
        available_port = find_available_port(default_port)
        
        if available_port != default_port:
            print(f"⚠️  Port {default_port} is in use, using port {available_port} instead")
        else:
            print(f"✅ Using default port {available_port}")
        
        print(f"🌐 Server starting at: http://localhost:{available_port}")
        
        # Start Flask app
        app.run(
            host=API_SETTINGS.get('host', '0.0.0.0'),
            port=available_port,
            debug=API_SETTINGS.get('debug', False)
        )
        
    except OSError as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try stopping other applications using ports 5000-5009")
        sys.exit(1)
