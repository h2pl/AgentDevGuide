# 08 — 记忆系统

Claude Code 的记忆系统分三层：会话内提取、session 级持久化、autoDream 后台反思。本章拆解 memdir 文件级存储、记忆检索和 KAIROS 守护进程。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [memdir 持久化](./01-memdir.md) | 文件级记忆、路径不可信校验、`using` 资源管理 |
| 02 | [记忆检索与 autoDream](./02-retrieval-dream.md) | `findRelevantMemories`、autoDream 反思、记忆注入扫描 |
| 03 | [KAIROS 守护进程](./03-kairos.md) | 后台记忆维护、记忆新鲜度、老化权重 |

> 学完本章后，请继续阅读 [09 — 子 Agent](../09-subagent/README.md)，看 AgentTool 如何隔离上下文。
