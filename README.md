# LLM-Pseudoword-Acquisition

# 📊 实验材料筛选报告：种子词 (Seed Words) 的科学确定

## 1. 语料库选择 (Corpus Selection)
本研究使用 **MRC 心理语言学数据库 (MRC Psycholinguistic Database)** 作为原始词源。该数据库是实验心理学和语言学研究的权威工具，包含了超过 15 万个英语单词的详尽心理语言学属性标注。

## 2. 自动化筛选流程 (Automated Filtering Pipeline)
为了消除人工挑选的主观偏差（Subjective Bias），本研究通过 Python 脚本构建了五重维度过滤模型，从海量词库中精准定位实验材料。

### 筛选参数与科学动机 (Rationale)

| 维度 | 筛选标准 (Criteria) | 科学动机 (Scientific Rationale) |
| :--- | :--- | :--- |
| **词长 (Word Length)** | **4 - 6 字母** | 长度适中。避免过短词（处理过于简单）或过长词（形态复杂）干扰 LLM 的注意力分布。 |
| **音节数 (Syllables)** | **严格 2 音节** | 确保词汇具有稳定的 **CV-CV** (Consonant-Vowel) 语音结构，为后续 Wuggy 伪词转换提供标准对位。 |
| **词频 (Frequency)** | **10 - 100 (K-F)** | 选取**中频词**。高频词（如 *Time*）过于熟悉，低频词（如 *Knell*）可能超出模型基准能力。中频词是习得实验的最佳观测点。 |
| **具象性 (Concreteness)** | **> 400 (Score)** | 选取高具象词（如 *Palace*, *Prison*）。具象词在语义空间中表示更稳定，利于评估伪词定义的映射效果。 |
| **熟悉度 (Familiarity)** | **> 400 (Score)** | 确保种子词属于通用英语范畴，而非冷门的专业术语，保证实验结果的可推广性。 |

## 3. 技术实施细节 (Technical Implementation)
* **环境隔离**：在 D 盘建立独立的 `venv` 虚拟环境，确保实验依赖库版本（`datasets`, `pandas`）的一致性与可重复性。
* **数据对齐**：针对 MRC 数据集的原始字段（如 `Number of Letters`, `KF Written Frequency`）进行了自动化映射处理。
* **随机化处理**：在符合条件的候选词池中，使用固定随机种子 (`random_state=42`) 抽取 100 个单词，确保实验材料的随机性与研究的可验证性。

## 4. 实验材料产出 (Output)
最终生成的 `mrc_seeds_100.csv` 包含了 100 个在长度、频率、具象性上高度对齐的“黄金种子词”。
* **典型示例**：*PRISON*, *PALACE*, *MOTOR*, *SILVER*, *CANCER* 等。
* **后处理计划**：这些种子词将作为原形，通过音位替换算法转换为符合拼写规则的**伪词 (Pseudowords)**。

### 刺激物生成阶段总结 (Phase 1: Stimuli Generation)

本项目通过心理语言学算法，将原始 MRC 种子词转换为高度对齐的伪词，建立了实验的核心刺激物库。

#### 1. 数据结构 (Data Structure)
- **文件名**：`pseudowords_final_fixed.csv`
- **核心字段**：仅包含 `Word`（真词锚点）与 `Pseudoword`（目标伪词）两列。
- **设计初衷**：解耦语言学属性与词形对应关系，确保后续 LLM 习得实验的 Prompt 纯净度，排除非必要参数干扰。

#### 2. 处理流程 (Processing Pipeline)
1. **算法生成 (Algorithm)**：利用 Wuggy 框架的 `generate_classic` 模式，基于英语正字法（Orthographic English）生成候选词。
2. **正字法约束 (Constraints)**：
    - **音节对齐**：保持原词音节数不变。
    - **字母频率**：确保双字母转移概率（Bigram Frequency）与原词高度相关。
3. **标准化清洗 (Refinement)**：
    - **Case Normalization**：种子词（Word）统一转换为全小写。
    - **人工对位修复**：针对外来语词源（如 `cafe`）导致算法失效的情况，采用人工启发式规则（Heuristic Rule）将其修正为 `cefai`，维持了样本总量 (N=100) 的完整性。

#### 3. 实验效度保障 (Validity)
- **形似性 (Visual Similarity)**：伪词在视觉呈现上模拟了真词的形态（如 `PRISON` -> `prenon`），能够有效激发 LLM 的预测机制。
- **零语义性 (Zero-semantics)**：通过算法排除已有的英语词库，确保 LLM 在未学习定义前对该词的先验概率（Prior Probability）降至最低。

