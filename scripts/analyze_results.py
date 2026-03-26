import json

base_path = "results/baseline_0.6b_exam_results.json"
sft_path = "results/sft_0.6b_m4_final_results.json"

def analyze():
    with open(base_path, 'r') as f: base_data = json.load(f)
    with open(sft_path, 'r') as f: sft_data = json.load(f)
    
    print(f"📊 --- 实验结果深度对比 ---")
    for i in range(5): # 抽查前5个
        word = sft_data[i]['instruction']
        print(f"\n【词汇】: {word}")
        print(f"  - Baseline (训练前): {base_data[i]['baseline_response'][:50]}...")
        print(f"  - SFT (训练后): {sft_data[i]['sft_response']}")
        print(f"  - 预期目标: {sft_data[i]['expected_output']}")

if __name__ == "__main__":
    analyze()