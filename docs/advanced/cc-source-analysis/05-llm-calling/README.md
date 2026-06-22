# 05 — LLM 调用层

`services/api/claude.ts` 是 Claude Code 的 LLM 统一调用层。它负责流式调用、重试、多模型路由、Fallback 切换，以及最关键的——保护 50-70K token 的 Prompt Cache。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [callModel 架构](./01-callmodel.md) | 统一调用层、SSE 流式、重试策略、Token 追踪 |
| 02 | [Sticky-on Latch](./02-sticky-latch.md) | Prompt Cache 的 7 个维度、缓存失效成本、Latch 保护机制 |
| 03 | [Fallback 与多模型路由](./03-fallback.md) | `FallbackTriggeredError`、模型切换、清除 thinking 签名 |

> 学完本章后，请继续阅读 [06 — 系统提示词](../06-system-prompt-engineering/README.md)，看 53KB 提示词如何动态拼装。
