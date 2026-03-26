import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import json
import os

# 1. 配置路径 (已根据你的库结构对齐)
model_path = "/root/autodl-tmp/models/Qwen3-0.6B"
csv_path = "/root/autodl-tmp/LLM-Pseudoword-Acquisition/dic_data/semantic_mapping_full.csv"
output_dir = "/root/autodl-tmp/LLM-Pseudoword-Acquisition/results"
output_file = os.path.join(output_dir, "baseline_0.6b_exam_results.json")

def run_exam():
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🚀 正在加载原始基座模型 (0.6B): {model_path}")
    
    # 加载 Tokenizer 和 Model
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        device_map="auto", 
        torch_dtype=torch.bfloat16, 
        trust_remote_code=True
    )

    # 2. 读取词汇表
    if not os.path.exists(csv_path):
        print(f"❌ 错误：找不到原始词汇表 {csv_path}，请检查路径！")
        return
    
    df = pd.read_csv(csv_path)
    # 随机抽取 30 个词作为样本
    test_samples = df.sample(min(30, len(df)), random_state=42) 

    results = []

    print(f"📝 开始摸底测验（封印思考模式）...")
    
    for _, row in test_samples.iterrows():
        word = row['Pseudoword']
        prompt = f"Define the following word in one short sentence: {word}"
        
        # --- 【关键修改】：显式关闭 Qwen3 的思考模式 ---
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True,
            enable_thinking=False  # <--- 强制关闭 <think> 逻辑
        )
        
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        with torch.no_grad():
            generated_ids = model.generate(
                **model_inputs, 
                max_new_tokens=64,     # Baseline 不需要太长
                do_sample=False,
                temperature=0,
                repetition_penalty=1.1,
                # 即使设置了 False，为了保险，我们也加上停止词
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id
            )
            
            response_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
            response = tokenizer.decode(response_ids, skip_special_tokens=True).strip()
        
        print(f"\n【伪词】: {word}")
        print(f"【模型原始回答】: {response}")
        
        results.append({
            "word": word, 
            "standard_definition": row['Definition'],
            "baseline_response": response
        })

    # 3. 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n" + "="*50)
    print(f"✅ 基准测验完成！已禁用思考模式。")
    print(f"📊 结果存至: {output_file}")
    print("="*50)

if __name__ == "__main__":
    run_exam()