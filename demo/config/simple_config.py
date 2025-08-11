"""
Simple configuration file for Product Retrieval System
Cấu hình đơn giản và dễ sử dụng
"""

# API settings
API_SETTINGS = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'cors_enabled': True,
    'max_page_size': 100,
    'default_page_size': 20
}

# ============================================================================
# BASIC SETTINGS
# ============================================================================

# Model names
EMBEDDING_MODEL_NAME = 'BAAI/bge-large-en-v1.5'
# EMBEDDING_MODEL_NAME = 'BAAI/bge-base-en-v1.5'

CROSS_ENCODER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
# CROSS_ENCODER_MODEL_NAME = 'BAAI/bge-reranker-base'


# File paths (absolute paths)
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATHS = {
    'raw_data': os.path.join(PROJECT_ROOT, 'data', 'ingredients v1.csv'),
    'ground_truth': os.path.join(PROJECT_ROOT, 'data', 'gt.csv'), 
    'metadata': os.path.join(PROJECT_ROOT, 'data', 'product_metadata.csv'),
    'embeddings': os.path.join(PROJECT_ROOT, 'data', 'embeddings_attention.npy'),
    'faiss_index': os.path.join(PROJECT_ROOT, 'data', 'faiss_index.index'),
    'evaluation_results': os.path.join(PROJECT_ROOT, 'data', 'evaluation_results.json')
}

# Processing settings
DATASET_LIMIT = 500
BATCH_SIZE = 32
MAX_LENGTH = 512

# Search settings
DEFAULT_TOP_K = 3
RETRIEVAL_K = 20  # For hybrid search first stage
MAX_TOP_K = 10

# Evaluation targets
TARGETS = {
    'hit_at_3_percent': 95.0,      # ≥ 95%
    'mrr_percent': 50.0,           # ≥ 50% 
    'precision_at_3_percent': 80.0, # ≥ 80%
    'response_time_ms': 200.0       # ≤ 200ms
}

# Interface settings
EXIT_COMMANDS = ['quit', 'exit', 'q', 'stop']
DEFAULT_SEARCH_METHOD = 'hybrid'  # 'bi_encoder' or 'hybrid'

# Database management settings
DB_MANAGEMENT = {
    'required_fields': ['name', 'brand', 'ingredients'],
    'optional_fields': ['categories', 'manufacturer', 'manufacturerNumber'],
    'max_text_length': 2000,
    'backup_before_update': True,
    'auto_save': True
}

# Database management settings
DB_MANAGEMENT = {
    'required_fields': ['name', 'brand', 'ingredients'],
    'optional_fields': ['categories', 'manufacturer', 'manufacturerNumber'],
    'max_text_length': 2000,
    'backup_before_update': True,
    'auto_save': True
}

# ============================================================================
# GLOBAL MODEL INSTANCES
# ============================================================================

# Global model instances - chỉ load 1 lần duy nhất
_global_embedding_model = None
_global_tokenizer = None
_global_cross_encoder = None

def get_global_embedding_model():
    """Get global embedding model instance - chỉ load 1 lần duy nhất"""
    global _global_embedding_model, _global_tokenizer
    
    if _global_embedding_model is None:
        print(f"🔄 Loading embedding model for the first time: {EMBEDDING_MODEL_NAME}")
        
        try:
            from sentence_transformers import SentenceTransformer
            from transformers import AutoTokenizer
            
            # Monitor GPU memory before loading (if available)
            monitor_gpu_memory("Before loading embedding model")
            
            _global_embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            _global_tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
            
            # Move to appropriate device
            device = get_device()
            _global_embedding_model = _global_embedding_model.to(device)
            
            print(f"✅ Embedding model loaded once on {device}")
            monitor_gpu_memory("After loading embedding model")
            
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            raise
    else:
        print("♻️ Reusing existing embedding model instance")
    
    return _global_embedding_model, _global_tokenizer

def get_global_cross_encoder():
    """Get global cross encoder instance - chỉ load 1 lần duy nhất"""
    global _global_cross_encoder
    
    if _global_cross_encoder is None:
        print(f"🔄 Loading cross encoder for the first time: {CROSS_ENCODER_MODEL_NAME}")
        
        try:
            from sentence_transformers import CrossEncoder
            
            # Monitor GPU memory before loading (if available)
            monitor_gpu_memory("Before loading cross encoder")
            
            _global_cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)
            
            device = get_device()
            if hasattr(_global_cross_encoder, 'to'):
                _global_cross_encoder = _global_cross_encoder.to(device)
            
            print(f"✅ Cross encoder loaded once on {device}")
            monitor_gpu_memory("After loading cross encoder")
            
        except Exception as e:
            print(f"❌ Error loading cross encoder: {e}")
            raise
    else:
        print("♻️ Reusing existing cross encoder instance")
    
    return _global_cross_encoder

def monitor_gpu_memory(context=""):
    """Monitor GPU memory usage"""
    try:
        import torch
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            memory_reserved = torch.cuda.memory_reserved() / 1024**3    # GB
            print(f"🖥️ GPU Memory {context}: {memory_allocated:.2f}GB allocated, {memory_reserved:.2f}GB reserved")
            return memory_allocated, memory_reserved
    except:
        pass
    return 0, 0

def clear_gpu_cache():
    """Clear GPU cache to free memory"""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("🧹 GPU cache cleared")
    except:
        pass

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_device():
    """Get the appropriate device for model inference"""
    try:
        import torch
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    except ImportError:
        return 'cpu'

def print_config():
    """Print current configuration"""
    print("🔧 Product Retrieval System Configuration")
    print("=" * 50)
    print(f"Embedding Model: {EMBEDDING_MODEL_NAME}")
    print(f"Cross-Encoder: {CROSS_ENCODER_MODEL_NAME}")
    print(f"Device: {get_device()}")
    print(f"Dataset Limit: {DATASET_LIMIT}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Max Length: {MAX_LENGTH}")
    print(f"Default Top-K: {DEFAULT_TOP_K}")
    print(f"Default Method: {DEFAULT_SEARCH_METHOD}")
    
    print(f"\n🎯 Performance Targets:")
    for metric, target in TARGETS.items():
        if 'percent' in metric:
            print(f"   • {metric.replace('_percent', '')}: ≥ {target}%")
        else:
            print(f"   • {metric}: ≤ {target}ms")
    print("=" * 50)

if __name__ == "__main__":
    print_config()
