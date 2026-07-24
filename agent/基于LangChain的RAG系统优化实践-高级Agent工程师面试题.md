# 基于LangChain的RAG系统优化实践 —— 高级Agent工程师面试题集

> 来源：智泊AI大模型实战课 L2阶段·攻坚篇 | Advanced RAG开发实战工坊
> 参考论文：《Seven Failure Points When Engineering a Retrieval Augmented Generation System》(https://arxiv.org/pdf/2401.05856)

---

## 目录

- [一、RAG商业化痛点与失败点分析](#一rag商业化痛点与失败点分析)
- [二、Advanced RAG架构设计](#二advanced-rag架构设计)
- [三、Pre-Retrieval预检索——索引优化](#三pre-retrieval预检索索引优化)
- [四、Pre-Retrieval预检索——查询优化](#四pre-retrieval预检索查询优化)
- [五、检索优化——混合检索](#五检索优化混合检索)
- [六、Post-Retrieval后检索优化](#六post-retrieval后检索优化)
- [七、LangChain集成与工程落地](#七langchain集成与工程落地)
- [八、综合实战与架构设计](#八综合实战与架构设计)

---

## 一、RAG商业化痛点与失败点分析

### 题目1：RAG系统七大失败点分析（高级）

**题目描述：**
论文《Seven Failure Points When Engineering a Retrieval Augmented Generation System》总结了RAG系统在工程化落地时的七大失败点。请将这些失败点按"索引构建过程"和"查询增强过程"两个阶段进行分类，并针对每个失败点给出至少一种优化方案。

**知识点：** RAG系统架构、失败模式分析、工程化优化策略

**能力等级：** 高级

**参考答案：**

**Index Process（文本向量化构建索引的过程）：**

| 失败点 | 问题描述 | 优化方案 |
|--------|---------|---------|
| Missing Content（内容缺失） | 原始文本中就没有问题的答案 | 增加相应知识库；数据清洗与增强（输入垃圾则输出垃圾）；更好的Prompt设计（让大模型在找不到答案时明确提示） |
| 文档加载准确性和效率 | PDF等文件加载时难以正确提取文字和图片信息 | 针对每种文档格式设计专门的读取器（Parser）；数据清洗与增强 |
| 文档切分的粒度 | 切分大小和位置影响检索上下文完整性和Token消耗 | 内容重叠分块（保持语义连贯性）；基于结构的分块（HTML/Markdown标题段落）；基于递归的分块（多级分隔符迭代）；根据嵌入模型选择最佳块大小（如text-embedding-ada-002在256/512块上效果更好） |

**Query Process（检索增强回答的过程中）：**

| 失败点 | 问题描述 | 优化方案 |
|--------|---------|---------|
| Missed Top Ranked（错过排名靠前的文档） | 相关知识块向量相似度排名不靠前，无法召回 | 增加召回topK数量；Reranking重排序 |
| Not in Context（提取上下文与答案无关） | 召回的内容与问题不相关 | 前述"内容缺失"和"错过排名靠前文档"的综合体现，需从源头优化 |
| Wrong Format（格式错误） | 需要JSON却给了字符串 | Prompt调优；使用PydanticOutputParser校验输出格式；Auto-Fixing自修复 |
| Incomplete（答案不完整） | 答案只回答了问题的一部分 | 问题拆分（引导用户精简问题，或将复杂问题拆成子问题分别回答后汇总） |
| Not Extracted（未提取到答案） | 上下文中有答案但大模型未提取出来 | 提示压缩技术 |
| Incorrect Specificity（答案不够具体或过于具体） | 回答的粒度不当 | 提示词改善；提升基座大模型能力 |

**评分标准：**
- 正确分类两个阶段（2分）
- 每个失败点描述准确且给出有效优化方案（每个1分，共7分）
- 能结合实际场景举例说明（1分）

---

### 题目2：文档切分策略的工程权衡（高级）

**题目描述：**
在RAG系统中，文档切分（Chunking）是一个关键环节。请详细说明以下三种切分策略的原理、优缺点及适用场景：
1. 内容重叠分块（Overlapping Chunking）
2. 基于结构的分块（Structural Chunking）
3. 基于递归的分块（Recursive Chunking）

并讨论：如何根据不同的嵌入模型和文档类型选择合适的chunk_size？

**知识点：** 文档切分策略、嵌入模型特性、Token优化

**能力等级：** 高级

**参考答案：**

**1. 内容重叠分块（Overlapping Chunking）**

- **原理：** 在相邻文本块之间保持一定比例的内容重叠（如overlap=200），确保语义上下文的连贯性
- **优点：** 避免关键信息被切分边界截断；保持跨块语义连贯性
- **缺点：** 增加存储冗余；重复内容可能被多次检索
- **适用场景：** 叙述性文本、技术文档等需要上下文连贯的场景

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,  # 20%重叠率
    separators=["\n\n", "\n", "。", ".", " ", ""]
)
```

**2. 基于结构的分块（Structural Chunking）**

- **原理：** 利用文档的固有结构标记（HTML标签、Markdown标题层级）进行分块，保持内容的逻辑性和完整性
- **优点：** 保留文档结构信息；块内容语义完整
- **缺点：** 依赖文档格式规范；对非结构化文本不适用
- **适用场景：** HTML页面、Markdown文档、有明确标题层级的结构化文档

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
```

**3. 基于递归的分块（Recursive Chunking）**

- **原理：** 使用多级分隔符从粗到细递归拆分：先按`\n\n`（段落）拆分，超过阈值的块再用`\n`（单换行）拆分，以此类推到空格、句号
- **优点：** 通用性强，适用于大多数文本类型；自动适应文本结构
- **缺点：** 可能破坏语义完整性；对特殊格式文本效果不佳
- **适用场景：** 通用文本处理，LangChain默认推荐方案

**Chunk_size选择策略：**

| 嵌入模型 | 推荐Chunk Size | 原因 |
|---------|---------------|------|
| OpenAI text-embedding-ada-002 | 256~512 tokens | 该模型在此范围内Embedding效果最佳 |
| 其他模型 | 参考模型文档 | 不同模型有不同的最佳输入长度 |

还需考虑：
- **文档类型：** 技术文档偏小（256-512），长文章偏大（512-1024）
- **用户查询特征：** 短查询用小chunk，长查询用大chunk
- **Token预算：** 需平衡检索精度和LLM调用成本

**评分标准：**
- 三种策略原理描述准确（各1分，共3分）
- 优缺点分析合理（各1分，共3分）
- Chunk_size选择策略有据可依（2分）
- 包含代码示例（1分）
- 结合实际场景说明（1分）

---

## 二、Advanced RAG架构设计

### 题目3：Advanced RAG三层架构设计（高级）

**题目描述：**
Advanced RAG在传统RAG（Naive RAG）的基础上增加了Pre-Retrieval和Post-Retrieval两个阶段。请详细阐述：
1. Advanced RAG的三层架构（Pre-Retrieval → Retrieval → Post-Retrieval）各阶段的核心目标
2. 与传统RAG相比，每层解决了哪些关键问题？
3. 画出架构流程图并说明各阶段的数据流转

**知识点：** Advanced RAG架构、检索增强全链路优化

**能力等级：** 高级

**参考答案：**

**三层架构核心目标：**

```
用户查询
    │
    ▼
┌──────────────────────────────────────┐
│  Pre-Retrieval（预检索阶段）           │
│  ┌──────────────┬──────────────────┐ │
│  │ 索引优化      │ 查询优化          │ │
│  │ · 摘要索引    │ · Enrich完善问题  │ │
│  │ · 父子索引    │ · Multi-Query    │ │
│  │ · 假设性问题  │ · Decomposition  │ │
│  │ · 元数据索引  │                  │ │
│  └──────────────┴──────────────────┘ │
│  目标：提高索引内容质量 + 明确用户意图  │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Retrieval（检索阶段）                 │
│  · 向量检索（语义相似度）               │
│  · 关键词检索（BM25精确匹配）           │
│  · 混合检索（Hybrid Search）           │
│  · 微调嵌入模型（领域适配）             │
│  目标：确定最相关的上下文               │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│  Post-Retrieval（后检索阶段）          │
│  · RAG-Fusion（RRF重排序）            │
│  · 上下文压缩与过滤                    │
│  · 结果验证与格式校验                  │
│  目标：优化上下文与查询的集成质量       │
└──────────────────┬───────────────────┘
                   ▼
              LLM生成答案
```

**各阶段解决的核心问题：**

| 阶段 | 传统RAG问题 | Advanced RAG解决方案 |
|------|------------|---------------------|
| Pre-Retrieval（索引优化） | 索引质量不高，检索精度低 | 摘要索引、父子索引、假设性问题索引、元数据索引提升索引质量 |
| Pre-Retrieval（查询优化） | 用户查询模糊、不完整 | Enrich引导完善问题、Multi-Query多路召回、Decomposition问题分解 |
| Retrieval | 单一向量检索有局限 | 混合检索（向量+关键词+SQL）、微调嵌入模型适配领域 |
| Post-Retrieval | 检索结果直接输入LLM，信息过载 | RAG-Fusion重排序、上下文压缩过滤，确保最相关内容优先 |

**数据流转说明：**

1. 用户输入原始查询 → Pre-Retrieval查询优化（Enrich/Multi-Query/Decomposition）→ 生成优化后的查询集合
2. 优化查询 → 在Pre-Retrieval优化后的索引上执行检索 → 返回候选文档集
3. 候选文档 → Post-Retrieval重排序和压缩 → 精选Top K上下文
4. 精选上下文 + 原始查询 → LLM → 生成最终答案

**评分标准：**
- 三层架构描述清晰（3分）
- 与传统RAG对比到位（3分）
- 架构图或流程描述准确（2分）
- 数据流转说明完整（2分）

---

## 三、Pre-Retrieval预检索——索引优化

### 题目4：摘要索引（Summary Index）的设计与实现（高级）

**题目描述：**
在RAG系统中，摘要索引（Summary Index）是一种处理半结构化数据（如包含文本和表格的文档）的有效策略。请回答：
1. 摘要索引解决的核心痛点是什么？
2. 描述摘要索引的完整工作流程（包含索引构建和检索两个阶段）
3. 使用LangChain实现一个基本的摘要索引检索器，写出核心代码
4. 摘要质量对检索效果有何影响？如何保证摘要质量？

**知识点：** 摘要索引、半结构化数据处理、LangChain实现

**能力等级：** 高级

**参考答案：**

**1. 核心痛点：**

处理半结构化数据时，传统RAG面临两大挑战：
- **文本拆分破坏表格结构：** 文本拆分可能将表格拆散，破坏数据完整性
- **表格嵌入语义搜索困难：** 表格数据直接Embedding后，语义相似性搜索效果不佳

**2. 完整工作流程：**

**索引构建阶段：**
1. 文档分块 → 对每个文本块，调用LLM生成摘要（summary）
2. 将摘要进行Embedding，存入摘要向量数据库（Summary Database）
3. 保持摘要与原始文本块的映射关系

**检索阶段：**
1. 用户查询向量化 → 在摘要向量数据库中检索最相关的summary
2. 通过映射关系回溯到对应的原始文本块
3. 将原始文本块作为上下文发送给LLM生成答案

**3. LangChain核心代码实现：**

```python
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List

# 步骤1：为每个文档块生成摘要
def generate_summaries(docs: List[Document], llm: ChatOpenAI) -> List[Document]:
    """为每个文档块生成摘要，构建摘要索引"""
    prompt = ChatPromptTemplate.from_template(
        "请为以下文档内容生成一个简洁的摘要，"
        "保留关键信息（包括表格中的重要数据）：\n\n{doc_content}\n\n摘要："
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    
    summary_docs = []
    for doc in docs:
        summary = chain.run(doc_content=doc.page_content)
        # 摘要文档的metadata中保留原始文档引用
        summary_doc = Document(
            page_content=summary,
            metadata={
                "source": doc.metadata.get("source"),
                "original_content": doc.page_content  # 保留原始内容
            }
        )
        summary_docs.append(summary_doc)
    
    return summary_docs

# 步骤2：构建摘要向量数据库
embeddings = OpenAIEmbeddings()
raw_docs = [...]  # 原始文档块
summary_docs = generate_summaries(raw_docs, ChatOpenAI(model="gpt-4o-mini"))
summary_vectorstore = Chroma.from_documents(summary_docs, embeddings)

# 步骤3：基于摘要检索并回溯原始文档
class SummaryRetriever:
    def __init__(self, summary_store: Chroma, k: int = 5):
        self.summary_store = summary_store
        self.k = k
    
    def retrieve(self, query: str) -> List[Document]:
        # 在摘要库中检索
        relevant_summaries = self.summary_store.similarity_search(query, k=self.k)
        
        # 回溯到原始文档
        original_docs = []
        for summary_doc in relevant_summaries:
            original_docs.append(Document(
                page_content=summary_doc.metadata["original_content"],
                metadata={"source": summary_doc.metadata["source"]}
            ))
        
        return original_docs

# 使用示例
retriever = SummaryRetriever(summary_vectorstore, k=5)
context_docs = retriever.retrieve("用户查询")
```

**4. 摘要质量的影响与保证：**

**影响：**
- 摘要过于简单 → 丢失关键信息（如表格数据）→ 检索召回率下降
- 摘要过于冗长 → 失去摘要索引的意义 → 检索效率降低
- 摘要偏题 → 检索结果与用户查询不匹配

**质量保证策略：**
- 设计专门的摘要Prompt，明确要求保留关键数据（数值、表格信息）
- 对摘要长度进行约束（如100-200字）
- 建立摘要质量评估机制（人工抽检 + 自动评估）
- 针对不同内容类型（纯文本、表格、图表）使用不同的摘要策略

**评分标准：**
- 痛点分析准确（2分）
- 工作流程完整清晰（2分）
- 代码实现正确且包含关键步骤（4分）
- 摘要质量讨论深入（2分）

---

### 题目5：父子索引（Parent-Child Index）的核心原理与应用（高级）

**题目描述：**
父子索引是Advanced RAG中解决"检索精度与上下文完整性矛盾"的关键技术。请详细回答：
1. 父子索引解决了什么矛盾？为什么这个矛盾在RAG中至关重要？
2. 描述父子索引的层级结构和检索替换逻辑
3. 列举至少3个适合父子索引的应用场景，并说明原因
4. 使用LangChain实现父子索引检索器

**知识点：** 父子索引、层级化文档结构、检索精度与上下文完整性权衡

**能力等级：** 高级

**参考答案：**

**1. 解决的核心矛盾：**

RAG系统中存在两个相互矛盾的需求：
- **检索精度需求：** 需要较小的文档块（如256 tokens），这样Embedding才能准确反映语义，检索到的内容才精准
- **上下文完整性需求：** 需要较大的文档块（如1024+ tokens），这样LLM才能获得足够的上下文生成全面准确的答案

父子索引通过**分层设计**同时满足这两个需求：用小块（子块）保证检索精度，用大块（父块）保证上下文完整性。

**2. 层级结构与检索替换逻辑：**

```
文档结构：
┌─────────────────────────────────────┐
│           父块（Parent Chunk）        │
│  ┌──────────┬──────────┬──────────┐ │
│  │ 子块 1   │ 子块 2   │ 子块 3   │ │
│  │ (叶子块) │ (叶子块) │ (叶子块) │ │
│  └──────────┴──────────┴──────────┘ │
└─────────────────────────────────────┘

检索流程：
1. 文档被分割成层级化块结构（Parent → Children）
2. 仅对最小的叶子块（子块）进行Embedding和索引
3. 检索时，在子块索引中检索Top K个最相关的叶子块
4. 如果N个叶子块指向同一个父块，用父块替换这些子块
5. 将父块（大文档块）送入LLM生成答案
```

**替换逻辑示例：**
- 检索到子块[2, 3, 5, 7, 8]
- 子块[2, 3]属于父块A，子块[5, 7, 8]属于父块B
- 最终送入LLM的上下文：父块A + 父块B（而非5个零散子块）

**3. 适用场景：**

| 场景 | 适用原因 |
|------|---------|
| 技术文档检索（如API文档） | 每个API有类/方法层级结构，子块是具体方法签名，父块是完整类文档 |
| 书籍内容检索 | 章节-段落层级结构，子块是段落，父块是完整章节 |
| 代码库检索 | 文件-函数层级结构，子块是具体函数，父块是完整文件/模块 |
| 法律文书检索 | 条款-解释层级结构，子块是具体条款，父块是完整法律文书 |

**4. LangChain实现：**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Tuple

class ParentChildRetriever:
    """父子索引检索器"""
    
    def __init__(
        self,
        parent_chunk_size: int = 2000,    # 父块大小
        child_chunk_size: int = 500,      # 子块大小
        child_chunk_overlap: int = 50,
        embeddings: OpenAIEmbeddings = None
    ):
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.embeddings = embeddings or OpenAIEmbeddings()
        
        # 子块 → 父块的映射关系
        self.child_to_parent: Dict[str, str] = {}
        # 父块内容存储
        self.parent_store: Dict[str, Document] = {}
        # 子块向量数据库
        self.child_vectorstore = None
    
    def build_index(self, documents: List[Document]):
        """构建父子索引"""
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.parent_chunk_size,
            chunk_overlap=0
        )
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.child_chunk_size,
            chunk_overlap=self.child_chunk_overlap
        )
        
        child_docs = []
        
        for doc in documents:
            # 1. 先切分成父块
            parent_chunks = parent_splitter.split_documents([doc])
            
            for p_idx, parent_chunk in enumerate(parent_chunks):
                parent_id = f"{doc.metadata.get('source', 'unknown')}_parent_{p_idx}"
                
                # 存储父块
                self.parent_store[parent_id] = parent_chunk
                
                # 2. 将父块进一步切分为子块
                child_chunks = child_splitter.split_documents([parent_chunk])
                
                for c_idx, child_chunk in enumerate(child_chunks):
                    child_id = f"{parent_id}_child_{c_idx}"
                    # 记录子块到父块的映射
                    self.child_to_parent[child_id] = parent_id
                    # 更新子块metadata
                    child_chunk.metadata["child_id"] = child_id
                    child_chunk.metadata["parent_id"] = parent_id
                    child_docs.append(child_chunk)
        
        # 3. 构建子块向量数据库
        self.child_vectorstore = Chroma.from_documents(
            child_docs, self.embeddings
        )
    
    def retrieve(self, query: str, top_k_children: int = 10) -> List[Document]:
        """检索并返回父块文档"""
        # 1. 在子块中检索
        relevant_children = self.child_vectorstore.similarity_search(
            query, k=top_k_children
        )
        
        # 2. 收集涉及的父块（去重，保持顺序）
        seen_parents = set()
        parent_docs = []
        for child in relevant_children:
            parent_id = child.metadata.get("parent_id")
            if parent_id and parent_id not in seen_parents:
                seen_parents.add(parent_id)
                parent_docs.append(self.parent_store[parent_id])
        
        return parent_docs

# 使用示例
retriever = ParentChildRetriever(
    parent_chunk_size=2000,
    child_chunk_size=500
)
retriever.build_index(documents)
results = retriever.retrieve("如何在Python中处理异常？", top_k_children=10)
```

**评分标准：**
- 矛盾分析深入（2分）
- 层级结构和替换逻辑描述清晰（2分）
- 应用场景合理且有说明（2分）
- 代码实现完整且逻辑正确（4分）

---

### 题目6：假设性问题索引（Hypothetical Question Index）的设计思路（高级）

**题目描述：**
假设性问题索引（HQ Index）是一种创新的索引优化策略。请回答：
1. 假设性问题索引的核心思想是什么？与传统直接对文档块Embedding的方式有何本质区别？
2. 描述完整的实现流程，包括索引构建和检索两个阶段
3. 为什么"用问题向量替换文档块向量"能够提升检索效果？
4. 这种策略有什么局限性？

**知识点：** 假设性问题索引、Query-Document对齐、语义检索优化

**能力等级：** 高级

**参考答案：**

**1. 核心思想与本质区别：**

**核心思想：** 在对文档进行切片时，利用LLM以该切片内容为假设条件，预先生成3-5个候选的相关性问题。这些问题与切片内容强相关，用问题的向量表示替代文档块的向量表示存入索引。

**本质区别：**

| 维度 | 传统方式 | 假设性问题索引 |
|------|---------|--------------|
| 索引内容 | 文档块原文 → Embedding | 假设性问题 → Embedding |
| 语义空间 | 文档语义空间 | 问题语义空间 |
| 匹配逻辑 | 用户问题 ↔ 文档块语义 | 用户问题 ↔ 假设性问题语义 |
| 检索效果 | 问题与文档答案的语义可能不直接匹配 | 问题与问题的语义匹配更直接 |

**关键洞察：** 用户查询是"问题"形式，而索引中存储的是"答案"形式的文档块。问题与答案虽然语义相关，但表达方式不同，直接匹配可能存在偏差。将索引统一为"问题"形式后，用户问题与假设性问题之间是同构匹配，检索精度更高。

**2. 完整实现流程：**

**索引构建阶段：**
```
文档块 → LLM生成3个假设性问题 → 问题Embedding → 存入向量数据库
                                        ↓
                              保留原始文档块映射关系
```

**检索阶段：**
```
用户查询 → Embedding → 在问题向量索引中搜索 → 找到最相关的假设性问题
                                                      ↓
                                          回溯到对应的原始文档块
                                                      ↓
                                          将原始文档块作为上下文发送给LLM
```

**3. 为什么效果更好？**

- **语义空间对齐：** 用户查询和假设性问题同属"问题空间"，语义相似度计算更精确
- **多角度覆盖：** 每个文档块生成3个问题，从不同角度覆盖该文档块可能被查询的方式
- **表达多样性：** 预生成的问题模拟了用户可能的各种提问方式，提高了召回率
- **减少语义鸿沟：** 避免了"问题→答案"跨语义空间的匹配误差

**4. 局限性：**

- **LLM生成成本：** 每个文档块需调用LLM 3次生成假设性问题，索引构建成本高
- **问题质量依赖LLM：** 生成的假设性问题质量直接影响检索效果，质量差的LLM可能生成不相关或低质量问题
- **静态性：** 预生成的问题是固定的，无法覆盖用户所有可能的提问方式
- **存储成本：** 每个文档块需要存储多个问题向量，存储开销增大
- **不适合频繁更新的知识库：** 文档更新后需要重新生成问题

**LangChain实现示例：**

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List

class HypotheticalQuestionIndex:
    """假设性问题索引构建器"""
    
    def __init__(self, llm: ChatOpenAI, num_questions: int = 3):
        self.llm = llm
        self.num_questions = num_questions
        
        self.question_prompt = ChatPromptTemplate.from_template(
            """请基于以下文档内容，生成{num_questions}个用户可能会提出的、
            与文档内容强相关的问题。问题应该多样化，覆盖文档中的不同知识点。

            文档内容：
            {doc_content}

            请严格按照以下JSON格式输出，不要输出其他内容：
            {{"questions": ["问题1", "问题2", "问题3"]}}
            """
        )
    
    def generate_questions(self, doc: Document) -> List[str]:
        """为单个文档块生成假设性问题"""
        response = self.llm.invoke(
            self.question_prompt.format(
                num_questions=self.num_questions,
                doc_content=doc.page_content
            )
        )
        # 解析JSON获取问题列表
        import json
        questions = json.loads(response.content)["questions"]
        return questions
    
    def build_hq_index(self, docs: List[Document]) -> List[Document]:
        """构建假设性问题索引"""
        hq_docs = []
        for doc in docs:
            questions = self.generate_questions(doc)
            for q in questions:
                hq_doc = Document(
                    page_content=q,  # 用问题替代文档内容
                    metadata={
                        "original_content": doc.page_content,  # 保留原始文档
                        "source": doc.metadata.get("source")
                    }
                )
                hq_docs.append(hq_doc)
        return hq_docs
```

**评分标准：**
- 核心思想阐述准确（2分）
- 与传统方式对比清晰（2分）
- 实现流程完整（2分）
- 原理分析有深度（2分）
- 局限性分析全面（2分）

---

### 题目7：元数据索引与SelfQueryRetriever（高级）

**题目描述：**
在大型企业知识库中（数百个不同来源和类型的知识文档），元数据索引是一种重要的"分层过滤与检索"策略。请回答：
1. 元数据索引解决的核心痛点是什么？为什么在大文档集下top-k检索不够？
2. 描述LangChain中SelfQueryRetriever的工作原理
3. 实现一个SelfQueryRetriever，支持按topic、author、year等元数据字段过滤
4. 讨论：如何利用LLM自动推理出用户查询中的元数据过滤条件？

**知识点：** 元数据索引、SelfQueryRetriever、分层过滤检索

**能力等级：** 高级

**参考答案：**

**1. 核心痛点：**

当企业知识库包含数百个不同来源和类型的文档时，简单依赖top-k检索会产生：
- **精度不足：** 不同领域的相似术语可能语义相近但实际无关（如"糖尿病足"vs"糖尿病视网膜病变"）
- **知识干扰：** 不同来源和类型的文档混合检索，结果互相干扰
- **召回偏差：** 跨领域的语义相似度比較可能产生误导

**解决方案：** 元数据索引——先通过元数据标签过滤缩小检索范围，再在过滤后的子集中进行向量检索。

**2. SelfQueryRetriever工作原理：**

```
用户查询："2024年关于人工智能的文章"
         │
         ▼
    LLM解析查询
         │
    ┌────┴────┐
    ▼         ▼
 语义查询    元数据过滤条件
 "人工智能"  year=2024, topic="人工智能"
    │         │
    └────┬────┘
         ▼
 向量数据库 → 先过滤再检索 → 返回Top K结果
```

SelfQueryRetriever将用户查询拆分为两部分：
- **查询字符串（query）：** 用于语义检索的纯文本
- **元数据过滤器（filter）：** 用于缩小检索范围的元数据条件

**3. LangChain实现：**

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.schema import Document

# 定义元数据字段
metadata_field_info = [
    AttributeInfo(
        name="topic",
        description="文章主题",
        type="string",
    ),
    AttributeInfo(
        name="author",
        description="文章作者",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="文章发布年份",
        type="integer",
    ),
    AttributeInfo(
        name="source_type",
        description="文章来源类型（论文、博客、官方文档等）",
        type="string",
    ),
]

# 文档内容描述
document_content_description = "科技博客文章和技术文档"

# 构建向量数据库
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 准备带元数据的文档
documents = [
    Document(
        page_content="LangChain是一个用于构建LLM应用的开源框架...",
        metadata={"topic": "人工智能", "author": "作者A", "year": 2024, "source_type": "博客"}
    ),
    Document(
        page_content="区块链技术通过分布式账本实现去中心化...",
        metadata={"topic": "区块链", "author": "作者B", "year": 2023, "source_type": "论文"}
    ),
    # ... 更多文档
]

vectorstore = Chroma.from_documents(documents, embeddings)

# 构建SelfQueryRetriever
self_query_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents=document_content_description,
    metadata_field_info=metadata_field_info,
    verbose=True
)

# 使用示例
# 查询："2024年作者A写的关于人工智能的文章"
results = self_query_retriever.invoke(
    "2024年作者A写的关于人工智能的LangChain应用"
)
# LLM自动解析为：
# query: "LangChain应用"
# filter: topic="人工智能" AND author="作者A" AND year=2024
```

**4. LLM自动推理元数据过滤条件：**

LLM通过以下步骤自动推理过滤条件：

1. **识别查询意图：** 分析用户查询中是否包含元数据相关的约束条件
2. **提取实体信息：** 识别年份、人名、主题等实体
3. **映射到元数据字段：** 将提取的实体与预定义的元数据字段进行匹配
4. **构建过滤表达式：** 生成结构化的过滤条件（如 `$and: [{topic: "人工智能"}, {year: 2024}]`）
5. **分离语义查询：** 将过滤条件之外的部分作为语义查询字符串

**关键设计要点：**
- 元数据字段定义要清晰，description字段帮助LLM准确理解
- 如果文档本身没有元数据标签，可先用LLM为文档推理生成元数据
- 过滤条件支持 `$eq`、`$ne`、`$gt`、`$gte`、`$lt`、`$lte`、`$in`、`$and`、`$or` 等操作符

**评分标准：**
- 痛点分析准确（2分）
- 工作原理描述清晰（2分）
- 代码实现完整（4分）
- LLM推理机制讨论深入（2分）

---

### 题目8：索引优化策略的综合选型（高级）

**题目描述：**
PPT中介绍了四种索引优化策略（摘要索引、父子索引、假设性问题索引、元数据索引）。请完成以下案例分析：

1. **新闻资讯平台：** 每天新增数千条新闻，用户需要快速获取新闻摘要
2. **法律检索系统：** 用户查询具体法律条款，需要完整的上下文解释
3. **药品咨询系统：** 用户描述症状，查询相关药品信息
4. **电商推荐系统：** 根据用户偏好（价格、品牌、类别）筛选和推荐商品

分别选择最合适的索引策略（可组合），并说明理由。

**知识点：** 索引策略综合应用、场景分析

**能力等级：** 高级

**参考答案：**

| 场景 | 推荐策略 | 理由 |
|------|---------|------|
| 新闻资讯平台 | **摘要索引** + 元数据索引 | 新闻量大，摘要索引可快速检索并生成简洁上下文；元数据索引可按时间、类别、来源过滤 |
| 法律检索系统 | **父子索引** + 假设性问题索引 | 父子索引保证条款检索精度和上下文完整性（条款→完整法律文书）；假设性问题覆盖用户多样化的法律提问方式 |
| 药品咨询系统 | **假设性问题索引** + 父子索引 | 用户症状描述多样（"感冒了吃什么药？"），假设性问题覆盖多种提问；父子索引保证药品说明完整性 |
| 电商推荐系统 | **元数据索引** + 摘要索引 | 元数据索引快速筛选价格、品牌、类别；摘要索引在筛选后精准检索商品描述 |

**选型决策框架：**

```
是否需要精确过滤？ → 是 → 元数据索引
是否需要上下文完整性？ → 是 → 父子索引
用户查询是否多样化？ → 是 → 假设性问题索引
是否需要快速检索和简洁上下文？ → 是 → 摘要索引
```

**评分标准：**
- 每个场景分析合理（每个2分，共8分）
- 能说明组合使用的原因（2分）

---

## 四、Pre-Retrieval预检索——查询优化

### 题目9：Enrich完善问题——多轮对话引导策略（高级）

**题目描述：**
在RAG应用中，用户往往通过口语化、简略的方式表达需求，导致查询模糊。Enrich策略通过LLM主动引导沟通来完善用户意图。请回答：
1. 用户口语化表达的常见问题有哪些？举例说明
2. 设计一个Enrich对话流程，包含意图识别、缺失信息追问、最终确认三个环节
3. 实现一个基于LangChain的Enrich查询优化器

**知识点：** 查询优化、多轮对话、意图识别

**能力等级：** 高级

**参考答案：**

**1. 用户口语化表达的常见问题：**

| 问题类型 | 示例 | 影响 |
|---------|------|------|
| 表达过于简略 | "那个怎么配置？" | 缺少主语和上下文，LLM无法理解 |
| 语义歧义 | "苹果多少钱？" | 无法区分是水果还是手机品牌 |
| 隐含要素缺失 | "帮我查一下" | 缺少查询对象、时间范围等关键参数 |
| 模糊描述 | "最近的那个东西" | 指代不明，无法确定查询目标 |
| 多意图混合 | "帮我查订单和物流" | 在同一查询中包含多个独立意图 |

**2. Enrich对话流程设计：**

```
┌──────────────────────────────────────────────┐
│              Enrich对话流程                     │
├──────────────────────────────────────────────┤
│                                               │
│  用户输入: "帮我查一下那个配置"                 │
│       │                                       │
│       ▼                                       │
│  ┌─────────────┐                              │
│  │ 意图识别     │ → 识别为"配置查询"类          │
│  └──────┬──────┘                              │
│         ▼                                     │
│  ┌─────────────┐                              │
│  │ 槽位检查     │ → 发现缺失: 系统名称、配置项   │
│  └──────┬──────┘                              │
│         ▼                                     │
│  ┌─────────────┐                              │
│  │ 主动追问     │ → "请问您想查询哪个系统的配置？  │
│  │              │    是数据库配置、服务配置还是   │
│  │              │    应用配置？"                │
│  └──────┬──────┘                              │
│         ▼                                     │
│  ┌─────────────┐                              │
│  │ 信息补全     │ → 用户: "数据库配置"          │
│  └──────┬──────┘                              │
│         ▼                                     │
│  ┌─────────────┐                              │
│  │ 槽位检查     │ → 仍有缺失: 具体配置项        │
│  └──────┬──────┘                              │
│         ▼                                     │
│  ┌─────────────┐                              │
│  │ 再次追问     │ → "数据库配置包含连接池、超时、 │
│  │              │    字符集等，您想了解哪一项？"  │
│  └──────┬──────┘                              │
│         ▼                                     │
│  ┌─────────────┐                              │
│  │ 最终确认     │ → "您想查询数据库连接池配置，   │
│  │              │    对吗？"                    │
│  └──────┬──────┘                              │
│         ▼                                     │
│  完善后的查询: "数据库连接池配置参数"            │
│                                               │
└──────────────────────────────────────────────┘
```

**3. LangChain实现：**

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import Dict, List, Optional
import json

class EnrichQueryOptimizer:
    """Enrich查询优化器 - 通过多轮对话完善用户意图"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.max_rounds = 3  # 最多追问3轮
        
        # 意图识别与槽位提取Prompt
        self.intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个查询意图分析助手。分析用户查询，输出JSON格式：

            {{
                "intent": "查询意图类型",
                "clarity_score": 1-10,  // 查询清晰度评分，1=非常模糊，10=非常清晰
                "extracted_slots": {{   // 已提取的槽位信息
                    "subject": "查询主题",
                    "scope": "查询范围",
                    "time_range": "时间范围",
                    "constraints": ["约束条件"]
                }},
                "missing_slots": ["缺失的关键信息"],
                "clarification_question": "如果clarity_score<7，生成追问问题"
            }}
            
            只输出JSON，不要输出其他内容。"""),
            ("human", "用户查询：{query}")
        ])
        
        # 最终查询生成Prompt
        self.consolidation_prompt = ChatPromptTemplate.from_messages([
            ("system", """基于以下对话历史，将用户意图完善为清晰、完整的查询语句。
            输出一个可以直接用于RAG检索的优化查询。"""),
            ("human", "对话历史：\n{conversation_history}\n\n请生成优化后的查询：")
        ])
    
    def enrich(self, query: str, conversation_history: List = None) -> Dict:
        """执行Enrich流程，返回完善后的查询和对话历史"""
        if conversation_history is None:
            conversation_history = []
        
        conversation_history.append(HumanMessage(content=query))
        
        for round_num in range(self.max_rounds):
            # 1. 意图识别与槽位检查
            intent_response = self.llm.invoke(
                self.intent_prompt.format(query=query)
            )
            intent_data = json.loads(intent_response.content)
            
            clarity_score = intent_data.get("clarity_score", 5)
            
            # 2. 如果清晰度足够，生成最终查询
            if clarity_score >= 7:
                consolidation = self.llm.invoke(
                    self.consolidation_prompt.format(
                        conversation_history=self._format_history(conversation_history)
                    )
                )
                return {
                    "enriched_query": consolidation.content,
                    "clarity_score": clarity_score,
                    "rounds": round_num + 1,
                    "conversation_history": conversation_history
                }
            
            # 3. 如果不够清晰，生成追问
            clarification = intent_data.get("clarification_question", "请提供更多信息")
            conversation_history.append(AIMessage(content=clarification))
            
            # 在实际应用中，这里会等待用户回复
            # 这里返回追问信息，由上层处理
            return {
                "needs_clarification": True,
                "clarification_question": clarification,
                "missing_slots": intent_data.get("missing_slots", []),
                "clarity_score": clarity_score,
                "rounds": round_num + 1,
                "conversation_history": conversation_history
            }
        
        # 达到最大轮数，强制生成最终查询
        consolidation = self.llm.invoke(
            self.consolidation_prompt.format(
                conversation_history=self._format_history(conversation_history)
            )
        )
        return {
            "enriched_query": consolidation.content,
            "clarity_score": clarity_score,
            "rounds": self.max_rounds,
            "conversation_history": conversation_history
        }
    
    def _format_history(self, history: List) -> str:
        return "\n".join([
            f"{'用户' if isinstance(m, HumanMessage) else '助手'}: {m.content}"
            for m in history
        ])

# 使用示例
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
optimizer = EnrichQueryOptimizer(llm)

result = optimizer.enrich("帮我查一下那个配置")
if result.get("needs_clarification"):
    print(f"系统追问: {result['clarification_question']}")
    # 获取用户回复后继续
    result2 = optimizer.enrich(
        "数据库连接池配置",
        conversation_history=result["conversation_history"]
    )
    print(f"优化后查询: {result2.get('enriched_query')}")
```

**评分标准：**
- 口语化问题分析全面（2分）
- 对话流程设计合理（3分）
- 代码实现完整可用（4分）
- 包含意图识别和槽位填充逻辑（1分）

---

### 题目10：Multi-Query多路召回的原理与实现（高级）

**题目描述：**
Multi-Query是查询优化中的重要策略，通过LLM生成多个相关查询来提升召回率。请回答：
1. Multi-Query解决的核心问题是什么？与单查询检索相比的优势在哪里？
2. 描述Multi-Query的完整工作流程
3. 实现一个基于LangChain的Multi-Query检索器
4. 讨论：Multi-Query可能带来哪些副作用？如何缓解？

**知识点：** Multi-Query、多路召回、查询扩展

**能力等级：** 高级

**参考答案：**

**1. 核心问题与优势：**

**核心问题：** 用户查询语句可能存在表达不准确、视角单一等问题，LLM无法正确理解导致答案不完整。

**优势对比：**

| 维度 | 单查询检索 | Multi-Query多路召回 |
|------|----------|-------------------|
| 召回广度 | 单一视角，可能遗漏相关内容 | 多视角覆盖，召回更全面 |
| 鲁棒性 | 对查询措辞敏感 | 多个查询相互补充，降低措辞偏差 |
| 答案完整性 | 可能不完整 | 综合多路结果，答案更完整 |
| 适用场景 | 简单明确查询 | 复杂、模糊、多义查询 |

**2. 完整工作流程：**

```
用户原始查询: "LangChain怎么用？"
         │
         ▼
    LLM生成N个相关查询:
         │
    ┌────┼────┬────────────┐
    ▼    ▼     ▼            ▼
  Q1   Q2    Q3           Q4
  "LangChain  "LangChain  "LangChain  "LangChain
   入门教程"  基本概念"    Chain用法"  实际案例"
    │    │     │            │
    ▼    ▼     ▼            ▼
  各自在向量数据库中检索
    │    │     │            │
    └────┴─────┴────────────┘
              │
              ▼
    合并所有检索结果（去重）
              │
              ▼
    将所有文档喂给LLM生成答案
```

**3. LangChain实现：**

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List
import json

class MultiQueryRetriever:
    """多路召回检索器"""
    
    def __init__(
        self,
        llm: ChatOpenAI,
        vectorstore: Chroma,
        num_queries: int = 3,
        k_per_query: int = 4
    ):
        self.llm = llm
        self.vectorstore = vectorstore
        self.num_queries = num_queries
        self.k_per_query = k_per_query
        
        self.query_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个查询扩展助手。基于用户的原始查询，生成{num_queries}个
            相关但不同视角的查询问题。这些查询应该从不同角度补充原始查询，帮助更全面地检索信息。

            要求：
            1. 每个查询应从不同角度出发
            2. 查询之间应有明显差异
            3. 保持与原查询的语义相关性

            严格按照JSON格式输出：
            {{"queries": ["查询1", "查询2", "查询3"]}}
            """),
            ("human", "原始查询: {query}")
        ])
    
    def generate_queries(self, query: str) -> List[str]:
        """生成多个相关查询"""
        response = self.llm.invoke(
            self.query_generation_prompt.format(
                num_queries=self.num_queries,
                query=query
            )
        )
        queries_data = json.loads(response.content)
        return queries_data.get("queries", [])
    
    def retrieve(self, query: str) -> List[Document]:
        """执行多路检索"""
        # 1. 生成相关查询
        expanded_queries = self.generate_queries(query)
        all_queries = [query] + expanded_queries  # 包含原始查询
        
        # 2. 对每个查询分别检索
        all_docs = []
        seen_content = set()  # 用于去重
        
        for q in all_queries:
            docs = self.vectorstore.similarity_search(q, k=self.k_per_query)
            for doc in docs:
                # 基于内容去重
                content_hash = hash(doc.page_content[:100])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    doc.metadata["source_query"] = q  # 标记来源查询
                    all_docs.append(doc)
        
        return all_docs

# 使用示例
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

multi_retriever = MultiQueryRetriever(
    llm=llm,
    vectorstore=vectorstore,
    num_queries=3,
    k_per_query=4
)

results = multi_retriever.retrieve("LangChain怎么用？")
print(f"检索到 {len(results)} 个文档")
```

**4. 副作用与缓解策略：**

**潜在副作用：**

| 副作用 | 描述 | 缓解策略 |
|--------|------|---------|
| Token消耗增加 | 多个查询 × 多个结果 = 大量上下文 | 限制总文档数；使用上下文压缩 |
| 检索噪声 | 不相关查询可能引入无关文档 | 后检索重排序（RAG-Fusion）；相似度阈值过滤 |
| 响应延迟 | 串行执行多个检索 | 并行执行多个查询的检索 |
| LLM生成成本 | 每次查询都需调用LLM生成扩展查询 | 缓存常见查询的扩展结果；使用更便宜的模型生成扩展查询 |
| 结果冗余 | 不同查询检索到相同文档 | 基于内容哈希去重（已在代码中实现） |

**缓解方案总结：**
```python
# 改进版：并行检索 + 重排序 + 数量限制
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedMultiQueryRetriever(MultiQueryRetriever):
    def retrieve(self, query: str) -> List[Document]:
        expanded_queries = self.generate_queries(query)
        all_queries = [query] + expanded_queries
        
        # 并行检索（使用线程池）
        with ThreadPoolExecutor(max_workers=len(all_queries)) as executor:
            futures = [
                executor.submit(
                    self.vectorstore.similarity_search, q, self.k_per_query
                )
                for q in all_queries
            ]
            all_results = [f.result() for f in futures]
        
        # 合并去重
        seen = set()
        merged = []
        for docs in all_results:
            for doc in docs:
                h = hash(doc.page_content[:100])
                if h not in seen:
                    seen.add(h)
                    merged.append(doc)
        
        return merged[:10]  # 限制最大返回数量
```

**评分标准：**
- 核心问题分析准确（2分）
- 工作流程描述清晰（2分）
- 代码实现完整（4分）
- 副作用分析与缓解策略合理（2分）

---

### 题目11：Decomposition问题分解——并行与串行策略（高级）

**题目描述：**
当用户提出复杂问题时，大模型可能不具备直接推理能力。Decomposition策略通过将复杂问题拆解为子问题来解决。请回答：
1. 什么是CoT（Chain of Thought）策略？它在问题分解中的作用是什么？
2. 对比并行执行和串行执行两种子任务策略的优缺点和适用场景
3. 实现一个Decomposition问题分解器，支持并行和串行两种模式

**知识点：** 问题分解、CoT策略、并行/串行执行模式

**能力等级：** 高级

**参考答案：**

**1. CoT策略与问题分解：**

CoT（Chain of Thought，思维链）是一种提示词工程策略，通过引导LLM逐步推理来分解复杂问题。

**在问题分解中的角色：**
- 将复杂问题拆解为逻辑上相互关联的子问题
- 每个子问题对应一个推理步骤
- 子问题之间形成依赖关系（DAG有向无环图）

**示例：**
```
原始问题："对比分析2023年和2024年人工智能在医疗领域的投资趋势"

CoT分解：
1. 2023年AI医疗领域投资总额是多少？
2. 2024年AI医疗领域投资总额是多少？
3. 主要投资领域和方向有哪些变化？
4. 增长率如何？变化原因是什么？
→ 汇总以上答案，形成对比分析
```

**2. 并行 vs 串行执行对比：**

| 维度 | 并行执行 | 串行执行 |
|------|---------|---------|
| **执行方式** | 所有子问题同时执行，最后汇总 | 依次执行，前一个答案作为下一个的提示词 |
| **适用场景** | 子问题之间无依赖关系 | 子问题之间有强依赖关系 |
| **响应速度** | 快（所有子问题同时处理） | 慢（需等待前序子问题完成） |
| **准确性** | 各子问题独立，互不影响 | 后序问题可利用前序答案，更准确 |
| **Token消耗** | 较高（所有子问题+答案） | 逐轮累积，可能更高 |
| **典型场景** | 多维度对比分析、独立信息查询 | 多步推理、因果链分析 |

**示例对比：**

并行场景：
```
"对比Python、Java、Go在Web开发中的优缺点"
→ 子问题1: Python Web开发优缺点（独立）
→ 子问题2: Java Web开发优缺点（独立）
→ 子问题3: Go Web开发优缺点（独立）
→ 汇总比较
```

串行场景：
```
"某公司2023年Q1利润下降15%，Q2恢复增长，Q3同比增长20%，全年利润率如何？"
→ 子问题1: 计算Q1利润（前提）
→ 子问题2: 基于Q1计算Q2利润（依赖Q1）
→ 子问题3: 基于Q2计算Q3利润（依赖Q2）
→ 得出结论
```

**3. LangChain实现：**

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List, Dict, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class DecompositionRetriever:
    """问题分解检索器 - 支持并行和串行两种模式"""
    
    def __init__(self, llm: ChatOpenAI, vectorstore, retriever):
        self.llm = llm
        self.vectorstore = vectorstore
        self.retriever = retriever
        
        # 问题分解Prompt
        self.decomposition_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个问题分解专家。将复杂问题拆解为多个子问题。

            分析子问题之间的依赖关系：
            - 如果子问题可以独立回答，标记为"parallel"
            - 如果子问题需要前序子问题的答案，标记为"sequential"

            严格按照JSON格式输出：
            {{
                "sub_questions": [
                    {{
                        "question": "子问题内容",
                        "type": "parallel|sequential",
                        "depends_on": [依赖的子问题索引，parallel类型为空数组]
                    }}
                ]
            }}
            """),
            ("human", "复杂问题：{query}")
        ])
        
        # 答案汇总Prompt
        self.aggregation_prompt = ChatPromptTemplate.from_messages([
            ("system", """基于以下子问题的答案，汇总生成最终答案。
            确保答案完整、连贯，覆盖原始问题的所有方面。"""),
            ("human", """原始问题：{query}

            子问题及答案：
            {sub_answers}

            请生成最终答案：""")
        ])
    
    def decompose(self, query: str) -> List[Dict]:
        """分解复杂问题"""
        response = self.llm.invoke(
            self.decomposition_prompt.format(query=query)
        )
        return json.loads(response.content)["sub_questions"]
    
    def _solve_single_question(self, question: str) -> str:
        """解决单个子问题"""
        docs = self.retriever.retrieve(question)
        context = "\n\n".join([d.page_content for d in docs])
        
        answer_prompt = ChatPromptTemplate.from_messages([
            ("system", "基于上下文回答问题。"),
            ("human", "上下文：\n{context}\n\n问题：{question}\n\n答案：")
        ])
        
        response = self.llm.invoke(
            answer_prompt.format(context=context, question=question)
        )
        return response.content
    
    def solve_parallel(self, sub_questions: List[Dict]) -> List[str]:
        """并行执行所有子问题"""
        answers = [None] * len(sub_questions)
        
        with ThreadPoolExecutor(max_workers=len(sub_questions)) as executor:
            futures = {
                executor.submit(self._solve_single_question, sq["question"]): i
                for i, sq in enumerate(sub_questions)
            }
            for future in as_completed(futures):
                idx = futures[future]
                answers[idx] = future.result()
        
        return answers
    
    def solve_sequential(self, sub_questions: List[Dict]) -> List[str]:
        """串行执行子问题"""
        answers = []
        previous_answers = ""
        
        for sq in sub_questions:
            question = sq["question"]
            # 如果有前序答案，附加到问题中
            if previous_answers:
                question = f"已知信息：{previous_answers}\n\n当前问题：{question}"
            
            answer = self._solve_single_question(question)
            answers.append(answer)
            previous_answers += f"\n{answer}"
        
        return answers
    
    def solve(self, query: str) -> str:
        """完整解决流程"""
        # 1. 分解问题
        sub_questions = self.decompose(query)
        
        # 2. 根据类型选择执行策略
        has_sequential = any(sq["type"] == "sequential" for sq in sub_questions)
        
        if has_sequential:
            answers = self.solve_sequential(sub_questions)
        else:
            answers = self.solve_parallel(sub_questions)
        
        # 3. 汇总答案
        sub_answers = "\n".join([
            f"子问题{i+1}: {sq['question']}\n答案: {ans}"
            for i, (sq, ans) in enumerate(zip(sub_questions, answers))
        ])
        
        final_response = self.llm.invoke(
            self.aggregation_prompt.format(
                query=query,
                sub_answers=sub_answers
            )
        )
        
        return final_response.content

# 使用示例
solver = DecompositionRetriever(llm, vectorstore, retriever)
answer = solver.solve("对比2023年和2024年AI在医疗和金融领域的投资趋势差异")
print(answer)
```

**执行策略选择流程图：**

```
复杂问题
    │
    ▼
问题分解（LLM + CoT）
    │
    ▼
子问题依赖分析
    │
    ├── 全部独立 → 并行执行 → 汇总
    │
    └── 存在依赖 → 串行执行 → 汇总
```

**评分标准：**
- CoT策略解释清晰（2分）
- 并行/串行对比分析到位（2分）
- 代码实现完整且支持两种模式（4分）
- 依赖分析逻辑合理（2分）

---

## 五、检索优化——混合检索

### 题目12：混合检索（Hybrid Search）的架构设计与实现（高级）

**题目描述：**
混合检索通过组合多种检索技术来弥补单一检索方式的不足。请回答：
1. 向量检索、关键词检索（BM25）、SQL检索各自的优势和局限性
2. 设计一个混合检索架构，说明如何融合向量检索和BM25检索的结果
3. 实现一个基于LangChain的混合检索器
4. 讨论：在什么场景下应该使用混合检索？什么场景下单一检索就足够？

**知识点：** 混合检索、BM25、向量检索、检索融合

**能力等级：** 高级

**参考答案：**

**1. 三种检索技术对比：**

| 维度 | 向量检索 | BM25关键词检索 | SQL检索 |
|------|---------|--------------|---------|
| **优势** | 捕捉语义相似性；理解同义词和近义词；处理自然语言查询 | 精确匹配关键词；适合专有名词和代码；可解释性强 | 精确结构化查询；支持复杂过滤条件；高效索引 |
| **局限** | 语义漂移；专有名词效果差；向量空间表示能力有限 | 无法理解语义；对自然语言不友好；同义词无法匹配 | 无法处理非结构化文本；需要预定义Schema |
| **适用数据** | 非结构化文本 | 长文本、技术文档 | 结构化数据库 |
| **典型场景** | 语义搜索、FAQ匹配 | 代码搜索、精确术语查找 | 报表查询、数据统计 |

**2. 混合检索架构设计：**

```
用户查询: "2024年AI Agent的最新进展"
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
    ┌─────────┐      ┌─────────┐       ┌─────────┐
    │ 向量检索  │      │BM25检索  │       │ 元数据过滤│
    │(语义相似) │      │(关键词)  │       │(year=2024)│
    └────┬────┘      └────┬────┘       └────┬────┘
         │                │                  │
         ▼                ▼                  ▼
    ┌─────────────────────────────────────────┐
    │           结果融合层（Fusion）            │
    │  ┌─────────────────────────────────┐    │
    │  │  RRF (Reciprocal Rank Fusion)   │    │
    │  │  或 加权分数融合                  │    │
    │  └─────────────────────────────────┘    │
    └────────────────────┬────────────────────┘
                         ▼
                  Top K 最终结果
```

**3. LangChain实现：**

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from typing import List, Tuple
import numpy as np

class HybridRetriever:
    """混合检索器 - 融合向量检索和BM25检索"""
    
    def __init__(
        self,
        documents: List[Document],
        embeddings: OpenAIEmbeddings = None,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5
    ):
        self.embeddings = embeddings or OpenAIEmbeddings()
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        
        # 构建向量检索器
        self.vectorstore = Chroma.from_documents(documents, self.embeddings)
        self.vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 20}
        )
        
        # 构建BM25检索器
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.bm25_retriever.k = 20
        
        # 使用LangChain内置的EnsembleRetriever（基于RRF）
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.vector_retriever, self.bm25_retriever],
            weights=[vector_weight, bm25_weight]
        )
    
    def retrieve_with_scores(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """检索并返回带分数的文档"""
        # 1. 向量检索
        vector_results = self.vectorstore.similarity_search_with_score(query, k=20)
        vector_scores = {doc.page_content: score for doc, score in vector_results}
        
        # 2. BM25检索
        bm25_results = self.bm25_retriever.get_relevant_documents(query)
        
        # 3. RRF融合
        return self._rrf_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            k=60,
            top_k=top_k
        )
    
    def _rrf_fusion(
        self,
        vector_results: List[Tuple[Document, float]],
        bm25_results: List[Document],
        k: int = 60,
        top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Reciprocal Rank Fusion (RRF) 融合算法
        
        RRF_score(d) = Σ(1 / (k + rank_i(d)))
        
        其中:
        - rank_i(d) 是文档d在第i个检索系统中的排名（从1开始）
        - k 是平滑常数（通常设为60）
        """
        rrf_scores = {}
        doc_map = {}
        
        # 处理向量检索结果
        for rank, (doc, score) in enumerate(vector_results, start=1):
            doc_id = doc.page_content[:100]
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
        
        # 处理BM25检索结果
        for rank, doc in enumerate(bm25_results, start=1):
            doc_id = doc.page_content[:100]
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
        
        # 按RRF分数排序
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [(doc_map[doc_id], score) for doc_id, score in sorted_docs[:top_k]]
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """检索并返回文档列表"""
        results = self.retrieve_with_scores(query, top_k)
        return [doc for doc, _ in results]

# 使用示例
documents = [...]  # 文档列表
hybrid_retriever = HybridRetriever(
    documents=documents,
    vector_weight=0.5,
    bm25_weight=0.5
)

results = hybrid_retriever.retrieve("2024年AI Agent的最新进展", top_k=5)
for i, doc in enumerate(results):
    print(f"排名 {i+1}: {doc.page_content[:100]}...")
```

**RRF公式详解：**

```
RRF_score(d) = Σ(1 / (k + rank_i(d)))

其中：
- N: 参与融合的检索列表数量（BM25+向量检索则N=2）
- rank_i(d): 文档d在第i个检索系统中的排名（从1开始计数）
- k: 平滑常数，通常设为60

示例：
检索系统1（向量）排名: A=2, B=1, C=3, D=4
检索系统2（BM25）排名: D=1, A=3, B=2, C=4

RRF(A) = 1/(60+2) + 1/(60+3) = 0.0161 + 0.0159 = 0.0320
RRF(B) = 1/(60+1) + 1/(60+2) = 0.0164 + 0.0161 = 0.0325
RRF(C) = 1/(60+3) + 1/(60+4) = 0.0159 + 0.0156 = 0.0315
RRF(D) = 1/(60+4) + 1/(60+1) = 0.0156 + 0.0164 = 0.0320

最终排名: B > A = D > C
```

**4. 场景选择指南：**

| 使用混合检索 | 单一检索足够 |
|------------|-----------|
| 异构数据（文本+表格+代码） | 同质化纯文本数据 |
| 需要精确匹配（专有名词、代码） | 纯语义理解场景 |
| 高准确率+召回率要求（医疗、法律） | 简单FAQ匹配 |
| 静态知识+实时数据融合 | 单一知识库检索 |
| 查询同时包含语义和关键词 | 查询明确且单一 |

**评分标准：**
- 三种技术对比分析准确（3分）
- 架构设计合理（2分）
- 代码实现完整且包含RRF融合（4分）
- 场景选择分析有深度（1分）

---

## 六、Post-Retrieval后检索优化

### 题目13：RAG-Fusion与RRF重排序（高级）

**题目描述：**
RAG-Fusion是在Multi-Query基础上结合RRF（Reciprocal Rank Fusion）进行结果重排序的策略。请回答：
1. RAG-Fusion与单纯的Multi-Query有什么区别？核心价值在哪里？
2. 详细解释RRF算法的数学原理，并举例说明
3. 实现一个完整的RAG-Fusion检索器
4. 讨论：RRF与基于分数的加权融合（Weighted Score Fusion）各自的优缺点

**知识点：** RAG-Fusion、RRF算法、检索结果重排序

**能力等级：** 高级

**参考答案：**

**1. RAG-Fusion vs Multi-Query：**

| 维度 | Multi-Query | RAG-Fusion |
|------|-----------|------------|
| 查询扩展 | 生成多个相关查询 | 同Multi-Query |
| 结果处理 | 直接合并所有检索结果 | 对多路检索结果进行RRF重排序 |
| 输出质量 | 包含所有结果，可能有噪声 | 精选Top K最相关文档 |
| 核心价值 | 提升召回率 | 提升召回率 + 提升精确率 |

**RAG-Fusion的核心价值：** 在Multi-Query扩展召回的基础上，通过RRF重排序过滤掉不相关文档，确保输入LLM的上下文既全面又精准。

**2. RRF算法数学原理：**

**公式：**
```
RRF_score(d) = Σ_{i=1}^{N} (1 / (k + rank_i(d)))
```

**参数说明：**
- `N`：参与融合的检索系统数量
- `rank_i(d)`：文档d在第i个检索系统中的排名（从1开始）
- `k`：平滑常数（通常为60），防止排名靠前的文档获得过高的权重

**为什么用倒数排名？**
- 排名靠前的文档获得更高分数
- 排名靠后的文档分数迅速衰减
- 平滑常数k避免第1名和第2名分数差距过大

**计算示例：**
```
假设有3个查询（N=3），检索结果排名如下：

        查询1    查询2    查询3
文档A:   第1名    第2名    未出现
文档B:   第3名    第1名    第2名
文档C:   第2名    第3名    第1名

RRF(A) = 1/(60+1) + 1/(60+2) = 0.0164 + 0.0161 = 0.0325
RRF(B) = 1/(60+3) + 1/(60+1) + 1/(60+2) = 0.0159 + 0.0164 + 0.0161 = 0.0484
RRF(C) = 1/(60+2) + 1/(60+3) + 1/(60+1) = 0.0161 + 0.0159 + 0.0164 = 0.0484

最终排名: B = C > A（B和C被所有查询检索到，排名更高）
```

**关键洞察：** RRF天然偏好"被多个检索系统一致认可"的文档，而非仅在单一系统中排名极高的文档。

**3. RAG-Fusion完整实现：**

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List, Dict, Tuple
from collections import defaultdict
import json

class RAGFusionRetriever:
    """RAG-Fusion检索器 - Multi-Query + RRF重排序"""
    
    def __init__(
        self,
        llm: ChatOpenAI,
        vectorstore: Chroma,
        num_queries: int = 4,
        k_per_query: int = 10,
        rrf_k: int = 60,
        final_top_k: int = 5
    ):
        self.llm = llm
        self.vectorstore = vectorstore
        self.num_queries = num_queries
        self.k_per_query = k_per_query
        self.rrf_k = rrf_k
        self.final_top_k = final_top_k
        
        self.query_prompt = ChatPromptTemplate.from_messages([
            ("system", """基于原始查询生成{num_queries}个不同视角的相关查询。
            输出JSON格式：{{"queries": ["查询1", "查询2", ...]}}"""),
            ("human", "{query}")
        ])
    
    def generate_queries(self, query: str) -> List[str]:
        """生成多个查询"""
        response = self.llm.invoke(
            self.query_prompt.format(
                num_queries=self.num_queries,
                query=query
            )
        )
        return json.loads(response.content)["queries"]
    
    def retrieve_per_query(self, queries: List[str]) -> Dict[str, List[Tuple[str, int]]]:
        """
        对每个查询执行检索，返回每个查询下的文档排名
        
        Returns:
            {query: [(doc_id, rank), ...]}
        """
        query_results = {}
        
        for query in queries:
            docs = self.vectorstore.similarity_search(query, k=self.k_per_query)
            ranked = [
                (doc.page_content[:100], rank + 1)  # rank从1开始
                for rank, doc in enumerate(docs)
            ]
            query_results[query] = ranked
        
        return query_results
    
    def _compute_rrf_scores(
        self, query_results: Dict[str, List[Tuple[str, int]]]
    ) -> Dict[str, Tuple[float, Document]]:
        """计算RRF分数"""
        rrf_scores = defaultdict(float)
        doc_map = {}
        
        # 同时需要获取完整文档，这里简化处理
        for query, ranked_docs in query_results.items():
            for doc_id, rank in ranked_docs:
                rrf_scores[doc_id] += 1.0 / (self.rrf_k + rank)
        
        return rrf_scores
    
    def retrieve(self, query: str) -> List[Document]:
        """执行RAG-Fusion检索"""
        # 1. 生成多个查询
        expanded_queries = self.generate_queries(query)
        all_queries = [query] + expanded_queries
        
        print(f"原始查询: {query}")
        print(f"扩展查询: {expanded_queries}")
        
        # 2. 对每个查询执行检索
        all_results = []
        seen_docs = set()
        
        for q in all_queries:
            docs = self.vectorstore.similarity_search(q, k=self.k_per_query)
            for rank, doc in enumerate(docs, start=1):
                doc_id = doc.page_content[:100]
                if doc_id not in seen_docs:
                    seen_docs.add(doc_id)
                    all_results.append((doc_id, doc, rank, q))
        
        # 3. 计算RRF分数
        rrf_scores = defaultdict(float)
        doc_store = {}
        
        for doc_id, doc, rank, query in all_results:
            rrf_scores[doc_id] += 1.0 / (self.rrf_k + rank)
            if doc_id not in doc_store:
                doc_store[doc_id] = doc
        
        # 4. 按RRF分数排序，返回Top K
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nRRF重排序结果（Top {self.final_top_k}）：")
        for i, (doc_id, score) in enumerate(sorted_docs[:self.final_top_k], 1):
            print(f"  排名{i}: RRF={score:.4f} | {doc_id[:80]}...")
        
        return [doc_store[doc_id] for doc_id, _ in sorted_docs[:self.final_top_k]]

# 完整的RAG-Fusion + LLM答案生成Pipeline
class RAGFusionPipeline:
    """RAG-Fusion完整Pipeline"""
    
    def __init__(self, retriever: RAGFusionRetriever, llm: ChatOpenAI):
        self.retriever = retriever
        self.llm = llm
        
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """基于以下上下文信息回答问题。如果上下文中没有相关信息，请明确说明。
            
            上下文：
            {context}
            """),
            ("human", "问题：{query}")
        ])
    
    def answer(self, query: str) -> str:
        """执行完整RAG-Fusion流程并生成答案"""
        # 1. RAG-Fusion检索
        context_docs = self.retriever.retrieve(query)
        context = "\n\n---\n\n".join([
            f"[文档{i+1}] {doc.page_content}"
            for i, doc in enumerate(context_docs)
        ])
        
        # 2. LLM生成答案
        response = self.llm.invoke(
            self.answer_prompt.format(context=context, query=query)
        )
        
        return response.content

