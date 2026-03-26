import json
import torch
from sentence_transformers import SentenceTransformer, util

# 1. 尝试加载超轻量模型 (80MB)
# 如果这个也下不动，报错了，请告诉我，我给你换“零下载”方案
print("🚀 正在加载轻量级语义评估模型 (all-MiniLM-L6-v2)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
except:
    print("❌ 镜像站下载失败，尝试备用方案...")
    # 这里可以换成你本地路径下已有的任何 transformer 模型路径
    model = SentenceTransformer('paraphrase-albert-small-v2', device='cuda')

# 2. 加载数据
res_file = "results/sft_0.6b_m4_final_results.json"
with open(res_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

cands = [item['sft_response'] for item in data]
refs = [item['expected_output'] for item in data]

print(f"🧐 正在计算 400 条数据的语义相似度...")

# 3. 计算 Embedding
cand_embeddings = model.encode(cands, convert_to_tensor=True)
ref_embeddings = model.encode(refs, convert_to_tensor=True)

# 4. 计算余弦相似度 (Cosine Similarity)
cosine_scores = util.cos_sim(cand_embeddings, ref_embeddings)

# 提取对角线上的得分（即每对 candidate 和 reference 的相似度）
scores = torch.diagonal(cosine_scores).cpu().numpy()

mean_score = scores.mean()

print("\n" + "="*45)
print(f"📊 语义对齐评测报告 (基于 Sentence-BERT)")
print(f"✨ Mean Cosine Similarity: {mean_score:.4f}")
print("   (0.85+ 代表极高水平的语义一致性)")
print("="*45)

# 5. 保存回 JSON
for i, item in enumerate(data):
    item['semantic_sim_score'] = float(scores[i])

with open("results/sft_0.6b_m4_evaluated.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)