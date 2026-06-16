# 工具 Schema 设计

> 工具调用的准确率不取决于模型有多强，而取决于你的 JSON Schema 写得有多好。一段模糊的描述能让 GPT-5.5 选错工具，一段精确的描述能让轻量模型也准确执行。

## 目录

- [Schema 是模型的"使用说明书"](#schema-是模型的使用说明书)
- [写好描述的四条原则](#写好描述的四条原则)
- [参数设计的反模式](#参数设计的反模式)
- [让模型"不得不选"的强制策略](#让模型不得不选的强制策略)
- [复杂参数的分拆艺术](#复杂参数的分拆艺术)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。在 [工具调用机制](./01-tool-calling-mechanism.md) 中，你了解了工具调用的完整流程。但流程跑通了不代表结果准确——模型经常选错工具、漏传参数、或者把字符串当成数字。这篇文章解决核心问题：**怎么设计工具 Schema，让模型每一次调用都精准无误**。

**JSON Schema** 是工具调用的"使用说明书"。模型在训练过程中学习了海量 API 文档和函数签名，参数优化的结果使它在生成工具调用时，高度依赖 Schema 中的描述文本和类型约束。描述写得好，轻量模型也能高准确率调用；描述写得差，旗舰模型也会犯低级错误。

## Schema 是模型的"使用说明书"

模型看不到你的函数实现，它只能看到 Schema 中的三个要素：

1. **工具名称** — 模型用它做初步匹配
2. **功能描述**（`description`）— 模型用它判断"这个工具能做什么"
3. **参数定义**（`properties` + `description`）— 模型用它决定"该传什么值"

下面是一个反例，展示了"最小化 Schema"有多危险：

```python
# 反例：描述过于模糊，模型很难理解工具的用途
bad_tool = {
    "name": "query",
    "description": "查询数据",
    "parameters": {
        "type": "object",
        "properties": {
            "q": {"type": "string"}
        }
    }
}
```

模型看到 `query` + `查询数据` 时，参数中编码的概率分布无法将其与"查订单""查用户""查库存"区分开。用户说"帮我看看昨天买的手机"，模型可能调用 `query` 传 `{"q": "手机"}`，但后端期望的是 `{"q": "order_12345"}` 或 `{"category": "phone", "date": "2026-06-15"}`。

## 写好描述的四条原则

### 1. 描述必须回答"这个工具解决什么问题"

不要只说工具"做什么"，要说它"解决什么问题"。模型在训练中见过的问题描述远多于技术动作描述。

```python
# ❌ 差：描述动作
"description": "查询订单数据库"

# ✅ 好：描述问题和场景
"description": "当用户想了解已购买商品的状态、物流信息或退款进度时，\n" \
              "根据用户提供的订单号或商品名称查询订单详情。"
```

### 2. 参数描述必须包含"期望格式"和"示例"

模型对参数的理解完全依赖描述文本。没有格式说明，它会猜测——而猜测往往是错的。

```python
# ❌ 差：没有格式说明
"order_id": {
    "type": "string",
    "description": "订单ID"
}

# ✅ 好：包含格式和示例
"order_id": {
    "type": "string",
    "description": "订单编号，格式为 ORD-年月日-4位序号，如 ORD-20260615-0892。"
}
```

**关键事实**：BFCL（Berkeley Function Calling Leaderboard）2025-2026 年的测试数据显示，参数描述包含示例的 Schema，模型调用准确率比无示例版本高 12-18%。这不是因为模型"更理解"了，而是因为描述文本中出现了与用户请求语义匹配的子串，激活了参数中对应的概率分布。

### 3. 枚举值必须穷举，且用自然语言解释

`enum` 告诉模型哪些值合法，但枚举值本身可能语义不清。加一句解释能大幅降低误选率。

```python
"status": {
    "type": "string",
    "enum": ["pending", "paid", "shipped", "delivered"],
    "description": "订单状态：pending（待付款）、paid（已付款）、shipped（已发货）、delivered（已签收）"
}
```

### 4. 必填参数用 `required` 强制，而非依赖模型推理

不要假设模型能从上下文中推断出必填参数。如果参数不传后端会报错，就必须把它放进 `required` 列表。

```python
"parameters": {
    "type": "object",
    "properties": {
        "city": {
            "type": "string",
            "description": "城市名称，如\"北京\"
        },
        "date": {
            "type": "string",
            "description": "日期，格式 YYYY-MM-DD，默认今天"
        }
    },
    "required": ["city"]  # 城市必须传，日期可以默认
}
```

## 参数设计的反模式

以下是从生产环境总结的常见错误，按出现频率排序：

| 反模式 | 示例 | 后果 | 修正 |
|--------|------|------|------|
| **过度泛化** | 一个 `query` 工具包揽所有查询 | 模型永远选它，但参数传不对 | 拆成 `search_product` / `get_order` / `query_user` |
| **嵌套过深** | 三层嵌套对象，参数描述超过 200 字 | 模型传参不全，漏掉嵌套字段 | 扁平化，或拆成多个工具 |
| **布尔陷阱** | 用布尔参数控制分支逻辑 | 模型传 `true`/`false` 的准确率仅 70% | 拆成两个独立工具 |
| **类型模糊** | `"type": "string"` 但期望 `"YYYY-MM-DD"` | 模型传 `"明天"`、`"6/15"` | 加 `pattern` 正则或枚举 |
| **描述冗余** | 把实现细节写进描述 | 干扰模型判断，占用 Token | 只写"做什么"和"格式" |

**布尔陷阱详解**：BFCL 测试显示，模型对布尔参数的判断准确率显著低于字符串和数值参数。原因在于布尔值在训练语料中出现频率低，且 `true`/`false` 的语义高度依赖上下文。如果你的工具用 `{"force": true}` 控制是否强制覆盖，建议拆成 `overwrite_file` 和 `merge_file` 两个工具，模型选错的概率会从 30% 降到 5% 以下。

## 让模型"不得不选"的强制策略

除了写好 Schema，你还可以通过 API 参数强制模型调用特定工具。

**OpenAI** 提供 `tool_choice` 参数：

```python
# 强制模型调用 get_weather，不传其他工具
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    tools=[weather_tool],
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)

# 强制模型必须调用某个工具（但不指定是哪个）
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    tools=[weather_tool, calendar_tool],
    tool_choice="required"  # 必须调用至少一个工具
)
```

**Anthropic** 提供类似的 `tool_choice`：

```python
# 强制调用特定工具
response = client.messages.create(
    model="claude-opus-4",
    messages=messages,
    tools=[weather_tool],
    tool_choice={"type": "tool", "name": "get_weather"}
)
```

**使用场景**：当你从用户输入中已明确知道该调用什么工具（比如用户点了"查天气"按钮），用强制策略避免模型"自由发挥"。这能节省一次推理、减少 Token 消耗、降低错误率。

## 复杂参数的分拆艺术

当一个工具需要 10 个以上参数，或者参数之间存在复杂的条件关系时，模型的调用准确率会急剧下降。BFCL 2026 数据显示，超过 8 个参数的工具，调用完整率从 95% 跌至 72%。

**解决方案：拆分，不是合并**。

```python
# ❌ 反例：一个超级工具，参数爆炸
"create_meeting": {
    "parameters": {
        "title": "string",
        "start_time": "string",
        "end_time": "string",
        "timezone": "string",
        "attendees": "array",
        "location": "string",
        "recurrence": "object",
        "reminder": "object",
        "description": "string",
        "visibility": "string"
    }
}

# ✅ 正例：拆成两个工具，每个职责单一
"create_simple_meeting": {
    "description": "创建一次性会议，只需标题、时间和参与者",
    "parameters": {
        "title": "string",
        "start_time": "string（ISO 8601）",
        "attendees": "array（邮箱列表）"
    }
}

"create_recurring_meeting": {
    "description": "创建周期性会议，支持重复规则和提醒设置",
    "parameters": {
        "title": "string",
        "start_time": "string",
        "recurrence_rule": "string（iCal RRULE 格式）",
        "reminder_minutes": "integer"
    }
}
```

**拆分原则**：按"用户意图"拆分，不是按"后端实现"拆分。如果用户会说两种不同的话（"帮我约个会" vs "每周一开例会"），就拆成两个工具。模型的选择依据是用户输入的语义匹配，不是后端的数据库表结构。

## 总结

- **Schema 是模型的唯一信息源**。模型看不到你的代码，只能依赖描述文本和类型约束生成调用。
- **描述四原则**：说清解决什么问题、给参数格式示例、枚举值加解释、必填参数用 `required` 强制。
- **五大反模式**：过度泛化、嵌套过深、布尔陷阱、类型模糊、描述冗余。避免它们能让准确率提升 15-25%。
- **强制策略**：已知该调用什么工具时，用 `tool_choice` 强制，避免模型自由发挥。
- **复杂参数要拆分**：超过 8 个参数的工具，调用完整率显著下降。按用户意图拆成单一职责的小工具。

> 学会了设计单个工具，下一步要解决的是：**多个工具如何协同工作？模型如何并行调用多个工具、如何处理工具间的依赖关系**？请继续阅读 [多工具编排](./03-multi-tool-orchestration.md)。

## 参考链接

- [OpenAI Function Calling Schema](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)
- [BFCL Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)
- [JSON Schema Specification](https://json-schema.org/)
- [Google Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
