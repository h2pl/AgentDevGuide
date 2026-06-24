# 生成实战与选型

> 图像、视频、原生输出——三篇文章把技术原理拆完了。这一篇把它们串成你可以直接使用的选型指南和实战工作流。回答一个问题：这么多工具，我该用哪个、怎么用、花多少钱。

## 目录

- [统一选型框架：五个决策维度](#统一选型框架五个决策维度)
- [图像生成：按场景、按成本、按精度](#图像生成按场景按成本按精度)
- [视频生成：什么时候值得掏钱](#视频生成什么时候值得掏钱)
- [Prompt 工程：生成质量的瓶颈不是模型](#prompt-工程生成质量的瓶颈不是模型)
- [成本全景：从免费到企业级](#成本全景从免费到企业级)
- [完整实战：搭建品牌物料自动生成系统](#完整实战搭建品牌物料自动生成系统)
- [常见问题与排错](#常见问题与排错)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。05 章的前三篇分别拆了图像生成（扩散模型）、视频生成（DiT/自回归/混合）、原生输出（统一Token空间）。这一篇不再讲原理——全是工程实战、成本计算、和选型决策。

## 统一选型框架：五个决策维度

选择生成工具时，不是"谁画得好用谁"——五个维度互相制约：

```
你的需求拆解：
  精度：需要最高画质 or 够用就行？
  迭代：一次性出图 or 需要来回改几十版？
  预算：免费方案够吗 or 可以每月 $10-50？
  生态：独立工具 or 需要和LLM/剪辑/发布联动？
  部署：纯云端 or 必须本地运行（隐私/合规）？
```

这些维度经常互相矛盾。Midjourney 画质第一但不支持迭代编辑。SD 能本地无限跑但画质需要额外调优。ChatGPT 的 DALL-E 最方便但画质有天花板。**没有最好的工具，只有最适合你当前需求组合的工具。**

## 图像生成：按场景、按成本、按精度

### 场景驱动的选型

**场景一：日常配图和小型创作**

不需要最高画质，但需要方便——在聊天中随口说"帮我生成一张封面图"就出图。

推荐：ChatGPT Plus（$20/月）内直接用 DALL-E 或 GPT-4o 原生生图。最大优势是**零切换成本**——写文案和配图在同一个界面完成。如果对画质要求不高（社交媒体配图级别），这一个工具就够了。

**场景二：追求最高画质的创作**

需要海报、插画、概念设计等对画面质感要求高的产出。

推荐：Midjourney（$10-60/月）。核心投入不在钱，在**学习 Prompt 工程**——同样的工具，Prompt 好坏能让出图画质差两个档次。花 30 分钟学透 Prompt 五维度（后面会讲），比升级到最贵的套餐更有价值。

**场景三：需要反复修改和精确控制**

不只是生成，还要"把这个元素去掉""把那个颜色改了""保持之前那只猫换一个背景"。

推荐：GPT-4o 原生输出。这是目前唯一支持"真编辑"而非"重新生成"的方案。DALL-E 和 Midjourney 的"编辑"本质上是重新生成整张图——一致性全靠运气。

**场景四：大批量、自动化、可定制**

每天需要生成数百张图，或者需要在自己的服务器上搭建生成管线。

推荐：Stable Diffusion 3.5 或 Flux，配合 ComfyUI（图形化节点工作流）或 diffusers 库（编程接口）。核心优势是**完全可控**——你可以用 ControlNet 精确控制构图、用 LoRA 定制风格、用脚本批量生成。

**场景五：中文内容创作**

需要生成包含中文文字的海报、封面、电商图。

推荐：豆包 Seedream 4.0 或 ChatGPT DALL-E。前者中文文字渲染国产最强，后者在 GPT-4o 集成后文字能力大幅提升。Midjourney 和 SD 在中文文字渲染上仍然不可靠。

**场景六：电商和商业场景**

商品图、模特换装、场景图批量制作。

推荐：通义万相（阿里）。电商场景有专项优化——模特换装、商品场景图生成是垂直刚需，通用工具在这个场景下效果不如专项工具。

### 成本驱动的决策

假设日常使用量：每天生成 20 张图。

| 方案 | 月成本 | 每张成本 | 适合 |
|------|:--:|:--:|------|
| ChatGPT Plus (DALL-E无限) | $20 | ≈$0.03 | 方便优先 |
| Midjourney Basic | $10 | ≈$0.017 | 画质优先，预算低 |
| Midjourney Standard | $30 | ≈$0.05 | 专业创作者 |
| SD本地(RTX 3090, 电费) | ≈$9 | ≈$0.015 | 量大、定制需求多 |
| Replicate托管SD/Flux | ≈$12 | ≈$0.02 | 不想买显卡 |
| DALL-E API直接调用 | ≈$48 | ≈$0.08 | 和自建App集成 |

**省钱洞察**：本地部署 SD/Flux 对于日生成量 >50 张的场景是最经济的。但如果只是偶尔生成几张图，ChatGPT Plus 的无限 DALL-E 是性价比之王——$20 包月不限次数。

## 视频生成：什么时候值得掏钱

视频生成比图像贵一个数量级——需要更谨慎的选型。

### 预算和场景的匹配

**零预算方案**：可灵免费额度（每天 3-6 次）。画质足够日常使用，中文 Prompt 体验好。适合：偶尔生成短视频配素材、尝试视频生成、学习 Prompt。

**轻量付费**：可灵付费（约 ¥30-50/月）或 Runway Basic（$15/月）。适合：定期需要 AI 视频素材的内容创作者。

**专业级**：Runway Standard（$35/月）。适合：把 AI 视频生成作为生产力工具的专业创作者、广告公司、影视工作室。

**批量级**：混合使用可灵（中文场景）+ Runway（高画质场景）+ 即梦 Seedance（人物场景）。不需要忠诚于一个工具——根据每段视频的需求动态选择。

### 视频生成的 ROI 思考

算一笔账：一段 10 秒的 AI 视频 vs 实拍或 3D 制作的 10 秒视频。

```
AI 视频生成：
  可灵：¥0-1/段（免费额度内）
  Runway：≈$0.50/段
  时间：2-5 分钟（生成+等待）

实拍：
  摄影师+器材+场地+模特+后期：¥500-5000/段
  时间：半天到一天

3D 制作：
  Blender/C4D 建模+渲染：¥200-1000/段
  时间：几小时到几天
```

**AI 视频生成的成本优势是 100-1000 倍的量级差**。当前画质还不能完全替代专业实拍和 3D，但对于社交媒体视频素材、产品演示、概念验证、广告 A/B 测试等场景，AI 方案已经足够好了。

## Prompt 工程：生成质量的瓶颈不是模型

有一个反直觉但被反复验证的规律：**出图质量 60% 取决于 Prompt 质量，25% 取决于选对模型，只有 15% 取决于模型本身的能力差异。**

同样的 Midjourney v6，A 能出惊艳的图，B 只能出平庸的图——差距不在工具，在 Prompt。

### 图像 Prompt 的五维度体系

```
维度 1：主体（Subject）—— 你要画什么？
  不是 "a cat"
  而是 "a orange tabby cat with green eyes, sitting upright"
  主体要具体到品种、颜色、姿态、表情

维度 2：环境（Environment）—— 在什么地方？
  不是 "on a windowsill"
  而是 "on a weathered wooden windowsill, overlooking a rainy Paris street,
         with a steaming cup of coffee and an open book beside it"
  环境要具体到材质、视角、氛围

维度 3：风格（Style）—— 什么画风？
  不是 "realistic"
  而是 "hyperrealistic digital painting, trending on ArtStation,
         cinematic lighting, 85mm lens, shallow depth of field"
  风格要具体到画种、平台审美、摄影参数

维度 4：光影（Lighting）—— 什么光线？
  不是 "good lighting"
  而是 "golden hour sunlight streaming through venetian blinds,
         warm color temperature, soft shadows, rim light on the fur"
  光影要具体到光源类型、方向、色温、阴影质感

维度 5：技术参数（Technical Parameters）
  不是默认
  而是 --ar 16:9 --v 6 --s 250 --c 50 --no text, watermark
  参数用模型能理解的方式指定分辨率和质量控制
```

### 视频 Prompt 的额外维度

视频 Prompt 除了图像五维度，还要加上两个专属维度：

```
维度 6：动作（Movement）—— 画面里发生什么？
  "一只猫从窗台轻盈地跳下来，落地后慢悠悠地甩了甩尾巴"
  动作要具体到起点、过程、终点、节奏

维度 7：镜头（Camera）—— 摄像机怎么拍？
  "镜头从低角度缓缓上摇，跟随猫的跳跃轨迹，在猫落地时轻微震动后定格"
  镜头要具体到机位、运动方式、焦距变化、节奏
```

镜头描述是目前 AI 视频生成最弱的控制维度——大部分模型只能大致跟随镜头方向，无法精确复现你写的复杂镜头运动。Runway 的运动笔刷部分解决了这个问题。

### 迭代策略：三遍法

**第一遍（方向探索）**：用极简 Prompt 出图，看模型的理解方向对不对。

```
"a cat sitting on a windowsill, golden hour"
→ 看看猫的姿势对不对、窗台的风格是不是想要的、光线方向对不对
```

**第二遍（质量提升）**：加入详细的风格、光影、环境描述。

```
"a orange tabby cat with green eyes sitting on a weathered wooden windowsill,
 overlooking a rainy Paris street, steaming coffee and open book beside,
 hyperrealistic digital painting, cinematic lighting, 85mm lens,
 shallow depth of field, golden hour sunlight through venetian blinds"
→ 画质应该已经很好，审视不满意的细节
```

**第三遍（精修）**：针对不满意的地方调整 Prompt，或使用编辑功能局部修改。

```
"--no distorted, ugly, blurry --ar 16:9"
→ 去掉不想要的东西，锁定最终参数
```

**不要期望第一遍就出完美结果。三遍法的核心是"快速迭代"——每遍不要纠结，不满意就调 Prompt 重来，比死磕一张图高效得多。**

## 成本全景：从免费到企业级

### 图像生成的月度成本

```
免费用（每天 3-5 张）：
  可灵免费额度：$0
  即梦免费额度：$0
  SD 本地（已有显卡）：≈$5 电费

轻量级（每天 10-20 张）：
  ChatGPT Plus (DALL-E)：$20/月
  Midjourney Basic：$10/月
  SD 本地：≈$9/月

中量级（每天 50-100 张）：
  Midjourney Standard：$30/月
  SD 本地：≈$15/月（电费+GPU折旧）
  SD/Flux 托管（Replicate）：≈$30/月 ← 推荐

大量级（每天 500+ 张）：
  SD 本地（RTX 4090）：≈$30/月 电费
  硬件投入：$1500（一次性，可用 3-5 年）
  月均摊：$25-40/月 + 电费 $30 = ≈$60/月
```

### 视频生成的月度成本

```
免费用（每天 2-3 段）：
  可灵：$0
  即梦：$0

轻量级（每天 5 段）：
  可灵付费：¥30-50/月
  Runway Basic：$15/月

中量级（每天 10-20 段）：
  Runway Standard：$35/月
  可灵 + Runway 混合：≈¥100/月

专业级（每天 50+ 段）：
  Runway Unlimited：$95/月
```

### 省钱的核心策略

1. **高频图生用 SD 本地**：显卡的一次性投入在每天 50+ 张时 3 个月回本
2. **低频用 ChatGPT Plus**：$20 包月无限 DALL-E，最低的方便成本
3. **视频用免费额度**：可灵和即梦的免费额度对大多数个人用户完全够用
4. **混合工具**：不需要忠诚于一个平台——初期用 ChatGPT 快速验证，定稿用 Midjourney 出高画质

## 完整实战：搭建品牌物料自动生成系统

把本章所有知识串成一个实际可用的系统：

```python
from openai import OpenAI
import asyncio
from typing import List, Dict

class BrandContentGenerator:
    """
    品牌物料自动生成器
    
    核心设计：文案和配图由同一个模型完成，
    共享上下文，保证风格一致性。
    """
    
    def __init__(self, brand_config: Dict):
        self.client = OpenAI()
        self.brand = brand_config
        self.cost_log = []  # 追踪成本
    
    async def generate_social_post(
        self, topic: str, platform: str = "wechat", 
        reference_images: List[str] = None
    ) -> Dict:
        """为指定话题生成完整的社交媒体内容"""
        
        # 第一步：用 GPT-4o 生成文案
        copy_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": f"""你是 {self.brand['name']} 的文案。
                品牌调性: {self.brand['tone']}
                品牌代表色: {', '.join(self.brand['colors'])}
                目标读者: {self.brand['audience']}"""
            }, {
                "role": "user",
                "content": f"为{topic}写一段{platform}文案，120-150字。"
            }]
        )
        copy = copy_response.choices[0].message.content
        
        # 第二步：用 GPT-4o 原生生成配图
        # 关键：生成图片时模型"知道"刚才的文案内容
        image_prompt = f"""
        为以下文案生成一张{platform}风格的配图：
        
        文案：{copy[:200]}
        品牌色：{', '.join(self.brand['colors'])}
        
        要求：
        - 留白充足，适合社交流媒体浏览
        - 如需包含文字，使用品牌代表色
        - 简洁现代的设计风格
        """
        
        image_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": image_prompt}]
        )
        
        # 记录成本
        self._log_cost(copy_response, image_response)
        
        return {
            "platform": platform,
            "topic": topic,
            "copy": copy,
            "image": image_response.choices[0].message.content,
            "hashtags": self._generate_hashtags(topic)
        }
    
    def _generate_hashtags(self, topic: str) -> List[str]:
        """基于话题生成相关标签"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # 简单任务用小模型省钱
            messages=[{
                "role": "user",
                "content": f"为'{topic}'生成5个社交媒体标签，每个不超过8个字"
            }]
        )
        return response.choices[0].message.content.split("\n")
    
    def _log_cost(self, *responses):
        """追踪API调用成本"""
        for resp in responses:
            usage = resp.usage
            prompt_cost = usage.prompt_tokens * 2.50 / 1_000_000
            completion_cost = usage.completion_tokens * 10.00 / 1_000_000
            self.cost_log.append(prompt_cost + completion_cost)
    
    def get_total_cost(self) -> float:
        return sum(self.cost_log)


# 使用示例
brand = {
    "name": "LearnAgent",
    "tone": "专业但不枯燥，像工程师给朋友讲技术",
    "colors": ["#2563EB", "#F8FAFC", "#059669"],
    "audience": "1-3年经验的应用程序员"
}

generator = BrandContentGenerator(brand)

# 生成一条微信推文
import asyncio
content = asyncio.run(generator.generate_social_post(
    topic="什么是AI Agent",
    platform="wechat"
))

print(f"文案: {content['copy'][:100]}...")
print(f"标签: {', '.join(content['hashtags'])}")
print(f"本次成本: ${generator.get_total_cost():.4f}")
```

这个系统的核心设计理念：**文案和配图由同一个模型在同一轮对话上下文中完成**——它们共享品牌调性、颜色偏好、文字内容的完整理解。传统模式下"GPT写文案 + Midjourney生成图"的组合做不到这种一致性——文案里的品牌色可能和配图完全不搭，配图可能完全不理解文案要表达的重点。

## 常见问题与排错

### 图像问题

**问题：手指/肢体畸变**
- 原因：扩散模型在复杂姿态上缺乏足够训练数据
- 解决：Prompt 中加入 "perfect hands, anatomically correct" 或避开需要详细手部特写的构图

**问题：文字拼写错误**
- 原因：大部分模型把文字当视觉纹理处理
- 解决：用 GPT-4o 原生输出或 DALL-E，避免 Midjourney/SD 生成复杂文字

**问题：多次生成不一致**
- 原因：每次生成是独立的随机过程
- 解决：保存随机种子（seed），用相同 seed 重新生成；或用 GPT-4o 的原生编辑功能

### 视频问题

**问题：运动不连贯或跳跃**
- 原因：扩散模型的时序注意力不够
- 解决：图生视频成功率远高于文生视频；降低运动强度（可灵的 motion strength）

**问题：背景物体扭曲**
- 原因：模型把注意力集中在主体上，忽略了背景的物理一致性
- 解决：Prompt 中特别描述背景物体的运动预期；先用图生视频

## 总结

- 生成工具选型没有"最好"，只有"最适合你的五个维度组合"——精度、迭代、预算、生态、部署
- **Prompt 决定了 60% 的出图质量**——花时间学好 Prompt 五维度+视频两维度，比花更多钱升级工具有效
- 迭代策略遵循**三遍法**：方向探索（简）→ 质量提升（详）→ 精修（调）
- 图像月度成本 $0-60，视频月度成本 $0-100——高频场景用本地部署 SD，低频用 ChatGPT Plus
- 原生多模态输出正在改变"文案+配图"的工作流——理解+生成在同一模型，上下文自然一致
- 05 章全部结束。六章的旅程还剩最后一站：[06 工程落地](../06-engineering-production/README.md) —— 怎么把多模态 AI 真正部署到生产环境

## 参考链接

- [DALL-E Prompt 工程指南](https://platform.openai.com/docs/guides/images/prompting)
- [Midjourney 参数完整指南](https://docs.midjourney.com/docs/parameter-list)
- [Stable Diffusion ComfyUI 工作流](https://comfyanonymous.github.io/ComfyUI_examples/)
- [可灵 Prompt 指南](https://klingai.kuaishou.com/)

> 生成领域全部讲完——从扩散模型的数学原理到品牌物料的自动化生产。但最好的 AI 如果没部署到线上就没有价值。最后一章 [06 工程落地](../06-engineering-production/README.md) 补齐从 demo 到生产的关键拼图：评测、RAG、成本、部署、安全。
