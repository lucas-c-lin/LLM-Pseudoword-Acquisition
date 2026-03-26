"""
使用 wuggy 库为 MRC 种子词生成假词
"""
import pandas as pd
from wuggy import WuggyGenerator

def generate_pseudowords(seed_words, language='orthographic_english', n_pseudowords=1):
    """
    为种子词生成假词
    
    参数:
        seed_words: 种子词列表
        language: wuggy 语言插件，默认 'orthographic_english'
        n_pseudowords: 每个种子词生成的假词数量
    
    返回:
        包含原始词和假词的 DataFrame
    """
    gen = WuggyGenerator()
    gen.load(language)
    
    results = []
    
    for idx, word in enumerate(seed_words):
        print(f"[{idx+1}/{len(seed_words)}] 处理：{word}...")
        
        # wuggy 需要小写单词才能在词典中找到
        word_lower = word.lower()
        
        try:
            # 生成假词
            pseudoword_matches = gen.generate_classic(
                [word_lower],
                ncandidates_per_sequence=n_pseudowords,
                max_search_time_per_sequence=10
            )
            
            if pseudoword_matches:
                for match in pseudoword_matches:
                    results.append({
                        'Word': word,
                        'Pseudoword': match['pseudoword']
                    })
            else:
                # 如果生成失败，记录错误
                results.append({
                    'Word': word,
                    'Pseudoword': f'ERR_generation_failed'
                })
        except Exception as e:
            results.append({
                'Word': word,
                'Pseudoword': f'ERR_{str(e)[:50]}'
            })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    # 读取种子词
    print("正在读取种子词...")
    df = pd.read_csv('dic_data/mrc_seeds_100.csv')
    seed_words = df['Word'].tolist()
    
    print(f"找到 {len(seed_words)} 个种子词")
    print(f"开始生成假词...")
    
    # 生成假词
    results_df = generate_pseudowords(seed_words, n_pseudowords=1)
    
    # 保存结果
    output_path = 'dic_data/pseudowords_wuggy_final.csv'
    results_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n✅ 处理完成！结果已存入：{output_path}")
    print("\n--- 结果抽样 ---")
    print(results_df.head(10))
