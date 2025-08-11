import os
import sys
import pandas as pd
import numpy as np
import faiss
import torch
import time
from sentence_transformers import SentenceTransformer, models
from transformers import AutoTokenizer
import ast
import json
from typing import List, Dict, Tuple
import re
import torch.nn as nn
from preprocess import create_text_corpus

# Add config path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_config import (
    EMBEDDING_MODEL_NAME, DATA_PATHS, BATCH_SIZE, MAX_LENGTH, get_device,
    get_global_embedding_model, monitor_gpu_memory
)


def load_embedding_model():
    """Load embedding model và tokenizer - sử dụng global instance"""
    print(f"🤖 Using global embedding model: {EMBEDDING_MODEL_NAME}")
    return get_global_embedding_model()


def split_text_into_chunks(text, tokenizer, max_length):
    """
    Chia text thành các chunks với độ dài tối đa max_length tokens
    """
    tokens = tokenizer.tokenize(text)
    chunks = []
    
    if len(tokens) <= max_length:
        return [text]  # Không cần chia nếu text đã ngắn
    
    for i in range(0, len(tokens), max_length - 20):  # Overlap 20 tokens để giữ context
        chunk = tokens[i:i+max_length]
        chunk_text = tokenizer.convert_tokens_to_string(chunk)
        chunks.append(chunk_text)
    
    return chunks

class AttentionPooling(nn.Module):
    """
    Attention pooling layer để kết hợp embeddings từ nhiều chunks
    """
    def __init__(self, embed_dim):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.Tanh(),
            nn.Linear(128, 1)
        )

    def forward(self, embeddings):
        # embeddings: [batch_size, num_chunks, embed_dim]
        scores = self.attention(embeddings)  # [batch_size, num_chunks, 1]
        weights = torch.softmax(scores, dim=1)  # [batch_size, num_chunks, 1]
        weighted = embeddings * weights  # [batch_size, num_chunks, embed_dim]
        pooled = weighted.sum(dim=1)  # [batch_size, embed_dim]
        return pooled

def embed_text_with_attention(text, model, tokenizer, max_length, device, batch_size=None):
    """
    Embed text với attention pooling cho text dài
    """
    if batch_size is None:
        batch_size = BATCH_SIZE
        
    # Chia chunk
    chunks = split_text_into_chunks(text, tokenizer, max_length)
    
    if len(chunks) == 1:
        # Text ngắn, embed bình thường với các tham số nhất quán
        return model.encode(
            text, 
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            max_length=max_length,
            device=device,
            convert_to_tensor=True
        )
    
    # Embed từng chunk
    chunk_embeddings = []
    for chunk in chunks:
        emb = model.encode(
            chunk, 
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            max_length=max_length,
            device=device,
            convert_to_tensor=True
        ).unsqueeze(0)  # [1, embed_dim]
        chunk_embeddings.append(emb)
    
    all_chunks = torch.cat(chunk_embeddings, dim=0).unsqueeze(0)  # [1, num_chunks, embed_dim]
    
    # Attention Pooling
    attn_pool = AttentionPooling(embed_dim=all_chunks.shape[-1]).to(device)
    pooled_embedding = attn_pool(all_chunks.to(device))  # [1, embed_dim]
    
    # Normalize final embedding
    pooled_embedding = torch.nn.functional.normalize(pooled_embedding, p=2, dim=1)
    
    return pooled_embedding.squeeze(0)


def create_embeddings_with_attention_pooling(model, tokenizer, max_length=None, batch_size=None):
    """
    Tạo embeddings với attention pooling cho các text vượt quá max_length
    """
    # Use config defaults if not specified
    if max_length is None:
        max_length = MAX_LENGTH
    if batch_size is None:
        batch_size = BATCH_SIZE
        
    # Sử dụng create_text_corpus để đảm bảo nhất quán với các module khác
    df = create_text_corpus()

    # Tokenize dữ liệu text_corpus để lấy độ dài
    df['token_length'] = df['text_corpus'].apply(lambda x: len(tokenizer.tokenize(x)))

    # Kiểm tra các thống kê
    print("Max token length:", df['token_length'].max())
    print("Min token length:", df['token_length'].min())
    print("Average token length:", df['token_length'].mean())

    # Optional: Kiểm tra số mẫu vượt quá giới hạn mặc định
    print(f"Số mẫu vượt quá {max_length} token:", (df['token_length'] > max_length).sum())

    device = get_device()
    print(f"🔄 Creating embeddings with attention pooling (device: {device})")
    
    # Phân tích độ dài text
    token_lengths = df['text_corpus'].apply(lambda x: len(tokenizer.tokenize(x)))
    long_texts = token_lengths > max_length
    
    print(f"📊 Text length analysis:")
    print(f"   • Total texts: {len(df)}")
    print(f"   • Long texts (>{max_length} tokens): {long_texts.sum()} ({long_texts.mean()*100:.1f}%)")
    print(f"   • Max token length: {token_lengths.max()}")
    print(f"   • Average token length: {token_lengths.mean():.1f}")
    
    embeddings_list = []
    
    # Xử lý từng text
    for idx, (_, row) in enumerate(df.iterrows()):
        text = row['text_corpus']
        text_length = token_lengths.iloc[idx]
        
        if text_length <= max_length:
            # Text ngắn - embed bình thường với các tham số giống embedding gốc
            embedding = model.encode(
                text,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
                max_length=max_length,
                device=device,
                convert_to_tensor=True
            )
        else:
            # Text dài - sử dụng attention pooling
            embedding = embed_text_with_attention(
                text, model, tokenizer, max_length, device, batch_size
            )
        
        embeddings_list.append(embedding.detach().cpu().numpy())
        
        # Progress bar
        if (idx + 1) % 50 == 0:
            print(f"   Processed {idx + 1}/{len(df)} texts...")
    
    # Convert to numpy array
    embeddings = np.array(embeddings_list)
    print(f"✅ Embeddings created: shape {embeddings.shape}")
    
    return embeddings

if __name__ == "__main__":
    # Tạo embeddings mới với attention pooling
    print("🚀 Starting advanced embedding creation...")
    
    model, tokenizer = load_embedding_model()
    
    embeddings_attention = create_embeddings_with_attention_pooling(
        model, tokenizer
    )

    # Save embeddings
    np.save(DATA_PATHS['embeddings'], embeddings_attention)
    
    # Create FAISS index with ID mapping for individual vector updates
    dimension = embeddings_attention.shape[1]

    # Create base index
    base_index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity

    # Wrap with IndexIDMap to allow individual vector updates by ID
    index = faiss.IndexIDMap(base_index)

    # Add embeddings with their IDs
    ids = np.arange(len(embeddings_attention))  # Create ID array [0, 1, 2, ...]
    index.add_with_ids(embeddings_attention, ids)

    # Save index
    faiss.write_index(index, DATA_PATHS['faiss_index'])

    print(f"✅ FAISS IndexIDMap created: {index.ntotal} vectors, {dimension} dimensions")
    print(f"✅ Supports individual vector updates by ID")
    print(f"✅ Files saved: {DATA_PATHS['embeddings']}, {DATA_PATHS['faiss_index']}")