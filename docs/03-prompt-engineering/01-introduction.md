# Prompt 工程入门

> 什么是 Prompt？LLM 怎么处理它？三种消息角色各有什么作用？这篇文章建立你对 Prompt 工程的基础认知，后面四篇的所有技巧都建立在这里。

## 目录

- [什么是 Prompt](#什么是-prompt)
- [三种消息角色](#三种消息角色)
- [LLM 怎么处理 Prompt](#llm-怎么处理-prompt)
- [写好 Prompt 的基本原则](#写好-prompt-的基本原则)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。前面两章你搞懂了 LLM 能做什么、怎么调 API。现在进入一个更关键的问题：**怎么写指令，才能让模型按你的要求工作？**

这门技术叫 Prompt 工程。听起来像玄学，其实是一套系统化的方法论——后面四篇文章会逐一展开。但这篇先解决更基本的问题：Prompt 到底是什么，LLM 是怎么理解它的。

## 什么是 Prompt

**Prompt 就是你发给 LLM 的全部输入。** 在 API 调用中，它是 `messages` 列表里的每一条消息；在 ChatGPT 对话框里，它是你输入的那段文字加上系统预设的指令。

LLM 收到 Prompt 后做的事情很简单：**根据这段文字，预测最可能的下一个 Token，然后一个接一个地生成回答。** 它不理解你的"意图"，只做统计意义上的续写。所以 Prompt 的质量直接决定了输出质量——同样的模型，换一段 Prompt，输出可能天差地别。

```
用户看到的：  "帮我写一封拒绝邮件"    →    模型输出完整邮件
实际发生的：  [system + user messages] → Token by Token 概率续写
```

**Prompt 工程的本质**：通过精心设计输入，引导 LLM 的概率分布朝你想要的方向偏移。不是"求"模型做好，而是给它足够的信号让它"不得不"做好。

## 三种消息角色

调用 Chat Completions API 时，每条消息都有一个 `role`：

| 角色 | 谁写的 | 作用 | 模型权重 |
|------|-------|------|---------|
| **System** | 开发者 | 定义 Agent 的身份、规则、边界 | 最高——模型会优先遵循 |
| **User** | 终端用户 | 提问、下指令、提供上下文 | 中等——模型据此回答 |
| **Assistant** | 模型自己 | 历史回复，用于维持对话连贯性 | 参考——模型会保持风格一致 |

一个典型的 API 调用：

```json
{
  "messages": [
    {"role": "system", "content": "你是一个专业的客服助手，只回答与产品相关的问题。"},
    {"role": "user", "content": "你们的退货政策是什么？"},
    {"role": "assistant", "content": "我们支持 7 天无理由退货。"},
    {"role": "user", "content": "那帮我退一下昨天买的耳机"}
  ]
}
```

**关键认知**：

- **System Prompt 是你对模型施加的最强控制**——它像"宪法"，User Prompt 不能覆盖它（大多数情况下）
- **Assistant 消息不只是历史记录**——它同时是 Few-shot 示例的载体（后面会讲）
- **角色的顺序很重要**——System 在最前，User 和 Assistant 交替，模型对最近的消息关注度最高

## LLM 怎么处理 Prompt

理解 LLM 处理 Prompt 的方式，能帮你写出更有效的指令：

**1. 逐 Token 阅读**

模型不是"理解整段话再回答"，而是一个 Token 一个 Token 地处理。所以：
- 关键信息放在开头（System Prompt）或结尾（最近的 User 消息）——中间的长文本容易被"稀释"
- 避免在 Prompt 中间插入大量无关内容

**2. 注意力机制**

模型对 Prompt 中每个 Token 的关注程度不同：
- 开头和结尾的内容权重更高
- 重复出现的关键词权重更高
- 结构化内容（列表、标签、代码块）比散文更容易被精确遵循

**3. 上下文窗口是有限的**

所有消息加起来不能超过模型的上下文窗口（参考 [模型对比](../02-model-access/01-model-comparison.md) 中的上下文窗口对比）。超出部分会被截断，通常是丢掉最早的消息。这意味着：
- 对话越长，模型越容易"忘记"早期内容
- System Prompt 不会被截断（各平台都做了保护）
- 长文档要精简后再塞进 Prompt

## 写好 Prompt 的基本原则

在学具体技巧之前，先掌握这六条原则。后面四篇文章的所有技术，都是这些原则的具体实现：

**1. 明确具体**

```
❌ "帮我写点东西"
✅ "帮我写一封 200 字以内的邮件，拒绝供应商的报价，语气礼貌但坚定"
```

模型无法猜测你没说清楚的需求。字数、格式、语气、受众——越具体，输出越可控。

**2. 给上下文**

```
❌ "这个 bug 怎么修？"
✅ "Python 3.11 环境，FastAPI 框架，报错 TypeError: cannot unpack non-iterable NoneType，完整 traceback 如下：..."
```

同样的问题，有无上下文，回答质量差 10 倍。

**3. 定义输出格式**

```
❌ "分析一下这两个方案"
✅ "对比这两个方案，用表格列出：成本、实施周期、风险三个维度"
```

不定义格式 = 接受模型的自由发挥。定义格式 = 得到可预测的结构化输出。

**4. 区分指令和数据**

```
❌ "总结这篇文章：[3000字文章]"
✅ "请总结以下文章。文章用 <article> 标签包裹。\n<article>\n[3000字文章]\n</article>"
```

用 XML 标签、分隔符把指令和数据分开，模型才能准确识别"哪些是指令，哪些是要处理的内容"。

**5. 给示例**

当文字描述不够精确时，给 2-3 个示例比写 500 字说明更有效。这是 Few-shot 的核心思想，02 篇会详细讲。

**6. 迭代优化**

好的 Prompt 不是一次写出来的，而是反复测试、调整出来的。每次输出不理想时，问自己：是哪条原则没做好？是太模糊、缺上下文、还是格式没定义？

## 总结

- **Prompt 是你发给 LLM 的全部输入**，模型根据它逐 Token 续写，Prompt 质量直接决定输出质量
- **三种消息角色**：System（开发者设定规则）> User（用户输入）> Assistant（模型历史回复），System 的权重最高
- **LLM 对开头和结尾的内容最敏感**，中间长文本容易被稀释；上下文窗口有限，对话越长越容易"失忆"
- **六条基本原则**：明确具体、给上下文、定义输出格式、区分指令和数据、给示例、迭代优化

这篇文章建立了 Prompt 工程的基础认知。接下来四篇文章逐一展开具体技术：

- [02 设计模式](./02-prompt-design-patterns.md)：四种组织 Prompt 的核心方法
- [03 结构化输出](./03-structured-output.md)：让输出能被代码消费
- [04 System Prompt](./04-system-prompt.md)：定义 Agent 的身份和边界
- [05 鲁棒性](./05-prompt-robustness.md)：应对意外输入的防御体系

> 基础概念搞清楚了，接下来学习四种核心的 Prompt 组织方式。请前往 [Prompt 设计模式](./02-prompt-design-patterns.md)。

## 参考链接

- [OpenAI — Chat Completions API](https://platform.openai.com/docs/guides/chat-completions) — messages 结构和角色定义
- [Anthropic — System Prompts](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts) — System Prompt 最佳实践
- [Prompt Engineering Guide](https://www.promptingguide.ai/) — 社区维护的系统化教程
