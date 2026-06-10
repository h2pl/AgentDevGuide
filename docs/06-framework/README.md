# 06 — 框架与编排

> 依赖：04 · 预计：4-5 天

## 学习目标

- 理解框架选型：Provider SDK vs LangGraph vs 自建
- 掌握 LangGraph 状态图、节点、条件路由
- 实现状态持久化和 Human-in-the-loop

## 内容大纲

<!-- TODO -->

## 动手练习

用 LangGraph 重构第 04 章的最小 Agent：
- 定义状态图和条件路由
- 实现 checkpoint 持久化（中断后可恢复）
- 加入 Human-in-the-loop 审批节点

## 推荐阅读

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph — How-to Guides](https://langchain-ai.github.io/langgraph/how-tos/)

## 完成标志

- [ ] 能用 LangGraph 构建有状态的 Agent
- [ ] 实现了 checkpoint 持久化
- [ ] 实现了 Human-in-the-loop 审批节点
