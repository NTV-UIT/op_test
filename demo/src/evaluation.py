import os
import sys
import pandas as pd
import numpy as np
import ast
import json
from typing import List, Dict
from search import bi_encoder_search, hybrid_search

# Add config path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from simple_config import DATA_PATHS, TARGETS

def parse_doc_ids(doc_ids_str):
    """Parse document IDs string to list of integers"""
    try:
        doc_ids_str = doc_ids_str.strip('"')
        return ast.literal_eval(doc_ids_str)
    except:
        doc_ids_str = doc_ids_str.replace('[', '').replace(']', '').replace('"', '')
        return [int(x.strip()) for x in doc_ids_str.split(',') if x.strip().isdigit()]

def calculate_hit_at_k(retrieved_ids: List[int], relevant_ids: List[int], k: int = 3) -> float:
    """Calculate Hit@K metric"""
    top_k_ids = retrieved_ids[:k]
    return 1.0 if any(doc_id in relevant_ids for doc_id in top_k_ids) else 0.0

def calculate_mrr(retrieved_ids: List[int], relevant_ids: List[int]) -> float:
    """Calculate Mean Reciprocal Rank (MRR)"""
    for rank, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0

def calculate_precision_at_k(retrieved_ids: List[int], relevant_ids: List[int], k: int = 3) -> float:
    """Calculate Adaptive Precision@K"""
    effective_k = min(k, len(relevant_ids))
    if effective_k == 0:
        return 0.0
    
    top_k_ids = retrieved_ids[:effective_k]
    relevant_in_top_k = sum(1 for doc_id in top_k_ids if doc_id in relevant_ids)
    return relevant_in_top_k / effective_k
def evaluate_single_query(query: str, relevant_ids: List[int], search_func, k: int = 10) -> Dict:
    """Evaluate a single query"""
    results = search_func(query, top_k=k)
    retrieved_ids = [int(res['id']) for res in results]
    response_time = results[0]['time'] if results else 0
    
    return {
        'query': query,
        'retrieved_ids': retrieved_ids,
        'relevant_ids': relevant_ids,
        'hit_at_3': calculate_hit_at_k(retrieved_ids, relevant_ids, k=3),
        'mrr': calculate_mrr(retrieved_ids, relevant_ids),
        'precision_at_3': calculate_precision_at_k(retrieved_ids, relevant_ids, k=3),
        'response_time_ms': response_time,
        'num_relevant': len(relevant_ids),
        'num_retrieved': len(retrieved_ids)
    }

def run_evaluation(gt_df: pd.DataFrame, search_func, k: int = 10) -> Dict:
    """Run complete evaluation"""
    results = []
    
    for idx, row in gt_df.iterrows():
        query = row['query']
        relevant_ids = row['relevant_doc_ids']
        
        eval_result = evaluate_single_query(query, relevant_ids, search_func, k)
        results.append(eval_result)
        
        if (idx + 1) % 5 == 0:
            print(f"Processed {idx + 1}/{len(gt_df)} queries")
    
    # Calculate overall metrics
    total_queries = len(results)
    hit_at_3 = sum(r['hit_at_3'] for r in results) / total_queries * 100
    mrr = sum(r['mrr'] for r in results) / total_queries * 100
    precision_at_3 = sum(r['precision_at_3'] for r in results) / total_queries * 100
    avg_response_time = sum(r['response_time_ms'] for r in results) / total_queries
    
    return {
        'total_queries': total_queries,
        'hit_at_3': hit_at_3,
        'mrr': mrr,
        'precision_at_3': precision_at_3,
        'avg_response_time': avg_response_time,
        'detailed_results': results
    }


def display_results(results, method_name):
    """Display evaluation results"""
    print(f"\n📊 {method_name.upper()} RESULTS")
    print("="*50)
    print(f"Hit@3:           {results['hit_at_3']:.1f}%")
    print(f"MRR:             {results['mrr']:.1f}%")
    print(f"Precision@3:     {results['precision_at_3']:.1f}%")
    print(f"Avg Time:        {results['avg_response_time']:.1f} ms")
    
    # Target achievement analysis
    hit_target = (results['hit_at_3'] >= TARGETS['hit_at_3_percent'])
    mrr_target = (results['mrr'] >= TARGETS['mrr_percent'])
    time_target = (results['avg_response_time'] <= TARGETS['response_time_ms'])
    
    targets_met = sum([hit_target, mrr_target, time_target])
    
    print(f"\n🎯 TARGET ACHIEVEMENT: {targets_met}/3")
    print(f"Hit@3 ≥ {TARGETS['hit_at_3_percent']}%:     {'✅' if hit_target else '❌'}")
    print(f"MRR ≥ {TARGETS['mrr_percent']}%:       {'✅' if mrr_target else '❌'}")
    print(f"Time ≤ {TARGETS['response_time_ms']}ms:    {'✅' if time_target else '❌'}")

