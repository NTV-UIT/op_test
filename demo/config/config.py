"""
Configuration file for Product Retrieval System
Chứa tất cả các cấu hình chung cho hệ thống truy vấn sản phẩm
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base project directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
NOTEBOOK_DIR = PROJECT_ROOT / "notebook"
CONFIG_DIR = PROJECT_ROOT / "config"

# Data files
RAW_DATA_FILE = DATA_DIR / "ingredients v1.csv"
GROUND_TRUTH_FILE = DATA_DIR / "gt.csv"
METADATA_FILE = DATA_DIR / "product_metadata.csv"
EMBEDDINGS_FILE = DATA_DIR / "embeddings_attention.npy"
FAISS_INDEX_FILE = DATA_DIR / "faiss_index.index"
EVALUATION_RESULTS_FILE = DATA_DIR / "evaluation_results.json"

# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

# Embedding model settings
EMBEDDING_MODEL = {
    'name': 'BAAI/bge-large-en-v1.5',
    'max_length': 512,
    'batch_size': 32,
    'normalize_embeddings': True,
    'device': 'cuda' if os.getenv('CUDA_VISIBLE_DEVICES') else 'auto'
}

# Cross-encoder model for re-ranking
CROSS_ENCODER_MODEL = {
    'name': 'cross-encoder/ms-marco-MiniLM-L-6-v2',
    'max_length': 512
}

# Alternative models (for experimentation)
ALTERNATIVE_MODELS = {
    'embedding': [
        'sentence-transformers/all-MiniLM-L6-v2',
        'intfloat/e5-large-v2',
        'BAAI/bge-base-en-v1.5'
    ],
    'cross_encoder': [
        'cross-encoder/ms-marco-TinyBERT-L-2-v2',
        'cross-encoder/ms-marco-MiniLM-L-4-v2'
    ]
}

# ============================================================================
# DATA PROCESSING CONFIGURATIONS
# ============================================================================

# Data preprocessing settings
DATA_CONFIG = {
    'dataset_limit': 500,  # Limit number of products to process
    'columns_to_drop': [
        "Unnamed: 15", "asins", "sizes", "weight", 
        "ean", "upc", "dateAdded", "dateUpdated"
    ],
    'required_feature_key': 'Ingredients',
    'text_fields': ['categories', 'ingredients', 'manufacturer', 'manufacturerNumber'],
    'clean_null_values': ['nan', 'None', None]
}

# Text corpus template
TEXT_CORPUS_TEMPLATE = (
    "This product is a {name} from the brand {brand}. "
    "It falls under the category of {categories} and contains ingredients such as {ingredients}. "
    "It is manufactured by {manufacturer} (manufacturer code: {manufacturerNumber})."
)

# ============================================================================
# SEARCH CONFIGURATIONS
# ============================================================================

# Search parameters
SEARCH_CONFIG = {
    'default_top_k': 3,
    'max_top_k': 10,
    'retrieval_k': 20,  # For hybrid search first stage
    'similarity_metric': 'cosine',  # cosine, euclidean, dot_product
    'index_type': 'IndexIDMap',  # Support for dynamic updates
}

# FAISS index settings
FAISS_CONFIG = {
    'index_type': 'IndexFlatIP',  # Inner Product for cosine similarity
    'use_gpu': False,  # Set to True if GPU available and beneficial
    'nprobe': 1,  # For IVF indices
    'metric': 'METRIC_INNER_PRODUCT'  # Will be converted to faiss constant when needed
}

# ============================================================================
# EVALUATION CONFIGURATIONS
# ============================================================================

# Evaluation metrics and targets
EVALUATION_CONFIG = {
    'metrics': ['hit_at_k', 'mrr', 'precision_at_k'],
    'k_values': [1, 3, 5, 10],
    'primary_k': 3,  # Main k value for reporting
    'targets': {
        'hit_at_3': 95.0,  # Target: ≥ 95%
        'mrr': 50.0,       # Target: ≥ 50%
        'precision_at_3': 80.0,  # Target: ≥ 80%
        'response_time_ms': 200.0  # Target: ≤ 200ms
    },
    'weights': {  # For computing overall score
        'hit_at_3': 0.4,
        'mrr': 0.3,
        'precision_at_3': 0.3
    }
}

# ============================================================================
# SYSTEM CONFIGURATIONS
# ============================================================================

# Performance settings
PERFORMANCE_CONFIG = {
    'max_query_length': 1000,
    'timeout_seconds': 30,
    'memory_limit_gb': 8,
    'parallel_workers': 4
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': PROJECT_ROOT / 'logs' / 'retrieval_system.log',
    'max_file_size': '10MB',
    'backup_count': 5
}

# ============================================================================
# UI/INTERFACE CONFIGURATIONS
# ============================================================================

# Interactive search interface
INTERFACE_CONFIG = {
    'max_results_display': 10,
    'show_scores': True,
    'show_timing': True,
    'show_method': True,
    'default_method': 'hybrid',  # 'bi_encoder' or 'hybrid'
    'exit_commands': ['quit', 'exit', 'q', 'stop'],
    'result_format': 'detailed'  # 'simple' or 'detailed'
}

# ============================================================================
# ADVANCED CONFIGURATIONS
# ============================================================================

# Attention pooling for long texts
ATTENTION_CONFIG = {
    'use_attention_pooling': True,
    'chunk_overlap': 20,
    'attention_hidden_dim': 128,
    'attention_dropout': 0.1
}

# Caching settings
CACHE_CONFIG = {
    'enable_query_cache': True,
    'cache_size': 1000,
    'cache_ttl_seconds': 3600,  # 1 hour
    'embedding_cache': True
}

# Experimental features
EXPERIMENTAL_CONFIG = {
    'use_query_expansion': False,
    'use_pseudo_relevance_feedback': False,
    'use_learned_sparse_retrieval': False,
    'ensemble_methods': False
}

# ============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# ============================================================================

def get_config_for_environment(env='development'):
    """
    Get configuration based on environment
    Args:
        env: 'development', 'production', 'testing'
    """
    if env == 'production':
        # Production optimizations
        EMBEDDING_MODEL['batch_size'] = 64
        SEARCH_CONFIG['default_top_k'] = 5
        LOGGING_CONFIG['level'] = 'WARNING'
        CACHE_CONFIG['cache_size'] = 5000
        
    elif env == 'testing':
        # Testing configurations
        DATA_CONFIG['dataset_limit'] = 50
        EMBEDDING_MODEL['batch_size'] = 8
        SEARCH_CONFIG['retrieval_k'] = 10
        LOGGING_CONFIG['level'] = 'DEBUG'
        
    elif env == 'development':
        # Development settings (default)
        LOGGING_CONFIG['level'] = 'INFO'
    
    return {
        'paths': {
            'project_root': PROJECT_ROOT,
            'data_dir': DATA_DIR,
            'src_dir': SRC_DIR,
            'raw_data': RAW_DATA_FILE,
            'ground_truth': GROUND_TRUTH_FILE,
            'metadata': METADATA_FILE,
            'embeddings': EMBEDDINGS_FILE,
            'faiss_index': FAISS_INDEX_FILE,
            'evaluation_results': EVALUATION_RESULTS_FILE
        },
        'models': {
            'embedding': EMBEDDING_MODEL,
            'cross_encoder': CROSS_ENCODER_MODEL,
            'alternatives': ALTERNATIVE_MODELS
        },
        'data': DATA_CONFIG,
        'search': SEARCH_CONFIG,
        'faiss': FAISS_CONFIG,
        'evaluation': EVALUATION_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'logging': LOGGING_CONFIG,
        'interface': INTERFACE_CONFIG,
        'attention': ATTENTION_CONFIG,
        'cache': CACHE_CONFIG,
        'experimental': EXPERIMENTAL_CONFIG,
        'environment': env
    }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [DATA_DIR, SRC_DIR, NOTEBOOK_DIR, CONFIG_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create logs directory
    (PROJECT_ROOT / 'logs').mkdir(exist_ok=True)

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check if required files exist for production
    if not RAW_DATA_FILE.exists():
        errors.append(f"Raw data file not found: {RAW_DATA_FILE}")
    
    # Validate model names
    if not EMBEDDING_MODEL['name']:
        errors.append("Embedding model name cannot be empty")
    
    # Validate targets
    for metric, target in EVALUATION_CONFIG['targets'].items():
        if not isinstance(target, (int, float)) or target < 0:
            errors.append(f"Invalid target for {metric}: {target}")
    
    return errors

def get_device():
    """Get the appropriate device for model inference"""
    import torch
    
    if EMBEDDING_MODEL['device'] == 'auto':
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        return EMBEDDING_MODEL['device']

# ============================================================================
# DEFAULT CONFIGURATION
# ============================================================================

# Export default configuration
DEFAULT_CONFIG = get_config_for_environment('development')

# Create directories on import
create_directories()

if __name__ == "__main__":
    # Configuration validation and testing
    print("🔧 Product Retrieval System Configuration")
    print("=" * 50)
    
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Embedding Model: {EMBEDDING_MODEL['name']}")
    print(f"Cross-Encoder: {CROSS_ENCODER_MODEL['name']}")
    print(f"Device: {get_device()}")
    
    # Validate configuration
    errors = validate_config()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("\n✅ Configuration is valid")
    
    # Show targets
    print(f"\n🎯 Performance Targets:")
    for metric, target in EVALUATION_CONFIG['targets'].items():
        unit = "%" if metric != 'response_time_ms' else "ms"
        operator = "≤" if metric == 'response_time_ms' else "≥"
        print(f"   • {metric}: {operator} {target}{unit}")
