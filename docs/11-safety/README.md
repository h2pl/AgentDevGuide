# 11 — 安全与治理

> 依赖：06 · 预计：2-3 天

## 学习目标

- 理解 Prompt 注入攻击与防御
- 实现工具级别权限控制
- 掌握沙箱执行和审计

## 内容大纲

<!-- TODO -->

## 动手练习

对之前构建的 Agent 进行安全加固：
- 实现 Prompt 注入检测
- 为工具调用添加权限分级
- 危险操作（如文件删除）强制人类审批

## 推荐阅读

- [OWASP — LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP — MCP Top 10 (Beta)](https://genai.owasp.org/resource/mcp-top-10/)

## 完成标志

- [ ] 能演示至少一种 Prompt 注入攻击并防御
- [ ] 实现了工具调用的权限分级
- [ ] 危险操作有人类审批机制
