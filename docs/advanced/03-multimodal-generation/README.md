# 03 — 多模态生成：创造能力

本章从"感知"翻转到"创造"——让模型生成图像和视频。和理解侧是完全不同的技术路线（扩散模型），需要单独建立认知。

## 学习路径

本章一篇长文系统覆盖生成侧的全部内容。

### 图像与视频生成

[图像与视频生成](./01-image-and-video-generation.md) 先讲清楚生成侧和理解侧的根本区别（Transformer vs 扩散模型），再从 API 接入、生成侧核心机制（VAE、去噪网络、文本编码器、采样算法）、条件引导、ControlNet，一路讲到视频生成、Prompt 策略和质量评估。

## 文章总览

| 文章 | 内容 |
|------|------|
| [图像与视频生成](./01-image-and-video-generation.md) | 生成侧完整机制（VAE / UNet / DiT / 采样算法）、API 对比、条件引导、视频生成、Prompt 策略 |

> 上一章：[02 — 多模态理解](../02-multimodal-understanding/README.md) —— 感知能力（视觉 + 语音）
>
> 下一章：[04 — 多模态推理与工程](../04-multimodal-reasoning/README.md) —— 把各模态串起来做协同推理，以及从 demo 到生产的工程实践。