# 使用示例
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

fusion_retriever = RAGFusionRetriever(
    llm=llm,
    vectorstore=vectorstore,
    num_queries=4,
    final_top_k=5
)

pipeline = RAGFusionPipeline(fusion_retriever, llm)
answer = pipeline.answer("LangChain中如何实现RAG系统？")
print(answer)
```

**4. RRF vs 加权分数融合：**

| 维度 | RRF | 加权分数融合 |
|------|-----|------------|
| **原理** | 基于排名位置，非原始分数 | 基于原始检索分数加权 |
| **分数归一化** | 不需要（排名天然可比） | 需要（不同检索系统分数范围不同） |
| **鲁棒性** | 高（对异常分数不敏感） | 低（异常分数可能主导结果） |
| **超参数** | 仅需k（平滑常数） | 需要各检索器的权重 |
| **可解释性** | 直观（排名越高贡献越大） | 依赖分数校准 |
| **适用场景** | 异构检索系统融合 | 同类型检索系统微调 |
| **实现复杂度** | 低 | 中（需要分数归一化） |

**评分标准：**
- RAG-Fusion与Multi-Query区别清晰（2分）
- RRF算法原理和举例正确（3分）
- 代码实现完整（4分）
- 融合方法对比分析准确（1分）

---

### 题目14：上下文压缩与过滤（高级）

**题目描述：**
在RAG系统中，检索到的文档块可能包含大量与查询无关的内容，直接输入LLM会增加成本和降低响应质量。请回答：
1. 上下文压缩的核心痛点和基本思路
2. 实现一个基于LangChain的上下文压缩器（Contextual Compression Retriever）
3. 讨论：上下文压缩的粒度如何控制？过度压缩的风险是什么？

**知识点：** 上下文压缩、LLM上下文窗口优化、信息过滤

**能力等级：** 高级

**参考答案：**

**1. 核心痛点与基本思路：**

**痛点：**
- 文档块划分时不知道用户查询，与查询最相关的信息可能被大量无关文本包围
- 直接输入完整文档块导致：
  - LLM调用成本增加（更多Token）
  - 响应质量下降（无关信息干扰LLM推理）
  - 上下文窗口浪费（限制了可提供的有效信息量）

**基本思路：**
- 检索后，使用给定查询对检索到的文档进行压缩
- 只保留与查询相关的信息，过滤无关内容
- 将压缩后的精炼上下文输入LLM

**2. LangChain实现：**

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List

class AdvancedContextCompressor:
    """高级上下文压缩器 - 组合多种压缩策略"""
    
    def __init__(self, llm: ChatOpenAI, embeddings: OpenAIEmbeddings):
        self.llm = llm
        self.embeddings = embeddings
        
        # 策略1: LLM提取相关内容
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """给定以下文档内容和用户查询，提取与查询直接相关的句子。
            去除与查询无关的内容。保持原文表述，不要改写。
            
            文档内容：
            {context}
            
            请提取与以下查询相关的内容："""),
            ("human", "{query}")
        ])
    
    def extract_relevant_content(
        self, doc: Document, query: str
    ) -> Document:
        """使用LLM提取文档中与查询相关的内容"""
        response = self.llm.invoke(
            self.extraction_prompt.format(
                context=doc.page_content,
                query=query
            )
        )
        
        extracted = response.content.strip()
        
        # 如果提取后内容为空或过短，保留原始文档
        if len(extracted) < 20:
            return doc
        
        return Document(
            page_content=extracted,
            metadata={
                **doc.metadata,
                "compressed": True,
                "original_length": len(doc.page_content),
                "compressed_length": len(extracted)
            }
        )
    
    def compress_by_similarity(
        self, docs: List[Document], query: str, threshold: float = 0.5
    ) -> List[Document]:
        """基于相似度阈值过滤文档"""
        if not docs:
            return docs
        
        query_embedding = self.embeddings.embed_query(query)
        
        filtered_docs = []
        for doc in docs:
            doc_embedding = self.embeddings.embed_query(doc.page_content)
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            
            if similarity >= threshold:
                doc.metadata["similarity_score"] = similarity
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        import numpy as np
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def compress(
        self,
        docs: List[Document],
        query: str,
        strategy: str = "hybrid",  # "llm", "similarity", "hybrid"
        max_docs: int = 5,
        max_tokens_per_doc: int = 500,
        similarity_threshold: float = 0.5
    ) -> List[Document]:
        """
        执行上下文压缩
        
        Args:
            docs: 待压缩的文档列表
            query: 用户查询
            strategy: 压缩策略
            max_docs: 最大文档数
            max_tokens_per_doc: 每个文档最大token数
            similarity_threshold: 相似度阈值
        """
        compressed = []
        
        for doc in docs[:max_docs]:
            if strategy in ("llm", "hybrid"):
                # LLM提取相关内容
                doc = self.extract_relevant_content(doc, query)
            
            # 截断过长的文档
            if len(doc.page_content) > max_tokens_per_doc:
                doc.page_content = doc.page_content[:max_tokens_per_doc] + "..."
            
            compressed.append(doc)
        
        if strategy in ("similarity", "hybrid"):
            # 相似度过滤
            compressed = self.compress_by_similarity(
                compressed, query, similarity_threshold
            )
        
        return compressed

# 使用示例
class CompressionRetrievalPipeline:
    """带压缩的检索Pipeline"""
    
    def __init__(
        self,
        base_retriever,
        compressor: AdvancedContextCompressor,
        llm: ChatOpenAI
    ):
        self.base_retriever = base_retriever
        self.compressor = compressor
        self.llm = llm
        
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """基于以下压缩后的上下文回答问题。如果无法回答，请明确说明。
            
            上下文：
            {context}
            """),
            ("human", "{query}")
        ])
    
    def retrieve_and_compress(self, query: str, top_k: int = 10) -> List[Document]:
        """检索 + 压缩"""
        # 1. 基础检索
        raw_docs = self.base_retriever.get_relevant_documents(query)[:top_k]
        
        print(f"原始检索: {len(raw_docs)} 个文档")
        print(f"原始总长度: {sum(len(d.page_content) for d in raw_docs)} 字符")
        
        # 2. 上下文压缩
        compressed_docs = self.compressor.compress(
            raw_docs, query,
            strategy="hybrid",
            max_docs=5,
            max_tokens_per_doc=500
        )
        
        print(f"压缩后: {len(compressed_docs)} 个文档")
        print(f"压缩后总长度: {sum(len(d.page_content) for d in compressed_docs)} 字符")
        
        return compressed_docs
    
    def answer(self, query: str) -> str:
        """完整问答流程"""
        docs = self.retrieve_and_compress(query)
        
        context = "\n\n---\n\n".join([
            f"[{i+1}] {doc.page_content}"
            for i, doc in enumerate(docs)
        ])
        
        response = self.llm.invoke(
            self.answer_prompt.format(context=context, query=query)
        )
        
        return response.content

# 使用LangChain内置的ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# 方式1：使用LLMChainExtractor
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# 方式2：使用EmbeddingsFilter（相似度过滤）
embeddings_filter = EmbeddingsFilter(
    embeddings=OpenAIEmbeddings(),
    similarity_threshold=0.76
)
similarity_compression_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,
    base_retriever=base_retriever
)
```

