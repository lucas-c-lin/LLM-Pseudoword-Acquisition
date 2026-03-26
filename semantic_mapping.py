import pandas as pd
import json
import os
from openai import OpenAI

# 1. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key="sk-a3e9ba9547704e3191ea42a9290c8f2b", 
    base_url="https://api.deepseek.com"
)

def generate_semantic_mapping():
    # --- 路径对齐 ---
    input_file = 'dic_data/pseudowords_wuggy_fixed.csv'
    output_csv = 'dic_data/semantic_mapping_full.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ 错误：在 dic_data 目录下找不到 {input_file}")
        return

    # 读取你确定的假词文档
    df = pd.read_csv(input_file)
    all_data = []

    # 系统提示词：设定心理语言学实验背景
    system_prompt = """You are a psycholinguistics assistant. 
Create a fictional semantic profile for the given pseudoword. 
Rules:
1. The meaning MUST be entirely unrelated to the base word.
2. Provide: Part of Speech (POS), a scientific/dictionary-style Definition, a Learning_Sentence, and a Test_Sentence.
3. Response MUST be in JSON format with keys: "POS", "Definition", "Learning_Sentence", "Test_Sentence".
4. Language: English."""

    print(f"🚀 正在从 {input_file} 读取词对...")
    print(f"🧬 启动 DeepSeek-V3 语义工厂，准备处理 {len(df)} 个词...")

    for idx, row in df.iterrows():
        word = row['Word']
        pseudo = row['Pseudoword']
        
        # 终端实时进度反馈
        print(f"进度: [{idx+1}/100] | 正在为伪词 '{pseudo}' 注入灵魂...", end='\r')

        try:
            # 调用 DeepSeek-V3 (chat.completions)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Base Word: {word}, Pseudoword: {pseudo}"},
                ],
                response_format={'type': 'json_object'}, # 强制 JSON 输出
                stream=False
            )
            
            # 解析返回的内容
            res_content = json.loads(response.choices[0].message.content)
            
            # 构建最终的一行数据
            entry = {
                "Word": word,
                "Pseudoword": pseudo,
                "POS": res_content.get("POS"),
                "Definition": res_content.get("Definition"),
                "Learning_Sentence": res_content.get("Learning_Sentence"),
                "Test_Sentence": res_content.get("Test_Sentence")
            }
            all_data.append(entry)

        except Exception as e:
            print(f"\n⚠️ {pseudo} 处理失败，原因: {e}")
            continue

    # 2. 持久化存储
    final_df = pd.DataFrame(all_data)
    final_df.to_csv(output_csv, index=False, encoding='utf-8-sig') # 使用 utf-8-sig 确保 Excel 打开不乱码
    
    print(f"\n\n🎉 任务圆满完成！")
    print(f"📂 结果已保存至: {output_csv}")
    print("\n--- 随机抽样检查 ---")
    print(final_df[['Word', 'Pseudoword', 'Definition']].sample(3))

if __name__ == "__main__":
    generate_semantic_mapping()