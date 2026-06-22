# 17 — IDE 集成层

## 核心问题
Claude Code 如何从 CLI 扩展到 IDE？Bridge 协议如何工作？

## 关键源码
- `src/bridge/` — 25+ 文件，IDE 桥接
- `src/bridge/bridgeMain.ts` — Bridge 主进程
- `src/bridge/bridgeProtocol.ts` — 协议定义
- `src/entrypoints/` — 多入口分发

## 主要内容

### 1. 多入口架构
```typescript
// 同一个 Agent 运行时，多个入口
src/entrypoints/
├── cli.tsx      — CLI 终端
├── init.ts      — 初始化
├── mcp.ts       — MCP 协议
├── sdk/         — SDK 调用
└── bridge/      — IDE 集成
```

### 2. Bridge 协议设计
```typescript
// WebSocket 双向通信
// 支持：
// - 消息传递
// - 文件操作
// - 状态同步
// - 远程执行
```

### 3. IDE 桥接场景
| 场景 | 实现 |
|------|------|
| VS Code 插件 | Bridge 协议 + WebSocket |
| JetBrains 插件 | Bridge 协议 + HTTP |
| 远程开发 | Bridge + SSH 隧道 |
| Web IDE | Bridge + HTTP API |

### 4. 状态同步机制
```typescript
// IDE 端状态 ↔ Claude Code 状态
// 实时同步：
// - 当前文件
// - 光标位置
// - 选中文本
// - 错误信息
```

### 5. 远程会话
```typescript
// 支持远程执行
// 桌面端 ↔ 远程服务器
// WebSocket 会话桥接
// 断线重连
```

### 6. 平台化设计
```typescript
// 从 CLI 工具到平台
// 同一个 Agent 运行时
// 服务：CLI / MCP / SDK / IDE
// 前端变化不污染核心逻辑
```

## 学习目标
- 理解多入口架构的设计
- 掌握 Bridge 协议的工程意义
- 明白从 CLI 到平台的演进
