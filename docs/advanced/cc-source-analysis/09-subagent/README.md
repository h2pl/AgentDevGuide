# 09 — 子 Agent

当任务过于复杂时，Claude Code 会启动子 Agent 在隔离环境中执行。本章拆解 AgentTool 的架构、Git Worktree 隔离和 50:1 的上下文压缩比。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [AgentTool 架构](./01-agenttool.md) | fork/run/resume、子 Agent 生命周期、上下文隔离 |
| 02 | [Git Worktree 隔离](./02-worktree.md) | 工作目录隔离、状态不污染父进程 |
| 03 | [上下文压缩](./03-compression.md) | 100K+ token → 1-2K 摘要、Explore/Verification Agent |

> 学完本章后，请继续阅读 [10 — 权限系统](../10-permissions/README.md)，看 Claude Code 如何控制子 Agent 的操作边界。
