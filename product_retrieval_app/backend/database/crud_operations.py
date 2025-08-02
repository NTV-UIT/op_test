import pandas as pd
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer
import time

class ProductManager:
    def __init__(self, data_path='../data/'):
        self.data_path = data_path
        self.model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        self.load_data()
    
    def load_data(self):
        """Load current data"""
        self.metadata_path = os.path.join(self.data_path, 'product_metadata.csv')
        self.index_path = os.path.join(self.data_path, 'faiss_index.index')
        self.embeddings_path = os.path.join(self.data_path, 'embeddings.npy')
        
        # Load metadata
        if os.path.exists(self.metadata_path):
            self.metadata_df = pd.read_csv(self.metadata_path)
        else:
            self.metadata_df = pd.DataFrame(columns=['id', 'name', 'brand', 'text_corpus'])
        
        # Load FAISS index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            # Create empty index
            dimension = 1024  # BGE-large dimension
            base_index = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIDMap(base_index)
        
        # Load embeddings
        if os.path.exists(self.embeddings_path):
            self.embeddings = np.load(self.embeddings_path)
        else:
            self.embeddings = np.empty((0, 1024))
    
    def create_text_corpus(self, product_data):
        """Create text corpus for product"""
        name = product_data.get('name', '')
        brand = product_data.get('brand', '')
        categories = product_data.get('categories', '')
        ingredients = product_data.get('ingredients', '')
        manufacturer = product_data.get('manufacturer', '')
        manufacturer_number = product_data.get('manufacturerNumber', '')
        
        text_corpus = (
            f"This product is a {name} from the brand {brand}. "
            f"It falls under the category of {categories} and contains ingredients such as {ingredients}. "
            f"It is manufactured by {manufacturer} (manufacturer code: {manufacturer_number})."
        )
        
        return text_corpus
    
    def add_product(self, product_data):
        """Add new product"""
        try:
            # Create new ID
            new_id = len(self.metadata_df)
            
            # Create text corpus
            text_corpus = self.create_text_corpus(product_data)
            
            # Add to metadata
            new_row = {
                'id': new_id,
                'name': product_data.get('name', ''),
                'brand': product_data.get('brand', ''),
                'text_corpus': text_corpus
            }
            self.metadata_df = pd.concat([self.metadata_df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Generate embedding
            embedding = self.model.encode([text_corpus], normalize_embeddings=True)
            
            # Add to FAISS index
            self.index.add_with_ids(embedding.astype('float32'), np.array([new_id], dtype='int64'))
            
            # Update embeddings array
            self.embeddings = np.vstack([self.embeddings, embedding])
            
            # Save changes
            self.save_data()
            
            return new_id
            
        except Exception as e:
            raise Exception(f"Failed to add product: {str(e)}")
    
    def update_product(self, product_id, product_data):
        """Update existing product"""
        try:
            if product_id not in self.metadata_df['id'].values:
                return False
            
            # Create new text corpus
            text_corpus = self.create_text_corpus(product_data)
            
            # Update metadata
            mask = self.metadata_df['id'] == product_id
            self.metadata_df.loc[mask, 'name'] = product_data.get('name', '')
            self.metadata_df.loc[mask, 'brand'] = product_data.get('brand', '')
            self.metadata_df.loc[mask, 'text_corpus'] = text_corpus
            
            # Generate new embedding
            new_embedding = self.model.encode([text_corpus], normalize_embeddings=True)
            
            # Update FAISS index
            self.index.remove_ids(np.array([product_id], dtype='int64'))
            self.index.add_with_ids(new_embedding.astype('float32'), np.array([product_id], dtype='int64'))
            
            # Update embeddings array
            self.embeddings[product_id] = new_embedding[0]
            
            # Save changes
            self.save_data()
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to update product: {str(e)}")
    
    def delete_product(self, product_id):
        """Delete product"""
        try:
            if product_id not in self.metadata_df['id'].values:
                return False
            
            # Remove from FAISS index
            self.index.remove_ids(np.array([product_id], dtype='int64'))
            
            # Remove from metadata
            self.metadata_df = self.metadata_df[self.metadata_df['id'] != product_id].reset_index(drop=True)
            
            # Save changes
            self.save_data()
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to delete product: {str(e)}")
    
    def get_stats(self):
        """Get database statistics"""
        return {
            'total_products': len(self.metadata_df),
            'total_vectors': self.index.ntotal,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'top_brands': self.metadata_df['brand'].value_counts().head(5).to_dict()
        }
    
    def get_recent_products(self, limit=20):
        """Get recent products"""
        return self.metadata_df.tail(limit).to_dict('records')
    
    def save_data(self):
        """Save all data to files"""
        self.metadata_df.to_csv(self.metadata_path, index=False)
        np.save(self.embeddings_path, self.embeddings)
        faiss.write_index(self.index, self.index_path)