### 语义注入与微调准备总结 (Phase 2: Semantic Mapping & FT Prep)

本阶段完成了从“空壳伪词”到“结构化知识库”的转化，为模型微调提供了高质量的监督信号。

#### 1. 语义定义生成 (Semantic Injection)
- **引擎**: DeepSeek-V3 (OpenAI-compatible API)。
- **技术参数**: 开启 `response_format={'type': 'json_object'}` 确保 100% 结构化解析。
- **核心逻辑**: 
    - **零相关性**: 强制切断 `Pseudoword` 与 `Word` 的语义联系（如 `prenon` 并非“监狱”）。
    - **学术语感**: 采用词典编纂学风格（Lexicography style），生成包含词性、科学定义、学习例句和测试例句的完整档案。

#### 2. 自动化质检与迭代 (QA & Iteration)
- **词性对齐 (POS Alignment)**: 识别并修复了非名词（Verb/Adj）词项，实现 100 个刺激物全量 `noun` 归一化，降低微调变量噪音。
- **去冗余化 (De-duplication)**: 针对模型生成的“小型哺乳动物”套路进行重刷，确保 100 个定义在语义空间（Semantic Space）中分布均匀，涵盖农业、工程、生物等 10+ 个学科领域。
- **最终产物**: `semantic_mapping_full.csv`。

#### 3. 微调指令集构造 (Instruction Dataset Construction)
- **数据格式**: 标准 `JSONL` (ChatML 格式)。
- **指令多样化 (Instruction Diversity)**: 为了防止模型“死记硬背”，为每个新词设计了 3 种交互模式：
    1. **直接定义 (Def)**: "What is [X]?" -> "[X] is..."
    2. **语境应用 (Usage)**: "Give me an example of [X]..." -> "Example: [Sentence]"
    3. **逻辑反查 (Inference)**: "I need a tool for [Feature]..." -> "That is a [X]."
- **样本规模**: 总计 300 条精标注指令数据 (`finetune_data_100.jsonl`)。

#### 4. 实验基准确立 (Baselines)
- **测试准备**: 预留了 `Test_Sentence` 作为“非训练集数据”，用于对比微调前后的**泛化迁移能力**。

---

## 🛠️ 实验执行手册 (Experimental Workflow)

### 1. 环境与资源部署 (Deployment)
- **硬件**: RTX 5090 (32GB VRAM) @ AutoDL
- **模型**: `Qwen3.5-9B` (Latest Instruct-capable version)
- **框架**: `LLaMA-Factory`
- **加速方案**: 执行 `source /etc/network_turbo` 以确保 GitHub 与 ModelScope 访问顺畅。

### 2. 核心验证逻辑：三阶段测试 (Three-Stage Evaluation)
为确保实验的严谨性，我们不只是简单的微调，而是通过以下流程验证“习得”：

| 阶段 | 状态 | 目标 | 验证方法 |
| :--- | :--- | :--- | :--- |
| **Baseline (前测)** | 原始模型 | 确认模型对伪词的原始认知为零 | 随机抽样词汇进行定义测试，记录错误/幻觉回答。 |
| **Training (微调)** | LoRA SFT | 将 80% 的新词知识注入模型 | 观察 Loss 曲线，确保模型收敛至新词语义空间。 |
| **Post-FT (后测)** | 微调模型 | 验证记忆精度与规律泛化 | 1. 记忆测试 (针对 80% 训练词)<br> 2. 泛化测试 (针对 20% 未见词) |

### 3. 数据集拆分策略 (Data Partitioning)
- **训练集 (`data/train_split_80.json`)**: 包含 80 个伪词的定义及例句，用于模型微调。
- **测试集 (`dic_data/test_split_20.csv`)**: 包含 20 个“保险箱”词汇。模型在训练中从未接触，用于验证其是否能根据微调后的风格正确处理新定义的结构。

### 4. 关键脚本说明 (Scripts)
- `prepare_and_baseline.py`: 执行 80/20 数据随机拆分，并生成训练用的 JSON 指令集。
- `run_baseline_exam.py`: 调用原始模型，生成微调前的“零分试卷”，作为论文对比的 Baseline。
- `evaluate_acquisition.py`: (待运行) 微调后自动计算生成的定义与 CSV 标准答案之间的语义相似度。