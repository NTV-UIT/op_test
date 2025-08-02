# Application settings

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Data paths
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = DATA_DIR / 'uploads'
LOGS_DIR = BASE_DIR / 'logs'

# Model settings
EMBEDDING_MODEL = 'BAAI/bge-large-en-v1.5'
CROSS_ENCODER_MODEL = 'BAAI/bge-reranker-base'
BATCH_SIZE = 32
MAX_SEQUENCE_LENGTH = 512

# Search settings
DEFAULT_TOP_K = 10
MAX_TOP_K = 100
DEFAULT_SEARCH_METHOD = 'hybrid'

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}

# Logging settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)