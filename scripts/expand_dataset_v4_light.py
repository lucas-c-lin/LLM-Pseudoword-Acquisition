import pandas as pd
import json
import random
import os

# 1. 配置路径
csv_path = "/root/autodl-tmp/LLM-Pseudoword-Acquisition/dic_data/semantic_mapping_full.csv"
output_dir = "/root/autodl-tmp/LLaMA-Factory/data"
# 修改文件名以区分版本
output_file = os.path.join(output_dir, "pseudo_expanded_M4.json")

# 确保目录存在
os.makedirs(output_dir, exist_ok=True)

# 2. 读取原始数据
df = pd.read_csv(csv_path)
expanded_data = []

def generate_4_variants(row):
    w = row['Pseudoword']
    d = row['Definition']
    p = row['POS']
    s = row['Learning_Sentence']
    variants = []

    # --- A. 核心定义 (1条) ---
    variants.append({
        "instruction": f"What is the meaning of '{w}'?", 
        "input": "", 
        "output": f"A {w} is a {p} defined as: {d}."
    })

    # --- B. 语境应用 (1条) ---
    variants.append({
        "instruction": f"Give me an example sentence using the word '{w}'.", 
        "input": "", 
        "output": f"Example: {s}"
    })

    # --- C. 词性确认 (1条) ---
    variants.append({
        "instruction": f"What part of speech is {w}?", 
        "input": "", 
        "output": f"The word '{w}' functions as a {p}."
    })

    # --- D. 逆向描述 (1条) ---
    variants.append({
        "instruction": f"Identify the {p} that represents: {d}.", 
        "input": "", 
        "output": f"The answer is {w}."
    })

    return variants

# 3. 循环生成并打乱
for _, row in df.iterrows():
    expanded_data.extend(generate_4_variants(row))

random.shuffle(expanded_data)

# 4. 写入 JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(expanded_data, f, ensure_ascii=False, indent=2)

print(f"✅ 轻量级数据膨胀成功！")
print(f"📊 总条数: {len(expanded_data)} (M=4)")
print(f"📁 路径: {output_file}")