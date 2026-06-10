# 01 — 模型接入

> 依赖：00 · 预计：2-3 天

## 学习目标

- 理解 Transformer 核心概念（注意力、token、context window）
- 掌握 LLM API 调用：同步、流式、多模型切换
- 了解模型选型与关键参数

## 内容大纲

<!-- TODO -->

## 动手练习

实现一个支持多模型切换的对话服务，要求：
- 支持至少 2 个模型（如 OpenAI + Qwen）
- 支持流式输出
- 包含错误重试和降级策略

## 推荐阅读

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Reference](https://docs.anthropic.com/en/api)

## 完成标志

- [ ] 能用代码调通至少 2 个模型的 API
- [ ] 理解 temperature / top_p / max_tokens 对输出的影响
- [ ] 实现了流式输出和错误重试
