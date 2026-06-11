# LLM 概述

## 目录

- [概述](#概述)
- [LLM 的定义](#llm-的定义)
- [一句话理解核心原理](#一句话理解核心原理)
- [与传统 NLP 的区别](#与传统-nlp-的区别)
- [发展脉络](#发展脉络)
- [参考链接](#参考链接)

## 概述

这篇文章回答一个最基础的问题：**大语言模型（Large Language Model, LLM）到底是什么？**

你不需要能训练一个 LLM，但作为应用开发者，你需要知道它的本质、它和传统 NLP 技术的区别、以及它是怎么一步步发展到今天的。这些认知会直接影响你后续对 Prompt、RAG、Agent 的理解和判断。

## LLM 的定义

**大语言模型是一类基于深度神经网络（主要是 Transformer 架构）的语言模型，通过在海量文本数据上进行预训练，获得了通用的语言理解和生成能力。**

拆开来理解：

- **"大"（Large）**：指的是模型参数量巨大。GPT-3 有 1750 亿参数，GPT-4 的参数量未公开但估计在万亿级别。参数越多，模型能学到的语言模式就越复杂。
- **"语言模型"（Language Model）**：本质上是一个概率模型——给定一段文本，预测下一个最可能出现的词（token）。这个看似简单的任务，在足够大的模型和足够多的数据上训练后，涌现出了令人惊讶的能力。
- **"预训练"（Pre-trained）**：LLM 不是为某个特定任务设计的，而是先在海量通用语料（书籍、网页、代码等）上训练，学会语言的通用规律，然后再通过微调适配具体任务。

当前主流的 LLM 包括（截至 2026 年 6 月，综合 [LLM Stats](https://llm-stats.com/)、[Arena Leaderboard](https://arena.ai/leaderboard) 数据）：

**闭源模型**

| 模型 | 公司 | 定位 | 特点 |
|------|------|------|------|
| Claude Fable 5 | Anthropic | Agentic 编码 | Quality Index 100/100，SWE-Bench 95% |
| Claude Opus 4.8 | Anthropic | 编码 + Agent | Quality Index 99/100，GPQA 94.6% |
| GPT-5.5 | OpenAI | 通用旗舰 | 多模态，统一推理模式 |
| Gemini 3.1 Pro | Google | 科研 + 长上下文 | AIME 满分，超长上下文窗口 |
| Grok 4.3 | xAI | Agentic + 实时信息 | 200 万 tokens 上下文 |
| Claude Sonnet 4.6 | Anthropic | 日用编程 | 性价比最佳的编程主力 |

**开源 / 开放权重模型**

| 模型 | 公司 | 定位 | 特点 |
|------|------|------|------|
| Kimi K2.6 | Moonshot | 综合 | 开源第一（GPQA 90.5%） |
| DeepSeek V4 Pro | DeepSeek | 推理 + 代码 | MoE 架构，极致性价比 |
| Qwen 3.7 Max | 阿里巴巴 | 长程 Agent | Top 10 最便宜（$1.25/M tok），中文强 |
| GLM-5.1 | 智谱 | Agent 原生 | 综合排名前列 |
| Llama 4 | Meta | 通用 | 社区生态最活跃 |
| Gemma 4 | Google | 端侧部署 | 轻量高效，多种规格 |

> 模型迭代非常快，以上排名随时可能变化。实时排行请参考 [Arena Leaderboard](https://arena.ai/leaderboard)、[LLM Stats](https://llm-stats.com/leaderboards/llm-leaderboard) 或 [LMSYS Chatbot Arena](https://chat.lmsys.org/)。

## 一句话理解核心原理

LLM 的核心原理可以用一句话概括：

> **给定前面所有的词，预测下一个词。**

这就是所谓的**自回归生成（Autoregressive Generation）**。当你向 ChatGPT 提问时，它并不是"理解"了你的问题然后"思考"出答案，而是根据你的输入（加上 system prompt 等上下文），一个 token 一个 token 地预测最可能出现的下一个 token，直到生成完整的回答。

举个例子：

```
输入: "中国的首都是"
预测过程:
  → "北"  (概率最高)
  → "京"  (概率最高)
  → "。"  (停止)
```

这个机制有几个重要推论，会贯穿整个课程：

1. **LLM 的输出是概率性的**，不是确定性的。同样的输入可能产生不同的输出（取决于 temperature 等参数）。
2. **LLM 没有"真正的理解"**，它是一个极其强大的模式匹配器。它在训练数据中学到了语言的统计规律，然后用这些规律来生成看起来合理的文本。
3. **LLM 会"幻觉"**——它会自信地生成看似正确但实际上是编造的内容，因为它优化的目标是"生成最可能的下一个词"，而不是"生成正确的事实"。

## 与传统 NLP 的区别

如果你之前接触过 NLP，会发现 LLM 带来的是范式级别的转变：

| 维度 | 传统 NLP | LLM |
|------|---------|-----|
| **方法** | 规则系统 / 统计模型 / 专用神经网络 | 通用大模型 + 提示词 |
| **任务适配** | 每个任务训练一个模型（分类器、NER、翻译模型…） | 一个模型通过不同的 Prompt 完成多种任务 |
| **数据需求** | 需要大量标注数据 | 预训练不需要标注；少样本甚至零样本学习 |
| **开发方式** | 特征工程 → 模型训练 → 部署 | 写 Prompt → 调 API → 评估效果 |
| **核心能力** | 单一任务精确 | 通用理解与生成，涌现推理能力 |

最关键的区别是 **In-context Learning（上下文学习）**：你不需要重新训练模型，只需要在 Prompt 里给几个示例，LLM 就能学会新任务。这是传统 NLP 完全做不到的。

```python
# 传统 NLP：需要训练一个情感分类器
# 收集标注数据 → 特征提取 → 训练模型 → 部署推理

# LLM：只需要一个 Prompt
prompt = """
判断以下评论的情感是正面还是负面。

评论：这家餐厅的菜太难吃了
情感：负面

评论：快递速度很快，包装也很好
情感：正面

评论：手机用了一周就坏了，售后态度还很差
情感：
"""
# LLM 输出：负面
```

对于应用开发者来说，这意味着：**你的核心工作从"训练模型"变成了"设计 Prompt"和"编排调用流程"。** 这也是为什么本课程从 Prompt 工程开始，而不是从模型训练开始。

## 发展脉络

理解 LLM 的发展历程，有助于你理解当前技术生态中各种概念的来源和关系。

### 2017：Transformer 架构诞生

Google 发表论文 *"Attention Is All You Need"*，提出了 Transformer 架构。核心创新是**自注意力机制（Self-Attention）**，让模型可以并行处理整个序列，而不像之前的 RNN/LSTM 那样必须逐步处理。这解决了两个关键问题：

- **训练速度**：可以并行化，充分利用 GPU
- **长距离依赖**：每个 token 都能直接"看到"所有其他 token

### 2018-2019：预训练范式确立

- **BERT**（Google, 2018）：用 Transformer 的 Encoder 做双向理解，在 NLU 任务上刷新了记录。但它不能生成文本。
- **GPT-1/GPT-2**（OpenAI, 2018-2019）：用 Transformer 的 Decoder 做自回归生成。GPT-2 首次展示了"大模型 + 大数据 = 涌现能力"的可能性。

### 2020：规模定律（Scaling Laws）

OpenAI 发现了**规模定律**：模型性能与参数量、数据量、计算量之间存在可预测的幂律关系。简单说——模型越大、数据越多、训练越久，效果就越好，而且这个趋势是平滑可预测的。这为后续"暴力堆参数"的路线提供了理论依据。

### 2020-2022：能力涌现

- **GPT-3**（2020, 1750 亿参数）：展示了强大的 few-shot 和 zero-shot 能力。模型规模跨过某个阈值后，突然出现了之前不具备的能力（如算术、翻译、推理），这被称为**涌现能力（Emergent Abilities）**。
- **Codex**（2021）：基于 GPT-3 在代码数据上微调，成为 GitHub Copilot 的基础。
- **InstructGPT**（2022）：引入 **RLHF（基于人类反馈的强化学习）**，让模型从"文本补全"变成"遵循指令"。

### 2022-2023：ChatGPT 时刻

- **ChatGPT**（2022.11）：基于 GPT-3.5 + RLHF + 对话微调，实现了自然的多轮对话，引爆了全球关注。
- **GPT-4**（2023.3）：多模态（支持图片输入），推理能力大幅提升。

这个阶段确立了现代 LLM 的三步训练流程：**预训练 → 指令微调（SFT）→ 人类对齐（RLHF）**，后续的文章会详细展开。

### 2023-2025：开源追赶 + Agent 兴起

- **Llama 系列**（Meta）让开源模型能力逐步逼近闭源
- **Qwen、DeepSeek** 等中国模型在中文和代码场景表现突出
- Agent 框架（LangChain、LangGraph）和协议（MCP、A2A）快速发展
- 多模态（文本 + 图片 + 语音 + 视频）成为标配

### 发展脉络总结

```
2017  Transformer 架构诞生
  ↓
2018  BERT（理解） + GPT-1（生成）
  ↓
2020  GPT-3 → 涌现能力 + 规模定律
  ↓
2022  InstructGPT → RLHF 对齐
  ↓
2022  ChatGPT → 对话式 AI 爆发
  ↓
2023  GPT-4 + 开源追赶（Llama / Qwen / DeepSeek）
  ↓
2024  Agent 框架 + MCP 协议 + 多模态
  ↓
2025  Agent 工程化、标准化（← 我们在这里）
```

## 参考链接

- [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762) — Transformer 原始论文
- [Wikipedia — Large Language Model](https://en.wikipedia.org/wiki/Large_language_model)
- [3Blue1Brown — But what is a GPT?](https://www.youtube.com/watch?v=wjZofJX0v4M) — 直观的视频讲解
- [Andrej Karpathy — State of GPT](https://www.youtube.com/watch?v=bZQun8Y4L2A) — GPT 训练全流程概览
- [Scaling Laws for Neural Language Models (2020)](https://arxiv.org/abs/2001.08361) — 规模定律原始论文
