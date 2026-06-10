# 03 — 工具调用

> 依赖：02 · 预计：2-3 天

## 学习目标

- 理解 Function Calling 完整机制
- 掌握工具 schema 设计
- 处理工具执行的工程问题

## 内容大纲

<!-- TODO -->

## 动手练习

实现一个能调用多个工具的对话 demo：
- 至少 3 个工具（如搜索、计算器、天气查询）
- 工具 schema 设计清晰
- 包含超时和错误处理

## 推荐阅读

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)

## 完成标志

- [ ] 理解 Function Calling 的定义→选择→执行→回传流程
- [ ] 能设计好的工具 schema（参数描述影响模型选择准确率）
- [ ] 实现了多工具并行调用和错误处理
