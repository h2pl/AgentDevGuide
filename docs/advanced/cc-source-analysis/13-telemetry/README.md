# 13 — 可观测性

Claude Code 的可观测性不是事后调试，而是设计时就考虑进去的。本章拆解三层 Sink、类型级数据治理和 Datadog 上报。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [三层 Sink](./01-three-sinks.md) | L1 Analytics、L2 Debug、L3 Telemetry 的分工 |
| 02 | [类型级数据治理](./02-type-governance.md) | `AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS` 等字段命名背后的契约 |
| 03 | [Datadog 与调试](./03-datadog.md) | 生产环境数据上报、调试工具、性能分析 |

> 学完本章后，请继续阅读 [14 — 设计哲学](../14-design-philosophy/README.md)，看 Claude Code 的工程价值观。
