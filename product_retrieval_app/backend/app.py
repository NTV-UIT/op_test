from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.search_engine import SearchEngine
from database.crud_operations import ProductManager
from utils.validation import validate_product_data

app = Flask(__name__, 
           template_folder='../frontend/templates/',
           static_folder='../frontend/static/')
CORS(app)

# Initialize components
search_engine = SearchEngine(data_path='../data/')
product_manager = ProductManager(data_path='../data/')

@app.route('/')
def dashboard():
    """Main dashboard"""
    stats = product_manager.get_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/search')
def search_page():
    """Search interface"""
    return render_template('search.html')

@app.route('/admin')
def admin_page():
    """Admin panel"""
    products = product_manager.get_recent_products(limit=20)
    return render_template('admin.html', products=products)

# API Routes
@app.route('/api/search', methods=['POST'])
def api_search():
    """Search API endpoint"""
    data = request.get_json()
    query = data.get('query', '')
    method = data.get('method', 'hybrid')
    top_k = data.get('top_k', 10)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        results = search_engine.search(query, method=method, top_k=top_k)
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def api_add_product():
    """Add product API"""
    data = request.get_json()
    
    # Validate data
    is_valid, errors = validate_product_data(data)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
    
    try:
        product_id = product_manager.add_product(data)
        return jsonify({
            'success': True,
            'message': 'Product added successfully',
            'product_id': product_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def api_update_product(product_id):
    """Update product API"""
    data = request.get_json()
    
    try:
        success = product_manager.update_product(product_id, data)
        if success:
            return jsonify({
                'success': True,
                'message': 'Product updated successfully'
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def api_delete_product(product_id):
    """Delete product API"""
    try:
        success = product_manager.delete_product(product_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Product deleted successfully'
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Get database statistics"""
    try:
        stats = product_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)