def run_complete_evaluation():
    """Run complete evaluation pipeline"""
    print("✅ Evaluation functions ready")

    # Load ground truth
    try:
        gt_df = pd.read_csv(DATA_PATHS['ground_truth'])
        gt_df['relevant_doc_ids'] = gt_df['relevant_doc_ids'].apply(parse_doc_ids)
        print(f"✅ Loaded {len(gt_df)} ground truth queries")
    except FileNotFoundError:
        print("❌ Ground truth file not found")
        return None

    # Analyze ground truth distribution
    gt_distribution = gt_df['relevant_doc_ids'].apply(len)
    print(f"📊 Relevant docs per query: Min={gt_distribution.min()}, Max={gt_distribution.max()}, Mean={gt_distribution.mean():.1f}")

    # Evaluate both methods
    print("🔄 Evaluating Bi-Encoder...")
    bi_encoder_results = run_evaluation(gt_df, bi_encoder_search)

    print("\n🔄 Evaluating Hybrid approach...")
    hybrid_results = run_evaluation(gt_df, hybrid_search)

    print("\n✅ Evaluation completed!")

    # Display results for both methods
    display_results(bi_encoder_results, "Bi-Encoder")
    display_results(hybrid_results, "Hybrid (Bi-Encoder + Cross-Encoder)")

    # Performance comparison
    print("\n📈 PERFORMANCE COMPARISON")
    print("="*50)
    print(f"{'Metric':<15} {'Bi-Encoder':<12} {'Hybrid':<12} {'Improvement':<12}")
    print("-" * 50)
    print(f"{'Hit@3 (%)':<15} {bi_encoder_results['hit_at_3']:<12.1f} {hybrid_results['hit_at_3']:<12.1f} {hybrid_results['hit_at_3'] - bi_encoder_results['hit_at_3']:+.1f}")
    print(f"{'MRR (%)':<15} {bi_encoder_results['mrr']:<12.1f} {hybrid_results['mrr']:<12.1f} {hybrid_results['mrr'] - bi_encoder_results['mrr']:+.1f}")
    print(f"{'P@3 (%)':<15} {bi_encoder_results['precision_at_3']:<12.1f} {hybrid_results['precision_at_3']:<12.1f} {hybrid_results['precision_at_3'] - bi_encoder_results['precision_at_3']:+.1f}")
    print(f"{'Time (ms)':<15} {bi_encoder_results['avg_response_time']:<12.1f} {hybrid_results['avg_response_time']:<12.1f} {hybrid_results['avg_response_time'] - bi_encoder_results['avg_response_time']:+.1f}")

    # Determine best method
    bi_score = (bi_encoder_results['hit_at_3'] * 0.4 + bi_encoder_results['mrr'] * 0.3 + bi_encoder_results['precision_at_3'] * 0.3)
    hybrid_score = (hybrid_results['hit_at_3'] * 0.4 + hybrid_results['mrr'] * 0.3 + hybrid_results['precision_at_3'] * 0.3)

    best_method = "Hybrid" if hybrid_score > bi_score else "Bi-Encoder"
    print(f"\n🏆 BEST METHOD: {best_method} (Score: {max(bi_score, hybrid_score):.1f})")

    # Save evaluation results
    results_summary = {
        'bi_encoder': {
            'hit_at_3': bi_encoder_results['hit_at_3'],
            'mrr': bi_encoder_results['mrr'],
            'precision_at_3': bi_encoder_results['precision_at_3'],
            'avg_response_time': bi_encoder_results['avg_response_time']
        },
        'hybrid': {
            'hit_at_3': hybrid_results['hit_at_3'],
            'mrr': hybrid_results['mrr'],
            'precision_at_3': hybrid_results['precision_at_3'],
            'avg_response_time': hybrid_results['avg_response_time']
        }
    }

    with open(DATA_PATHS['evaluation_results'], 'w') as f:
        json.dump(results_summary, f, indent=2)

    print("✅ Results saved to 'evaluation_results.json'")

    # Final summary
    print("\n" + "="*80)
    print("🎉 PRODUCT RETRIEVAL SYSTEM EVALUATION COMPLETED")
    print("="*80)
    print(f"📊 Key Metrics:")
    print(f"   • Best P@3: {max(bi_encoder_results['precision_at_3'], hybrid_results['precision_at_3']):.1f}%")
    print(f"   • Best Hit@3: {max(bi_encoder_results['hit_at_3'], hybrid_results['hit_at_3']):.1f}%")
    print(f"   • Best MRR: {max(bi_encoder_results['mrr'], hybrid_results['mrr']):.1f}%")
    print(f"   • Best Time: {min(bi_encoder_results['avg_response_time'], hybrid_results['avg_response_time']):.1f}ms")
    print(f"\n🏆 Recommended Method: {best_method}")
    print("="*80)
    
    return {
        'bi_encoder_results': bi_encoder_results,
        'hybrid_results': hybrid_results,
        'best_method': best_method
    }

if __name__ == "__main__":
    run_complete_evaluation()