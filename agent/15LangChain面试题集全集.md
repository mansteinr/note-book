# LangChain 面试题集全集 - 系统化能力评估指南

> 面试核心目标：系统化评估候选人对 LangChain 框架的核心概念、底层原理、组件设计、工程实践和实战应用能力的掌握程度。
> 本文档覆盖**十大模块**，共 **30 道面试题**，难度涵盖初级、中级、高级三个层次，每题包含参考答案与评分标准。

---

## 目录

- [一、LangChain 概述与核心概念（3题）](#一langchain-概述与核心概念3题)
- [二、底层原理与架构设计（3题）](#二底层原理与架构设计3题)
- [三、Models 与 Prompt 管理（3题）](#三models-与-prompt-管理3题)
- [四、Chains 与 LCEL（3题）](#四chains-与-lcel3题)
- [五、Memory 记忆机制（3题）](#五memory-记忆机制3题)
- [六、Agents 智能代理（3题）](#六agents-智能代理3题)
- [七、Retrieval 检索增强（3题）](#七retrieval-检索增强3题)
- [八、Tools 工具调用（3题）](#八tools-工具调用3题)
- [九、Callbacks 与可观测性（3题）](#九callbacks-与可观测性3题)
- [十、工程实践与综合应用（3题）](#十工程实践与综合应用3题)
- [十一、面试官使用指南与能力分级](#十一面试官使用指南与能力分级)
- [十二、总结](#十二总结)

---

## 一、LangChain 概述与核心概念（3题）

### Q1：什么是 LangChain？其核心价值与定位是什么？

**难度级别**：初级
**考察维度**：概念理解

**问题描述**：
请阐述 LangChain 的定义、核心价值和在 LLM 应用开发中的定位。为什么需要 LangChain 而不是直接调用 LLM API？

**参考答案**：

```
定义:
  LangChain 是一个用于构建 LLM 应用的开源框架，
  提供了将 LLM 与外部数据源、工具、记忆等组件
  编排成完整应用的标准接口和组件库。

核心价值:
  1. 抽象统一: 统一不同 LLM 的调用接口（OpenAI/Anthropic/本地模型）
  2. 组件丰富: 提供 Prompt/Chain/Agent/Memory/Retrieval 等全套组件
  3. 编排能力: 将多个组件组合成复杂工作流
  4. 生态集成: 数百个第三方工具和数据源集成
  5. 可观测: 内置 Tracing/Logging/Metrics

为什么需要 LangChain（vs 直接调 API）:

  直接调 API:
    response = openai.ChatCompletion.create(messages=[...])
    → 只能做单轮对话，无法管理状态、调用工具、检索知识
  
  用 LangChain:
    chain = RetrievalQA.from_chain_type(llm, retriever) 
            | ConversationalMemory()
            | AgentTools()
    → 能构建 RAG、Agent、多轮对话等复杂应用

定位（LLM 应用技术栈）:
  业务应用 → LangChain 编排层 → LLM 推理层 → 模型层
  
  LangChain 是"胶水层"，连接 LLM 与真实世界
```

**评分标准**：
- 3分：能说出 LangChain 的定义
- 4分：能说明核心价值和与直接调 API 的区别
- 5分：能说明其在技术栈中的定位

---

### Q2：LangChain 的核心组件有哪些？各自职责？

**难度级别**：初级
**考察维度**：组件理解

**问题描述**：
请列举 LangChain 的六大核心组件，并说明各自职责。

**参考答案**：

```
六大核心组件:

  ┌─────────────────────────────────────────────┐
  │            LangChain 核心组件                │
  ├──────────┬──────────┬──────────┬───────────┤
  │  Models  │  Prompts │  Chains  │  Memory   │
  ├──────────┼──────────┴──────────┴───────────┤
  │   Indexes/Retrieval  │     Agents/Tools     │
  └──────────────────────┴──────────────────────┘

1. Models（模型）: LLM 调用抽象
   • LLM: 文本输入→文本输出（GPT-3.5/4）
   • ChatModel: 消息输入→消息输出（ChatGPT）
   • Embedding: 文本→向量

2. Prompts（提示词）: Prompt 模板管理
   • PromptTemplate: 文本模板
   • ChatPromptTemplate: 聊天模板
   • FewShotPromptTemplate: 少样本模板

3. Chains（链）: 组件编排
   • LLMChain: LLM + Prompt
   • SequentialChain: 顺序链
   • LCEL: 声明式链（新方式）

4. Memory（记忆）: 状态管理
   • ConversationBufferMemory: 全量对话
   • ConversationSummaryMemory: 摘要
   • VectorStoreMemory: 向量检索

5. Indexes/Retrieval（检索）: 外部数据接入
   • DocumentLoader: 文档加载
   • TextSplitter: 文本分割
   • VectorStore: 向量存储
   • Retriever: 检索器

6. Agents/Tools（代理/工具）: 自主决策
   • Agent: 决策引擎
   • Tool: 外部工具（搜索/计算/API）
   • AgentExecutor: 执行器
```

**评分标准**：
- 3分：能列出 4 个以上组件
- 4分：能说明各自职责
- 5分：能说明组件间的协作关系

---

### Q3：LangChain 的版本演进与 LCEL？

**难度级别**：中级
**考察维度**：版本演进

**问题描述**：
LangChain 经历了从旧版 Chain 到 LCEL 的演进。请说明 LCEL 是什么、解决了什么问题、与旧版 Chain 的区别。

**参考答案**：

```
版本演进:
  v0.1: 旧版 Chain（LLMChain/SequentialChain等）
  v0.2: 引入 LCEL（LangChain Expression Language）
  v0.3: LCEL 成为主推方式，旧版 Chain 逐步废弃

LCEL 是什么:
  LangChain 表达式语言，用管道符 | 组合组件
  
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_openai import ChatOpenAI
  
  prompt = ChatPromptTemplate.from_template("讲个关于{topic}的笑话")
  model = ChatOpenAI()
  
  # LCEL 方式（新）
  chain = prompt | model | StrOutputParser()
  result = chain.invoke({"topic": "程序员"})

LCEL 解决的问题:
  1. 统一接口: 所有组件实现 Runnable 协议
  2. 流式支持: 原生支持 stream/astream
  3. 异步支持: 原生支持 ainvoke
  4. 批处理: 原生支持 batch
  5. 可组合: 用 | 简洁地串联组件

与旧版 Chain 区别:
  ┌──────────┬─────────────────┬─────────────────┐
  │          │ 旧版 Chain       │ LCEL            │
  ├──────────┼─────────────────┼─────────────────┤
  │ 语法      │ 类继承/方法调用   │ 管道符 |        │
  │ 流式      │ 需额外实现       │ 原生支持         │
  │ 异步      │ 需额外实现       │ 原生支持         │
  │ 批处理    │ 需额外实现       │ 原生支持         │
  │ 可读性    │ 一般             │ 高（声明式）     │
  │ 调试      │ 难               │ 有 Tracing       │
  └──────────┴─────────────────┴─────────────────┘

Runnable 协议（LCEL 核心）:
  每个组件实现 Runnable 接口:
  • invoke: 单次调用
  • batch: 批量调用
  • stream: 流式输出
  • ainvoke/abatch/astream: 异步版本
```

**评分标准**：
- 3分：能说出 LCEL 是管道符组合
- 4分：能说明 LCEL 解决的问题
- 5分：能对比旧版并解释 Runnable 协议

---

## 二、底层原理与架构设计（3题）

### Q4：LangChain 的 Runnable 协议原理？

**难度级别**：高级
**考察维度**：底层原理

**问题描述**：
LCEL 的核心是 Runnable 协议。请说明 Runnable 的设计原理、核心方法和工作机制。

**参考答案**：

```
Runnable 协议: 所有 LCEL 组件的统一接口

核心设计思想:
  • 统一接口: 所有组件实现相同方法
  • 可组合: 组件间可通过 | 串联
  • 多模式: 同步/异步/流式/批量统一支持

Runnable 核心方法:

  class Runnable(BaseModel):
      def invoke(self, input, config=None) -> Any:
          """单次同步调用"""
      
      async def ainvoke(self, input, config=None) -> Any:
          """异步调用"""
      
      def batch(self, inputs, config=None) -> List[Any]:
          """批量调用"""
      
      def stream(self, input, config=None) -> Iterator[Any]:
          """流式输出"""
      
      async def astream(self, input, config=None) -> AsyncIterator[Any]:
          """异步流式"""

管道符 | 的工作原理:
  chain = prompt | model | parser
  
  等价于:
  chain = prompt.pipe(model).pipe(parser)
  
  pipe 方法实现:
  def pipe(self, other):
      return RunnableSequence(self, other)
  
  RunnableSequence.invoke:
  def invoke(self, input, config):
      # 依次调用每个组件，前一个输出作为后一个输入
      for step in self.steps:
          input = step.invoke(input, config)
      return input

流式输出原理:
  def stream(self, input, config):
      # 每个组件产生迭代器
      iterator = iter([input])
      for step in self.steps:
          iterator = step.stream(iterator, config)
      yield from iterator

优势:
  • 一次实现，四种调用方式都支持
  • 组件可自由组合
  • 内置错误处理和重试
  • 支持 Callback（Tracing/Metrics）

RunnableLambda（自定义组件）:
  from langchain_core.runnables import RunnableLambda
  
  def process(text):
      return text.upper()
  
  runnable = RunnableLambda(process)
  chain = prompt | model | runnable  # 自定义函数也可加入链
```

**评分标准**：
- 3分：能说出 Runnable 有 invoke/stream 方法
- 4分：能说明管道符的实现原理
- 5分：能解释流式输出的工作机制

---

### Q5：LangChain 的 Callback 机制与 Tracing 原理？

**难度级别**：高级
**考察维度**：可观测性

**问题描述**：
LangChain 如何实现可观测性？请说明 Callback 机制和 LangSmith Tracing 的原理。

**参考答案**：

```
Callback 机制: 在组件执行的关键节点触发回调

Callback 支持的事件:
  • on_llm_start: LLM 调用开始
  • on_llm_new_token: LLM 生成新 token（流式）
  • on_llm_end: LLM 调用结束
  • on_chain_start/end: Chain 开始/结束
  • on_tool_start/end: 工具调用开始/结束
  • on_agent_action: Agent 决策
  • on_agent_finish: Agent 结束
  • on_text: 文本处理
  • on_retry: 重试

自定义 Callback:
  from langchain_core.callbacks import BaseCallbackHandler
  
  class MyHandler(BaseCallbackHandler):
      def on_llm_start(self, serialized, prompts, **kwargs):
          print(f"LLM调用: {prompts}")
      
      def on_llm_end(self, response, **kwargs):
          print(f"LLM返回: {response}")
      
      def on_tool_start(self, tool, input_str, **kwargs):
          print(f"工具调用: {tool}({input_str})")
  
  # 使用
  chain.invoke(input, config={"callbacks": [MyHandler()]})

LangSmith Tracing 原理:
  
  ┌──────────────┐
  │  应用代码     │
  └──────┬───────┘
         │ 每个组件执行时
  ┌──────▼───────┐
  │  Callback     │ ← 自动注入 TracingCallback
  │  收集事件      │
  └──────┬───────┘
         │ 异步上报
  ┌──────▼───────┐
  │  LangSmith    │ ← 可视化平台
  │  存储可视化    │
  └──────────────┘

  Tracing 能看到:
  • 每个组件的输入/输出
  • 执行顺序和耗时
  • LLM 的 Token 消耗
  • 错误和重试
  • 完整调用链路

启用 Tracing:
  export LANGCHAIN_TRACING_V2=true
  export LANGCHAIN_API_KEY=xxx
  
  # 自动对所有调用启用 Tracing
  chain.invoke(input)  # 自动上报到 LangSmith

应用场景:
  • 调试: 定位哪一步出错
  • 优化: 找出性能瓶颈
  • 监控: 线上追踪每条请求
  • 成本: 统计 Token 消耗
```

**评分标准**：
- 3分：能说出 Callback 的概念
- 4分：能自定义 Callback 并说明事件
- 5分：能解释 LangSmith Tracing 原理

---

### Q6：LangChain 的配置管理与环境隔离？

**难度级别**：中级
**考察维度**：工程实践

**问题描述**：
企业级应用需要管理多环境（开发/测试/生产）、多模型。请说明 LangChain 的配置管理方案。

**参考答案**：

```
配置管理三层方案:

1. 环境变量（基础）
   .env 文件:
   OPENAI_API_KEY=sk-xxx
   ANTHROPIC_API_KEY=xxx
   LANGCHAIN_TRACING_V2=true
   
   from dotenv import load_dotenv
   load_dotenv()  # 加载环境变量

2. 配置文件（结构化）
   config.yaml:
   development:
     model: gpt-3.5-turbo
     temperature: 0.7
     max_tokens: 1000
   production:
     model: gpt-4
     temperature: 0.3
     max_tokens: 2000
   
   import yaml
   with open('config.yaml') as f:
       config = yaml.safe_load(f)[env]

3. 动态配置（运行时）
   from langchain_openai import ChatOpenAI
   
   def create_llm(env='dev'):
       config = load_config(env)
       return ChatOpenAI(
           model=config['model'],
           temperature=config['temperature'],
           max_tokens=config['max_tokens'],
       )

多模型管理:
  class ModelManager:
      def __init__(self):
          self.models = {
              'gpt4': ChatOpenAI(model='gpt-4'),
              'gpt35': ChatOpenAI(model='gpt-3.5-turbo'),
              'claude': ChatAnthropic(model='claude-3'),
          }
      
      def get(self, name):
          return self.models[name]
      
      def route(self, task_type):
          routing = {
              'simple': 'gpt35', 'complex': 'gpt4', 'long': 'claude',
          }
          return self.models[routing.get(task_type, 'gpt35')]

环境隔离最佳实践:
  • 密钥用环境变量，不写入代码
  • 不同环境用不同配置文件
  • 生产环境用更低的 temperature
  • 开发环境可开启 Tracing，生产按需
  • API Key 定期轮换
```

**评分标准**：
- 3分：能说明环境变量配置
- 4分：能给出配置文件方案
- 5分：能设计多模型路由和环境隔离

---

## 三、Models 与 Prompt 管理（3题）

### Q7：LangChain 中 LLM 与 ChatModel 的区别？

**难度级别**：初级
**考察维度**：模型理解

**问题描述**：
LangChain 区分了 LLM 和 ChatModel 两类模型。请说明区别和使用场景。

**参考答案**：

```
LLM（旧版接口）:
  • 输入: 字符串 → 输出: 字符串
  • 适用于: 补全模型（GPT-3, LLaMA）
  
  from langchain_openai import OpenAI
  llm = OpenAI()
  result = llm.invoke("中国的首都是")  # → "北京"

ChatModel（推荐）:
  • 输入: 消息列表 → 输出: AI 消息
  • 适用于: 对话模型（GPT-3.5/4, Claude）
  
  from langchain_openai import ChatOpenAI
  from langchain_core.messages import HumanMessage, SystemMessage
  
  chat = ChatOpenAI()
  messages = [
      SystemMessage(content="你是助手"),
      HumanMessage(content="你好")
  ]
  result = chat.invoke(messages)

消息类型:
  • SystemMessage: 系统指令（设定角色）
  • HumanMessage: 用户消息
  • AIMessage: 模型回复
  • FunctionMessage/ToolMessage: 工具返回

选择建议:
  • 新项目一律用 ChatModel
  • LLM 主要是兼容旧模型
  • ChatModel 支持工具调用、结构化输出
```

**评分标准**：
- 3分：能说出输入输出不同
- 4分：能说明消息类型
- 5分：能给出选择建议

---

### Q8：PromptTemplate 的设计与变量管理？

**难度级别**：中级
**考察维度**：Prompt 工程

**问题描述**：
请说明 LangChain 的 PromptTemplate 设计，包括变量管理、模板复用和动态构建。

**参考答案**：

```
PromptTemplate 基础:
  from langchain_core.prompts import PromptTemplate
  
  template = "请用{language}写一个{task}的代码示例"
  prompt = PromptTemplate.from_template(template)
  
  result = prompt.format(language="Python", task="排序")
  # "请用Python写一个排序的代码示例"

ChatPromptTemplate（推荐）:
  from langchain_core.prompts import ChatPromptTemplate
  
  template = ChatPromptTemplate.from_messages([
      ("system", "你是{role}专家"),
      ("human", "请解释{concept}"),
  ])

变量管理:
  • 自动提取变量: from_template 会解析 {var}
  • 部分填充: 用 partial 预填部分变量
  
  prompt = PromptTemplate.from_template("{role}解释{concept}")
  partial = prompt.partial(role="Python专家")
  partial.format(concept="装饰器")

动态 Prompt（根据条件选择模板）:
  templates = {
      "simple": "简单解释{topic}",
      "detailed": "详细解释{topic}，包含原理和示例",
  }
  
  def get_prompt(level):
      return PromptTemplate.from_template(templates[level])

FewShotPromptTemplate:
  from langchain_core.prompts import FewShotPromptTemplate
  
  examples = [
      {"input": "开心", "output": "悲伤"},
      {"input": "高", "output": "矮"},
  ]
  
  example_prompt = PromptTemplate.from_template("{input} → {output}")
  
  few_shot = FewShotPromptTemplate(
      examples=examples,
      example_prompt=example_prompt,
      suffix="现在请处理: {input}",
      input_variables=["input"],
  )

Prompt 持久化:
  prompt.save("my_prompt.json")
  prompt = PromptTemplate.from_file("my_prompt.json")
```

**评分标准**：
- 3分：能使用基本 PromptTemplate
- 4分：能使用 partial 和动态选择
- 5分：能使用 FewShotPrompt 和持久化

---

### Q9：如何实现结构化输出？

**难度级别**：中级
**考察维度**：输出控制

**问题描述**：
LLM 输出通常是自由文本。请说明 LangChain 如何实现结构化输出。

**参考答案**：

```
方式 1: Pydantic + with_structured_output（推荐）
  from pydantic import BaseModel
  from langchain_openai import ChatOpenAI
  
  class Person(BaseModel):
      name: str
      age: int
      skills: list[str]
  
  llm = ChatOpenAI()
  structured_llm = llm.with_structured_output(Person)
  
  result = structured_llm.invoke("张三，25岁，会Python和Java")
  print(result.name)    # "张三"

方式 2: JsonOutputParser
  from langchain_core.output_parsers import JsonOutputParser
  
  parser = JsonOutputParser(pydantic_object=Person)
  
  chain = prompt | llm | parser

方式 3: Function Calling
  llm = ChatOpenAI().bind(
      functions=[{
          "name": "extract_person",
          "parameters": Person.schema()
      }],
      function_call={"name": "extract_person"}
  )

方式 4: Output Parser
  from langchain_core.output_parsers import (
      PydanticOutputParser,
      CommaSeparatedListOutputParser,
  )

最佳实践:
  • 优先用 with_structured_output（最简洁）
  • 复杂格式用 JsonOutputParser
  • 降低 temperature（0~0.3）保证稳定
  • 加重试机制处理格式错误
```

**评分标准**：
- 3分：能使用 OutputParser
- 4分：能使用 with_structured_output
- 5分：能对比多种方式并给出最佳实践

---

## 四、Chains 与 LCEL（3题）

### Q10：LCEL 的链组合模式有哪些？

**难度级别**：中级
**考察维度**：链设计

**问题描述**：
请说明 LCEL 支持的链组合模式，并给出示例。

**参考答案**：

```
LCEL 链组合模式:

1. 顺序链（Sequential）: 用 | 串联
  chain = prompt | model | parser
  result = chain.invoke({"topic": "AI"})

2. 并行链（Parallel）: RunnableParallel
  from langchain_core.runnables import RunnableParallel
  
  parallel = RunnableParallel(
      summary=prompt | model,
      translation=translate_prompt | model,
  )
  result = parallel.invoke({"text": "..."})

3. 条件分支（Branch）: RunnableBranch
  from langchain_core.runnables import RunnableBranch
  
  branch = RunnableBranch(
      (lambda x: x["type"] == "code", code_chain),
      (lambda x: x["type"] == "text", text_chain),
      default_chain,
  )

4. 任意映射（Map）: RunnableLambda
  from langchain_core.runnables import RunnableLambda
  
  chain = prompt | model | RunnableLambda(lambda x: x.upper())

5. 透传（Passthrough）: RunnablePassthrough
  from langchain_core.runnables import RunnablePassthrough
  
  # 透传原始输入 + 添加检索结果
  chain = RunnableParallel(
      context=retriever,
      question=RunnablePassthrough()
  ) | prompt | model

RAG 完整示例（LCEL）:
  from langchain_core.runnables import RunnablePassthrough
  
  def format_docs(docs):
      return "\n".join(d.page_content for d in docs)
  
  rag_chain = (
      {"context": retriever | format_docs, 
       "question": RunnablePassthrough()}
      | prompt
      | model
      | StrOutputParser()
  )
  
  result = rag_chain.invoke("什么是RAG？")

6. 带记忆的链:
  from langchain_core.runnables.history import RunnableWithMessageHistory
  
  chain_with_history = RunnableWithMessageHistory(
      chain, lambda session_id: memory,
      input_messages_key="input",
      history_messages_key="history",
  )
```

**评分标准**：
- 3分：能用 | 串联顺序链
- 4分：能用 RunnableParallel 和 RunnablePassthrough
- 5分：能设计 RAG 完整链和带记忆链

---

### Q11：如何实现链的错误处理与重试？

**难度级别**：高级
**考察维度**：健壮性

**问题描述**：
LLM 调用可能失败（超时/限流/格式错误）。请说明 LCEL 的错误处理和重试机制。

**参考答案**：

```
LCEL 错误处理:

1. with_retry（重试）
  from langchain_openai import ChatOpenAI
  
  llm = ChatOpenAI().with_retry(
      stop_after_attempt=3,
      wait_exponential_jitter=True,
  )

2. with_fallbacks（降级）
  primary = ChatOpenAI(model="gpt-4")
  fallback = ChatOpenAI(model="gpt-3.5-turbo")
  
  llm = primary.with_fallbacks([fallback])
  # gpt-4 失败时自动降级到 gpt-3.5

3. RunnableLambda 异常处理
  from langchain_core.runnables import RunnableLambda
  
  def safe_parse(text):
      try:
          return json.loads(text)
      except:
          return {"error": "parse_failed", "raw": text}
  
  chain = prompt | model | RunnableLambda(safe_parse)

4. 超时控制
  import asyncio
  
  async def invoke_with_timeout(chain, input, timeout=30):
      try:
          return await asyncio.wait_for(
              chain.ainvoke(input), timeout=timeout
          )
      except asyncio.TimeoutError:
          return "请求超时"

最佳实践:
  • LLM 调用必加重试（API 不稳定）
  • 重要场景加降级（主模型挂了用备模型）
  • 输出解析加 try-except
  • 设置超时（防止无限等待）
  • 记录错误用于分析
```

**评分标准**：
- 3分：能用 with_retry
- 4分：能用 with_fallbacks 降级
- 5分：能设计完整错误处理方案

---

### Q12：LCEL 的流式输出与异步调用？

**难度级别**：高级
**考察维度**：性能优化

**问题描述**：
请说明 LCEL 如何实现流式输出和异步调用。

**参考答案**：

```
流式输出:
  chain = prompt | model | StrOutputParser()
  
  # 同步流式
  for chunk in chain.stream({"topic": "AI"}):
      print(chunk, end="", flush=True)
  
  # 异步流式
  async for chunk in chain.astream({"topic": "AI"}):
      print(chunk, end="")

异步调用:
  result = await chain.ainvoke({"topic": "AI"})
  
  # 批量异步（并发）
  results = await chain.abatch([
      {"topic": "AI"}, {"topic": "ML"}, {"topic": "DL"}
  ])

流式原理:
  LCEL 的 stream 会自动将链中每个组件转为流式:
  
  prompt | model | parser
  
  1. prompt.invoke(input) → 格式化 Prompt
  2. model.stream(prompt) → 逐 token 生成
  3. parser.stream(tokens) → 逐块解析
  
  整体: 边生成边解析边输出

并发批处理:
  results = await chain.abatch(inputs, config={
      "max_concurrency": 5  # 最多5个并发
  })

适用场景:
  流式 ✅: 聊天界面（打字机效果）、长文本生成
  异步 ✅: Web 服务、批量处理、多任务编排

Web 服务示例（FastAPI）:
  from fastapi import FastAPI
  from fastapi.responses import StreamingResponse
  
  app = FastAPI()
  chain = prompt | model | StrOutputParser()
  
  @app.post("/chat")
  async def chat(input: str):
      async def generate():
          async for chunk in chain.astream({"input": input}):
              yield f"data: {chunk}\n\n"
      return StreamingResponse(generate())
```

**评分标准**：
- 3分：能用 stream 和 ainvoke
- 4分：能解释流式原理
- 5分：能给出 Web 服务示例

---

## 五、Memory 记忆机制（3题）

### Q13：LangChain Memory 的类型与选型？

**难度级别**：中级
**考察维度**：记忆管理

**问题描述**：
请列举 LangChain 的 Memory 类型，说明各自原理和选型依据。

**参考答案**：

```
Memory 类型:

1. ConversationBufferMemory（全量缓存）
   • 保存所有对话历史
   • 简单但 Token 消耗线性增长

2. ConversationBufferWindowMemory（滑窗）
   • 只保留最近 K 轮对话
   • Token 消耗可控

3. ConversationSummaryMemory（摘要）
   • 用 LLM 将历史对话总结为摘要
   • 节省 Token，但会丢失细节

4. ConversationSummaryBufferMemory（摘要+缓冲）
   • 短期保留原文，长期转为摘要
   • 平衡细节和 Token

5. VectorStoreRetrieverMemory（向量检索）
   • 将对话存入向量库
   • 按相关性检索历史
   • 适合超长对话

6. EntityMemory（实体记忆）
   • 提取并记忆对话中的实体

选型依据:
  ┌──────────────────┬────────┬──────────┬──────────┐
  │ 类型              │ Token  │ 细节保留  │ 适用场景  │
  ├──────────────────┼────────┼──────────┼──────────┤
  │ Buffer           │ 高     │ 完整      │ 短对话    │
  │ Window           │ 低     │ 近期完整  │ 客服      │
  │ Summary          │ 低     │ 摘要      │ 长对话    │
  │ SummaryBuffer    │ 中     │ 近期+摘要 │ 通用推荐  │
  │ Vector           │ 可控   │ 相关检索  │ 超长对话  │
  │ Entity           │ 低     │ 实体      │ 信息追踪  │
  └──────────────────┴────────┴──────────┴──────────┘
```

**评分标准**：
- 3分：能列出 3 种以上 Memory
- 4分：能说明各自原理
- 5分：能给出选型依据

---

### Q14：如何在 LCEL 中集成 Memory？

**难度级别**：中级
**考察维度**：记忆集成

**问题描述**：
LCEL 推荐用 RunnableWithMessageHistory 管理记忆。请说明其用法和原理。

**参考答案**：

```
RunnableWithMessageHistory: LCEL 的记忆管理器

基本用法:
  from langchain_core.runnables.history import RunnableWithMessageHistory
  from langchain_core.chat_history import InMemoryChatMessageHistory
  
  chain = prompt | model | StrOutputParser()
  
  session_store = {}
  
  def get_history(session_id: str):
      if session_id not in session_store:
          session_store[session_id] = InMemoryChatMessageHistory()
      return session_store[session_id]
  
  chain_with_history = RunnableWithMessageHistory(
      chain, get_history,
      input_messages_key="input",
      history_messages_key="history",
  )
  
  result = chain_with_history.invoke(
      {"input": "我叫张三"},
      config={"configurable": {"session_id": "user123"}}
  )
  
  result = chain_with_history.invoke(
      {"input": "我叫什么？"},
      config={"configurable": {"session_id": "user123"}}
  )
  # → "你叫张三"（有记忆）

Prompt 模板配合:
  prompt = ChatPromptTemplate.from_messages([
      ("system", "你是助手"),
      ("placeholder", "{history}"),
      ("human", "{input}"),
  ])

持久化存储:
  from langchain_community.chat_message_histories import RedisChatMessageHistory
  
  def get_history(session_id):
      return RedisChatMessageHistory(
          session_id, url="redis://localhost:6379"
      )

原理:
  1. 用户调用时传入 session_id
  2. get_history 根据 session_id 获取历史
  3. 将历史消息注入 Prompt
  4. 调用 LLM 生成回复
  5. 将本轮对话存入历史
  6. 返回结果
```

**评分标准**：
- 3分：能用 RunnableWithMessageHistory
- 4分：能配置 session_id 和持久化
- 5分：能解释工作原理

---

### Q15：多用户会话隔离如何实现？

**难度级别**：高级
**考察维度**：工程实践

**问题描述**：
线上服务有多个用户同时使用。请说明如何实现会话隔离。

**参考答案**：

```
会话隔离: 每个用户/会话有独立的记忆

方案 1: session_id 区分
  config={"configurable": {"session_id": f"{user_id}_{session_id}"}}
  
  user1: session "user1_001" → 独立历史
  user2: session "user2_001" → 独立历史

方案 2: 持久化存储 + session_id
  from langchain_redis import RedisChatMessageHistory
  
  def get_history(session_id: str):
      return RedisChatMessageHistory(
          session_id=session_id,
          url="redis://redis:6379/0",
          key_prefix="chat:"
      )
  
  # Redis key: chat:user1_001 → 隔离

方案 3: 数据库存储
  from langchain_postgres import PostgresChatMessageHistory
  
  def get_history(session_id: str):
      return PostgresChatMessageHistory(
          table_name="chat_history",
          session_id=session_id,
          connection=engine
      )

完整多用户服务:
  from fastapi import FastAPI
  
  app = FastAPI()
  
  @app.post("/chat/{user_id}")
  async def chat(user_id: str, message: str):
      session_id = f"{user_id}_{get_session(user_id)}"
      result = await chain_with_history.ainvoke(
          {"input": message},
          config={"configurable": {"session_id": session_id}}
      )
      return {"response": result}

会话管理:
  • 会话超时: 30分钟无活动自动清理
  • 会话列表: 用户可查看历史会话
  • 会话切换: 同一用户可有多会话
  • 数据清理: 过期会话定期清理

性能优化:
  • Redis 缓存热会话
  • 冷会话持久化到数据库
  • 大会话自动摘要
  • 并发控制（避免同会话并发写入）
```

**评分标准**：
- 3分：能用 session_id 区分
- 4分：能实现持久化存储
- 5分：能设计完整多用户服务和会话管理

---

## 六、Agents 智能代理（3题）

### Q16：LangChain Agent 的核心原理是什么？

**难度级别**：高级
**考察维度**：Agent 原理

**问题描述**：
请说明 LangChain Agent 的工作原理，包括 ReAct 模式和决策流程。

**参考答案**：

```
Agent 本质: LLM 作为决策引擎，自主选择工具完成任务

ReAct 模式（Reasoning + Acting）:
  
  循环流程:
  ┌──────────────────────────────────┐
  │  1. Thought: 分析当前状态         │
  │  2. Action: 选择工具并调用        │
  │  3. Observation: 观察工具返回     │
  │  4. 重复 1-3 直到完成             │
  │  5. Final Answer: 给出最终答案    │
  └──────────────────────────────────┘

示例:
  用户: "北京今天天气怎么样？"
  
  Thought: 我需要查询北京天气
  Action: search_weather("北京")
  Observation: 北京晴，25℃
  Thought: 得到天气信息，可以回答了
  Final Answer: 北京今天晴天，气温25℃

Agent 类型:
  1. ReAct Agent: Thought-Action-Observation 循环
  2. OpenAI Functions Agent: 利用 Function Calling
  3. Structured Chat Agent: 支持多参数工具
  4. Self-Ask Agent: 分解问题为子问题

LCEL 创建 Agent:
  from langchain.agents import create_tool_calling_agent, AgentExecutor
  
  tools = [search_tool, calculator_tool]
  agent = create_tool_calling_agent(llm, tools, prompt)
  
  executor = AgentExecutor(
      agent=agent, tools=tools, verbose=True,
      max_iterations=5, handle_parsing_errors=True,
  )
  
  result = executor.invoke({"input": "北京天气如何？"})

决策流程:
  1. 用户输入 → 构造 Prompt（含工具描述）
  2. LLM 决策: 调用哪个工具 + 参数
  3. 执行工具 → 获取结果
  4. 结果加入上下文 → LLM 再次决策
  5. 判断是否完成 → 完成/继续
```

**评分标准**：
- 3分：能说出 ReAct 模式
- 4分：能用 AgentExecutor
- 5分：能解释决策流程

---

### Q17：Agent 的工具选择机制如何优化？

**难度级别**：高级
**考察维度**：Agent 优化

**问题描述**：
当工具数量很多时（如 20+），Agent 选择工具的准确率会下降。请说明优化方案。

**参考答案**：

```
工具选择挑战:
  • 工具多 → Prompt 长 → LLM 困惑
  • 相似工具 → 选择错误
  • 参数提取 → 格式错误

优化方案:

1. 工具描述优化
   ❌ "search: 搜索"
   ✅ "search_web(query: str): 搜索互联网获取最新信息
        适用: 需要实时数据、新闻、事实查询
        参数: query - 搜索关键词
        返回: 搜索结果摘要"

2. 工具检索（Tool Retrieval）
   • 不把所有工具放入 Prompt
   • 根据用户问题检索最相关的 Top-K 工具
   
   class ToolRetriever:
      def __init__(self, tools, embedding):
          self.tool_vectors = {
              t.name: embedding.embed_query(t.description)
              for t in tools
          }
      
      def get_relevant_tools(self, query, k=5):
          query_vec = embedding.embed_query(query)
          scores = {n: cosine(query_vec, v) 
                   for n, v in self.tool_vectors.items()}
          top_k = sorted(scores, key=scores.get, reverse=True)[:k]
          return [t for t in tools if t.name in top_k]

3. 工具分层
   层1: 常用工具（始终可用，3~5个）
   层2: 专业工具（按需检索）

4. 工具分组
   • 按功能分组（搜索/计算/文件/数据库）
   • 先选组，再选具体工具

5. Few-shot 示例
   "示例:
    '查天气' → search_weather
    '算数' → calculator"

6. 错误恢复
   handle_parsing_errors=True

效果评估:
  • 工具选择准确率
  • 参数提取准确率
  • 任务完成率
  • 平均迭代次数
```

**评分标准**：
- 3分：能优化工具描述
- 4分：能实现工具检索
- 5分：能设计工具分层和效果评估

---

### Q18：如何限制 Agent 的执行次数和成本？

**难度级别**：高级
**考察维度**：成本控制

**问题描述**：
Agent 可能陷入无限循环或过度调用工具。请说明如何限制执行次数和控制成本。

**参考答案**：

```
限制方案:

1. 迭代次数限制
   executor = AgentExecutor(
       agent=agent, tools=tools,
       max_iterations=5,
       early_stopping_method="generate",
   )

2. Token 消耗限制
   from langchain.callbacks import TokenCountingHandler
   
   token_counter = TokenCountingHandler()
   
   executor = AgentExecutor(
       agent=agent, tools=tools,
       callbacks=[token_counter],
   )
   
   if token_counter.total_tokens > 10000:
       raise Exception("Token 超限")

3. 超时控制
   import asyncio
   
   async def run_with_timeout(executor, input, timeout=60):
       try:
           return await asyncio.wait_for(
               executor.ainvoke(input), timeout=timeout
           )
       except asyncio.TimeoutError:
           return "处理超时"

4. 工具调用限制
   class LimitedTool:
       def __init__(self, tool, max_calls=3):
           self.tool = tool
           self.max_calls = max_calls
           self.call_count = 0
       
       def invoke(self, input):
           if self.call_count >= self.max_calls:
               raise Exception("工具调用超限")
           self.call_count += 1
           return self.tool.invoke(input)

5. 成本估算与预警
   class CostMonitor(BaseCallbackHandler):
       def __init__(self, budget=0.5):
           self.budget = budget
           self.cost = 0
       
       def on_llm_end(self, response, **kwargs):
           tokens = response.llm_output['token_usage']
           self.cost += (
               tokens['prompt_tokens'] * 0.03 / 1000 +
               tokens['completion_tokens'] * 0.06 / 1000
           )
           if self.cost > self.budget:
               raise Exception(f"成本超限: ${self.cost:.2f}")

监控指标:
  • 平均迭代次数（目标 <3）
  • 平均 Token 消耗
  • 平均成本/请求
  • 超时率
  • 任务完成率

最佳实践:
  • max_iterations 设为 3~5
  • 设成本上限
  • 加超时（60s 内）
  • 监控并优化 Prompt
```

**评分标准**：
- 3分：能用 max_iterations
- 4分：能实现 Token 和成本监控
- 5分：能设计完整限制方案和监控

---

## 七、Retrieval 检索增强（3题）

### Q19：LangChain RAG 的完整流程？

**难度级别**：中级
**考察维度**：RAG 实现

**问题描述**：
请用 LangChain 实现一个完整的 RAG 流程。

**参考答案**：

```
RAG 完整流程:

  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ 文档加载  │ → │ 文本分割  │ → │ 向量化    │ → │ 向量存储  │
  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘
                                                     │
  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
  │ 生成回答  │ ← │ LLM 生成  │ ← │ 检索      │ ←─────┘
  └──────────┘   └──────────┘   └──────────┘

1. 文档加载
   from langchain_community.document_loaders import PyPDFLoader
   loader = PyPDFLoader("document.pdf")
   docs = loader.load()

2. 文本分割
   from langchain_textsplitters import RecursiveCharacterTextSplitter
   
   splitter = RecursiveCharacterTextSplitter(
       chunk_size=500, chunk_overlap=50,
       separators=["\n\n", "\n", "。", "，", " "]
   )
   chunks = splitter.split_documents(docs)

3. 向量化 + 存储
   from langchain_openai import OpenAIEmbeddings
   from langchain_chroma import Chroma
   
   embeddings = OpenAIEmbeddings()
   vectorstore = Chroma.from_documents(
       chunks, embeddings, persist_directory="./chroma"
   )

4. 检索
   retriever = vectorstore.as_retriever(
       search_type="similarity",
       search_kwargs={"k": 5}
   )

5. 生成（LCEL）
   from langchain_core.runnables import RunnablePassthrough
   
   prompt = ChatPromptTemplate.from_template("""
   根据以下资料回答问题:
   {context}
   问题: {question}
   """)
   
   def format_docs(docs):
       return "\n\n".join(d.page_content for d in docs)
   
   rag_chain = (
       {"context": retriever | format_docs,
        "question": RunnablePassthrough()}
       | prompt | llm | StrOutputParser()
   )
   
   result = rag_chain.invoke("什么是RAG？")

多轮对话 RAG:
   from langchain_core.runnables.history import RunnableWithMessageHistory
   
   rag_with_memory = RunnableWithMessageHistory(
       rag_chain, get_history,
       input_messages_key="question",
       history_messages_key="history",
   )
```

**评分标准**：
- 3分：能实现基本 RAG 流程
- 4分：能用 LCEL 组合
- 5分：能实现多轮对话 RAG

---

### Q20：如何优化 RAG 的检索质量？

**难度级别**：高级
**考察维度**：检索优化

**问题描述**：
基础 RAG 的检索质量往往不佳。请说明优化方案。

**参考答案**：

```
检索质量优化:

1. 文本分割优化
   • 合适的 chunk_size（500~1000）
   • chunk_overlap（50~100）避免切断
   • 按语义分割（句子/段落边界）
   • 父子分片（小块检索，大块返回上下文）

2. Embedding 优化
   • 选好的 Embedding 模型（bge-large/m3e）
   • 领域微调 Embedding
   • 多语言用 multilingual 模型

3. 多种检索方式
   # MMR（最大边际相关性，去重）
   retriever = vectorstore.as_retriever(
       search_type="mmr",
       search_kwargs={"k": 5, "fetch_k": 20, "lambda": 0.5}
   )

4. 混合检索（Hybrid Search）
   • 向量检索（语义）+ 关键词检索（BM25）
   
   from langchain_community.retrievers import BM25Retriever
   from langchain.retrievers import EnsembleRetriever
   
   bm25 = BM25Retriever.from_documents(chunks)
   vector = vectorstore.as_retriever()
   
   ensemble = EnsembleRetriever(
       retrievers=[bm25, vector], weights=[0.3, 0.7]
   )

5. Query 重写（Multi-Query）
   from langchain.retrievers.multi_query import MultiQueryRetriever
   
   retriever = MultiQueryRetriever.from_llm(
       retriever=vectorstore.as_retriever(), llm=llm
   )

6. 重排序（Reranking）
   from langchain_cohere import CohereRerank
   from langchain.retrievers import ContextualCompressionRetriever
   
   compressor = CohereRerank(top_n=5)
   compression_retriever = ContextualCompressionRetriever(
       base_compressor=compressor,
       base_retriever=vectorstore.as_retriever(search_kwargs={"k": 20})
   )

7. 元数据过滤
   retriever = vectorstore.as_retriever(
       search_kwargs={"filter": {"source": "official_docs"}}
   )

8. HyDE（假设性文档嵌入）
   from langchain.retrievers import HydeRetriever
   
   hyde = HydeRetriever(
       llm=llm, base_retriever=vectorstore.as_retriever()
   )

评估指标:
  • 召回率 / 准确率 / MRR / 端到端答案准确率
```

**评分标准**：
- 3分：能优化 chunk 和 Embedding
- 4分：能实现混合检索和重排序
- 5分：能实现 Query 重写和 HyDE

---

### Q21：如何实现增量索引和文档更新？

**难度级别**：高级
**考察维度**：工程实践

**问题描述**：
文档库会不断更新。请说明如何实现增量索引。

**参考答案**：

```
增量索引方案:

1. 文档变更检测
   import hashlib
   
   def get_file_hash(path):
       with open(path, 'rb') as f:
           return hashlib.md5(f.read()).hexdigest()
   
   def detect_changes(doc_dir, known_hashes):
       changes = {"added": [], "modified": [], "deleted": []}
       current_files = set()
       
       for file in Path(doc_dir).glob("**/*"):
           if file.is_file():
               current_files.add(str(file))
               h = get_file_hash(file)
               if str(file) not in known_hashes:
                   changes["added"].append(file)
               elif known_hashes[str(file)] != h:
                   changes["modified"].append(file)
               known_hashes[str(file)] = h
       
       for old_file in list(known_hashes):
           if old_file not in current_files:
               changes["deleted"].append(old_file)
       
       return changes

2. 增量更新向量库
   def update_vectorstore(vectorstore, changes):
       for doc_id in changes["deleted"] + changes["modified"]:
           vectorstore.delete([doc_id])
       
       new_docs = []
       for file in changes["added"] + changes["modified"]:
           docs = loader.load(file)
           chunks = splitter.split_documents(docs)
           for chunk in chunks:
               chunk.metadata["doc_id"] = str(file)
           new_docs.extend(chunks)
       
       if new_docs:
           vectorstore.add_documents(new_docs)

3. 定时同步
   from apscheduler import AsyncIOScheduler
   
   scheduler = AsyncIOScheduler()
   scheduler.add_job(sync_documents, 'interval', hours=1)
   scheduler.start()

4. 版本控制
   • 保留历史版本（支持回滚）
   • 用时间戳区分版本
   
   retriever = vectorstore.as_retriever(
       search_kwargs={"filter": {"version": {"$lte": current_version}}}
   )

最佳实践:
  • 文档 ID 唯一且稳定（用路径/hash）
  • 变更检测用 hash
  • 增量而非全量重建
  • 定时同步 + 手动触发
  • 更新后验证检索效果
```

**评分标准**：
- 3分：能实现基本增删
- 4分：能实现变更检测
- 5分：能设计定时同步和版本控制

---

## 八、Tools 工具调用（3题）

### Q22：如何定义和注册自定义工具？

**难度级别**：中级
**考察维度**：工具开发

**问题描述**：
请说明 LangChain 中如何定义自定义工具。

**参考答案**：

```
定义工具的三种方式:

方式 1: @tool 装饰器（推荐）
   from langchain_core.tools import tool
   
   @tool
   def search_weather(city: str) -> str:
       """查询指定城市的天气。
       
       Args:
           city: 城市名称（中文）
       
       Returns:
           天气描述
       """
       return f"{city}今天晴，25℃"

方式 2: 继承 BaseTool
   from langchain_core.tools import BaseTool
   
   class CalculatorTool(BaseTool):
       name: str = "calculator"
       description: str = "数学计算器，支持四则运算"
       
       def _run(self, expression: str) -> str:
           try:
               return str(eval(expression))
           except:
               return "计算错误"
       
       async def _arun(self, expression: str) -> str:
           return self._run(expression)

方式 3: StructuredTool
   from langchain_core.tools import StructuredTool
   from pydantic import BaseModel
   
   class SearchInput(BaseModel):
       query: str
       max_results: int = 5
   
   search_tool = StructuredTool.from_function(
       func=search_func, name="search",
       description="搜索互联网", args_schema=SearchInput
   )

使用工具:
   tools = [search_weather, calculator_tool, search_tool]
   agent = create_tool_calling_agent(llm, tools, prompt)
   executor = AgentExecutor(agent=agent, tools=tools)
   
   result = executor.invoke({"input": "北京天气如何？"})

最佳实践:
  • 工具名清晰（动词_名词）
  • 描述包含功能、参数、返回
  • 参数有类型注解
  • 加错误处理
  • 异步场景实现 _arun
```

**评分标准**：
- 3分：能用 @tool 定义工具
- 4分：能继承 BaseTool
- 5分：能用 StructuredTool 并给出最佳实践

---

### Q23：如何实现工具的参数验证和错误处理？

**难度级别**：高级
**考察维度**：工具健壮性

**问题描述**：
LLM 提取的工具参数可能有误。请说明如何做参数验证和错误处理。

**参考答案**：

```
参数验证:

1. Pydantic Schema 验证
   from pydantic import BaseModel, Field, validator
   
   class WeatherInput(BaseModel):
       city: str = Field(..., description="城市名称")
       date: str = Field("today", description="日期")
       
       @validator('city')
       def city_not_empty(cls, v):
           if not v.strip():
               raise ValueError("城市不能为空")
           return v
   
   @tool(args_schema=WeatherInput)
   def search_weather(city: str, date: str) -> str:
       """查询天气"""
       return f"{city} {date} 天气..."

2. 运行时验证
   @tool
   def send_email(to: str, subject: str, body: str) -> str:
       """发送邮件"""
       if '@' not in to:
           return "错误: 邮箱格式不正确"
       if len(subject) > 100:
           return "错误: 标题过长"
       try:
           smtp.send(to, subject, body)
           return "发送成功"
       except Exception as e:
           return f"发送失败: {str(e)}"

错误处理策略:

1. 返回错误信息（让 LLM 决策）
   def _run(self, input):
       try:
           return do_something(input)
       except Exception as e:
           return f"执行失败: {e}"
   
   # LLM 看到错误后可调整参数重试

2. Agent 级错误处理
   executor = AgentExecutor(
       agent=agent, tools=tools,
       handle_parsing_errors=True,
   )

3. 重试机制
   from tenacity import retry, stop_after_attempt
   
   @tool
   @retry(stop=stop_after_attempt(3))
   def call_api(input: str) -> str:
       response = requests.get(...)
       response.raise_for_status()
       return response.text

4. 超时控制
   @tool
   async def long_running_task(input: str) -> str:
       try:
           return await asyncio.wait_for(
               do_async_work(input), timeout=30
           )
       except asyncio.TimeoutError:
           return "任务超时"

最佳实践:
  • 用 Pydantic 做参数 Schema
  • 工具内部做验证
  • 错误信息返回给 LLM（可重试）
  • 加超时和重试
  • 记录工具调用日志
```

**评分标准**：
- 3分：能用 Pydantic 验证
- 4分：能实现错误返回策略
- 5分：能设计重试、超时、日志完整方案

---

### Q24：如何实现工具的权限控制？

**难度级别**：高级
**考察维度**：安全设计

**问题描述**：
某些工具（如删除文件、发送邮件）需要权限控制。请说明如何实现。

**参考答案**：

```
权限控制方案:

1. 工具分级
   • 公开工具: 所有用户可用（查询/搜索）
   • 授权工具: 需用户确认（发送邮件/修改数据）
   • 管理工具: 仅管理员可用（删除/系统配置）

2. Human-in-the-loop（人工确认）
   executor = AgentExecutor(
       agent=agent, tools=[send_email],
       tools_requiring_confirmation=["send_email"],
   )

3. 基于角色的权限（RBAC）
   class SecureTool(BaseTool):
       name: str = "delete_file"
       description: str = "删除文件（需管理员权限）"
       required_role: str = "admin"
       
       def _run(self, path: str, user_role: str = "user") -> str:
           if user_role != self.required_role:
               raise ToolException(f"权限不足: 需要 {self.required_role}")
           os.remove(path)
           return f"已删除 {path}"

4. 工具白名单/黑名单
   class ToolManager:
       def __init__(self, all_tools):
           self.all_tools = all_tools
           self.user_tools = {}
       
       def grant(self, user_id, tool_names):
           self.user_tools[user_id] = set(tool_names)
       
       def get_tools(self, user_id):
           allowed = self.user_tools.get(user_id, set())
           return [t for t in self.all_tools if t.name in allowed]

5. 操作审计
   class AuditHandler(BaseCallbackHandler):
       def on_tool_start(self, tool, input_str, **kwargs):
           log_audit(
               user_id=kwargs.get('user_id'),
               tool=tool, input=input_str,
               timestamp=datetime.now()
           )

6. 敏感操作二次验证
   @tool
   def transfer_money(amount: float, to: str) -> str:
       """转账（需二次验证）"""
       if amount > 10000:
           return "大额转账需人工审核"
       code = send_verification_code(user.phone)
       if not verify_code(code):
           return "验证失败"
       return f"已转账 {amount} 至 {to}"

最佳实践:
  • 高危工具必须人工确认
  • 基于角色控制可用工具
  • 记录所有工具调用审计日志
  • 敏感操作二次验证
  • 工具参数做范围限制
```

**评分标准**：
- 3分：能实现人工确认
- 4分：能实现 RBAC
- 5分：能设计审计和二次验证

---

## 九、Callbacks 与可观测性（3题）

### Q25：LangChain 的 Callback 系统设计？

**难度级别**：中级
**考察维度**：可观测性

**问题描述**：
请说明 LangChain Callback 系统的设计和用法。

**参考答案**：

```
Callback 系统: 在组件执行的关键节点触发自定义逻辑

核心接口: BaseCallbackHandler
  from langchain_core.callbacks import BaseCallbackHandler
  
  class MyCallback(BaseCallbackHandler):
      # LLM 相关
      def on_llm_start(self, serialized, prompts, **kwargs): ...
      def on_llm_new_token(self, token, **kwargs): ...
      def on_llm_end(self, response, **kwargs): ...
      def on_llm_error(self, error, **kwargs): ...
      
      # Chain 相关
      def on_chain_start(self, serialized, inputs, **kwargs): ...
      def on_chain_end(self, outputs, **kwargs): ...
      
      # Tool 相关
      def on_tool_start(self, serialized, input_str, **kwargs): ...
      def on_tool_end(self, output, **kwargs): ...
      
      # Agent 相关
      def on_agent_action(self, action, **kwargs): ...
      def on_agent_finish(self, finish, **kwargs): ...

使用方式:

1. 全局 Callback
   import langchain
   langchain.verbose = True  # 详细输出