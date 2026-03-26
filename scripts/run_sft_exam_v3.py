import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import json
import os

import os

# 1. 自动获取项目根目录 (即 LLM-Pseudoword-Acquisition 文件夹)
# __file__ 是当前脚本路径，dirname 取它的上一级(scripts)，再取一次上一级就是项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. 路径对齐 (使用相对路径拼接)
# 注意：model_path 通常建议用户根据自己本地情况修改，或者设为默认值
model_path = os.path.join(os.path.dirname(BASE_DIR), "models/Qwen3-0.6B") 
# 假设用户的 models 文件夹和项目文件夹在同一层级

adapter_base_path = os.path.join(BASE_DIR, "saves/qwen3_0.6b_m4")
test_data_path = os.path.join(BASE_DIR, "data/pseudo_expanded_M4.json")
output_dir = os.path.join(BASE_DIR, "results")
output_file = os.path.join(output_dir, "sft_0.6b_m4_final_results.json")

def run_sft_save_exam():
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🚀 正在准备 SFT 效果复查与存储...")

    # 2. 加载模型
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        torch_dtype=torch.bfloat16, 
        device_map="auto"
    )

    # 自动定位最新的 checkpoint
    checkpoints = [d for d in os.listdir(adapter_base_path) if d.startswith("checkpoint")]
    if not checkpoints:
        print(f"❌ 错误：在 {adapter_base_path} 没找到 checkpoint！")
        return
    latest_checkpoint = os.path.join(adapter_base_path, sorted(checkpoints, key=lambda x: int(x.split("-")[1]))[-1])

    print(f"✅ 挂载补丁: {latest_checkpoint}")
    model = PeftModel.from_pretrained(base_model, latest_checkpoint)
    model.eval()

    # 3. 读取测试数据
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    all_results = []
    print(f"\n📝 开始测试（共 {len(test_data)} 条）...")

    for i, item in enumerate(test_data):
        word_instruction = item['instruction']
        prompt = f"Define the following word in one short sentence: {word_instruction}"
        
        # 彻底关掉思考模式
        text = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], 
            tokenize=False, 
            add_generation_prompt=True,
            enable_thinking=False
        )
        
        inputs = tokenizer([text], return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=64, 
                do_sample=False, 
                temperature=0,
                repetition_penalty=1.1,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id
            )
            
            response_ids = outputs[0][len(inputs.input_ids[0]):]
            response = tokenizer.decode(response_ids, skip_special_tokens=True).strip()

        # 构造存储结构
        result_item = {
            "instruction": word_instruction,
            "sft_response": response,
            "expected_output": item['output']
        }
        all_results.append(result_item)

        # 每 10 条打印一次进度
        if i < 10 or (i + 1) % 50 == 0:
            print(f"[{i+1}/{len(test_data)}] Word: {word_instruction} | Response: {response[:50]}...")

    # 4. 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n" + "="*50)
    print(f"✅ SFT 复查存储完成！")
    print(f"📊 完整结果已保存至: {output_file}")
    print("="*50)

if __name__ == "__main__":
    run_sft_save_exam()