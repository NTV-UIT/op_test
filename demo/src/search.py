import os
import sys
import pandas as pd
import numpy as np
import faiss
import torch
import time
from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import AutoTokenizer
import ast
import json
from typing import List, Dict, Tuple
import re
import torch.nn as nn
from embedding import load_embedding_model

# Add config path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_config import (
    EMBEDDING_MODEL_NAME, CROSS_ENCODER_MODEL_NAME, DATA_PATHS, 
    DEFAULT_TOP_K, RETRIEVAL_K, MAX_TOP_K, DEFAULT_SEARCH_METHOD,
    EXIT_COMMANDS, BATCH_SIZE, get_device, get_global_embedding_model, 
    get_global_cross_encoder, monitor_gpu_memory
)

# Global variables
DEVICE = get_device()

# Functions for backward compatibility

# Backward compatibility functions - delegate to global searcher instance
_global_searcher = None

def get_global_searcher():
    """Get global searcher instance"""
    global _global_searcher
    if _global_searcher is None:
        _global_searcher = ProductSearcher()
    return _global_searcher

def bi_encoder_search(query, top_k=None, use_current_db=False):
    """Backward compatibility function"""
    searcher = get_global_searcher()
    if top_k is None:
        top_k = DEFAULT_TOP_K
    
    # Class ProductSearcher hiện tại chỉ có 2 tham số cho bi_encoder_search
    results, scores = searcher.bi_encoder_search(query, top_k)
    
    # Chuyển đổi format để tương thích với evaluation
    formatted_results = []
    response_time = results[0]['time'] if results else 0  # Lấy thời gian từ kết quả đầu tiên
    
    for i, (result, score) in enumerate(zip(results, scores)):
        formatted_result = result.copy()
        formatted_result['score'] = score
        formatted_result['rank'] = i + 1
        formatted_result['time'] = response_time  # Sử dụng thời gian thực
        formatted_results.append(formatted_result)
    
    return formatted_results

def hybrid_search(query, top_k=None, retrieval_k=None, use_current_db=False):
    """Backward compatibility function"""
    searcher = get_global_searcher()
    if top_k is None:
        top_k = DEFAULT_TOP_K
    if retrieval_k is None:
        retrieval_k = RETRIEVAL_K
    
    # Class ProductSearcher hiện tại chỉ có 2 tham số cho hybrid_search
    results, scores = searcher.hybrid_search(query, top_k, retrieval_k)
    
    # Chuyển đổi format để tương thích với evaluation
    formatted_results = []
    response_time = results[0]['time'] if results else 0  # Lấy thời gian từ kết quả đầu tiên
    
    for i, (result, score) in enumerate(zip(results, scores)):
        formatted_result = result.copy()
        formatted_result['score'] = score
        formatted_result['rank'] = i + 1
        formatted_result['time'] = response_time  # Sử dụng thời gian thực
        formatted_results.append(formatted_result)
    
    return formatted_results

def search_current_database(query, method=None, top_k=None):
    """Backward compatibility function"""
    searcher = get_global_searcher()
    return searcher.search_current_database(query, method, top_k)

def display_search_results(results, query):
    """Display search results in a formatted way"""
    print(f"\n🔍 Search Results for: '{query}'")
    print("="*60)
    
    if not results:
        print("❌ No results found")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']} - {result['brand']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Method: {result['method']}")
        print(f"   Time: {result['time']:.1f}ms")
        if 'cross_encoder_score' in result:
            print(f"   Cross-Encoder Score: {result['cross_encoder_score']:.4f}")

def interactive_search():
    """Interactive search interface"""
    searcher = get_global_searcher()
    if searcher.index is None or searcher.metadata_df is None:
        print("❌ Cannot run search - models or data not loaded")
        print("Please run embedding.py first to create the index and metadata")
        return
    
    print("\n🔍 INTERACTIVE PRODUCT SEARCH")
    print("="*50)
    print("Available methods:")
    print("1. Bi-Encoder (fast)")
    print("2. Hybrid (bi-encoder + cross-encoder, more accurate)")
    print("\nType 'quit' or 'exit' to stop")
    print("="*50)
    
    while True:
        try:
            # Get user input
            query = input("\n🔎 Enter your search query: ").strip()
            
            # Check for exit commands
            if query.lower() in EXIT_COMMANDS:
                print("👋 Goodbye!")
                break
            
            if not query:
                print("❌ Please enter a valid query")
                continue
            
            # Ask for search method
            method_input = input(f"Choose method (1=bi-encoder, 2=hybrid) [default: {DEFAULT_SEARCH_METHOD}]: ").strip()
            
            if method_input == '1':
                method = 'bi_encoder'
                search_func = bi_encoder_search
            else:
                method = 'hybrid'
                search_func = hybrid_search
            
            # Get number of results
            try:
                top_k_input = input(f"Number of results [default: {DEFAULT_TOP_K}]: ").strip()
                top_k = int(top_k_input) if top_k_input else DEFAULT_TOP_K
                top_k = max(1, min(top_k, MAX_TOP_K))  # Limit between 1-MAX_TOP_K
            except ValueError:
                top_k = DEFAULT_TOP_K
            
            print(f"\n🔄 Searching for '{query}' using {method.replace('_', '-')} method...")
            
            # Perform search
            start_time = time.time()
            results = search_func(query, top_k=top_k)
            search_time = (time.time() - start_time) * 1000
            
            # Display results
            if results:
                print(f"\n✅ Found {len(results)} results in {search_time:.1f}ms")
                display_search_results(results, query)
                
                # Show detailed info option
                detail_input = input("\n📋 Show detailed product info? (y/n) [default: n]: ").strip().lower()
                if detail_input == 'y':
                    for i, result in enumerate(results, 1):
                        print(f"\n📦 Product {i} Details:")
                        print(f"   ID: {result['id']}")
                        print(f"   Name: {result['name']}")
                        print(f"   Brand: {result['brand']}")
                        print(f"   Score: {result['score']:.4f}")
                        if 'cross_encoder_score' in result:
                            print(f"   Cross-Encoder Score: {result['cross_encoder_score']:.4f}")
                        print(f"   Text: {result['text'][:200]}...")
            else:
                print("❌ No results found")
                print("💡 Try different keywords or check spelling")
                
        except KeyboardInterrupt:
            print("\n\n👋 Search interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")


