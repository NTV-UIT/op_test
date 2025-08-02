import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
import time
import os

class SearchEngine:
    def __init__(self, data_path='../data/'):
        self.data_path = data_path
        self.model = None
        self.cross_encoder = None
        self.index = None
        self.metadata_df = None
        self.load_components()
    
    def load_components(self):
        """Load all search components"""
        print("🔄 Loading search components...")
        
        # Load models
        self.model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        self.cross_encoder = CrossEncoder('BAAI/bge-reranker-base')
        
        # Load FAISS index
        index_path = os.path.join(self.data_path, 'faiss_index.index')
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            print(f"✅ Loaded FAISS index: {self.index.ntotal} vectors")
        
        # Load metadata
        metadata_path = os.path.join(self.data_path, 'product_metadata.csv')
        if os.path.exists(metadata_path):
            self.metadata_df = pd.read_csv(metadata_path)
            print(f"✅ Loaded metadata: {len(self.metadata_df)} products")
    
    def search(self, query, method='hybrid', top_k=10):
        """Main search function"""
        if method == 'hybrid':
            return self.hybrid_search(query, top_k)
        else:
            return self.bi_encoder_search(query, top_k)
    
    def bi_encoder_search(self, query, top_k=10):
        """Bi-encoder search"""
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.metadata_df):
                row = self.metadata_df.iloc[idx]
                results.append({
                    'id': int(row['id']),
                    'name': row['name'],
                    'brand': row['brand'],
                    'score': float(score),
                    'method': 'bi_encoder',
                    'response_time': (time.time() - start_time) * 1000
                })
        
        return results
    
    def hybrid_search(self, query, top_k=10, retrieval_k=50):
        """Hybrid search with re-ranking"""
        start_time = time.time()
        
        # Step 1: Bi-encoder retrieval
        bi_results = self.bi_encoder_search(query, retrieval_k)
        
        if not bi_results:
            return []
        
        # Step 2: Cross-encoder re-ranking
        query_doc_pairs = []
        for result in bi_results:
            # Use text corpus if available, otherwise name + brand
            text = result.get('text_corpus', f"{result['name']} {result['brand']}")
            query_doc_pairs.append([query, text])
        
        # Get cross-encoder scores
        cross_scores = self.cross_encoder.predict(query_doc_pairs)
        
        # Update results with cross-encoder scores
        for i, result in enumerate(bi_results):
            result['cross_encoder_score'] = float(cross_scores[i])
            result['method'] = 'hybrid'
            result['response_time'] = (time.time() - start_time) * 1000
        
        # Sort by cross-encoder score and return top-k
        bi_results.sort(key=lambda x: x['cross_encoder_score'], reverse=True)
        return bi_results[:top_k]