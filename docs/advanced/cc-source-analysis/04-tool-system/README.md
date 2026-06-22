# 04 — 工具系统

## 核心问题
Claude Code 的 40+ 工具如何统一注册、按需加载？工具执行 Pipeline 有哪些步骤？

## 关键源码
- `src/Tool.ts` (792 行) — 工具基类
- `src/tools.ts` (373 行) — 工具注册表
- `src/tools/` — 40+ 工具实现
- `src/services/tools/toolExecution.ts` (1745 行) — 执行流水线
- `src/services/tools/StreamingToolExecutor.ts` (530 行) — 并发调度

## 主要内容

### 1. Tool 接口设计
```typescript
interface Tool {
  name: string;
  inputSchema: ZodSchema;
  call(input, context): Promise<ToolResult>;
  
  // 元数据
  prompt(): string;              // 向模型描述自己
  isReadOnly(): boolean;         // 是否只读
  isConcurrencySafe(): boolean;  // 能否并发
  isDestructive(): boolean;      // 是否有破坏性
  
  // UI 渲染
  renderToolUseMessage(): ReactNode;
  renderToolResultMessage(): ReactNode;
  
  // 权限
  checkPermissions(): PermissionResult;
}
```

### 2. 42 个工具分类
| 类别 | 工具 | 数量 |
|------|------|------|
| 核心工具 | Bash, FileRead, FileWrite, FileEdit, Glob, Grep | 6 |
| 搜索与网络 | WebFetch, WebSearch | 2 |
| 子 Agent | AgentTool, ExploreAgent, VerificationAgent | 3 |
| 任务管理 | TaskCreate, TaskUpdate, TaskList | 3 |
| MCP 工具 | 动态加载 | N |
| 其他 | TodoWrite, AskUserQuestion, EnterPlanMode... | 28 |

### 3. 工具执行 Pipeline（8 步）
1. **Zod 输入校验** — 运行时类型检查
2. **tool.validateInput()** — 业务逻辑校验
3. **runPreToolUseHooks()** — PreToolUse 钩子（可修改输入或阻断）
4. **resolveHookPermissionDecision()** — 合并 Hook 和权限决策
5. **canUseTool()** — 权限检查
6. **tool.call()** — 执行工具
7. **runPostToolUseHooks()** — PostToolUse 钩子
8. **createToolResultMessage()** — 组装结果消息

### 4. 并发调度策略
| 工具类型 | isConcurrencySafe | 原因 |
|---------|-------------------|------|
| Read | true | 只读，不修改状态 |
| Glob / Grep | true | 只读搜索 |
| Write / Edit | false | 写入文件，需串行 |
| Bash | false | 执行命令，需串行 |

### 5. 错误级联取消
- siblingAbortController：一个 Bash 出错，abort 所有兄弟进程
- 但不触发父控制器，不会终止整个 turn

## 学习目标
- 理解 Tool 接口的完整设计
- 掌握 8 步执行 Pipeline
- 明白并发调度的工程意义