**3. 压缩粒度控制与风险：**

**压缩粒度控制策略：**

| 粒度级别 | 方式 | 风险 |
|---------|------|------|
| 文档级 | 过滤整个文档 | 可能丢失关键信息 |
| 段落级 | 保留相关段落 | 段落上下文可能不完整 |
| 句子级 | 提取相关句子 | 句子间逻辑关系断裂 |
| 短语级 | 提取关键词 | 丢失语义结构 |

**过度压缩的风险：**

1. **语义断裂：** 提取的句子失去上下文，LLM无法正确理解
2. **信息丢失：** 关键信息被误判为无关而过滤掉
3. **答案偏差：** 过度聚焦查询关键词，忽略相关但表述不同的信息
4. **幻觉增加：** 上下文不完整，LLM可能"脑补"缺失信息

**最佳实践：**
- 采用"宽松过滤"策略：宁可多保留，不轻易丢弃
- 保留原始文档的元数据引用，便于追溯
- 结合多种压缩策略的混合方案
- 对压缩结果进行人工评估，建立质量基准

**评分标准：**
- 痛点分析准确（2分）
- 代码实现完整（4分）
- 压缩粒度控制策略合理（2分）
- 风险分析深入（2分）

---

## 七、LangChain集成与工程落地

### 题目15：LangChain中Advanced RAG各组件的集成方案（高级）

