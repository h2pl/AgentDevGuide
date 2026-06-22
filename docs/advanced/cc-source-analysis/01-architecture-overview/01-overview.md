# 01 — 整体架构

## 导读

Claude Code 是 Anthropic 开发的 AI 编程助手，2026 年 3 月因 npm 包的 source map 配置失误，51 万行 TypeScript 源码意外泄露。这是目前最完整的商业级 AI Agent 架构实例。

读完本章，你将理解：
- Claude Code 不是"API 包装器"，而是完整的 Agent 操作系统
- 51 万行代码中，AI 决策逻辑只占 1.6%，其余 98.4% 是工程基础设施
- 五层架构的职责划分和模块依赖关系
- Kernel + Harness 设计哲学：模型负责思考，Harness 负责兜底

**TL;DR**：
1. Claude Code 的核心是一个 88 行的 while 循环，但包裹着 40 万行的工程基础设施
2. 五层架构：入口层 → Agent 循环层 → 工具执行层 → 权限控制层 → 系统提示层
3. 设计哲学：不信任模型的自觉性，用工程系统让 AI "不出事"

---

## 一、源码定位

### 1.1 关键文件路径

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/main.tsx` | 4683 | 主入口，启动编排 |
| `src/query.ts` | 1729 | Agent 循环核心 |
| `src/QueryEngine.ts` | 1295 | 查询引擎（Headless/SDK 模式） |
| `src/Tool.ts` | 792 | 工具基类定义 |
| `src/tools.ts` | 373 | 工具注册表 |
| `src/services/api/claude.ts` | 3212 | LLM 统一调用层 |
| `src/services/compact/compact.ts` | 1581 | 上下文压缩主逻辑 |
| `src/tools/AgentTool/AgentTool.tsx` | 1320 | 子 Agent 调度 |
| `src/memdir/memdir.ts` | 471 | 记忆持久化 |
| `src/utils/permissions/` | 22+ 文件 | 权限系统 |

### 1.2 代码规模分布

| 模块 | 文件数 | 代码行数 | 占比 | 职责 |
|------|--------|----------|------|------|
| 终端 UI | 389 | ~70,000 | 14% | React + Ink 渲染 |
| 工具系统 | 184 | ~29,000 | 6% | 40+ 工具实现 |
| 命令系统 | 207 | ~15,000 | 3% | 40+ slash 命令 |
| 权限安全 | - | ~60,000 | 12% | 多层权限检查 |
| Agent 核心 | - | ~8,000 | 1.6% | while 循环 + 工具调度 |
| 基础设施 | 564 | ~330,000 | 64% | 工具函数、类型定义 |

**关键洞察**：51 万行代码中，真正跟 AI 决策相关的只占 1.6%。剩下的 98.4% 全是工程基础设施：权限管理、上下文压缩、会话存储、工具调度。

这个比例本身就说明一个问题：做一个好用的 AI 编程工具，模型能力只是起点，真正的壁垒在工程。

### 1.3 架构位置

```
┌─────────────────────────────────────────┐
│         CLI 入口层 (entrypoints/)        │
│  cli.tsx → main.tsx → launchRepl()      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Agent 循环层 (query.ts)            │
│  while(true) { callModel → runTools }   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      工具执行层 (tools/)                │
│  Tool.ts → toolExecution.ts → 40+ 工具  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      权限控制层 (permissions/)          │
│  canUseTool() → 7 种模式 → ML 分类器    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      系统提示层 (prompts.ts)            │
│  53KB 动态提示词 + 缓存冻结             │
└─────────────────────────────────────────┘
```

---

## 二、核心实现剖析

### 2.1 Kernel + Harness 架构

Claude Code 的核心，说出来可能让人意外，就是一个 while 循环：

```typescript
// query.ts - 简化版
while (true) {
  // 1. 调用模型
  const response = await callModel(messages);
  
  // 2. 执行模型请求的工具
  if (response.tool_use) {
    const results = await runTools(response.tool_use);
    messages.push(...results);
  }
  
  // 3. 判断是否继续
  if (response.stop_reason === 'end_turn') {
    break;
  }
}
```

没有复杂的 planner，没有状态机，没有多步编排图。模型读上下文，决定下一步干什么，调工具，观察结果，继续走。整个过程是完全由模型驱动的，它自己决定什么时候停下来，什么时候再跑一轮。

研究者把这叫 **Kernel + Harness 架构**：一个极薄的 AI 内核，包在一个很厚的确定性外壳里，所有工程复杂度都在循环外面，不在里面。

换句话说，Claude Code 不是靠精巧的编排逻辑让 AI "更聪明"，而是靠工程系统让 AI "不出事"。模型负责思考，Harness 负责兜底。这个分工清晰得让人意外。

### 2.2 五层架构详解

#### 第一层：CLI 入口层

```typescript
// main.tsx 前 20 行
import { profileCheckpoint } from './utils/startupProfiler.js';
profileCheckpoint('main_tsx_entry'); // 第一行开始计时

