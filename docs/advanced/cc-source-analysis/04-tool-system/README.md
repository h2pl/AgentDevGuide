# 04 — 工具系统

Claude Code 内置 42 个工具，从文件读写到 Bash 执行，从子 Agent 到 MCP 扩展。本章拆解工具的接口设计、注册机制、执行 Pipeline 和并发调度策略。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [工具接口与注册](./01-tool-basics.md) | `Tool.ts` 接口、`tools.ts` 注册表、42 个工具分类 |
| 02 | [工具执行 Pipeline](./02-execution-pipeline.md) | 8 步执行流程、Pre/Post Hook、权限检查、结果组装 |
| 03 | [并发调度](./03-concurrency.md) | `isConcurrencySafe`、并行/串行策略、siblingAbortController |
| 04 | [关键工具实现](./04-key-tools.md) | BashTool、EditTool、AgentTool 的设计取舍 |

> 学完本章后，请继续阅读 [05 — LLM 调用层](../05-llm-calling/README.md)，看 Claude Code 如何统一管理模型调用。
