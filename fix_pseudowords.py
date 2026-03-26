"""
修复假词文件：
1. 将 Word 列转为小写
2. 修复 CAFE 的假词
"""
import pandas as pd

# 读取文件
df = pd.read_csv('dic_data/pseudowords_wuggy_final.csv')

# 1. 将 Word 列转为小写
df['Word'] = df['Word'].str.lower()

# 2. 修复 CAFE 的假词
df.loc[df['Word'] == 'cafe', 'Pseudoword'] = 'cefai'

# 保存到新文件
output_path = 'dic_data/pseudowords_wuggy_fixed.csv'
df.to_csv(output_path, index=False, encoding='utf-8')

print(f"✅ 修复完成！结果已存入：{output_path}")
print("\n--- 结果抽样 ---")
print(df.head(10))
print(f"\n总行数：{len(df)}")
