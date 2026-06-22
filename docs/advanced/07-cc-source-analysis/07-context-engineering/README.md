# 07 — 上下文工程

CC 的上下文工程体系——五层压缩管线、compact.ts（1705 行）、autoCompact.ts（351 行）、microCompact.ts（530 行）与 prompt.ts（374 行）逐层分析。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [上下文工程源码分析](./01-context-engineering-source.md) | 五层压缩管线：自动触发、手动压缩、微压缩、摘要策略 |

## 涉及源码

- `services/compact/compact.ts`（1705 行）
- `services/compact/autoCompact.ts`（351 行）
- `services/compact/microCompact.ts`（530 行）
- `services/compact/prompt.ts`（374 行）

## 对应理论章节

> [07 — 上下文工程](../../../07-context-engineering/README.md) — 上下文窗口是最稀缺的资源，压缩是延长对话生命周期的关键。