**题目描述：**
在实际项目中，需要将PPT中介绍的各种Advanced RAG策略集成到LangChain Pipeline中。请设计一个完整的Advanced RAG Pipeline，包含以下组件：
1. 元数据索引（SelfQueryRetriever）
2. 查询优化（Multi-Query + Decomposition）
3. 混合检索（向量 + BM25）
4. 后检索重排序（RAG-Fusion + RRF）
5. 上下文压缩

请画出架构图并给出核心集成代码。

**知识点：** LangChain Pipeline设计、组件集成、工程化实践

**能力等级：** 高级

**参考答案：**

**架构设计：**

```
┌─────────────────────────────────────────────────────────────┐
│                   Advanced RAG Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  用户查询                                                     │
│     │                                                        │
│     ▼                                                        │
│  ┌──────────────────────────────────────┐                    │
│  │  Phase 1: 查询分析与优化               │                    │
│  │  ┌────────────┐  ┌────────────────┐  │                    │
│  │  │ 复杂度判断  │  │ 元数据提取      │  │                    │
│  │  │ (简单/复杂) │  │ (SelfQuery)    │  │                    │
│  │  └─────┬──────┘  └───────┬────────┘  │                    │
│  │        │                 │            │                    │
│  │        ▼                 ▼            │                    │
│  │  ┌────────────┐  ┌────────────────┐  │                    │
│  │  │ Decompose  │  │ Multi-Query    │  │                    │
│  │  │ 问题分解    │  │ 多路查询生成    │  │                    │
│  │  └─────┬──────┘  └───────┬────────┘  │                    │
│  └────────┼─────────────────┼────────────┘                    │
│           │                 │                                 │
│           ▼                 ▼                                 │
│  ┌──────────────────────────────────────┐                    │
│  │  Phase 2: 混合检索                     │                    │
│  │  ┌──────────┐  ┌──────────┐          │                    │
│  │  │ 向量检索  │  │BM25检索   │          │                    │
│  │  │(语义)    │  │(关键词)   │          │                    │
│  │  └────┬─────┘  └────┬─────┘          │                    │
│  │       └──────┬──────┘                 │                    │
│  │              ▼                        │                    │
│  │  ┌──────────────────────┐            │                    │
│  │  │ 元数据过滤 + 结果合并  │            │                    │
│  │  └──────────┬───────────┘            │                    │
│  └─────────────┼────────────────────────┘                    │
│                │                                              │
│                ▼                                              │
│  ┌──────────────────────────────────────┐                    │
│  │  Phase 3: 后检索优化                   │                    │
│  │  ┌──────────────────────┐            │                    │
│  │  │ RAG-Fusion RRF重排序  │            │                    │
│  │  └──────────┬───────────┘            │                    │
│  │             ▼                         │                    │
│  │  ┌──────────────────────┐            │                    │
│  │  │ 上下文压缩与过滤       │            │                    │
│  │  └──────────┬───────────┘            │                    │
│  └─────────────┼────────────────────────┘                    │
│                │                                              │
│                ▼                                              │
│  ┌──────────────────────────────────────┐                    │
│  │  Phase 4: 答案生成                     │                    │
│  │  ┌──────────────────────┐            │                    │
│  │  │ LLM生成 + 格式校验     │            │                    │
│  │  │ (PydanticOutputParser) │            │                    │
│  │  └──────────────────────┘            │                    │
│  └──────────────────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**核心集成代码：**

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json

class QueryComplexity(Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"

@dataclass
class PipelineConfig:
    """Pipeline配置"""
    # 查询优化
    num_multi_queries: int = 3
    max_decomposition_depth: int = 3
    
    # 检索
    retrieval_k: int = 20
    vector_weight: float = 0.5
    bm25_weight: float = 0.5
    
    # 后检索
    rrf_k: int = 60
    final_top_k: int = 5
    similarity_threshold: float = 0.5
    
    # 压缩
    compression_enabled: bool = True
    max_compressed_tokens: int = 2000

class AdvancedRAGPipeline:
    """Advanced RAG完整Pipeline"""
    
    def __init__(
        self,
        llm: ChatOpenAI,
        embeddings: OpenAIEmbeddings,
        documents: List[Document],
        metadata_field_info: List[AttributeInfo],
        config: PipelineConfig = None
    ):
        self.llm = llm
        self.embeddings = embeddings
        self.config = config or PipelineConfig()
        
        # 构建向量存储
        self.vectorstore = Chroma.from_documents(documents, embeddings)
        
        # 构建BM25检索器
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.bm25_retriever.k = self.config.retrieval_k
        
        # 构建向量检索器
        self.vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.config.retrieval_k}
        )
        
        # 构建混合检索器
        self.hybrid_retriever = EnsembleRetriever(
            retrievers=[self.vector_retriever, self.bm25_retriever],
            weights=[self.config.vector_weight, self.config.bm25_weight]
        )
        
        # 构建SelfQueryRetriever（元数据过滤）
        self.self_query_retriever = SelfQueryRetriever.from_llm(
            llm=llm,
            vectorstore=self.vectorstore,
            document_contents="技术文档和知识库文章",
            metadata_field_info=metadata_field_info
        )
        
        # 构建上下文压缩器
        if self.config.compression_enabled:
            self.compressor = LLMChainExtractor.from_llm(llm)
            self.compression_retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=self.hybrid_retriever
            )
        else:
            self.compression_retriever = self.hybrid_retriever
        
        # 查询优化Prompts
        self._init_prompts()
    
    def _init_prompts(self):
        """初始化各类Prompt"""
        self.complexity_prompt = ChatPromptTemplate.from_messages([
            ("system", """判断问题的复杂度。简单问题可以直接回答，复杂问题需要分解。
            输出JSON: {{"complexity": "simple|complex", "reason": "原因"}}"""),
            ("human", "{query}")
        ])
        
        self.decomposition_prompt = ChatPromptTemplate.from_messages([
            ("system", """将复杂问题分解为子问题。输出JSON:
            {{"sub_questions": ["子问题1", "子问题2", ...]}}"""),
            ("human", "{query}")
        ])
        
        self.multi_query_prompt = ChatPromptTemplate.from_messages([
            ("system", """生成{num}个不同视角的相关查询。输出JSON:
            {{"queries": ["查询1", "查询2", ...]}}"""),
            ("human", "{query}")
        ])
        
        self.final_answer_prompt = ChatPromptTemplate.from_messages([
            ("system", """基于上下文回答问题。如果无法回答，请明确说明。
            
            上下文：
            {context}
            """),
            ("human", "{query}")
        ])
    
    def analyze_query_complexity(self, query: str) -> QueryComplexity:
        """分析查询复杂度"""
        response = self.llm.invoke(
            self.complexity_prompt.format(query=query)
        )
        data = json.loads(response.content)
        return QueryComplexity(data["complexity"])
    
    def decompose_query(self, query: str) -> List[str]:
        """分解复杂问题"""
        response = self.llm.invoke(
            self.decomposition_prompt.format(query=query)
        )
        return json.loads(response.content)["sub_questions"]
    
    def generate_multi_queries(self, query: str) -> List[str]:
        """生成多路查询"""
        response = self.llm.invoke(
            self.multi_query_prompt.format(
                num=self.config.num_multi_queries,
                query=query
            )
        )
        return json.loads(response.content)["queries"]
    
    def retrieve_with_rrf(
        self, queries: List[str]
    ) -> List[Document]:
        """多查询检索 + RRF融合"""
        from collections import defaultdict
        
        all_docs = {}  # doc_id -> (doc, rrf_score)
        
        for query in queries:
            docs = self.hybrid_retriever.get_relevant_documents(query)
            for rank, doc in enumerate(docs[:self.config.retrieval_k], start=1):
                doc_id = doc.page_content[:100]
                rrf_score = 1.0 / (self.config.rrf_k + rank)
                
                if doc_id in all_docs:
                    _, existing_score = all_docs[doc_id]
                    all_docs[doc_id] = (doc, existing_score + rrf_score)
                else:
                    all_docs[doc_id] = (doc, rrf_score)
        
        # 按RRF分数排序
        sorted_docs = sorted(
            all_docs.values(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [doc for doc, _ in sorted_docs[:self.config.final_top_k]]
    
    def compress_context(
        self, docs: List[Document], query: str
    ) -> List[Document]:
        """压缩上下文"""
        if not self.config.compression_enabled:
            return docs
        
        compressed = []
        total_tokens = 0
        
        for doc in docs:
            # 使用LLM提取相关内容
            extract_prompt = ChatPromptTemplate.from_messages([
                ("system", """提取与查询相关的句子。只保留直接相关的内容。
                
                文档：
                {context}
                """),
                ("human", "查询：{query}")
            ])
            
            response = self.llm.invoke(
                extract_prompt.format(
                    context=doc.page_content,
                    query=query
                )
            )
            
            extracted = response.content.strip()
            if len(extracted) > 20:
                compressed.append(Document(
                    page_content=extracted,
                    metadata=doc.metadata
                ))
                total_tokens += len(extracted)
            
            if total_tokens > self.config.max_compressed_tokens:
                break
        
        return compressed or docs[:2]  # 如果压缩后为空，保留前2个原始文档
    
    def answer_simple(self, query: str) -> str:
        """处理简单查询"""
        # 生成多路查询
        expanded_queries = self.generate_multi_queries(query)
        all_queries = [query] + expanded_queries
        
        # RRF检索
        docs = self.retrieve_with_rrf(all_queries)
        
        # 压缩
        docs = self.compress_context(docs, query)
        
        # 生成答案
        context = "\n\n---\n\n".join([
            f"[{i+1}] {doc.page_content}"
            for i, doc in enumerate(docs)
        ])
        
        response = self.llm.invoke(
            self.final_answer_prompt.format(context=context, query=query)
        )
        
        return response.content
    
    def answer_complex(self, query: str) -> str:
        """处理复杂查询"""
        # 问题分解
        sub_questions = self.decompose_query(query)
        
        sub_answers = []
        for sq in sub_questions:
            # 对每个子问题执行完整检索流程
            sub_answer = self.answer_simple(sq)
            sub_answers.append({
                "question": sq,
                "answer": sub_answer
            })
        
        # 汇总
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """汇总子问题答案，生成最终完整回答。
            
            子问题及答案：
            {sub_answers}
            """),
            ("human", "原始问题：{query}")
        ])
        
        sub_answers_text = "\n\n".join([
            f"Q: {sa['question']}\nA: {sa['answer']}"
            for sa in sub_answers
        ])
        
        response = self.llm.invoke(
            summary_prompt.format(
                sub_answers=sub_answers_text,
                query=query
            )
        )
        
        return response.content
    
    def answer(self, query: str) -> Dict:
        """完整Pipeline入口"""
        # 元数据提取（可选）
        try:
            metadata_docs = self.self_query_retriever.get_relevant_documents(query)
        except:
            metadata_docs = []
        
        # 复杂度判断
        complexity = self.analyze_query_complexity(query)
        
        if complexity == QueryComplexity.SIMPLE:
            answer = self.answer_simple(query)
            return {
                "query": query,
                "complexity": "simple",
                "answer": answer,
                "metadata_docs_count": len(metadata_docs)
            }
        else:
            answer = self.answer_complex(query)
            return {
                "query": query,
                "complexity": "complex",
                "answer": answer,
                "metadata_docs_count": len(metadata_docs)
            }

# 使用示例
metadata_field_info = [
    AttributeInfo(name="topic", description="主题", type="string"),
    AttributeInfo(name="author", description="作者", type="string"),
    AttributeInfo(name="year", description="年份", type="integer"),
]

pipeline = AdvancedRAGPipeline(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    embeddings=OpenAIEmbeddings(),
    documents=documents,
    metadata_field_info=metadata_field_info,
    config=PipelineConfig(
        num_multi_queries=3,
        final_top_k=5,
        compression_enabled=True
    )
)

result = pipeline.answer("LangChain中如何实现高级RAG系统？")
print(result["complexity"])
print(result["answer"])
```

