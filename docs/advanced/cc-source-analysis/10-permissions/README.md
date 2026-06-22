# 10 — 权限系统

## 核心问题
Claude Code 的 7 种权限模式如何工作？ML 分类器如何自动判断安全性？

## 关键源码
- `src/utils/permissions/permissions.ts` — 权限决策管道
- `src/utils/permissions/permissionRules.ts` — 规则定义
- `src/utils/permissions/dangerousPatterns.ts` — 危险模式检测
- `src/utils/permissions/mlClassifier.ts` — ML 分类器

## 主要内容

### 1. 三层防护结构
| 层次 | 机制 | 作用 |
|------|------|------|
| 第 1 层 | 工具注册过滤 | 被禁的工具从模型视野移除 |
| 第 2 层 | 单次调用检查 | 根据工具名、参数、工作目录验证 |
| 第 3 层 | 交互式询问 | 无匹配规则时实时问用户 |

### 2. 7 种运行模式
| 模式 | 特点 | 适用场景 |
|------|------|---------|
| default | 只对高风险操作询问 | 日常使用 |
| auto | ML 分类器自动判断 | 信任环境 |
| plan | 只读，不执行 | 方案评审 |
| bypassPermissions | 完全信任 | 沙箱环境 |
| denyAll | 全部拒绝 | 安全审计 |
| askAll | 全部询问 | 学习模式 |
| custom | 自定义规则 | 高级用户 |

### 3. 8 级规则优先级
```
Policy → User → Project → Local → CLI flag → cliArg → command → session
```
- 设计哲学：安全不应该是粗暴的全部拦截
- 精确地只拦那些真正需要人判断的操作

### 4. ML 分类器（auto 模式）
```typescript
// 训练数据：历史审批记录
// 特征：工具名、参数、工作目录、文件类型
// 输出：allow / deny / ask
// 用户 93% 的审批通过率不是取消审批的理由
// 而是引入沙箱让 Agent 在边界内自由运作
```

### 5. 23 项 Bash 安全检查
```typescript
// 危险命令检测
- rm -rf /
- chmod 777
- curl | sh
- 管道注入
- 环境变量泄露
// 18 个被屏蔽的 Zsh 内建命令
```

### 6. Permission Hook 注入点
```typescript
// PreToolUse：工具执行前
// PostToolUse：工具执行后
// 可以修改输入、阻断执行、记录审计
```

## 学习目标
- 理解三层防护的设计
- 掌握 7 种模式的适用场景
- 明白 ML 分类器的工程意义
