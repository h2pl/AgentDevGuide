# 12 — 会话持久化

Claude Code 需要支持数小时的长任务。本章拆解 append-only 状态存储、checkpoint 机制和 resume 流程。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [状态管理](./01-state.md) | `bootstrap/state.ts`、约 150 个字段、append-only 设计 |
| 02 | [Resume 机制](./02-resume.md) | checkpoint、会话恢复、`/resume` 命令 |

> 学完本章后，请继续阅读 [13 — 可观测性](../13-telemetry/README.md)，看 Claude Code 如何追踪运行状态。
