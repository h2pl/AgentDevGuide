# 08 — 上下文工程

上下文窗口是 Agent 最昂贵的资源。学会装配、压缩和预算上下文，让你的 Agent 又快又准又省钱。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [上下文窗口：Agent 的瓶颈资源](./01-context-window-bottleneck.md) | 上下文窗口的本质限制、"迷失在中间"现象、信息优先级设计 |
| 02 | [上下文压缩策略](./02-context-compression.md) | 摘要压缩、Token 裁剪、滑动窗口、选择性注入 |
| 03 | [Token 预算与成本控制](./03-token-budget-cost.md) | Prompt Caching、KV Cache、上下文预算分配、成本优化实战 |
| 04 | [上下文卸载与隔离](./04-context-offloading-isolation.md) | 文件系统当无限记忆、可逆压缩、分层工具空间、主子 Agent 隔离 |
| 05 | [上下文失败模式与反模式](./05-context-failure-patterns.md) | 四种失效模式深度分析、七个常见反模式、不同规模工程路线图 |

> 学完本章后，请继续阅读 [09 — 框架与编排](../09-framework/README.md)，用 LangGraph 等框架管理复杂的 Agent 流程。
