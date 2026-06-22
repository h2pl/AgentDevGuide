# Claude Code 源码解析 — 从理论到生产级 Agent

Claude Code 是 Anthropic 官方的终端 AI 编码助手，也是目前最成熟的零框架 Agent 实现之一。它不依赖 LangChain、LangGraph 等任何 Agent 框架，用纯 TypeScript 手写全部核心链路，代码量超过 10 万行。

本栏目逐模块拆解 Claude Code 的核心源码，每个模块对应核心 16 章的一个理论概念——不是"它做了什么"，而是"它为什么这样做"以及"这个设计决策对应哪条架构原理"。

> 前置知识：本栏目假设你已完成核心 16 章的学习。每篇文章会回溯到对应章节的理论基础。
>
> 源码版本：基于 `E:/Projects/claude-code/` 本地源码，版本随更新同步。

## 文章索引

| 篇号 | CC 模块 | 对应理论章节 | 核心问题 |
|------|---------|-------------|----------|
| 01 | query.ts | Ch06 Agent循环 | 600 行 while True 怎么运转？turn 计数、stop_reason、并发工具执行 |
| 02 | Tool.ts | Ch05 工具调用 | buildTool 工厂模式、Schema 自动生成、权限回调 |
| 03 | services/api/ | Ch03 模型接入 | 统一调用封装、重试机制、token 用量追踪 |
| 04 | system prompt | Ch04 Prompt工程 | 提示组装流程、前缀缓存冻结策略 |
| 05 | services/compact/ | Ch07 上下文工程 | 三级压缩策略、首尾保留+中间摘要 |
| 06 | memdir/ | Ch09 记忆管理 | 文件级持久记忆、反思提炼机制 |
| 07 | AgentTool/ | Ch12 多Agent | 子 Agent 上下文隔离、消息路由 |
| 08 | utils/permissions/ | Ch15 安全 | 分级权限模型、危险模式拦截 |
| 09 | utils/telemetry/ | Ch14 可观测 | Span 树结构、成本累计追踪 |
