# 07 — 上下文工程

200K 的上下文窗口听着很大，但复杂的多文件调试 session 很快就能填满。Claude Code 设计了 5 层渐进式压缩机制，从便宜到贵依次触发，92% 的情况在低层就能解决。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [五层压缩概览](./01-five-layers.md) | Budget reduction、snip、microcompact、contextCollapse、autocompact |
| 02 | [自动压缩](./02-autocompact.md) | 触发阈值、CLAUDE.md 永不删除、熔断机制 |
| 03 | [微压缩与折叠](./03-micro-collapse.md) | microcompact 按 tool_use_id 压缩、contextCollapse 归档摘要 |
| 04 | [预算与熔断](./04-budget.md) | Token 预算分配、MAX_CONSECUTIVE_FAILURES=3、成本控制 |

> 学完本章后，请继续阅读 [08 — 记忆系统](../08-memory/README.md)，看 Claude Code 如何实现跨会话记忆。
