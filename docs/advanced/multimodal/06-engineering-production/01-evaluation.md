# 多模态评估体系

> 前面五章你学会了多模态 AI 能做什么、怎么工作、怎么调 API。但一个根本问题还没回答：怎么知道它做得好不好？多模态的评估比纯文本复杂一个维度——你需要同时衡量看图准不准、听音清不清楚、生成的图画得好不好看。而且这些指标之间经常矛盾。

## 目录

- [为什么多模态评估比文本难](#为什么多模态评估比文本难)
- [理解侧评估：看图听音对不对](#理解侧评估看图听音对不对)
- [生成侧评估：画得好不好看](#生成侧评估画得好不好看)
- [视频评估：多出来的时间维度](#视频评估多出来的时间维度)
- [语音评估：WER 和 MOS 之外](#语音评估wer-和-mos-之外)
- [综合 Benchmark 全景](#综合-benchmark-全景)
- [实战：搭建多模态评估流水线](#实战搭建多模态评估流水线)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。这一章来到工程的起点——不是写代码，而是**定义什么叫"好"**。没有评估体系，你无法判断一个模型升级是否真的有价值、无法比较两个候选方案、无法在生产环境中监控质量退化。

## 为什么多模态评估比文本难

纯文本评估相对成熟——BLEU/ROUGE 度量文本相似度、困惑度度量语言模型质量、人类偏好评分度量对齐程度。但多模态引入了几个纯文本没有的评估挑战：

### 多维度不可通约

多模态系统的输出往往跨越多个维度。一个视觉问答系统同时要判断"答案对不对"（文本维度）和"看图是否准确"（视觉维度）。两个维度的好坏没法直接相加——85 分的文字理解 + 90 分的视觉精度，这个系统应该打多少分？

更麻烦的是，有些任务中两个维度相互矛盾。一个生图模型可能会画得很好看（视觉维度高）但没按你的 Prompt 来（文本维度低）。给这张图打几分？

### 主观性不可避免

"这张图画得好不好看"本质上是一个主观判断。FID（Fréchet Inception Distance）可以量化生成图和真实图的分布差异，CLIP Score 可以量化图和文字的匹配度——但一张 FID 低、CLIP Score 高的图可能"精确但不美"，而一张 FID 高、CLIP Score 低的图可能"不精确但很有美感"。

图像生成目前没有一个客观指标能完全替代人类审美判断。音频同理——一段 TTS 的 MOS（Mean Opinion Score）靠人工打分，无法被声学参数完全替代。

### 跨模态任务缺少统一标准

"给一张图，写一段文字描述"——多长的描述算好？详细到像素级别的描述 vs 诗意概括的描述，哪个更好？答案取决于应用场景。搜索引擎需要高度精确的描述，社交媒体需要吸引人的描述。同一个任务，不同场景的"好"完全不同。

## 理解侧评估：看图听音对不对

多模态理解系统的评估比其他生成系统相对更成熟——因为答案通常是可验证的。

### 图文理解的核心指标

**准确率**。最简单的指标——问 100 个关于图片的问题，答对了多少个。但"答对"的判断本身可能是模糊的——"图片里有几只猫？"→ 3 只是精确的，"有猫"不精确但也不算完全错误。

**MMBench**。目前最被广泛采用的中文多模态理解基准。覆盖 20 个能力维度，从基础感知（物体识别）到高级认知（逻辑推理、专业知识）。每道题有唯一标准答案，支持全自动评分。

**MME（Multimodal Evaluation）**。另一个综合基准，特点是包含 14 个子任务的大规模测试。它同时报告**感知**分数和**认知**分数——前者衡量"看到了什么"，后者衡量"理解了什么"。

**OCRBench**。专门评估文字提取能力的基准。对于文档理解、UI 分析等场景，OCR 能力往往比通用视觉理解更重要。它测试模型在文字识别、文字定位、文字理解三个层次的准确度。

### 图文理解的能力分解

一个好的评估不应该只看总分——要分解到具体能力维度，才能定位问题：

```
MMBench 能力维度示例：
  CP (Coarse Perception):    粗粒度感知 — "图里有什么"
  FP (Fine Perception):      细粒度感知 — "第三个人的帽子是什么颜色"
  IR (Image Reasoning):      图像推理 — "为什么这个场景不合理"
  LR (Logical Reasoning):    逻辑推理 — "根据这张图，接下来会发生什么"
  AR (Attribute Reasoning):  属性推理 — "比较两个物体的大小/颜色/位置"
  SC (Science):              科学知识 — "这是什么自然现象"
```

一个模型 CP 85 分、IR 52 分——你知道它"看"没问题，但"想"有短板。一个模型 CP 52 分、IR 40 分——它"看"和"想"都不行。**能力分解比总分更有指导意义。**

### 视觉定位评估

对于 Qwen-VL 这类支持视觉定位（Grounding）的模型，评估指标更复杂：

- **IoU（Intersection over Union）**：预测框和真实框的重叠度，>0.5 算正确
- **Referring Expression Comprehension**：给定"图中穿红色衣服的人"，模型能否正确框出目标
- **Grounding Recall**：图片中所有应该被定位的物体中，模型找到了几个

### 评估的陷阱

**数据污染**。很多公开 Benchmark 的测试数据可能已经混入了训练数据——模型不是在"理解"，而是在"回忆"。一个极端例子：2023 年某个模型在 ScienceQA 上得分极高，但后续分析发现它只是记住了训练数据中类似的题目模式，并没有真正的科学推理能力。

**语言偏见**。大部分 Benchmark 是英文的。一个模型可能在 MMBench 英文版上得分很高，但中文版大幅下降——不是能力问题，是训练数据分布的偏差。

**评估 prompt 敏感性**。同一个问题，换一种问法——"图里有几只猫" vs "数一下图中有多少只猫"——模型的表现可能有明显波动。这提示我们不要用一两道题去判断模型能力。

## 生成侧评估：画得好不好看

生成侧的评估远比理解侧困难——回答"对不对"有一个客观标准，"画得好不好看"没有。

### FID：衡量生成图和真实图的分布差异

FID 是图像生成领域最常用的量化指标。它把生成图和真实图分别映射到 Inception 网络的特征空间，计算两个分布之间的 Fréchet 距离。

```
FID 的计算逻辑：
  真实图集合 → InceptionV3 → 特征分布 A（均值μ_r, 协方差Σ_r）
  生成图集合 → InceptionV3 → 特征分布 B（均值μ_g, 协方差Σ_g）

  FID = ||μ_r - μ_g||² + Tr(Σ_r + Σ_g - 2√(Σ_r Σ_g))

  解读：FID 越低越好，表示生成图的质量分布越接近真实图
```

**FID 的问题**：它衡量的是"生成图集合和真实图集合的整体统计差异"，但无法评判单张图的质量。一个模型的 FID = 5，另一模型 FID = 8——前者生成图的**整体分布**更接近真实，但如果后者在特定子类别（如人像）上更好，FID 看不出来。

### CLIP Score：衡量图文匹配度

CLIP Score = cosine_similarity(CLIP(生成图), CLIP(Prompt 文本))

它衡量的是"这张图和你的 Prompt 是否匹配"。一个非常有用但容易被误解的指标：

```
正确的理解：
  CLIP Score 高 = 图和文字内容一致
  CLIP Score 低 = 图和文字内容不一致

错误的解读：
  CLIP Score 高 = 图更"好看"  ← 不对！
  只表示图文匹配度，不衡量审美质量
```

一张正确跟随 Prompt 的丑陋图，CLIP Score 可能比一张画风精美但内容跑偏的图更高。

### FID 和 CLIP Score 的组合使用

实践中通常组合 FID 和 CLIP Score 来衡量生图模型——FID 管画质，CLIP Score 管理解。理想的模型是：FID 低（画质好）+ CLIP Score 高（理解准）。

### 人类评估：绕不开的最终标准

对于生成任务，人工评分仍然是最终标准。两种常见方式：

**A/B 测试**。给人类评判员两张图（A 和 B），问题是"哪张更好"。不告诉评判员哪张是哪个模型生成的——避免品牌偏见。统计 A 和 B 的胜出比例，得出哪个模型更优。

**Mean Opinion Score（MOS）**。1-5 分打分制，多位评判员对同一张图打分取平均。问题在于不同评判员的"3 分"标准可能完全不同——有人给 3 分代表"还行"，有人给 3 分代表"勉强及格"。

**实践中最有效的组合**：自动化指标（FID + CLIP Score）做大规模筛选和趋势监控，人工 A/B 测试做关键决策。

## 视频评估：多出来的时间维度

视频生成模型的评估比图像更复杂——多了时间维度的考量。

### 时序一致性指标

**FVD（Fréchet Video Distance）**。视频版的 FID——把视频映射到时序特征空间，衡量生成视频和真实视频的分布差异。它对运动连贯性比 FID 更敏感。

**帧间相似度**。连续两帧之间的结构相似度（SSIM）。如果相邻帧的 SSIM 波动过大，说明有跳帧或形变。但 SSIM 过低不一定不好——快速动作场景的相邻帧本来就不相似。

**Temporal Consistency Loss**。训练中使用的内部指标——约束模型的生成使相邻帧的特征表示足够接近。

### 视频评估的真实困境

当前没有一个公认的"视频版 MMBench"。不同视频生成产品的宣传数据（"我们的运动连贯性比竞品高 30%"）基本都是各自定义的自评指标，不具有可比性。**视频评估目前最可靠的方式仍然是人工 A/B 测试。**

## 语音评估：WER 和 MOS 之外

### STT 的核心指标

**WER（Word Error Rate）**：词错误率。衡量识别结果和真实文本之间的差异。

```
WER = (替换 + 插入 + 删除的单词数) / 真实文本单词数

一段 100 个单词的录音：
  识别结果错了 5 个词 → WER = 5%
```

WER 的局限：把所有错误视为同等严重。"识别成"和"识别成"——前者一个关键动词的变化，后者一个无意义的虚词变化，WER 权重一样。

**CER（Character Error Rate）**：中文字错误率。中文的最小单元是字不是词——把"他们在吃饭"识别成"他们在吃面"是 1/5 的字错误率。

### TTS 的核心指标

**MOS（Mean Opinion Score）**：1-5 分的主观评分。当前最好的 TTS 系统（ElevenLabs、GPT-4o 语音）的 MOS 约 4.5-4.7，接近真人的 4.8-4.9。

**MCD（Mel Cepstral Distortion）**：梅尔倒谱失真——衡量合成语音和真实语音在频谱层面的差异。比 MOS 更客观，但和人的感知不完全对应。

## 综合 Benchmark 全景

| Benchmark | 评估维度 | 模态 | 适用场景 |
|-----------|---------|:--:|------|
| MMBench | 20维综合能力 | 图文 | 通用视觉理解 |
| MME | 感知+认知 | 图文 | 通用视觉理解 |
| OCRBench | OCR精确度 | 图文 | 文档和文字场景 |
| MathVista | 数学视觉推理 | 图文 | 图表和数学题 |
| MMMU | 大学级多模态理解 | 图文 | 复杂专业知识 |
| Video-MME | 视频理解 | 视频 | 视频问答和推理 |
| AISHELL | 中文语音识别 | 音频 | 中文STT |
| LibriSpeech | 英文语音识别 | 音频 | 英文STT |

## 实战：搭建多模态评估流水线

```python
class MultimodalEvaluator:
    """多模态系统的综合评估器"""
    
    def __init__(self):
        self.results = {}
    
    def evaluate_vision_understanding(self, model, test_set):
        """评估视觉理解能力"""
        correct = 0
        dimension_scores = {}  # 按能力维度分解
        
        for item in test_set:
            answer = model.answer(item["image"], item["question"])
            
            if self._is_correct(answer, item["ground_truth"]):
                correct += 1
                dimension = item.get("dimension", "general")
                dimension_scores[dimension] = dimension_scores.get(dimension, 0) + 1
        
        accuracy = correct / len(test_set)
        
        # 按维度分解
        dimension_accuracy = {
            dim: score / len([i for i in test_set if i.get("dimension") == dim])
            for dim, score in dimension_scores.items()
            if len([i for i in test_set if i.get("dimension") == dim]) > 0
        }
        
        return {
            "overall_accuracy": accuracy,
            "dimension_breakdown": dimension_accuracy,
            "total_samples": len(test_set)
        }
    
    def evaluate_grounding(self, model, test_set):
        """评估视觉定位能力"""
        total_iou = 0
        count = 0
        
        for item in test_set:
            predicted_bbox = model.locate(item["image"], item["target"])
            iou = self._calculate_iou(predicted_bbox, item["ground_truth_bbox"])
            total_iou += iou
            count += 1
        
        return {
            "mean_iou": total_iou / count,
            "iou_above_0.5": sum(1 for _ in 
                [(item, model.locate(item["image"], item["target"])) 
                 for item in test_set] 
                if self._calculate_iou(
                    model.locate(item["image"], item["target"]),
                    item["ground_truth_bbox"]
                ) > 0.5
            ) / len(test_set)
        }
    
    def evaluate_generation_quality(self, generated_images, reference_images):
        """评估生成图片质量"""
        from pytorch_fid import fid_score
        fid = fid_score.calculate_fid_given_paths(
            [generated_images, reference_images],
            batch_size=50, device="cuda"
        )
        
        # CLIP Score 计算
        clip_scores = []
        for gen_img, prompt in generated_images:
            score = self._calculate_clip_score(gen_img, prompt)
            clip_scores.append(score)
        
        return {
            "FID": fid,
            "CLIP_Score_mean": sum(clip_scores) / len(clip_scores),
            "CLIP_Score_std": self._std(clip_scores)
        }
    
    def evaluate_stt_accuracy(self, model, audio_files, ground_truths):
        """评估语音识别准确率"""
        total_wer = 0
        total_cer = 0
        
        for audio, gt in zip(audio_files, ground_truths):
            transcript = model.transcribe(audio)
            wer = self._calculate_wer(transcript, gt)
            cer = self._calculate_cer(transcript, gt)
            total_wer += wer
            total_cer += cer
        
        return {
            "WER": total_wer / len(audio_files),
            "CER": total_cer / len(audio_files),
            "samples": len(audio_files)
        }
```

## 总结

- 多模态评估的挑战来自**三个层面**：多维度不可通约、主观性不可避免、跨模态任务缺少统一标准
- 理解侧评估相对成熟：**MMBench/MME** 覆盖 20+ 能力维度，**能力分解比总分更有指导意义**
- 生成侧评估仍然严重依赖人工判断：**FID 管画质、CLIP Score 管理解**，但两者都不是"好看"的完美度量
- 视频评估是最弱的环节——时序一致性指标（FVD/帧间SSIM）仍处于学术阶段，**人工 A/B 测试是当前最可靠的标准**
- 语音评估相对规范：**WER/CER（识别）、MOS/MCD（合成）** 是行业标准
- 评估不是"做完之后打分的环节"，而是**持续的过程**——从选型决策到上线监控
- 下一篇把评估体系应用到信息检索场景：[多模态 RAG](./02-multimodal-rag.md)

## 参考链接

- [MMBench 官方](https://mmbench.opencompass.org.cn/)
- [MME Benchmark](https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models/tree/Evaluation)
- [FID 指标详解](https://arxiv.org/abs/1706.08500)
- [CLIP Score 计算](https://arxiv.org/abs/2104.08718)
- [AISHELL 中文语音数据集](https://www.aishelltech.com/aishell_3)

> 评估体系搭好了。但一个系统不只是"好不好"——它还要能"找得到"信息。下一篇 [多模态 RAG](./02-multimodal-rag.md) 拆解怎么让 AI 在一堆图片和文档里精确检索。
