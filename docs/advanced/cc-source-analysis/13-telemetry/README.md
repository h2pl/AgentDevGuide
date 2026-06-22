# 13 — 可观测性

## 核心问题
Claude Code 的三层可观测体系如何工作？类型级数据治理是什么？

## 关键源码
- `src/services/analytics/index.ts` (158 行) — 追踪入口
- `src/services/analytics/sink.ts` (100 行) — 数据上报
- `src/services/analytics/events.ts` — 事件定义
- `src/services/analytics/types.ts` — 类型定义

## 主要内容

### 1. 三层可观测体系
| 层次 | 用途 | 后端 |
|------|------|------|
| L1 Analytics Events | 产品分析、用户行为 | Datadog |
| L2 Debug Logs | 调试日志 | 本地文件 |
| L3 Telemetry | 性能指标 | 遥测服务 |

### 2. L1 Analytics Events
```typescript
// 代码任意位置调用
logEvent("tengu_tool_use", {...});
// 经过事件队列 + Sink 路由
// 分别发送到两个后端：
// - Datadog：采样后的事件
// - 内部分析：完整事件
```

### 3. 类型级数据治理
```typescript
// AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS
// 这个类型名本身就是一个契约
// 要往遥测里发的每个字符串都必须被开发者手动确认
// 不包含代码/路径
// 编译期强制执行
// 把数据治理规则编码进了类型系统
```

### 4. Span 树追踪
```typescript
// 类似 OpenTelemetry 的 Span 概念
// 每个工具调用是一个 Span
// 可以追踪：
// - 调用耗时
// - Token 用量
// - 成本
// - 错误率
```

### 5. 成本追踪
```typescript
// 实时追踪：
// - totalCostUSD
// - modelUsage
// - totalAPIDuration
// 可以按会话、按天、按项目统计
```

### 6. 可观测性的设计哲学
- 不是事后调试，是设计时考虑
- 类型安全 > 运行时检查
- 采样 > 全量（成本控制）

## 学习目标
- 理解三层可观测体系的设计
- 掌握类型级数据治理的工程意义
- 明白成本追踪的实现