class ProductSearcher:
    """Class để encapsulate search functionality cho các module khác"""
    
    def __init__(self):
        """Khởi tạo ProductSearcher"""
        self.model, self.tokenizer = load_embedding_model()
        self.cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)
        self._load_data()
    
    def _load_data(self):
        """Load/reload index và metadata"""
        try:
            self.index = faiss.read_index(DATA_PATHS['faiss_index'])
            self.metadata_df = pd.read_csv(DATA_PATHS['metadata'])
            print(f"✅ ProductSearcher loaded: {self.index.ntotal} vectors, {len(self.metadata_df)} products")
        except FileNotFoundError as e:
            print(f"❌ Error loading search data: {e}")
            self.index = None
            self.metadata_df = None
    
    def bi_encoder_search(self, query: str, top_k: int = 5) -> Tuple[List[Dict], List[float]]:
        """Bi-encoder search"""
        if self.index is None or self.metadata_df is None:
            return [], []
        
        start_time = time.time()
        
        # Tạo embedding cho query
        query_embedding = self.model.encode(
            query, 
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,
            device=DEVICE,
            convert_to_tensor=True
        ).cpu().numpy().reshape(1, -1)
        
        # Search trong FAISS index
        scores, indices = self.index.search(query_embedding, top_k)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        results = []
        result_scores = []
        
        for score, idx in zip(scores[0], indices[0]):
            if score > 0:  # Có kết quả
                # Kiểm tra xem index có phải IndexIDMap không
                if hasattr(self.index, 'index_to_id'):
                    # IndexIDMap - idx là ID thực
                    row = self.metadata_df[self.metadata_df['id'] == idx]
                    if not row.empty:
                        row = row.iloc[0]
                        result = {
                            'id': row['id'],
                            'name': row['name'],
                            'brand': row['brand'],
                            'ingredients': row.get('ingredients', ''),
                            'categories': row.get('categories', ''),
                            'manufacturer': row.get('manufacturer', ''),
                            'manufacturerNumber': row.get('manufacturerNumber', ''),
                            'text_corpus': row['text_corpus'],
                            'time': response_time  # Thêm thời gian
                        }
                        results.append(result)
                        result_scores.append(float(score))
                else:
                    # Regular index - idx là array position
                    if idx < len(self.metadata_df):
                        row = self.metadata_df.iloc[idx]
                        result = {
                            'id': row['id'],
                            'name': row['name'],
                            'brand': row['brand'],
                            'ingredients': row.get('ingredients', ''),
                            'categories': row.get('categories', ''),
                            'manufacturer': row.get('manufacturer', ''),
                            'manufacturerNumber': row.get('manufacturerNumber', ''),
                            'text_corpus': row['text_corpus'],
                            'time': response_time  # Thêm thời gian
                        }
                        results.append(result)
                        result_scores.append(float(score))
        
        return results, result_scores
    
    def hybrid_search(self, query: str, top_k: int = 5, retrieval_k: int = 20) -> Tuple[List[Dict], List[float]]:
        """Hybrid search với bi-encoder + cross-encoder"""
        if self.index is None or self.metadata_df is None:
            return [], []
        
        start_time = time.time()
        
        # Stage 1: Bi-encoder retrieval với số lượng lớn hơn
        bi_results, bi_scores = self.bi_encoder_search(query, retrieval_k)
        
        if not bi_results:
            return [], []
        
        # Stage 2: Cross-encoder re-ranking
        pairs = [(query, result['text_corpus']) for result in bi_results]
        cross_scores = self.cross_encoder.predict(pairs)
        
        # Kết hợp scores và sắp xếp
        combined_results = list(zip(bi_results, cross_scores))
        combined_results.sort(key=lambda x: x[1], reverse=True)
        
        # Tính tổng thời gian
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Lấy top-k kết quả
        final_results = []
        final_scores = []
        
        for result, score in combined_results[:top_k]:
            # Cập nhật thời gian cho từng kết quả
            result['time'] = total_time
            final_results.append(result)
            final_scores.append(float(score))
        
        return final_results, final_scores


if __name__ == "__main__":
    # Check if running in interactive mode or test mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode with predefined queries
        searcher = get_global_searcher()
        if searcher.index is not None and searcher.metadata_df is not None:
            test_queries = [
                "organic chocolate",
                "protein powder", 
                "gluten free bread"
            ]
            
            print("🧪 Testing search functionality...")
            
            for query in test_queries:
                print(f"\nTesting query: '{query}'")
                
                # Test bi-encoder
                bi_results = bi_encoder_search(query, top_k=3)
                print(f"Bi-encoder found {len(bi_results)} results")
                
                # Test hybrid
                hybrid_results = hybrid_search(query, top_k=3)
                print(f"Hybrid found {len(hybrid_results)} results")
                
                # Display results
                display_search_results(hybrid_results, query)
            
            print("\n✅ Search functionality test completed!")
        else:
            print("❌ Cannot test search - models or data not loaded")
    else:
        # Interactive mode
        interactive_search()


