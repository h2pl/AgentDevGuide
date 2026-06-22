# 02 — 启动流程

从用户敲下 `claude` 到看到 REPL 界面，Claude Code 用 Fast-path 分发、并行预取、延迟初始化等手段，把冷启动压缩到约 135ms。本章拆解启动的五个阶段。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [启动入口](./01-entry.md) | `cli.tsx` Fast-path 分发、子命令按需加载 |
| 02 | [启动优化](./02-optimization.md) | MDM/Keychain 并行预取、API 预连接、延迟初始化 |
| 03 | [初始化与 REPL](./03-initialization.md) | Commander 参数解析、`init.ts`、Sticky-on Latch、REPL 渲染 |

> 学完本章后，请继续阅读 [03 — Agent 循环](../03-agent-loop/README.md)，进入 Claude Code 最核心的 while 循环。
