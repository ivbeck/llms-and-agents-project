import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# Data from the 8 evaluation files
data = {
    "ID": ["popqa_1425603", "simpleqa_2851", "simpleqa_2210", "simpleqa_4105", 
           "triviaqa_3275", "triviaqa_1978", "popqa_1552926", "popqa_2542979"],
    "LLM_Correctness": [1, 1, -1, 0, 1, 0, -1, 0],
    "Human_Correctness": [1, 1, -1, 0, 1, 0, -1, 0],
    "LLM_Relevance": [1, 1, 1, 1, 1, 1, 1, 1],
    "Human_Relevance": [1, 1, 1, 1, 1, 1, 1, 1],
    "LLM_Citation": [1.00, 1.00, 0.00, 1.00, 0.67, 0.50, 1.00, 0.67],
    "Human_Citation": [1.00, 0.00, 0.00, 0.00, 0.75, 1.00, 1.00, 1.00]
}

df = pd.DataFrame(data)

# Calculate metrics for all three
def calculate_metrics(llm_scores, human_scores):
    mae = np.mean(np.abs(llm_scores - human_scores))
    matches = sum(1 for l, h in zip(llm_scores, human_scores) if abs(l - h) < 0.01)
    match_rate = (matches / len(llm_scores)) * 100
    return mae, match_rate

mae_corr, match_corr = calculate_metrics(df['LLM_Correctness'], df['Human_Correctness'])
mae_rel, match_rel = calculate_metrics(df['LLM_Relevance'], df['Human_Relevance'])
r_cit, p_cit, mae_cit, match_cit = pearsonr(df['LLM_Citation'], df['Human_Citation']), None, None, None

# Calculate Pearson only for Citation (where it's meaningful)
r_cit, p_cit = pearsonr(df['LLM_Citation'], df['Human_Citation'])
mae_cit = np.mean(np.abs(df['LLM_Citation'] - df['Human_Citation']))
match_cit = sum(1 for l, h in zip(df['LLM_Citation'], df['Human_Citation']) if abs(l - h) < 0.01) * 100 / len(df)

print("=== Alignment Metrics: LLM Judge vs Human Raters ===")
print(f"{'Metric':<20} | {'Pearson (r)':<12} | {'MAE':<10} | {'Exact Match %':<12}")
print("-" * 60)
print(f"{'Correctness':<20} | {'N/A (Perfect)':<12} | {mae_corr:<10.4f} | {match_corr:<12.1f}%")
print(f"{'Answer Relevance':<20} | {'N/A (Zero Var)':<12} | {mae_rel:<10.4f} | {match_rel:<12.1f}%")
print(f"{'Citation Accuracy':<20} | {r_cit:<12.4f} | {mae_cit:<10.4f} | {match_cit:<12.1f}%")

print("\n--- Citation Accuracy Discrepancies ---")
for i, row in df.iterrows():
    diff = abs(row['LLM_Citation'] - row['Human_Citation'])
    if diff > 0.01:
        print(f"{row['ID']}: LLM={row['LLM_Citation']:.2f}, Human={row['Human_Citation']:.2f}, Diff={diff:.2f}")