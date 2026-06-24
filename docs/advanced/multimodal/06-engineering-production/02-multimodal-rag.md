# 多模态 RAG

> 传统的 RAG 系统只检索文字——你的知识库里有一万份文档，用户问一个问题，系统找到最相关的几段文字，喂给 LLM 生成回答。但如果你有一万张产品图片、一万份 PDF 图表、一万段产品演示视频呢？多模态 RAG 就是让检索系统能"看懂"非文字内容。

## 目录

- [从文字 RAG 到多模态 RAG](#从文字-rag-到多模态-rag)
- [图像检索：三种策略](#图像检索三种策略)
- [ColPali：PDF 检索的范式转变](#colpali-pdf-检索的范式转变)
- [视频和音频检索](#视频和音频检索)
- [多模态 RAG 的完整架构](#多模态-rag-的完整架构)
- [实战：搭建一个产品文档多模态 RAG](#实战搭建一个产品文档多模态-rag)
- [框架选型](#框架选型)
- [总结](#总结)
- [参考链接](#参考链接)

你好，我是江小湖。评估体系让我们知道 AI 好不好。但好还不够——它还得能"找"。如果你的知识库里存储了大量图片、PDF、视频，用户问"上次那个蓝色的产品原型图在哪"——文字搜索找不到，你需要多模态 RAG。

## 从文字 RAG 到多模态 RAG

### 传统 RAG 的局限

传统 RAG（Retrieval-Augmented Generation）的工作流是：

```
文档 → 切分段落 → 文字嵌入（Embedding）→ 向量数据库
用户提问 → 向量检索 → 找到Top-K相关段落 → LLM生成回答
```

这个流程假设**知识全部是文字形式**。当你的知识库中包含图片、图表、PDF 扫描件时，这个流程就断了——文字 Embedding 看不懂图片。

### 多模态 RAG 要解决的核心问题

问题一：**怎么给图片和视频生成可检索的向量？** 文本有 BERT/OpenAI Embedding API，图片怎么变成可检索的向量？

问题二：**图文混合检索怎么做？** 用户问"那个蓝色的产品界面"——这个问题既有视觉属性（蓝色），又有语义属性（产品界面）。怎么同时检索到视觉上匹配和语义上相关的图片？

问题三：**检索到图片后怎么喂给 LLM？** 传统 RAG 检索到文字段落直接拼接进 Prompt。多模态 RAG 检索到一张图——是把图片本身传给 VLM，还是把图片的文字描述传给 LLM？

## 图像检索：三种策略

### 策略一：基于描述的检索

最直觉的方案——把图片变成文字，然后走传统 RAG 管道：

```
原始图片 → VLM 生成文字描述 → 文字 Embedding → 向量数据库
用户提问 → 文字向量检索 → 找到相关描述 → 返回对应图片
```

**优点**：简单、直接、兼容现有文字 RAG 基础设施。

**缺点**：信息损失。你的图片里可能有一个关键细节（某个按钮的位置、某个数值、某个颜色），但 VLM 在生成描述时没有提到这个细节——那它在检索时就是不可见的。

```python
# 基于描述的图片索引
def index_images_by_description(images):
    for image in images:
        # VLM 生成描述
        description = vlm.describe(image)
        # 文字嵌入
        embedding = text_embedder.embed(description)
        # 存储
        vector_db.insert(
            id=image.id,
            embedding=embedding,
            metadata={"description": description, "image_path": image.path}
        )
```

这个方案适合：图片内容是"一件红色的T恤""一张办公室的照片"这类描述能充分概括的场景。不适合：需要检索精确视觉细节的场景。

### 策略二：基于 CLIP 的视觉嵌入

直接用多模态 Embedding 模型（CLIP 或其改进版 SigLIP）把图片映射到向量空间，在这个空间中做语义检索：

```python
import clip
import torch

model, preprocess = clip.load("ViT-B/32")

def index_images_clip(images):
    for image in images:
        # CLIP 视觉编码 → 512维向量
        image_input = preprocess(image).unsqueeze(0)
        with torch.no_grad():
            image_embedding = model.encode_image(image_input)

        vector_db.insert(
            id=image.id,
            embedding=image_embedding.numpy(),
            metadata={"image_path": image.path}
        )

def search_images_clip(query):
    # 文字查询也是用CLIP编码到同一个512维空间
    text_tokens = clip.tokenize([query])
    with torch.no_grad():
        query_embedding = model.encode_text(text_tokens)

    # 在同一个向量空间中检索图片
    results = vector_db.search(query_embedding.numpy(), top_k=5)
    return results
```

**优点**：
- 不需要文字中介——图片直接变向量，没有描述导致的信息损失
- 图文在同一个语义空间——用户用文字搜图片，天然支持
- CLIP 是免费开源的

**缺点**：
- CLIP 的对齐是"整张图 vs 整段文字"——粒度粗。搜索"图片里戴蓝色帽子的人"，CLIP 可能返回了所有有蓝色元素的图片（蓝天、蓝车、蓝色衣服），而不是专门有蓝色帽子的
- CLIP 的训练数据以自然照片为主——对文档、图表、UI 截图的理解偏弱

### 策略三：多向量混合检索

现代多模态 RAG 的最佳实践——**组合多个 Embedding 模型的信息**：

```python
class HybridImageIndexer:
    def __init__(self):
        self.clip_model = CLIP("ViT-L-14")      # 视觉语义
        self.text_embedder = OpenAIEmbeddings()    # 文字语义
        self.vlm = GPT4oVision()                   # 详细描述

    def index(self, image, metadata=None):
        # 向量一：CLIP 视觉嵌入（捕获非语言化的视觉信息）
        clip_vec = self.clip_model.encode_image(image)
        
        # 向量二：VLM 描述的文字嵌入（捕获显式描述的语义信息）
        description = self.vlm.describe(image)
        desc_vec = self.text_embedder.embed(description)
        
        # 向量三：结构化元数据的嵌入（产品ID、类别等）
        meta_text = f"{metadata.get('product_name', '')} 
                     {metadata.get('category', '')}"
        meta_vec = self.text_embedder.embed(meta_text)
        
        # 存储：一个图片条目关联三个向量
        vector_db.insert_multivector(
            id=image.id,
            vectors=[clip_vec, desc_vec, meta_vec],
            metadata=metadata,
            image=image
        )
    
    def search(self, query, alpha=0.5):
        # 并行检索，加权融合
        clip_results = vector_db.search_clip(query, top_k=20)
        text_results = vector_db.search_text(query, top_k=20)
        
        # 融合排序（reciprocal rank fusion）
        return self._fuse_results(clip_results, text_results, alpha=alpha)
```

多向量方案的思路是：**不同的 Embedding 捕获不同类型的信息，检索时综合利用**。CLIP 捕获视觉直觉（"这张图的调性和那张图很像"），文字嵌入捕获显式语义（"蓝色""产品界面""按钮"），元数据嵌入捕获结构化信息。

## ColPali：PDF 检索的范式转变

传统的 PDF RAG 管道是：

```
PDF → OCR → 提取文字 → 文字Embedding → 检索
      ↑
   问题：表格结构、图片内容、版面信息全丢了
```

ColPali 彻底改变了这个范式——**不对 PDF 做 OCR，直接用视觉语言模型理解 PDF 页面的视觉内容**：

```
PDF 每一页 → 直接作为图片输入 VLM → 生成每页的视觉嵌入 → 检索
               ↑
    文字、表格、图表、版面结构全部保留
```

ColPali 不"读文字后嵌入"，而是"看图后嵌入"。一个包含复杂表格和图表交错排版的 PDF 页面，OCR 会把这些内容切成碎片、丢失版面结构。ColPali 保留了页面的视觉完整性——表格的列对齐、图表的颜色编码、版面的层级结构在嵌入中全部保留。

```python
from colpali import ColPali
from PIL import Image

model = ColPali.from_pretrained("vidore/colpali-v1.2")

def index_pdf_pages(pdf_path):
    pages = convert_pdf_to_images(pdf_path, dpi=200)
    
    page_embeddings = []
    for i, page in enumerate(pages):
        # ColPali 直接对页面图片编码
        embedding = model.encode(page)
        vector_db.insert(
            id=f"{pdf_path}_page_{i}",
            embedding=embedding,
            metadata={"pdf": pdf_path, "page": i, "page_image": page}
        )
        page_embeddings.append(embedding)
    
    return page_embeddings

def search_pdf(query):
    query_embedding = model.encode_text(query)
    results = vector_db.search(query_embedding, top_k=5)
    # 返回最相关的 PDF 页面（包含文字、表格、图表的完整视觉内容）
    return results
```

ColPali 特别适合：学术论文（公式+图表混排）、财务报表（复杂表格）、设计文档（文字+架构图）、法律合同（复杂排版+签章）。传统 OCR+Embedding 在这些场景下的准确率可能只有 60-70%，ColPali 能做到 85-95%。

## 视频和音频检索

### Twelve Labs：语义视频检索

Twelve Labs 是目前最成熟的视频检索 API。它不只是"找到包含特定物体的帧"——而是"用自然语言搜视频片段"：

```python
from twelvelabs import TwelveLabs

client = TwelveLabs(api_key="YOUR_KEY")

# 在视频库中语义搜索
results = client.search(
    query="顾客在收银台用手机支付的片段",
    index_id="store_surveillance"
)

for segment in results:
    print(f"视频: {segment.video_id}")
    print(f"时间: {segment.start:.1f}s - {segment.end:.1f}s")
    print(f"置信度: {segment.confidence:.2f}")
```

### 音频检索

音频检索有两种思路：

**思路一：转写后文字检索**。Whisper 转写成文字 → 文字 Embedding → 文字 RAG。简单但丢失了语调和情感信息。

**思路二：直接音频 Embedding**。用 CLAP（CLIP 的音频版本，Contrastive Language-Audio Pretraining）把音频直接映射到向量空间。文字搜索音频和文字搜索图片的逻辑完全一样——因为 CLAP 用和 CLIP 相同的对比学习思路，把音频和文字对齐到同一个空间。

## 多模态 RAG 的完整架构

一个生产级的多模态 RAG 系统各组件协同：

```
输入层：接收用户的查询（文字、图片或混合）
    ↓
路由层：判断查询类型 → 路由到对应的检索管道
    ├── 纯文字查询 → 文字 Embedding → 文字向量库
    ├── 文字搜图片 → CLIP/SigLIP → 图片向量库
    ├── 图片搜图片 → 直接视觉Embedding → 图片向量库
    └── PDF/文档查询 → ColPali → 文档向量库
    
检索层：多路检索 + 结果融合（RRF / 加权求和）
    ↓
重排序层：用更强的模型对融合后的Top-K结果重新排序
    ↓
生成层：将检索到的内容（文字+图片+表格）送入 LLM/VLM 生成回答
```

### 结果融合策略

多路检索会返回多个排序列表——CLIP 返回一个排序、文字 Embedding 返回另一个排序。怎么融合？

**RRF（Reciprocal Rank Fusion）**是最常用的方案：

```python
def reciprocal_rank_fusion(results_lists, k=60):
    """
    多个检索结果列表的融合排序
    results_lists: [[(doc_id, score), ...], [(doc_id, score), ...]]
    """
    scores = {}
    for results in results_lists:
        for rank, (doc_id, _) in enumerate(results):
            # 排名越靠前权重越高
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    
    # 按融合分数重新排序
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

RRF 不关心原始分数的量纲——CLIP 的余弦相似度和文字 Embedding 的余弦相似度不在同一个数值范围，RRF 只看排名。

## 实战：搭建一个产品文档多模态 RAG

```python
class ProductDocRAG:
    """产品文档多模态 RAG 系统"""
    
    def __init__(self):
        self.clip = CLIP("ViT-L-14")
        self.text_embedder = OpenAIEmbeddings()
        self.vlm = GPT4oVision()
        self.vector_db = Milvus()
        self.colpali = ColPali("vidore/colpali-v1.2")
    
    def index_document(self, file_path):
        """索引入口——自动判断文档类型并选择索引策略"""
        if file_path.endswith(".pdf"):
            return self._index_pdf(file_path)
        elif file_path.endswith((".png", ".jpg", ".jpeg")):
            return self._index_image(file_path)
        elif file_path.endswith(".txt"):
            return self._index_text(file_path)
    
    def _index_pdf(self, pdf_path):
        pages = convert_to_images(pdf_path, dpi=200)
        for i, page in enumerate(pages):
            colpali_vec = self.colpali.encode(page)
            text = ocr_extract(page)
            text_vec = self.text_embedder.embed(text)
            
            self.vector_db.insert_multivector(
                id=f"{pdf_path}_p{i}",
                vectors={"colpali": colpali_vec, "text": text_vec},
                metadata={"source": pdf_path, "page": i, "ocr_text": text[:500]}
            )
    
    def _index_image(self, image_path):
        image = Image.open(image_path)
        clip_vec = self.clip.encode_image(image)
        description = self.vlm.describe(image)
        desc_vec = self.text_embedder.embed(description)
        
        self.vector_db.insert_multivector(
            id=image_path,
            vectors={"clip": clip_vec, "description": desc_vec},
            metadata={"path": image_path, "description": description}
        )
    
    def search(self, query, top_k=5):
        """多路检索 + 融合"""
        # 并行检索
        clip_results = self.vector_db.search("clip", query, top_k=20)
        text_results = self.vector_db.search("text", query, top_k=20)
        colpali_results = self.vector_db.search("colpali", query, top_k=20)
        
        # RRF融合
        fused = reciprocal_rank_fusion(
            [clip_results, text_results, colpali_results], k=60
        )
        
        # 用VLM重排序Top-10
        top_10 = fused[:10]
        reranked = self._rerank_with_vlm(query, top_10)
        
        return reranked[:top_k]
    
    def _rerank_with_vlm(self, query, candidates):
        scored = []
        for doc_id, _ in candidates:
            doc = self.vector_db.get(doc_id)
            # 让VLM判断检索结果和查询的相关性
            relevance = self.vlm.judge_relevance(
                query=query,
                content=doc["image"] if "image" in doc else doc["ocr_text"]
            )
            scored.append((doc_id, relevance))
        return sorted(scored, key=lambda x: x[1], reverse=True)
    
    def answer(self, query):
        results = self.search(query)
        context = []
        for doc_id, _ in results:
            doc = self.vector_db.get(doc_id)
            context.append(doc)  # 包含图片或PDF页面的完整内容
        
        return self.vlm.chat([
            {"role": "system", "content": "基于提供的文档内容回答用户问题。"},
            {"role": "user", "content": [{"type": "text", "text": query}] + [
                {"type": "image_url", "image_url": doc["image"]}
                for doc in context if "image" in doc
            ]}
        ])
```

## 框架选型

| 框架 | 多模态支持 | 部署 | 适合 |
|------|:--:|------|------|
| **LlamaIndex** | 原生支持图片+PDF+ColPali | Python | 需要深度定制管道的开发者 |
| **LangChain** | 基础多模态检索 | Python | 已有 LangChain 项目 |
| **Milvus** | 多向量存储+混合搜索 | Docker/K8s | 大规模生产部署 |
| **Weaviate** | 原生多模态向量 | Docker/云 | 中小规模 |
| **Chroma** | 基础向量存储 | Python | 快速原型 |

## 总结

- 多模态 RAG 的核心突破是**让检索系统"看懂"非文字内容**——不是先转文字再检索，而是直接在视觉/音频空间中检索
- 图像检索三种策略：**描述检索**（简单但信息损失）、**CLIP嵌入**（无损失但粒度和领域局限）、**多向量混合**（生产级最佳实践）
- **ColPali 改变了 PDF 检索**——不对 PDF 做 OCR，直接对页面图片编码，表格/图表/版面的视觉信息完整保留
- 多路检索需要结果融合——**RRF 根据排名融合**，不受不同 Embedding 模型分数尺度的影响
- 多模态 RAG 的检索结果直接包含图片——**最终生成时必须用 VLM**，纯文本 LLM 看不懂检索到的图片内容
- 下一篇从"找信息"转向"管成本"：[成本建模与优化](./03-cost-optimization.md)

## 参考链接

- [ColPali 论文](https://arxiv.org/abs/2407.01449)
- [CLIP 论文](https://arxiv.org/abs/2103.00020)
- [Twelve Labs 文档](https://docs.twelvelabs.io/)
- [LlamaIndex 多模态 RAG](https://docs.llamaindex.ai/en/stable/examples/multi_modal/)
- [Milvus 混合搜索](https://milvus.io/docs/hybrid_search.md)

> 多模态 RAG 让你能从海量图片和文档中找到需要的信息。但每次检索都在烧 Token。下一篇 [成本建模与优化](./03-cost-optimization.md) 教你算清账本。