**评分标准：**
- 架构设计合理完整（3分）
- 各组件正确集成（3分）
- 代码结构清晰可维护（2分）
- 包含复杂度判断和分流逻辑（2分）

---

## 八、综合实战与架构设计

### 题目16：Advanced RAG系统架构设计——金融智能助手（高级）

**题目描述：**
请设计一个面向金融领域的Advanced RAG智能助手系统，满足以下需求：
1. 知识库包含：上市公司财报（PDF）、实时股票数据（API）、金融新闻（多源）、行业研报（混合格式）
2. 用户查询类型：数据查询（"某公司2024年Q1营收"）、对比分析（"A公司和B公司盈利能力对比"）、趋势预测（"某行业未来走势"）
3. 系统要求：高准确率、低延迟、可解释性

请从以下维度进行设计：
- 数据处理Pipeline（多格式文档加载、清洗、切分）
- 索引策略选择（针对不同数据类型）
- 查询优化策略（针对不同查询类型）
- 检索与后检索优化
- 答案生成与验证

**知识点：** 系统架构设计、多源数据融合、金融领域应用

**能力等级：** 高级

**参考答案：**

**整体架构：**

```
┌─────────────────────────────────────────────────────────────────┐
│                    金融智能助手 Advanced RAG                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   数据接入层                               │    │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │    │
│  │  │PDF   │ │API   │ │新闻  │ │研报  │                   │    │
│  │  │解析器│ │适配器│ │爬虫  │ │解析器│                   │    │
│  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘                   │    │
│  └─────┼────────┼────────┼────────┼─────────────────────────┘    │
│        │        │        │        │                               │
│        ▼        ▼        ▼        ▼                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   数据处理层                               │    │
│  │  · 数据清洗（去噪、去重、格式标准化）                        │    │
│  │  · 表格提取（Camelot/Tabula）                             │    │
│  │  · 实体识别（公司名、股票代码、财务指标）                    │    │
│  │  · 时间戳标注（财报周期、新闻发布时间）                      │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   索引构建层                               │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │父子索引   │ │摘要索引   │ │元数据索引 │ │假设性问题 │  │    │
│  │  │(财报)    │ │(新闻)    │ │(研报)    │ │(FAQ)     │  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   查询处理层                               │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │    │
│  │  │ 查询分类器    │ │ 查询优化器    │ │ 混合检索器    │    │    │
│  │  │ (数据/分析/   │ │ (Enrich/     │ │ (向量+BM25   │    │    │
│  │  │  预测)       │ │  Multi-Query │ │  +SQL)       │    │    │
│  │  │              │ │  /Decompose) │ │              │    │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘    │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   后处理层                                 │    │
│  │  · RAG-Fusion RRF重排序                                   │    │
│  │  · 上下文压缩过滤                                          │    │
│  │  · 数值校验（财务数据交叉验证）                              │    │
│  │  · 格式校验（PydanticOutputParser）                       │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   答案生成层                               │    │
│  │  · 来源引用（标注数据来源文档/时间）                         │    │
│  │  · 置信度评分                                              │    │
│  │  · 免责声明（非投资建议）                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**1. 数据处理Pipeline：**

```python
class FinancialDataPipeline:
    """金融数据处理Pipeline"""
    
    def __init__(self):
        self.pdf_parser = FinancialPDFParser()  # 财报PDF解析器
        self.news_parser = NewsParser()         # 新闻解析器
        self.report_parser = ReportParser()     # 研报解析器
        self.data_cleaner = DataCleaner()       # 数据清洗器
        
    def process_financial_report(self, pdf_path: str) -> List[Document]:
        """处理财报PDF"""
        # 1. 使用专门的PDF解析器（保留表格结构）
        raw_data = self.pdf_parser.parse(pdf_path)
        
        # 2. 提取表格数据（资产负债表、利润表、现金流量表）
        tables = extract_tables_camelot(pdf_path)
        
        # 3. 实体识别
        entities = extract_financial_entities(raw_data)
        
        # 4. 构建父子索引结构
        parent_docs = []
        for section in raw_data.sections:
            parent = Document(
                page_content=section.full_text,
                metadata={
                    "type": "financial_report",
                    "company": entities.company_name,
                    "stock_code": entities.stock_code,
                    "fiscal_period": section.period,
                    "section": section.title,
                    "tables": section.tables
                }
            )
            parent_docs.append(parent)
        
        return parent_docs
    
    def process_news(self, news_items: List[Dict]) -> List[Document]:
        """处理金融新闻"""
        docs = []
        for item in news_items:
            # 生成摘要
            summary = self._generate_summary(item["content"])
            
            doc = Document(
                page_content=summary,  # 使用摘要索引
                metadata={
                    "type": "news",
                    "source": item["source"],
                    "publish_time": item["timestamp"],
                    "related_companies": item["companies"],
                    "related_sectors": item["sectors"],
                    "sentiment": item["sentiment"],  # 情感分析
                    "original_content": item["content"]
                }
            )
            docs.append(doc)
        
        return docs
    
    def process_research_report(self, report_path: str) -> List[Document]:
        """处理行业研报"""
        # 研报通常包含图表、数据表格、文字分析
        # 使用元数据索引，按行业、公司、分析师、时间等标签分类
        report = self.report_parser.parse(report_path)
        
        return [
            Document(
                page_content=chunk.text,
                metadata={
                    "type": "research_report",
                    "industry": report.industry,
                    "companies": report.companies,
                    "analyst": report.analyst,
                    "publish_date": report.date,
                    "rating": report.rating,
                    "target_price": report.target_price,
                    "chunk_type": chunk.type  # "text", "table", "chart"
                }
            )
            for chunk in report.chunks
        ]
