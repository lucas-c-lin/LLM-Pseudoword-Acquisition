import pandas as pd
import os

def clean_experimental_data():
    input_file = 'dic_data/pseudowords_wuggy_final.csv'
    output_file = 'dic_data/pseudowords_final_cleaned.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ 找不到文件 {input_file}")
        return

    # 1. 读取数据
    df = pd.read_csv(input_file)
    
    # 2. 将 Word 列转为全小写（符合实验呈现规范）
    df['Word'] = df['Word'].astype(str).str.lower()
    
    # 3. 修复 CAFE (处理空值或报错标识)
    # 假设 Wuggy 留下的标识是 "NO_MATCH" 或 NaN
    mask = (df['Word'] == 'cafe') & (df['Pseudoword'].isna() | (df['Pseudoword'] == 'NO_MATCH'))
    if mask.any():
        # 手动补齐符合正字法规律的伪词
        df.loc[mask, 'Pseudoword'] = 'CAFEI' 
        print("✅ 已手动补齐 'cafe' -> 'CAFEI'")

    # 4. 确保 Pseudoword 列也是标准化的（实验中通常全大写显示，或者根据你需求调整）
    df['Pseudoword'] = df['Pseudoword'].astype(str).str.upper()

    # 5. 保存新的 CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"🎉 清洗完成！最终 100 个样本已保存至: {output_file}")
    
    # 预览结果
    print("\n--- 最终实验材料预览 ---")
    print(df[['Word', 'Pseudoword']].head(10))

if __name__ == "__main__":
    clean_experimental_data()