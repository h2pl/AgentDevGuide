# 02 — 多模态视觉：图像、视频与文档

视觉是最成熟、用得最多的多模态能力。本章从通用图像理解出发，逐步扩展到视频时序分析和文档/图表解析，覆盖视觉理解的三大应用方向。

## 学习路径

本章六篇文章按"静态→动态→结构化→实战→场景→成本"的顺序展开。

### 1. 通用视觉理解

[视觉理解](./01-vision-understanding.md) 覆盖最基础的能力：图像分析 API 接入、视频帧提取、图像 token 成本优化。这是所有视觉应用的起点。

### 2. 视频理解

[视频理解](./02-video-understanding.md) 进入时间维度：帧采样策略、长视频处理、时序推理。视频不是"很多张图片"——时间维度的信息让理解变得完全不同。

### 3. 文档与图表理解

[文档与图表理解](./03-document-understanding.md) 聚焦最实用的场景：PDF 解析、复杂表格提取、图表数据解读。这是 Agent 处理真实世界文档的核心能力。

### 4. 实战指南

[实战指南](./04-practical-guide.md) 回答三个问题：怎么选模型、怎么设计工作流、怎么排查故障。从场景判断到 Prompt 优化到监控告警的完整落地指南。

### 5. Agent 场景

[Agent 场景](./05-agent-scenarios.md) 聚焦四个已经产品化的视觉 Agent 场景：屏幕操作 Agent、文档处理 Agent、视觉 QA Agent 和多模态 RAG Agent，给出每个场景的架构模式、模型选型和实测数据。

### 6. 成本优化

[成本优化](./06-cost-optimization.md) 系统性分析多模态视觉的成本构成和优化策略：分辨率与细节模式、缓存策略、Batch API + 模型混用、视频专项优化，以及各场景的优化前后成本对比。

## 文章总览

| 文章 | 内容 |
|------|------|
| [视觉理解](./01-vision-understanding.md) | 图像分析 API、视频帧提取、图像 token 成本优化 |
| [视频理解](./02-video-understanding.md) | 帧采样策略、长视频处理、时序推理、模型能力对比 |
| [文档与图表理解](./03-document-understanding.md) | PDF 解析、版面分析、表格提取、图表解读、方案选型 |
| [实战指南](./04-practical-guide.md) | 场景判断、模型选型决策树、工作流设计、质量调优与排障 |
| [Agent 场景](./05-agent-scenarios.md) | 屏幕 Agent、文档处理 Agent、视觉 QA、多模态 RAG |
| [成本优化](./06-cost-optimization.md) | 分辨率模式、缓存策略、Batch API、模型混用、视频专项优化 |

> 上一章：[01 — 多模态基础](../01-multimodal-fundamentals/README.md) —— 认知与机制基础
>
> 下一章：[03 — 语音与音频](../03-multimodal-speech/README.md) —— 进入听觉维度。