```

**2. 索引策略选择：**

| 数据类型 | 推荐索引策略 | 理由 |
|---------|------------|------|
| 上市公司财报（PDF） | 父子索引 + 元数据索引 | 财报有清晰结构（公司→年度→报表类型），父子索引保证上下文完整性；元数据按公司/年份/报表类型过滤 |
| 金融新闻 | 摘要索引 + 元数据索引 | 新闻量大且时效性强，摘要索引快速检索；元数据按时间/公司/行业过滤 |
| 行业研报 | 元数据索引 + 假设性问题索引 | 研报来源多样，元数据按行业/分析师/评级过滤；假设性问题覆盖多样化的查询方式 |
| 实时股票数据（API） | SQL检索 + 元数据索引 | 结构化数据，SQL精确查询；元数据按股票代码/时间范围过滤 |

**3. 查询优化策略：**

| 查询类型 | 优化策略 | 示例 |
|---------|---------|------|
| 数据查询 | Enrich完善问题（补充公司名、时间范围） | "营收" → "腾讯控股2024年Q1营收" |
| 对比分析 | Decomposition分解（拆成独立子问题） | "A和B盈利对比" → A盈利分析 + B盈利分析 + 对比汇总 |
| 趋势预测 | Multi-Query多路召回（多角度检索） | "某行业趋势" → 行业现状 + 历史数据 + 政策影响 + 竞争格局 |

**4. 检索与后检索优化：**

```python
class FinancialRetrievalOptimizer:
    """金融领域检索优化器"""
    
    def __init__(self):
        # 混合检索：向量 + BM25 + SQL（实时数据）
        self.vector_retriever = None  # 语义检索
        self.bm25_retriever = None    # 关键词精确匹配（股票代码、公司名）
        self.sql_retriever = None     # 结构化数据查询（实时行情）
        
        # 金融领域微调的嵌入模型
        self.domain_embeddings = None  # FinBERT embeddings
    
    def retrieve(self, query: str, query_type: str) -> List[Document]:
        if query_type == "data_query":
            # 数据查询：BM25优先（精确匹配）+ 向量补充
            bm25_results = self.bm25_retriever.retrieve(query)
            vector_results = self.vector_retriever.retrieve(query)
            sql_results = self.sql_retriever.query(query)  # 实时数据
            
            return self._merge_results(bm25_results, vector_results, sql_results)
        
        elif query_type == "comparison":
            # 对比分析：Multi-Query + RRF
            return self._rag_fusion_retrieve(query)
        
        elif query_type == "prediction":
            # 趋势预测：多源融合 + 时间加权
            return self._time_weighted_retrieve(query)
    
    def _validate_financial_data(self, docs: List[Document]) -> List[Document]:
        """财务数据交叉验证"""
        validated = []
        for doc in docs:
            # 检查数值一致性（不同来源的同一数据应一致）
            if self._has_numerical_data(doc):
                confidence = self._cross_validate(doc)
                doc.metadata["confidence"] = confidence
                if confidence > 0.7:  # 低置信度数据过滤
                    validated.append(doc)
            else:
                validated.append(doc)
        return validated
