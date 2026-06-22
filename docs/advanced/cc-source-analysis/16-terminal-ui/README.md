# 16 — 终端 UI 框架

Claude Code 不是输出纯文本，而是用 React + 自研 Ink 框架渲染完整的终端 UI。本章拆解 Ink 渲染器和组件树。

## 目录

| # | 文章 | 内容 |
|---|------|------|
| 01 | [Ink 渲染器](./01-ink.md) | `src/ink/` 自研终端渲染器、diff 更新、焦点管理 |
| 02 | [组件树与交互](./02-components.md) | React 组件分层、输入处理、动画与状态同步 |

> 学完本章后，请继续阅读 [17 — IDE 集成层](../17-ide-integration/README.md)，看 Bridge 协议如何连接 IDE。
