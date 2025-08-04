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
CROSS_ENCODER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

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