import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';
startMdmRawRead(); // 并行：MDM 配置子进程

import { startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';
startKeychainPrefetch(); // 并行：Keychain 预读（节省 65ms）
```

入口层的设计思路：**把昂贵的 I/O 操作提前到 import 阶段并行执行**。因为 Node/Bun 的 import 本身需要 ~135ms 来加载模块，这段时间正好可以用来做异步预热。

#### 第二层：Agent 循环层

```typescript
// query.ts - State 类型
type State = {
  messages: Message[]                    // 对话历史
  toolUseContext: ToolUseContext         // 工具执行上下文
  autoCompactTracking: ...               // 自动压缩追踪
  maxOutputTokensRecoveryCount: number   // 输出截断恢复计数 (≤3)
  hasAttemptedReactiveCompact: boolean   // 是否尝试过响应式压缩
  turnCount: number                      // 当前轮次
  transition: Continue | undefined       // 上次循环的继续原因
}
```

循环状态是一个可变对象，跨迭代携带。当 LLM 的输出因 `max_output_tokens` 被截断时，循环不会直接结束，而是自动续写，最多重试 3 次。这保证了长回答不会被意外切断。

#### 第三层：工具执行层

```typescript
// Tool.ts - 工具接口
interface Tool {
  name: string;
  inputSchema: ZodSchema;
  call(input, context): Promise<ToolResult>;
  
  // 元数据
  prompt(): string;              // 向模型描述自己
  isReadOnly(): boolean;         // 是否只读
  isConcurrencySafe(): boolean;  // 能否并发
  isDestructive(): boolean;      // 是否有破坏性
  
  // 权限
  checkPermissions(): PermissionResult;
}
```

工具不是简单的函数，而是带权限、描述、UI 的完整对象。每个工具都要告诉模型"我能做什么"，告诉权限系统"我有什么风险"，告诉 UI "我长什么样"。

#### 第四层：权限控制层

```typescript
// 三层防护结构
// 第 1 层：工具注册过滤
// 被禁的工具直接从模型视野里移除，模型连看都看不到

// 第 2 层：单次调用检查
// 每次工具调用都根据工具名、参数、工作目录做规则验证

// 第 3 层：交互式询问
// 没有匹配规则时实时问用户，用户的回答变成当前 session 的规则
```

7 种运行模式，从 default（只对高风险操作询问）到 auto（ML 分类器自动判断）到 bypassPermissions（完全信任，用于沙箱环境）。

8 级规则优先级：Policy → User → Project → Local → CLI flag → cliArg → command → session。

设计哲学是：安全不应该是粗暴的全部拦截，而是精确地只拦那些真正需要人判断的操作。

#### 第五层：系统提示层

```typescript
// 系统提示词 = 数百个碎片动态拼装
systemPrompt = [
  ...getBasePrompt(),           // 基础指令
  ...getSafetyRules(),          // 安全守则（~5677 token）
  ...getToolDescriptions(),     // 工具描述
  ...getProjectContext(),       // 项目上下文（CLAUDE.md）
  ...getModeSpecificRules(),    // 模式特定规则
  ...getUserPreferences(),      // 用户偏好
];
```

Claude Code 不是一个系统提示，而是数百个提示碎片在运行时动态拼装。根据模式、工具和上下文的不同，注入不同的提示片段。光是安全守则就有约 5,677 个 token——相当于两万字的行为规范，每次对话都带进去。

---

## 三、关键设计点

### 3.1 不信任模型的自觉性

Claude Code 的设计哲学第一条：**不信任模型的自觉性**。

模型只是一个文本生成器，它没有能力执行任何代码、读写任何文件。它的"指挥方式"非常简单：在生成的文本中嵌入一个结构化的指令，告诉运行时"我想用这个工具，参数是这些"。运行时识别出这个指令，执行工具，然后把结果喂回给模型。

这意味着：
- 模型不能直接访问文件系统
- 模型不能直接执行命令
- 模型不能直接修改状态
- 所有操作都要经过工具系统 + 权限检查

### 3.2 上下文是稀缺资源

200K 的上下文窗口听着很大，实际跑一个复杂的多文件调试 session，填满的速度比想象的快。

Claude Code 设计了 5 层压缩机制，从便宜到贵依次触发：

1. Budget reduction — 削减工具输出的预览长度
2. Snip — 删掉会话前面已经没用的工具结果
3. Microcompact — 压缩特定段落
4. Context collapse — 把大段对话总结成摘要
5. Auto-compact — 全 session 总结，最后手段

系统在上下文用到 92% 的时候自动触发，从第 1 层开始往下试，能在便宜的层解决就不动贵的。

这个设计的好处是：大部分时候前两层就能腾出足够空间，不需要动到代价最大的全 session 总结。

### 3.3 安全层要互不绕过

权限系统的设计原则：**安全不应该是粗暴的全部拦截，而是精确地只拦那些真正需要人判断的操作**。

三层防护结构：
- 第 1 层（工具注册过滤）：被禁的工具直接从模型视野里移除
- 第 2 层（单次调用检查）：每次工具调用都做规则验证
- 第 3 层（交互式询问）：没有匹配规则时实时问用户

8 级规则优先级确保：全局策略 > 用户配置 > 项目配置 > 临时设置。

### 3.4 生态的关键是模型"感知到"自己的能力

4 种扩展机制：
- Hooks（零成本）— 事件触发的确定性脚本，模型完全不参与
- Skills（低成本）— 可复用的动作模板，模型按需调用
- Plugins（中成本）— 打包的工具集，有独立上下文
- MCP（高成本）— 完整的外部服务集成

不是所有事情都该用 MCP，确定性操作用 Hook，知识复用用 Skill，别什么都往 MCP 上堆。一个 MCP 服务的工具描述可能就占几千 token，接五六个 MCP 光工具列表就吃掉了你十分之一的上下文窗口。

正确的思路是：能用 Hook 解决的不用 Skill，能用 Skill 解决的不上 MCP，越轻量越好。

---

## 四、对比其他实现

### 4.1 vs Hermes

Hermes 是另一个开源 Agent 框架，核心差异：

| 维度 | Claude Code | Hermes |
|------|------------|--------|
| 架构 | Kernel + Harness | 状态机驱动 |
| 循环 | while(true) 简单循环 | 显式状态机 |
| 权限 | 三层防护 + ML 分类器 | 基于角色的访问控制 |
| 压缩 | 5 层渐进式 | 单层全量压缩 |
| 扩展 | 4 种机制 | MCP 为主 |

Hermes 的状态机更复杂，但 Claude Code 的简单循环 + 厚 Harness 更容易理解和调试。

### 4.2 vs OpenClaw

OpenClaw 是另一个商业级 Agent，核心差异：

| 维度 | Claude Code | OpenClaw |
|------|------------|----------|
| 语言 | TypeScript | Python |
| UI | React + Ink | 命令行 |
| 权限 | 7 种模式 + 8 级优先级 | 简单的 allow/deny |
| 记忆 | memdir + autoDream | 向量数据库 |
| 子 Agent | Git Worktree 隔离 | 进程隔离 |

OpenClaw 的 Python 生态更丰富，但 Claude Code 的 TypeScript 栈在终端 UI 和类型安全上更强。

### 4.3 vs LearnAgent 自建

LearnAgent 是我们自建的 Agent 系统，核心差异：

| 维度 | Claude Code | LearnAgent |
|------|------------|------------|
| 规模 | 51 万行 | ~4000 行 |
| 工具 | 40+ | 10+ |
| 权限 | 完整三层防护 | 简单的 allow/deny |
| 压缩 | 5 层渐进式 | 单层全量压缩 |
| 子 Agent | 支持 | 不支持 |

LearnAgent 是教学项目，聚焦核心概念，不追求生产级功能。

---

## 五、面试考点

### 5.1 高频问题

**Q1: Claude Code 的核心架构是什么？**

A: Kernel + Harness 架构。一个极薄的 AI 内核（88 行 while 循环），包在一个很厚的确定性外壳里（40 万行工程基础设施）。模型负责思考，Harness 负责兜底。

**Q2: 为什么 51 万行代码中 AI 决策逻辑只占 1.6%？**

A: 因为做一个好用的 AI 编程工具，模型能力只是起点，真正的壁垒在工程。权限管理、上下文压缩、会话存储、工具调度这些工程基础设施才是让 AI "不出事"的关键。

**Q3: Claude Code 的五层架构是什么？**

A: 
1. CLI 入口层：Commander.js + React/Ink
2. Agent 循环层：while(true) 状态机
3. 工具执行层：40+ 工具的注册与调度
4. 权限控制层：多层安全检查
5. 系统提示层：53KB 动态提示词构建

**Q4: 为什么用 while(true) 而不是状态机？**

A: 因为整个过程是完全由模型驱动的，它自己决定什么时候停下来，什么时候再跑一轮。简单的 while 循环 + 厚 Harness 更容易理解和调试，不需要显式的状态机。

**Q5: Claude Code 的权限系统如何设计？**

A: 三层防护结构：
- 第 1 层（工具注册过滤）：被禁的工具直接从模型视野里移除
- 第 2 层（单次调用检查）：每次工具调用都做规则验证
- 第 3 层（交互式询问）：没有匹配规则时实时问用户

7 种运行模式，8 级规则优先级。设计哲学是：安全不应该是粗暴的全部拦截，而是精确地只拦那些真正需要人判断的操作。

---

## 六、本章小结

### Takeaway

1. Claude Code 不是"API 包装器"，而是完整的 Agent 操作系统
2. 51 万行代码中，AI 决策逻辑只占 1.6%，其余 98.4% 是工程基础设施
3. Kernel + Harness 架构：模型负责思考，Harness 负责兜底

### 思考题

1. 为什么 Claude Code 选择 while(true) 而不是显式状态机？
2. 5 层压缩机制的设计哲学是什么？
3. 三层权限防护结构如何防止绕过？
4. 4 种扩展机制的成本差异是什么？
5. CLAUDE.md 为什么享有"永不删除"的特权？

---

## 参考资料

- [Claude Code 源码泄露分析](https://jingkaitang.github.io/writing/claude-code-source-code-leak/)
- [51 万行代码 AI 只占 1.6%](https://blog.csdn.net/wuShiJingZuo/article/details/160836992)
- [Claude Code 源码架构深度解析 V2.1](https://raw.githubusercontent.com/tvytlx/ai-agent-deep-dive/master/ai-agent-deep-dive-v2.1.pdf)
- [MBZUAI/UCL 论文：Dive into Claude Code](https://arxiv.org/abs/2604.14228)
