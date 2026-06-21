# 进阶扩展 — 多模态 AI 系统化讲解

核心 16 章覆盖了 Agent 开发的完整知识栈：从 LLM 基础到工具调用，从 RAG 到多 Agent 协作，从评测到生产交付。但 AI 的世界不止于文本——2026 年的前沿模型已经能同时处理图像、语音、视频等多种模态。

本栏目从多模态的基本概念出发，按照"认知→感知→创造→综合"的递进逻辑，分 4 章系统讲清楚多模态 AI 的全貌。无论你是想让 Agent 看懂截图、听懂语音、还是生成图像，这里都能帮你建立完整的理解。

> 前置知识：本栏目假设你已完成核心 16 章的学习，尤其是 [02 LLM 基础](../02-llm-basics/README.md)、[05 工具调用](../05-tool-use/README.md)、[08 RAG](../08-rag-pipeline/README.md) 和 [09 记忆管理](../09-memory-management/README.md)。

## 章节导航

| 阶段 | 章节 | 核心问题 |
|------|------|----------|
| 认知与机制 | [01 多模态基础](./01-multimodal-fundamentals/README.md) | 多模态是什么？模型内部怎么处理不同模态的信息？ |
| 感知能力 | [02 多模态理解](./02-multimodal-understanding/README.md) | 怎么让模型看懂图片、听懂语音？ |
| 创造能力 | [03 多模态生成](./03-multimodal-generation/README.md) | 怎么让模型生成图像和视频？ |
| 综合与交付 | [04 多模态推理与工程](./04-multimodal-reasoning/README.md) | 多模态综合推理怎么做？从 demo 到生产要补什么？ |

## 两条技术路线

多模态 AI 不是"一套统一技术"，而是两条截然不同的技术路线的结合：

- **理解侧**（Transformer 体系）：让模型"看懂"和"听懂"——输入图像/音频，输出文字/结构化信息
- **生成侧**（扩散模型体系）：让模型"创造"——输入文字描述，输出图像/视频

两条路线的架构、训练方式、推理过程和成本结构完全不同。第 1 章会详细拆解这个区分，后续章节分别深入。

## 文章索引

| 章节 | 文章 | 内容 |
|------|------|------|
| 01 多模态基础 | [多模态 AI 全景](./01-multimodal-fundamentals/01-multimodal-landscape.md) | 什么是多模态、模态异质性、2026 模型全景、模态组合速查 |
| | [多模态核心机制](./01-multimodal-fundamentals/02-core-mechanisms.md) | 理解 vs 生成两条路线、编码、融合、对齐 |
| 02 多模态理解 | [视觉理解](./02-multimodal-understanding/01-vision-understanding.md) | 图像/视频理解 API、Computer Use、视觉 RAG、成本优化 |
| | [语音与音频](./02-multimodal-understanding/02-speech-and-audio.md) | STT/TTS、Realtime API、语音 Agent 循环、中断处理 |
| 03 多模态生成 | [图像与视频生成](./03-multimodal-generation/01-image-and-video-generation.md) | 扩散模型机制、API 对比、条件引导、视频生成、Prompt 策略 |
| 04 推理与工程 | [多模态推理](./04-multimodal-reasoning/01-cross-modal-reasoning.md) | 跨模态推理、能力边界、多步推理链、多模态记忆 |
| | [多模态工程实践](./04-multimodal-reasoning/02-multimodal-in-production.md) | 评估指标、成本模型、可观测性、安全治理、上线 checklist |