```

**5. 答案生成与验证：**

```python
class FinancialAnswerGenerator:
    """金融答案生成器"""
    
    def generate(self, query: str, context_docs: List[Document]) -> Dict:
        """生成答案并附带来源引用和置信度"""
        
        # 生成答案
        answer = self._generate_with_citations(query, context_docs)
        
        # 数值校验
        if answer.contains_numerical_data:
            answer = self._validate_numbers(answer, context_docs)
        
        return {
            "answer": answer.text,
            "citations": answer.citations,  # 来源引用
            "confidence": answer.confidence,
            "disclaimer": "本回答基于公开信息，不构成投资建议",
            "data_sources": [
                {
                    "type": doc.metadata["type"],
                    "source": doc.metadata.get("source"),
                    "date": doc.metadata.get("publish_time"),
                    "relevance": doc.metadata.get("similarity_score")
                }
                for doc in context_docs
            ]
        }
```

**关键设计决策总结：**

1. **多格式解析器：** 针对财报PDF使用专门的表格提取工具（Camelot），保留数据结构
2. **分层索引：** 不同数据类型使用不同的索引策略，而非一刀切
3. **查询分流：** 根据查询类型路由到不同的处理Pipeline
4. **领域适配：** 使用金融领域微调的嵌入模型（如FinBERT）
5. **数据校验：** 财务数据交叉验证，确保准确性
6. **可解释性：** 所有答案附带来源引用和置信度评分

**评分标准：**
- 数据处理Pipeline设计合理（2分）
- 索引策略选择有据可依（2分）
- 查询优化策略针对性强（2分）
- 检索与后检索设计完整（2分）
- 答案生成包含校验和引用（2分）

---

## 附录：快速参考表

| PPT章节 | 核心知识点 | 对应题目 |
|---------|----------|---------|
| RAG商业化痛点分析 | 七大失败点、优化方向 | 题目1 |
| 文档切分粒度 | 重叠分块、结构分块、递归分块、Chunk大小选择 | 题目2 |
| Advanced RAG概述 | Pre-Retrieval / Retrieval / Post-Retrieval 三层架构 | 题目3 |
| 摘要索引 | LLM生成摘要、摘要向量库、半结构化数据 | 题目4 |
| 父子索引 | 层级化块结构、子块检索→父块替换 | 题目5 |
| 假设性问题索引 | 问题向量替代文档向量、Query-Document对齐 | 题目6 |
| 元数据索引 | SelfQueryRetriever、分层过滤检索 | 题目7 |
| 索引优化综合 | 四种策略对比与场景选型 | 题目8 |
| Enrich完善问题 | 多轮对话引导、意图识别、槽位填充 | 题目9 |
| Multi-Query多路召回 | 查询扩展、多视角检索 | 题目10 |
| Decomposition问题分解 | CoT策略、并行/串行执行 | 题目11 |
| 混合检索 | 向量+BM25+SQL、RRF融合 | 题目12 |
| RAG-Fusion | Multi-Query+RRF重排序 | 题目13 |
| 上下文压缩 | LLM提取、相似度过滤 | 题目14 |
| LangChain集成 | Pipeline设计、组件集成 | 题目15 |
| 金融助手实战 | 系统架构设计、多源数据融合 | 题目16 |

---

> **文档说明：** 本题集共包含16道高级面试题，涵盖PPT中"基于LangChain的RAG系统优化实践"的全部核心知识点。每道题均包含问题描述、知识点标注、能力等级、详细参考答案（含代码示例）和评分标准。适合高级Agent工程师面试评估和技术能力提升。