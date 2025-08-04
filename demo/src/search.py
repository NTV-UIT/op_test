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
    EXIT_COMMANDS, BATCH_SIZE, get_device
)

# Global variables
DEVICE = get_device()

# Load models and data
print("🔄 Loading models and data...")
model, tokenizer = load_embedding_model()
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)

# Load index and metadata
try:
    index = faiss.read_index(DATA_PATHS['faiss_index'])
    metadata_df = pd.read_csv(DATA_PATHS['metadata'])
    print(f"✅ Loaded index with {index.ntotal} vectors")
    print(f"✅ Loaded metadata for {len(metadata_df)} products")
except FileNotFoundError:
    print("❌ Index or metadata file not found. Please run embedding.py first.")
    index = None
    metadata_df = None

# Current database variables (for dynamic updates)
current_index = index
current_metadata_df = metadata_df

def bi_encoder_search(query, top_k=None, use_current_db=False):
    """Basic bi-encoder search"""
    if top_k is None:
        top_k = DEFAULT_TOP_K
        
    if index is None or metadata_df is None:
        return []
        
    time_start = time.time()
    
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        device=DEVICE
    )
    
    # Use current database if specified
    search_index = current_index if use_current_db else index
    search_metadata = current_metadata_df if use_current_db else metadata_df
    
    distances, indices = search_index.search(query_embedding, top_k)
    time_end = time.time()
    response_time = (time_end - time_start) * 1000
    
    results = []
    for idx, score in zip(indices[0], distances[0]):
        # Handle IndexIDMap (indices are actual IDs) vs regular index
        if use_current_db:
            # Using IndexIDMap - indices are product IDs
            product_row = search_metadata[search_metadata['id'] == idx]
            if not product_row.empty:
                row = product_row.iloc[0]
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'brand': row['brand'],
                    'score': float(score),
                    'text': row['text_corpus'],
                    'time': response_time,
                    'method': 'bi_encoder'
                })
        else:
            # Regular index - indices are array positions
            if idx < len(search_metadata):
                row = search_metadata.iloc[idx]
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'brand': row['brand'],
                    'score': float(score),
                    'text': row['text_corpus'],
                    'time': response_time,
                    'method': 'bi_encoder'
                })
    
    return results

def hybrid_search(query, top_k=None, retrieval_k=None, use_current_db=False):
    """Hybrid search với Bi-Encoder + Cross-Encoder"""
    if top_k is None:
        top_k = DEFAULT_TOP_K
    if retrieval_k is None:
        retrieval_k = RETRIEVAL_K
        
    time_start = time.time()
    
    # Step 1: Bi-Encoder retrieval
    bi_results = bi_encoder_search(query, top_k=retrieval_k, use_current_db=use_current_db)
    retrieval_time = time.time()
    
    # Step 2: Prepare for Cross-Encoder
    query_doc_pairs = []
    candidate_docs = []
    
    for result in bi_results:
        query_doc_pairs.append([query, result['text']])
        candidate_docs.append(result)
    
    # Step 3: Cross-Encoder re-ranking
    if len(query_doc_pairs) > 0:
        cross_scores = cross_encoder.predict(query_doc_pairs)
        
        for i, doc in enumerate(candidate_docs):
            doc['cross_encoder_score'] = float(cross_scores[i])
            doc['bi_encoder_score'] = doc['score']
        
        candidate_docs.sort(key=lambda x: x['cross_encoder_score'], reverse=True)
    
    reranking_time = time.time()
    total_time = (reranking_time - time_start) * 1000
    
    # Return top-k results
    final_results = candidate_docs[:top_k]
    for result in final_results:
        result['time'] = total_time
        result['method'] = 'hybrid'
        result['retrieval_time_ms'] = (retrieval_time - time_start) * 1000
        result['reranking_time_ms'] = (reranking_time - retrieval_time) * 1000
    
    return final_results


# Enhanced search function for current database
def search_current_database(query, method=None, top_k=None):
    """Search trong database hiện tại với các thay đổi"""
    if method is None:
        method = DEFAULT_SEARCH_METHOD
    if top_k is None:
        top_k = DEFAULT_TOP_K
        
    if method == 'hybrid':
        return hybrid_search(query, top_k=top_k, use_current_db=True)
    else:
        return bi_encoder_search(query, top_k=top_k, use_current_db=True)

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
    if index is None or metadata_df is None:
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
        
        # Load index và metadata
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
        start_time = time.time()
        scores, indices = self.index.search(query_embedding, top_k)
        response_time = (time.time() - start_time) * 1000
        
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
                        results.append({
                            'id': row['id'],
                            'name': row['name'],
                            'brand': row['brand'],
                            'ingredients': row.get('ingredients', ''),
                            'categories': row.get('categories', ''),
                            'manufacturer': row.get('manufacturer', ''),
                            'manufacturerNumber': row.get('manufacturerNumber', ''),
                            'text_corpus': row['text_corpus']
                        })
                        result_scores.append(float(score))
                else:
                    # Regular index - idx là array position
                    if idx < len(self.metadata_df):
                        row = self.metadata_df.iloc[idx]
                        results.append({
                            'id': row['id'],
                            'name': row['name'],
                            'brand': row['brand'],
                            'ingredients': row.get('ingredients', ''),
                            'categories': row.get('categories', ''),
                            'manufacturer': row.get('manufacturer', ''),
                            'manufacturerNumber': row.get('manufacturerNumber', ''),
                            'text_corpus': row['text_corpus']
                        })
                        result_scores.append(float(score))
        
        return results, result_scores
    
    def hybrid_search(self, query: str, top_k: int = 5, retrieval_k: int = 20) -> Tuple[List[Dict], List[float]]:
        """Hybrid search với bi-encoder + cross-encoder"""
        if self.index is None or self.metadata_df is None:
            return [], []
        
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
        
        # Lấy top-k kết quả
        final_results = []
        final_scores = []
        
        for result, score in combined_results[:top_k]:
            final_results.append(result)
            final_scores.append(float(score))
        
        return final_results, final_scores


if __name__ == "__main__":
    # Check if running in interactive mode or test mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode with predefined queries
        if index is not None and metadata_df is not None:
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


