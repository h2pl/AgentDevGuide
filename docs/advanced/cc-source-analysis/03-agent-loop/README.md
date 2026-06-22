# 03 — Agent 循环

Agent 循环是 Claude Code 的心脏。`query.ts` 用 1612 行代码包裹了一个 88 行的 while 循环，处理输出截断、上下文溢出、工具失败等边界情况，让模型驱动的循环能在生产环境里稳定运行。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [Agent 循环](./01-loop.md) | while 循环本质、State 状态机、Withholding、7 种 continue reason |
| 02 | [消息预处理流水线](./02-preprocessing.md) | applyToolResultBudget、snip、microcompact、contextCollapse、autocompact |
| 03 | [StreamingToolExecutor](./03-streaming-executor.md) | 并发调度、siblingAbortController、错误级联取消 |

> 学完本章后，请继续阅读 [04 — 工具系统](../04-tool-system/README.md)，看 42 个工具如何统一注册和调度。
