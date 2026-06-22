# 08 — 记忆系统

## 核心问题
Claude Code 如何实现跨会话记忆？autoDream 反思系统如何工作？KAIROS 守护进程是什么？

## 关键源码
- `src/memdir/memdir.ts` (471 行) — 记忆持久化
- `src/memdir/findRelevantMemories.ts` (128 行) — 记忆检索
- `src/memdir/memoryAge.ts` — 记忆老化
- `src/memdir/memoryScan.ts` — 记忆扫描
- `src/memdir/memoryTypes.ts` — 记忆类型
- `src/services/autoDream/autoDream.ts` — Dream 反思系统

## 主要内容

### 1. 三层渐进式记忆管线
| 层次 | 机制 | 特点 |
|------|------|------|
| Auto Memory Extraction | 实时提取 | 主对话中自动提取关键信息 |
| Session Memory | 会话级 | 单次会话内的短期记忆 |
| Auto Dream | 跨会话 | 后台 forked agent 整合长期记忆 |

### 2. memdir 文件级持久化
```typescript
// 记忆存储在 ~/.claude/memories/ 目录
// 每个项目一个文件
// 格式：Markdown，人类可读
// 版本可控（可以 git 管理）
```

### 3. autoDream 反思系统
```typescript
// 后台 forked agent 模式
// 不阻塞主对话
// 定期整合短期记忆为长期知识
// 用便宜模型做筛选
```

### 4. KAIROS 守护进程（隐藏功能）
```typescript
// 持久助手模式
// 永不睡觉的后台进程
// 持续监控项目变化
// 主动提供建议
```

### 5. 记忆预取的精妙设计
```typescript
// using 声明（TypeScript 5.2 Explicit Resource Management）
using pendingMemoryPrefetch = startRelevantMemoryPrefetch(messages, ...);
// generator 在任何退出路径都会触发 dispose
// 预取在第一次调用时启动
// 在工具执行完成后消费——完美隐藏在工具执行的 5-30 秒里
```

### 6. 新鲜度管理
```typescript
// 把时间问题变成数据问题
// 每条记忆带时间戳
// 老化的记忆权重降低
// 定期清理过期记忆
```

### 7. 安全：记忆路径不可信
- 记忆文件可能被恶意修改
- 加载时需要校验
- 防止 prompt injection

## 学习目标
- 理解三层记忆管线的设计
- 掌握 autoDream 的工程意义
- 明白 KAIROS 的隐藏功能
