# 10 — 评测与可观测

> 依赖：06 · 预计：3-4 天

## 学习目标

- 设计 Agent 评测集
- 实现全链路 Trace
- 掌握 LLM-as-Judge 方法

## 内容大纲

<!-- TODO -->

## 动手练习

为之前构建的 Agent 搭建评测和可观测体系：
- 构建 20+ 条评测用例
- 接入 Trace 系统（如 LangSmith / Langfuse）
- 实现 LLM-as-Judge 自动评分

## 推荐阅读

- [Anthropic — Evaluating AI Agents](https://www.anthropic.com/engineering/evaluating-ai-agents)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Langfuse](https://langfuse.com/docs)

## 完成标志

- [ ] 构建了评测集并能跑通自动评测
- [ ] 接入了 Trace 系统，能追踪每一步决策
- [ ] 能通过 Trace 定位失败原因（prompt / 工具 / 检索 / 模型）
