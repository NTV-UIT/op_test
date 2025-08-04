import os
import sys
import pandas as pd
import numpy as np
import re

# Add config path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_config import DATA_PATHS, DATASET_LIMIT

def load_and_process_data(data_file=None, limit=None):
    """Load và xử lý dữ liệu sản phẩm"""
    
    # Use config defaults if not specified
    if data_file is None:
        data_file = DATA_PATHS['raw_data']
    if limit is None:
        limit = DATASET_LIMIT
    
    # Load data
    df = pd.read_csv(data_file)
    
    # Remove unnecessary columns
    columns_to_drop = ["Unnamed: 15", "asins", "sizes", "weight", "ean", "upc", "dateAdded", "dateUpdated"]
    df = df.drop([col for col in columns_to_drop if col in df.columns], axis=1)
    
    # Clean data
    df.dropna(inplace=True)
    df = df[df['features.key'] == 'Ingredients']
    df.rename(columns={'features.value': 'ingredients'}, inplace=True)
    df.drop(columns=['features.key'], inplace=True)
    
    # Normalize text
    df['name'] = df['name'].str.strip().str.title()
    df['ingredients'] = df['ingredients'].str.lower()
    
    # Limit dataset size
    df = df.head(limit).reset_index(drop=True)
    df['id'] = range(len(df))
    
    return df

def clean_text(text):
    """Clean text data"""
    if pd.isnull(text) or text in ['nan', 'None']:
        return ''
    text = re.sub(r'[\xa0\n\r\t]+', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def preprocess_data(data_file=None, limit=None):
    """Tiền xử lý dữ liệu và tạo text corpus"""
    df = load_and_process_data(data_file, limit)
    
    # Clean text fields
    for col in ['categories', 'ingredients', 'manufacturer', 'manufacturerNumber']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: clean_text(x))
    
    df['brand'] = df['brand'].apply(lambda x: '' if pd.isnull(x) else str(x).strip())
    df['name'] = df['name'].apply(lambda x: '' if pd.isnull(x) else str(x).strip())
    
    # Create comprehensive text corpus
    df['text_corpus'] = (
        "This product is a " + df['name'] + " from the brand " + df['brand'] + ". "
        "It falls under the category of " + df['categories'].str.lower() + " and contains ingredients such as " + df['ingredients'].str.lower() + ". "
        "It is manufactured by " + df['manufacturer'].str.lower() + " (manufacturer code: " + df['manufacturerNumber'].str.lower() + ")."
    )
    
    return df

def create_text_corpus(data_file=None, limit=None):
    """Wrapper function để tạo text corpus - sử dụng cho embedding.py"""
    return preprocess_data(data_file, limit)


def create_text_corpus_for_product(name, brand, ingredients, categories='', manufacturer='', manufacturerNumber=''):
    """
    Tạo text corpus cho một sản phẩm đơn lẻ
    Sử dụng cùng logic với preprocess_data để đảm bảo nhất quán
    """
    # Clean và chuẩn hóa input
    name = clean_text(name) if name else ''
    brand = clean_text(brand) if brand else ''
    ingredients = clean_text(ingredients) if ingredients else ''
    categories = clean_text(categories) if categories else ''
    manufacturer = clean_text(manufacturer) if manufacturer else ''
    manufacturerNumber = clean_text(manufacturerNumber) if manufacturerNumber else ''
    
    # Tạo text corpus theo cùng format với preprocess_data
    text_corpus = (
        f"This product is a {name} from the brand {brand}. "
        f"It falls under the category of {categories.lower()} and contains ingredients such as {ingredients.lower()}. "
        f"It is manufactured by {manufacturer.lower()} (manufacturer code: {manufacturerNumber.lower()})."
    )
    
    return text_corpus


if __name__ == "__main__":
    # Process data
    df = preprocess_data()
    
    print(f"✅ Processed {len(df)} products")
    print(f"✅ Sample text corpus: {df['text_corpus'].iloc[0][:100]}...")
    
    # Save processed data
    metadata_df = df.copy()
    metadata_df.to_csv(DATA_PATHS['metadata'], index=False)
    
    print(f"✅ Metadata saved to product_metadata.csv")