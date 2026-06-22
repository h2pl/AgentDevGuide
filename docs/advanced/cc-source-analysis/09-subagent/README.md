# 09 — 子 Agent

## 核心问题
Claude Code 的子 Agent 如何隔离上下文？50:1 压缩比如何实现？

## 关键源码
- `src/tools/AgentTool/AgentTool.tsx` (1320 行) — 核心调度
- `src/tools/AgentTool/UI.tsx` — UI 渲染
- `src/tools/AgentTool/prompt.ts` — 子 Agent 提示词
- `src/utils/forkedAgent.ts` — fork 机制
- `src/tools/AgentTool/forkSubagent.ts` — fork 子流程
- `src/tools/AgentTool/runAgent.ts` (973 行) — 运行时

## 主要内容

### 1. 为什么需要多个 Agent
- 主 Agent 上下文有限（200K token）
- 复杂任务需要并行探索
- 避免上下文污染

### 2. 三种子 Agent 角色
| 角色 | 用途 | 特点 |
|------|------|------|
| Explore Agent | 只读探索 | 裁剪出来的只读专家 |
| Verification Agent | 验证代码 | 整个系统里最狠的 prompt |
| Worker Agent | 执行任务 | Coordinator 模式下的工作者 |

### 3. Git Worktree 隔离
```typescript
// 每个 subagent 跑在独立的 git worktree 里
// 文件系统隔离，上下文隔离
// 不会互相污染
// 可以并行执行
```

### 4. 50:1 压缩比
```typescript
// subagent 内部可能消耗 100K+ token
// 但返回给父 agent 的只是 1,000-2,000 token 的摘要
// 压缩比约 50:1
// 父 agent 的上下文不会被撑爆
```

### 5. Fork path 的 cache 优化
```typescript
// forkSubagent.ts 显式化 prompt cache 设计
// 子 Agent 继承父 Agent 的 cache-safe params
// 提升并行调用的缓存命中率
```

### 6. runAgent.ts 完整运行时
```typescript
// 子 Agent 的完整生命周期
1. 创建独立 worktree
2. 初始化独立上下文
3. 执行任务（可能多轮）
4. 生成摘要
5. 清理 worktree
6. 返回摘要给父 Agent
```

### 7. 任务系统
```typescript
// TaskCreate/TaskUpdate/TaskList
// 多步骤任务可视化推进
// 子 Agent 可以更新任务状态
```

## 学习目标
- 理解 Git Worktree 隔离的设计
- 掌握 50:1 压缩比的工程意义
- 明白三种子 Agent 的职责划分
