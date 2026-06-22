# 01 — 整体架构

Claude Code 不是简单的 API 包装器，而是一个由 51 万行 TypeScript 构成的完整 Agent 操作系统。本章从代码规模、分层架构和横向对比三个角度，建立对 Claude Code 的全局认知。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [51 万行的真相](./01-overview.md) | 源码泄露事件、1.6% AI 决策、代码分布、三种运行模式 |
| 02 | [五层架构](./02-five-layers.md) | CLI 入口层、Agent 循环层、工具执行层、权限控制层、系统提示层 |
| 03 | [三大框架对比](./03-comparison.md) | Claude Code vs Hermes vs OpenClaw，谁更值得学 |

> 学完本章后，请继续阅读 [02 — 启动流程](../02-startup-flow/README.md)，看 Claude Code 如何把冷启动压缩到 135ms。
