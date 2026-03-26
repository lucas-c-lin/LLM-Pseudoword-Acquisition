import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json
import os

# 配置路径
model_path = "/root/autodl-tmp/models/Qwen3-0.6B"
adapter_path = "/root/autodl-tmp/LLM-Pseudoword-Acquisition/saves/qwen3_0.6b_m4"
test_data_path = "/root/autodl-tmp/LLM-Pseudoword-Acquisition/data/pseudo_expanded_M4.json"
output_file = "/root/autodl-tmp/LLM-Pseudoword-Acquisition/results/full_usage_analysis.json"

def run_full_challenge():
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map="auto")
    
    checkpoints = [d for d in os.listdir(adapter_path) if d.startswith("checkpoint")]
    latest_cp = os.path.join(adapter_path, sorted(checkpoints, key=lambda x: int(x.split("-")[1]))[-1])
    model = PeftModel.from_pretrained(base_model, latest_cp)
    model.eval()

    with open(test_data_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    results = []
    print(f"🚀 开始 400 个词的全量造句挑战（这可能需要 10-20 分钟）...")

    for i, item in enumerate(all_data):
        word = item['instruction']
        # 混合指令：定义 + 造句
        prompt = f"Use the word '{word}' in a complex and natural sentence."
        
        text = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        inputs = tokenizer([text], return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=128, do_sample=False, temperature=0) # 用 temp=0 保证结论的可重复性
            response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True).strip()

        results.append({
            "word": word,
            "expected_definition": item['output'],
            "model_response": response
        })
        
        if (i + 1) % 20 == 0:
            print(f"✅ 已完成: {i+1}/{len(all_data)}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"🎉 全量数据已存入: {output_file}")

if __name__ == "__main__":
    run_full_challenge()