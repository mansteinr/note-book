# 高级AI全栈工程师面试题

> 涵盖AI核心概念、前后端开发、系统架构、性能优化等全面内容

---

## 目录

1. [AI核心概念篇](#ai核心概念篇)
2. [前端开发篇](#前端开发篇)
3. [后端开发篇](#后端开发篇)
4. [AI集成篇](#ai集成篇)
5. [系统架构篇](#系统架构篇)
6. [性能优化篇](#性能优化篇)
7. [安全性篇](#安全性篇)
8. [项目实战篇](#项目实战篇)

---

## AI核心概念篇

### 一、选择题

**1. RAG（检索增强生成）的主要作用是什么？**
A. 提高模型推理速度
B. 增强模型生成能力，提供实时/专业知识
C. 减少模型参数
D. 完全替代模型训练

> **答案：B**  
> RAG通过检索相关上下文数据，增强模型生成能力，让模型能基于最新/专业知识回答。

---

**2. Agent（智能体）的核心能力不包括以下哪个？**
A. 自主决策
B. 工具使用
C. 状态管理
D. 模型训练

> **答案：D**  
> Agent的核心能力是自主决策、工具使用、状态管理、目标导向，不包括模型训练。

---

**3. FunctionCall（函数调用）在AI系统中的作用类似于什么？**
A. 前端组件库
B. 后端API接口
C. 插件系统
D. 数据库查询

> **答案：C**  
> FunctionCall让AI能够调用外部函数，类似前端插件系统或后端API集成。

---

**4. MCP（模型上下文协议）主要解决什么问题？**
A. 模型精度不足
B. 不同AI系统之间的标准化通信
C. 推理速度慢
D. 内存占用高

> **答案：B**  
> MCP是AI世界的通信协议标准，解决不同系统间的标准化交互问题。

---

**5. 在向量检索中，"嵌入"（Embedding）的作用是什么？**
A. 压缩文本大小
B. 将文本转换为数值向量表示
C. 加密文本内容
D. 提高文本可读性

> **答案：B**  
> Embedding将文本转换为高维数值向量，用于计算相似度和检索。

---

### 二、简答题

**1. 请详细解释RAG的工作原理，并说明其与Fine-tuning（微调）的区别和适用场景。**

> **答案：**  
> **RAG工作原理**：
> 1. **检索阶段**：将用户查询转换为向量，在向量数据库中检索最相关的文档片段
> 2. **增强阶段**：将检索到的相关上下文与用户查询组合，构建增强的提示词
> 3. **生成阶段**：将增强提示输入LLM，让模型基于上下文生成回答
> 
> **与Fine-tuning的区别**：
> - **RAG**：通过检索提供上下文，不改变模型参数，适合实时/动态知识，更新成本低
> - **Fine-tuning**：修改模型参数，适合固定知识，更新成本高，可能导致遗忘
> 
> **适用场景**：
> - **RAG**：知识库问答、客服系统、实时数据增强
> - **Fine-tuning**：领域特定任务、风格适配、性能优化

---

**2. Agent的核心架构包括哪些组件？请描述一个Agent的完整工作流程。**

> **答案：**  
> **Agent核心架构**：
> - **LLM大脑**：负责推理和决策
> - **工具库**：Agent可调用的工具集合
> - **记忆模块**：短期/长期记忆
> - **规划模块**：任务分解和规划
> - **执行模块**：工具调用和结果整合
> 
> **完整工作流程**：
> 1. **理解用户意图**：分析用户请求，明确目标
> 2. **规划任务**：将复杂任务分解为可执行步骤
> 3. **选择工具**：根据任务选择合适的工具
> 4. **执行工具调用**：调用FunctionCall执行具体操作
> 5. **观察结果**：分析工具返回结果
> 6. **反思与调整**：根据结果调整策略
> 7. **整合输出**：生成最终回答
> 8. **更新记忆**：记录交互和结果

---

**3. FunctionCall的工作流程是什么？在实现FunctionCall时需要注意哪些关键点？**

> **答案：**  
> **工作流程**：
> 1. **函数注册**：定义函数名称、描述、参数schema
> 2. **意图识别**：LLM判断用户请求是否需要调用函数
> 3. **参数提取**：从用户对话中提取函数所需参数
> 4. **执行调用**：实际调用函数并获取结果
> 5. **结果整合**：将函数结果作为上下文，让LLM生成最终回答
> 
> **关键点**：
> - **函数描述清晰**：让LLM准确理解函数用途
> - **参数schema完整**：使用JSON Schema描述参数类型和要求
> - **错误处理**：处理函数执行失败的情况
> - **幂等设计**：多次调用不产生副作用
> - **安全验证**：验证函数调用的安全性
> - **超时控制**：避免函数执行时间过长

---

**4. 请从系统架构的角度说明RAG、Agent、FunctionCall、MCP四者的关系和协同方式。**

> **答案：**  
> **四者关系**：
> - **MCP**：底层通信协议，标准化各组件间的交互
> - **FunctionCall**：工具调用层，让AI能够执行具体操作
> - **RAG**：知识检索层，提供上下文增强
> - **Agent**：决策和控制层，协调整个流程
> 
> **协同方式**：
> ```
> 用户 → UI层 
>      → Agent层（决策、状态管理）
>      → FunctionCall层（工具调用）
>      → RAG层（知识检索）
>      → 数据源层（向量DB、API、文件）
>      → MCP协议（标准化通信）
> ```
> 
> **具体协同**：
> 1. Agent通过MCP接收用户请求
> 2. Agent决定需要使用RAG检索知识
> 3. Agent调用FunctionCall执行具体操作
> 4. 所有通信通过MCP标准化，确保兼容性

---

### 三、编程题

**1. 实现一个简单的RAG系统，包括文本切分、向量化存储、相似度检索三个核心部分。**

> **参考答案：**
```javascript
// simple-rag.js
class SimpleRAG {
  constructor() {
    this.documents = [];
    this.embeddings = [];
  }

  // 文本切分
  splitText(text, chunkSize = 500, overlap = 100) {
    const chunks = [];
    let start = 0;
    while (start < text.length) {
      const end = start + chunkSize;
      const chunk = text.slice(start, end);
      chunks.push(chunk);
      start = end - overlap;
    }
    return chunks;
  }

  // 简单的文本向量化（实际中使用OpenAI Embeddings或Sentence-Transformers）
  async embedText(text) {
    const words = text.toLowerCase().split(/\s+/);
    const vector = new Array(100).fill(0);
    words.forEach((word, i) => {
      const hash = word.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
      vector[hash % 100] += 1;
    });
    const norm = Math.sqrt(vector.reduce((a, b) => a + b * b, 0));
    return vector.map(v => v / norm);
  }

  // 添加文档到RAG系统
  async addDocuments(texts) {
    for (const text of texts) {
      const chunks = this.splitText(text);
      for (const chunk of chunks) {
        const embedding = await this.embedText(chunk);
        this.documents.push({ text: chunk, embedding });
        this.embeddings.push(embedding);
      }
    }
  }

  // 计算余弦相似度
  cosineSimilarity(a, b) {
    const dot = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const normA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const normB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    return dot / (normA * normB);
  }

  // 相似度检索
  async retrieve(query, topK = 3) {
    const queryEmbedding = await this.embedText(query);
    const results = this.documents.map((doc, i) => ({
      text: doc.text,
      similarity: this.cosineSimilarity(queryEmbedding, doc.embedding)
    }));
    results.sort((a, b) => b.similarity - a.similarity);
    return results.slice(0, topK);
  }

  // 增强生成
  async generateWithRAG(query, llm) {
    const retrieved = await this.retrieve(query);
    const context = retrieved.map(r => r.text).join('\n\n');
    const prompt = `基于以下上下文回答问题：
上下文：${context}
问题：${query}
回答：`;
    return await llm(prompt);
  }
}

// 使用示例
async function demo() {
  const rag = new SimpleRAG();
  
  // 添加文档
  await rag.addDocuments([
    "RAG（检索增强生成）是一种将信息检索与文本生成结合的技术...",
    "Agent（智能体）具有自主决策、工具使用、状态管理等能力...",
    "FunctionCall让AI能够调用外部函数，类似插件系统..."
  ]);

  // 检索并生成回答
  const answer = await rag.generateWithRAG("什么是RAG？", async (p) => `模拟回答：${p}`);
  console.log(answer);
}

demo();
```

---

**2. 实现一个Agent类，具备简单的工具调用和对话管理能力。**

> **参考答案：**
```javascript
// simple-agent.js
class SimpleAgent {
  constructor() {
    this.memory = []; // 对话记忆
    this.tools = {}; // 可用工具
  }

  // 注册工具
  registerTool(name, description, func) {
    this.tools[name] = { name, description, func };
  }

  // 添加到记忆
  addToMemory(role, content) {
    this.memory.push({ role, content, timestamp: Date.now() });
  }

  // 简单的决策逻辑（实际中使用LLM）
  decideAction(query) {
    // 基于关键词决定使用哪个工具
    const lowerQuery = query.toLowerCase();
    if (lowerQuery.includes('天气')) return 'getWeather';
    if (lowerQuery.includes('计算') || lowerQuery.includes('算')) return 'calculate';
    if (lowerQuery.includes('搜索') || lowerQuery.includes('查找')) return 'search';
    return 'chat';
  }

  // 执行工具调用
  async callTool(toolName, args) {
    if (!this.tools[toolName]) throw new Error(`工具 ${toolName} 不存在`);
    try {
      const result = await this.tools[toolName].func(args);
      return { success: true, result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // 生成响应
  async handleRequest(query) {
    // 添加用户请求到记忆
    this.addToMemory('user', query);

    // 决策使用哪个工具
    const action = this.decideAction(query);

    let toolResult = null;
    if (action !== 'chat') {
      // 简单的参数提取（实际中使用LLM）
      const args = this.extractArgs(query, action);
      toolResult = await this.callTool(action, args);
    }

    // 生成响应（实际中使用LLM）
    const response = this.generateResponse(query, action, toolResult);

    // 添加到记忆
    this.addToMemory('assistant', response);

    return response;
  }

  // 简单的参数提取
  extractArgs(query, toolName) {
    const args = {};
    if (toolName === 'getWeather') {
      const cityMatch = query.match(/(?:北京|上海|广州|深圳|杭州)/);
      args.city = cityMatch ? cityMatch[0] : '北京';
    }
    if (toolName === 'calculate') {
      const exprMatch = query.match(/(\d+\s*[+\-*/]\s*\d+)/);
      args.expression = exprMatch ? exprMatch[0] : '0';
    }
    if (toolName === 'search') {
      args.query = query.replace(/(?:搜索|查找)/, '').trim();
    }
    return args;
  }

  // 生成响应
  generateResponse(query, action, toolResult) {
    if (action === 'chat') {
      return `我理解您的问题：${query}。这是一个对话响应。`;
    }
    if (toolResult?.success) {
      return `工具 ${action} 执行成功！结果：${JSON.stringify(toolResult.result)}`;
    }
    return `工具执行失败：${toolResult?.error}`;
  }
}

// 使用示例
async function demo() {
  const agent = new SimpleAgent();

  // 注册工具
  agent.registerTool('getWeather', '获取天气信息', async ({ city }) => {
    const weatherData = {
      '北京': '晴天，25°C',
      '上海': '多云，22°C',
      '广州': '小雨，28°C'
    };
    return weatherData[city] || '暂无该城市天气数据';
  });

  agent.registerTool('calculate', '执行计算', async ({ expression }) => {
    return eval(expression); // 仅示例，实际中要安全处理
  });

  agent.registerTool('search', '搜索信息', async ({ query }) => {
    return `搜索结果：这是关于"${query}"的信息...`;
  });

  // 使用Agent
  const response1 = await agent.handleRequest('今天北京天气怎么样？');
  console.log(response1);

  const response2 = await agent.handleRequest('帮我计算 25 * 4');
  console.log(response2);
}

demo();
```

---

## 前端开发篇

### 一、选择题

**1. 在AI应用前端开发中，最适合处理流式响应的方式是？**
A. fetch API
B. EventSource
C. WebSocket
D. Axios

> **答案：C**  
> WebSocket或ReadableStream + fetch都适合处理流式响应，WebSocket提供双向实时通信。

---

**2. 对于Agent的对话状态管理，以下哪个状态管理方案最合适？**
A. localStorage
B. Redux/Zustand
C. URL参数
D. sessionStorage

> **答案：B**  
> 需要复杂状态管理和持久化的Agent对话，Redux/Zustand是更好的选择。

---

**3. 在AI聊天界面中，Markdown渲染通常使用什么库？**
A. React-markdown
B. Marked
C. Highlight.js
D. A和B都可以

> **答案：D**  
> React-markdown适合React应用，Marked适合Vue或原生应用，两者都可以渲染Markdown。

---

### 二、简答题

**1. 请设计一个AI聊天应用的前端架构，并说明各组件的职责。**

> **答案：**  
> **前端架构**：
> ```
> src/
> ├── components/
> │   ├── ChatInput/      # 输入组件
> │   ├── ChatMessages/   # 消息列表组件
> │   ├── MessageBubble/  # 单条消息组件
> │   ├── TypingIndicator/# 输入指示器
> │   └── ToolCalls/      # 工具调用展示
> ├── hooks/
> │   ├── useChat/        # 聊天逻辑Hook
> │   ├── useAgent/       # Agent管理Hook
> │   └── useStreaming/   # 流式响应Hook
> ├── store/
> │   └── chatStore/      # 聊天状态管理
> ├── services/
> │   ├── aiService/      # AI API服务
> │   └── mcpClient/      # MCP协议客户端
> └── utils/
>     ├── markdown/       # Markdown渲染
>     └── storage/        # 本地存储
> ```
> 
> **组件职责**：
> - **ChatInput**：处理用户输入，支持文本、文件上传
> - **ChatMessages**：渲染消息列表，支持滚动加载
> - **MessageBubble**：单条消息，支持Markdown、代码高亮
> - **useChat**：封装聊天逻辑，包括消息发送、流式响应处理
> - **chatStore**：管理聊天历史、Agent状态、工具调用历史
> - **aiService**：封装AI API调用
> - **mcpClient**：MCP协议通信

---

**2. 在处理LLM流式响应时，有哪些技术挑战？如何解决？**

> **答案：**  
> **技术挑战**：
> 1. **数据流解析**：处理Server-Sent Events或WebSocket数据流
> 2. **Markdown增量渲染**：支持部分渲染和实时更新
> 3. **错误重连**：连接断开时的自动重连机制
> 4. **中断和取消**：支持用户中途取消生成
> 5. **性能优化**：长文本渲染的性能问题
> 
> **解决方案**：
> 1. **数据流解析**：使用ReadableStream + TextDecoder
> 2. **增量渲染**：虚拟列表、增量DOM更新
> 3. **错误重连**：指数退避重试策略
> 4. **中断取消**：AbortController + Promise.race
> 5. **性能优化**：Memo、懒加载、分页渲染
> 
> **代码示例**：
```javascript
async function streamChat(prompt, onMessage, onComplete) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ prompt }),
    signal: controller.signal
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullText = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    fullText += chunk;
    onMessage(fullText);
  }
  onComplete(fullText);
}
```

---

### 三、编程题

**1. 实现一个支持流式响应的聊天组件，使用React和ReadableStream。**

> **参考答案：**
```jsx
// StreamChat.jsx
import { useState, useRef, useEffect, useCallback } from 'react';

function StreamChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const scrollRef = useRef(null);
  const abortControllerRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamingMessage]);

  // 发送消息
  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = { role: 'user', content: input.trim(), id: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    setCurrentStreamingMessage('');

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          messages: [...messages, userMessage] 
        }),
        signal: abortControllerRef.current.signal
      });

      // 处理流式响应
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        setCurrentStreamingMessage(prev => prev + chunk);
      }

      // 添加完整消息
      const assistantMessage = { 
        role: 'assistant', 
        content: currentStreamingMessage, 
        id: Date.now() + 1 
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Error:', error);
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: '抱歉，发生了错误。', 
          id: Date.now() 
        }]);
      }
    } finally {
      setIsStreaming(false);
      setCurrentStreamingMessage('');
      abortControllerRef.current = null;
    }
  }, [input, isStreaming, messages, currentStreamingMessage]);

  // 取消生成
  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {isStreaming && (
          <div className="message assistant">
            <div className="message-content">{currentStreamingMessage}</div>
            <button onClick={handleCancel} className="cancel-btn">
              取消
            </button>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
          placeholder="输入消息..."
          disabled={isStreaming}
        />
        <button onClick={handleSend} disabled={isStreaming || !input.trim()}>
          {isStreaming ? '发送中...' : '发送'}
        </button>
      </div>
    </div>
  );
}

export default StreamChat;
```

---

## 后端开发篇

### 一、选择题

**1. 在Node.js中处理AI API流式响应，最合适的方式是？**
A. Promise
B. ReadableStream
C. EventEmitter
D. 定时器

> **答案：B**  
> ReadableStream是处理流式响应的标准方式。

---

**2. 对于向量数据库，以下哪个不是常用选择？**
A. Pinecone
B. Weaviate
C. Redis
D. PostgreSQL

> **答案：C**  
> Redis虽然可以存向量，但不是专门的向量数据库，Pinecone、Weaviate、PostgreSQL(pgvector)都是常用选择。

---

**3. LangChain主要解决什么问题？**
A. 模型训练
B. LLM应用编排
C. 数据存储
D. 前端渲染

> **答案：B**  
> LangChain是LLM应用编排框架，用于构建复杂的LLM应用。

---

### 二、简答题

**1. 设计一个RAG后端服务的架构，包括数据层、服务层、API层。**

> **答案：**  
> **架构设计**：
> ```
> src/
> ├── api/
> │   └── routes/
> │       ├── chat.js       # 聊天API
> │       └── documents.js  # 文档管理API
> ├── services/
> │   ├── ragService.js     # RAG核心服务
> │   ├── embeddingService.js # 向量化服务
> │   └── llmService.js     # LLM服务
> ├── models/
> │   └── vectorStore.js    # 向量数据库操作
> ├── middleware/
> │   ├── auth.js           # 身份验证
> │   └── rateLimit.js      # 限流
> └── utils/
>     ├── textSplitter.js  # 文本切分
>     └── cache.js          # 缓存
> ```
> 
> **核心流程**：
> 1. **文档处理**：上传文档 → 切分 → 向量化 → 存入向量DB
> 2. **检索查询**：接收问题 → 向量化 → 相似度检索 → 返回相关文档
> 3. **生成回答**：检索上下文 + 用户问题 → 提示词构建 → LLM生成
> 4. **流式输出**：使用SSE或WebSocket流式返回结果

---

**2. 在构建AI后端服务时，如何处理API限流和成本控制？**

> **答案：**  
> **限流策略**：
> - **用户级限流**：每个用户有请求配额
> - **Token级限流**：限制总Token消耗
> - **IP级限流**：防止攻击
> - **队列系统**：超出限流时排队处理
> 
> **成本控制**：
> - **提示词优化**：减少不必要的Token
> - **缓存策略**：相似问题复用结果
> - **模型选择**：根据任务选择合适模型
> - **批量处理**：合并多个请求
> - **预算监控**：实时监控和预警
> 
> **技术实现**：
```javascript
// 限流中间件示例
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import redis from 'redis';

const client = redis.createClient();

const apiLimiter = rateLimit({
  store: new RedisStore({ client }),
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 100, // 100次请求
  message: '请求过于频繁，请稍后再试'
});

// Token计数
async function countTokens(text) {
  const tokens = text.split(/\s+/).length; // 简化计算
  return tokens;
}

// 缓存问答
import NodeCache from 'node-cache';
const answerCache = new NodeCache({ stdTTL: 3600 });

function getCachedAnswer(question) {
  const hash = require('crypto')
    .createHash('md5')
    .update(question)
    .digest('hex');
  return answerCache.get(hash);
}

function setCachedAnswer(question, answer) {
  const hash = require('crypto')
    .createHash('md5')
    .update(question)
    .digest('hex');
  answerCache.set(hash, answer);
}
```

---

### 三、编程题

**1. 基于Express.js实现一个简单的RAG后端API，包括文档上传、检索、聊天接口。**

> **参考答案：**
```javascript
// rag-backend.js
import express from 'express';
import multer from 'multer';
import { OpenAI } from 'openai';
import { Pinecone } from '@pinecone-database/pinecone';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';

const app = express();
const upload = multer({ dest: 'uploads/' });
app.use(express.json());

// 配置
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
const index = pinecone.index('rag-documents');

const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});

// 向量化
async function createEmbeddings(texts) {
  const embeddings = await Promise.all(
    texts.map(async text => {
      const response = await openai.embeddings.create({
        model: 'text-embedding-ada-002',
        input: text
      });
      return response.data[0].embedding;
    })
  );
  return embeddings;
}

// 上传文档API
app.post('/api/documents', upload.single('file'), async (req, res) => {
  try {
    const fileText = req.file ? require('fs').readFileSync(req.file.path, 'utf-8') : req.body.text;
    
    // 切分文本
    const chunks = await textSplitter.splitText(fileText);
    
    // 向量化
    const embeddings = await createEmbeddings(chunks);
    
    // 存入Pinecone
    const vectors = chunks.map((text, i) => ({
      id: `doc-${Date.now()}-${i}`,
      values: embeddings[i],
      metadata: { text, source: req.file?.originalname || 'text' }
    }));
    
    await index.upsert(vectors);
    
    res.json({ success: true, chunks: chunks.length });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: '处理文档失败' });
  }
});

// 检索API
app.post('/api/retrieve', async (req, res) => {
  try {
    const { query, topK = 5 } = req.body;
    
    // 向量化查询
    const queryEmbedding = (await openai.embeddings.create({
      model: 'text-embedding-ada-002',
      input: query
    })).data[0].embedding;
    
    // 向量检索
    const results = await index.query({
      topK,
      vector: queryEmbedding,
      includeMetadata: true
    });
    
    const documents = results.matches.map(match => ({
      text: match.metadata.text,
      score: match.score,
      source: match.metadata.source
    }));
    
    res.json({ success: true, documents });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: '检索失败' });
  }
});

// 聊天API（流式响应）
app.post('/api/chat', async (req, res) => {
  try {
    const { messages, useRAG = true } = req.body;
    const userMessage = messages[messages.length - 1].content;
    
    let context = '';
    if (useRAG) {
      // 检索相关文档
      const queryEmbedding = (await openai.embeddings.create({
        model: 'text-embedding-ada-002',
        input: userMessage
      })).data[0].embedding;
      
      const results = await index.query({
        topK: 3,
        vector: queryEmbedding,
        includeMetadata: true
      });
      
      context = results.matches.map(match => match.metadata.text).join('\n\n');
    }
    
    // 构建提示词
    const systemPrompt = context 
      ? `基于以下上下文回答问题：\n${context}\n\n问题：`
      : '';
    
    // 流式响应
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    
    const stream = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: systemPrompt },
        ...messages
      ],
      stream: true
    });
    
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || '';
      res.write(content);
    }
    
    res.end();
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: '聊天失败' });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`RAG服务运行在 http://localhost:${PORT}`);
});
```

---

## AI集成篇

### 一、选择题

**1. 以下哪个不是LangChain的核心概念？**
A. Chain（链）
B. Agent（智能体）
C. Prompt Template（提示词模板）
D. Component（组件）

> **答案：D**  
> LangChain的核心概念包括Chain、Agent、Prompt Template、Memory、Tool等，Component是更通用的术语。

---

**2. 对于大文件的向量化，以下哪种方案最合理？**
A. 单线程同步处理
B. 多线程并发处理
C. 使用消息队列异步处理
D. 直接全部加载到内存

> **答案：C**  
> 大文件向量化是耗时操作，使用消息队列异步处理更可靠。

---

**3. 在使用多个LLM模型时，最好的实践是什么？**
A. 直接调用所有模型
B. 使用统一的接口抽象
C. 只使用一个模型
D. 写重复的调用代码

> **答案：B**  
> 使用统一接口抽象，可以轻松切换和组合多个模型。

---

### 二、简答题

**1. 请说明如何使用LangChain实现一个带工具调用的Agent。**

> **答案：**  
> **实现步骤**：
> 1. **定义工具**：创建Agent可调用的工具
> 2. **初始化LLM**：选择合适的LLM模型
> 3. **创建Agent**：使用LangChain的Agent类
> 4. **执行Agent**：接收用户输入，让Agent自主决策
> 
> **代码示例**：
```javascript
import { OpenAI } from 'openai';
import { AgentExecutor, createOpenAIFunctionsAgent } from 'langchain/agents';
import { ChatOpenAI } from '@langchain/openai';
import { SerpAPI } from '@langchain/community/tools/serpapi';
import { Calculator } from '@langchain/community/tools/calculator';
import { PromptTemplate } from '@langchain/core/prompts';

async function createAgent() {
  const tools = [new SerpAPI(), new Calculator()];
  
  const prompt = PromptTemplate.fromTemplate(`
    你是一个有帮助的AI助手，可以使用以下工具：
    {tools}
    工具名称: {tool_names}
    用户问题: {input}
    {agent_scratchpad}
  `);
  
  const llm = new ChatOpenAI({ temperature: 0 });
  const agent = await createOpenAIFunctionsAgent({
    llm,
    tools,
    prompt
  });
  
  return new AgentExecutor({ agent, tools });
}

async function runAgent(query) {
  const executor = await createAgent();
  const result = await executor.invoke({ input: query });
  return result;
}
```

---

**2. 在生产环境中使用向量数据库需要考虑哪些因素？**

> **答案：**  
> **关键因素**：
> 1. **性能**：检索延迟、吞吐量
> 2. **可扩展性**：数据量增长后的扩展能力
> 3. **成本**：存储和计算成本
> 4. **可靠性**：数据持久性、备份
> 5. **功能**：元数据过滤、混合搜索
> 6. **易用性**：API、文档、支持
> 
> **选型对比**：
> | 数据库 | 特点 | 适用场景 |
> |--------|------|----------|
> | Pinecone | 托管服务、易用、成本高 | 快速原型、小规模 |
> | Weaviate | 开源、功能丰富、自托管 | 生产环境、需要定制 |
> | pgvector | PostgreSQL扩展、结构化数据 | 已有PostgreSQL |
> | Milvus | 开源、高性能、复杂功能 | 大规模、高要求 |
> 
> **生产优化**：
> - **索引优化**：选择合适的索引算法（HNSW、IVF）
> - **分批处理**：大数据量分批插入
> - **监控告警**：监控延迟、错误率
> - **缓存策略**：热点数据缓存
> - **分库分表**：按业务维度分库

---

### 三、编程题

**1. 使用LangChain实现一个文档问答系统，集成RAG和对话记忆。**

> **参考答案：**
```javascript
// langchain-rag-chat.js
import { ChatOpenAI } from '@langchain/openai';
import { OpenAIEmbeddings } from '@langchain/openai';
import { PineconeStore } from '@langchain/pinecone';
import { Pinecone } from '@pinecone-database/pinecone';
import { ConversationalRetrievalQAChain } from 'langchain/chains';
import { BufferMemory } from 'langchain/memory';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import { TextLoader } from 'langchain/document_loaders/fs/text';

class RAGChatSystem {
  constructor() {
    this.llm = new ChatOpenAI({ temperature: 0, modelName: 'gpt-3.5-turbo' });
    this.embeddings = new OpenAIEmbeddings();
    this.pinecone = new Pinecone();
    this.memory = {};
  }

  // 初始化向量存储
  async initVectorStore(indexName = 'langchain-documents') {
    const index = this.pinecone.Index(indexName);
    this.vectorStore = await PineconeStore.fromExistingIndex(this.embeddings, {
      pineconeIndex: index
    });
  }

  // 添加文档
  async addDocuments(filePath) {
    const loader = new TextLoader(filePath);
    const documents = await loader.load();
    
    const textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200
    });
    
    const docs = await textSplitter.splitDocuments(documents);
    
    await PineconeStore.fromDocuments(docs, this.embeddings, {
      pineconeIndex: this.pinecone.Index('langchain-documents')
    });
  }

  // 获取或创建会话记忆
  getSessionMemory(sessionId) {
    if (!this.memory[sessionId]) {
      this.memory[sessionId] = new BufferMemory({
        memoryKey: 'chat_history',
        inputKey: 'question',
        outputKey: 'text',
        returnMessages: true
      });
    }
    return this.memory[sessionId];
  }

  // 创建RAG对话链
  async createRAGChain(sessionId) {
    const memory = this.getSessionMemory(sessionId);
    const retriever = this.vectorStore.asRetriever();
    
    return ConversationalRetrievalQAChain.fromLLM(
      this.llm,
      retriever,
      {
        memory,
        returnSourceDocuments: true,
        combineDocumentsChainInputKey: 'chat_history',
        questionGeneratorChainOptions: {
          llm: this.llm
        }
      }
    );
  }

  // 聊天
  async chat(sessionId, question) {
    const chain = await this.createRAGChain(sessionId);
    const response = await chain.invoke({ question });
    return {
      answer: response.text,
      sourceDocuments: response.sourceDocuments?.map(doc => ({
        text: doc.pageContent,
        source: doc.metadata.source
      }))
    };
  }
}

// 使用示例
async function demo() {
  const ragChat = new RAGChatSystem();
  await ragChat.initVectorStore();
  
  // 添加文档
  await ragChat.addDocuments('./knowledge-base.txt');
  
  // 开始对话
  const sessionId = 'user-123';
  const response1 = await ragChat.chat(sessionId, '什么是RAG？');
  console.log('回答1:', response1.answer);
  
  const response2 = await ragChat.chat(sessionId, '它有什么优点？');
  console.log('回答2:', response2.answer);
  
  console.log('来源文档:', response2.sourceDocuments);
}

demo();
```

---

## 系统架构篇

### 一、选择题

**1. 在AI应用中，处理异步任务（如文档向量化）最好使用什么？**
A. 直接处理
B. 定时任务
C. 消息队列
D. 定时轮询

> **答案：C**  
> 消息队列可以解耦、异步处理、确保任务可靠执行。

---

**2. 对于多模型支持，最好的架构设计是？**
A. 硬编码每个模型
B. 策略模式
C. 单例模式
D. 工厂模式 + 策略模式

> **答案：D**  
> 工厂模式创建模型实例，策略模式统一调用接口，适合多模型支持。

---

**3. 以下哪个不是微服务架构在AI应用中的优势？**
A. 独立扩展
B. 技术栈灵活
C. 简单易部署
D. 故障隔离

> **答案：C**  
> 微服务的优势包括独立扩展、技术栈灵活、故障隔离，但部署和运维更复杂。

---

### 二、简答题

**1. 请设计一个企业级AI应用的系统架构，包括技术选型和各模块职责。**

> **答案：**  
> **系统架构**：
> ```
> ┌─────────────────────────────────────────────────────────────────┐
> │                        前端应用层                                │
> │         React/Vue Web应用，移动端，浏览器扩展                    │
> └─────────────────────────────────────────────────────────────────┘
>                                    │
> ┌─────────────────────────────────────────────────────────────────┐
> │                        API网关层                                 │
> │         路由、鉴权、限流、监控、缓存                              │
> └─────────────────────────────────────────────────────────────────┘
>                                    │
> ┌─────────────────────────────────────────────────────────────────┐
> │                        服务层                                    │
> │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
> │  │Chat服务      │ │文档服务      │ │Agent服务      │ │模型服务    │ │
> │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
> └─────────────────────────────────────────────────────────────────┘
>                                    │
> ┌─────────────────────────────────────────────────────────────────┐
> │                        数据层                                    │
> │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
> │  │向量DB    │ │关系DB    │ │缓存      │ │对象存储   │ │消息队列    │ │
> │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────────┘ │
> └─────────────────────────────────────────────────────────────────┘
>                                    │
> ┌─────────────────────────────────────────────────────────────────┐
> │                        AI层                                      │
> │  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────────┐ │
> │  │LLM API      │ │Embedding    │ │Fine-tuned模型              │ │
> │  └─────────────┘ └─────────────┘ └───────────────────────────┘ │
> └─────────────────────────────────────────────────────────────────┘
> ```
> 
> **技术选型**：
> - **前端**：React + TypeScript + Zustand
> - **后端**：Node.js + Express 或 Python + FastAPI
> - **向量DB**：Pinecone 或 Weaviate
> - **关系DB**：PostgreSQL
> - **缓存**：Redis
> - **消息队列**：RabbitMQ 或 Kafka
> - **AI框架**：LangChain + OpenAI API

---

**2. 请说明在AI应用中如何设计可观测性系统，包括监控、日志、追踪。**

> **答案：**  
> **可观测性三支柱**：
> 1. **日志**：记录应用行为
> 2. **指标**：监控系统性能
> 3. **追踪**：追踪请求链路
> 
> **监控指标**：
> - **业务指标**：API调用量、响应延迟、用户满意度
> - **性能指标**：LLM响应时间、向量化延迟、检索QPS
> - **成本指标**：Token消耗、API调用成本
> - **资源指标**：CPU、内存、磁盘、网络
> 
> **日志规范**：
> - 结构化日志（JSON格式）
> - 包含请求ID、用户ID、时间戳
> - 分级日志（debug、info、warn、error）
> - 记录敏感信息前脱敏
> 
> **追踪方案**：
> - OpenTelemetry实现分布式追踪
> - 记录LLM调用、向量检索、数据库操作
> - 关联前端请求ID和后端TraceID
> 
> **技术选型**：
> - **日志**：Winston/Pino → Elasticsearch → Kibana
> - **指标**：Prometheus + Grafana
> - **追踪**：OpenTelemetry + Jaeger
> 
> **告警规则**：
> - LLM延迟超过阈值
> - 错误率超过阈值
> - Token消耗异常增长

---

### 三、设计题

**1. 请设计一个企业级的知识库问答系统，包括文档处理流水线、RAG检索、多模态支持。**

> **设计思路**：
```
┌─────────────────────────────────────────────────────────┐
│  用户界面层 - Web/移动端/API                             │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│  文档处理流水线                                           │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │
│  │上传  │ │解析  │ │切分  │ │向量化│ │索引  │        │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘        │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│  知识索引层 - 向量数据库 + 元数据过滤                     │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│  RAG检索层 - 混合检索、重排序、上下文压缩                │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│  LLM生成层 - 多模型支持、提示词工程、输出验证             │
└─────────────────────────────────────────────────────────┘

关键设计点：
1. 文档处理流水线：支持PDF、Word、PPT、图片、网页等
2. 多模态支持：图文问答
3. 混合检索：向量检索 + 关键词检索 + 元数据过滤
4. 重排序：使用交叉编码器提升相关性
5. 问答优化：上下文压缩、提示词优化
6. 反馈循环：用户反馈持续改进
```

---

## 性能优化篇

### 一、选择题

**1. 在向量检索中，什么索引算法适合高召回率场景？**
A. FLAT（暴力检索）
B. IVF（倒排文件）
C. HNSW（层次化小世界）
D. PQ（乘积量化）

> **答案：A**  
> FLAT是暴力检索，精度最高但速度最慢，适合小数据集或高召回率场景。

---

**2. 对于LLM提示词优化，以下哪种不是常用方法？**
A. 提示词压缩
B. 上下文剪枝
C. 增加模型参数
D. 使用更高效的模型

> **答案：C**  
> 增加模型参数是模型层面的优化，不是提示词优化方法。

---

**3. 缓存LLM响应时，什么作为缓存键最合适？**
A. 原始文本
B. 文本哈希
C. 用户ID
D. 时间戳

> **答案：B**  
> 文本哈希作为缓存键，可以高效命中相似问题。

---

### 二、简答题

**1. 请说明在RAG系统中提升检索质量和性能的方法。**

> **答案：**  
> **检索质量提升**：
> - **切分策略**：语义切分、重叠窗口、层级切分
> - **向量化优化**：选择合适的Embedding模型、微调模型
> - **混合检索**：向量检索 + BM25关键词检索
> - **重排序**：使用交叉编码器或LLM重排
> - **元数据过滤**：时间、来源、类别等过滤
> - **查询重写**：LLM优化或重写用户查询
> 
> **检索性能优化**：
> - **索引优化**：HNSW索引参数调优
> - **向量压缩**：PQ、SCANN等压缩算法
> - **缓存热点**：热点问题缓存结果
> - **批量检索**：多查询并行处理
> - **分片部署**：大数据集分片部署
> 
> **代码示例**：
```javascript
// 混合检索 + 重排序示例
async function hybridSearch(query) {
  // 1. 向量检索
  const vectorResults = await vectorStore.similaritySearch(query, 10);
  
  // 2. 关键词检索
  const keywordResults = await keywordSearch(query, 10);
  
  // 3. 合并去重
  const merged = mergeResults(vectorResults, keywordResults);
  
  // 4. 重排序
  const reranked = await rerank(query, merged);
  
  return reranked.slice(0, 5);
}
```

---

**2. 如何优化LLM API调用的成本和性能？**

> **答案：**  
> **成本优化**：
> - **模型选择**：根据任务选合适模型，不要大材小用
> - **提示词优化**：压缩不必要的内容，精简
> - **输出限制**：max_tokens、temperature等参数调优
> - **缓存策略**：相似问题缓存，减少重复调用
> - **批量处理**：批量API调用减少开销
> 
> **性能优化**：
> - **流式输出**：SSE/WebSocket即时返回
> - **异步处理**：非阻塞IO处理多个请求
> - **连接池**：复用HTTP连接
> - **边缘部署**：近用户部署降低延迟
> - **本地模型**：小模型本地部署加速简单任务
> 
> **成本监控**：
```javascript
// 记录API调用成本
const costs = {
  'gpt-4': { prompt: 0.03, completion: 0.06 },
  'gpt-3.5-turbo': { prompt: 0.001, completion: 0.002 }
};

async function trackUsage(model, promptTokens, completionTokens) {
  const cost = 
    (promptTokens / 1000) * costs[model].prompt + 
    (completionTokens / 1000) * costs[model].completion;
  
  await database.insert('usage', {
    model,
    promptTokens,
    completionTokens,
    cost,
    timestamp: Date.now()
  });
  
  return cost;
}
```

---

### 三、编程题

**1. 实现一个带缓存和智能模型选择的LLM调用服务。**

> **参考答案：**
```javascript
// smart-llm-service.js
import { createHash } from 'crypto';
import NodeCache from 'node-cache';
import { OpenAI } from 'openai';

class SmartLLMService {
  constructor() {
    this.cache = new NodeCache({ stdTTL: 3600 }); // 1小时缓存
    this.openai = new OpenAI();
    this.costs = {
      'gpt-4': { prompt: 0.03, completion: 0.06 },
      'gpt-3.5-turbo': { prompt: 0.001, completion: 0.002 }
    };
  }

  // 生成缓存键
  getCacheKey(prompt, model, temperature) {
    const data = { prompt, model, temperature };
    return createHash('md5').update(JSON.stringify(data)).digest('hex');
  }

  // 简单的模型选择逻辑
  selectModel(prompt) {
    const isSimple = prompt.length < 100 && 
                     /^(你好|谢谢|天气|时间|日期)/i.test(prompt);
    
    return isSimple ? 'gpt-3.5-turbo' : 'gpt-4';
  }

  // 计算Token数量（简化版）
  estimateTokens(text) {
    return Math.ceil(text.length / 4);
  }

  // 计算成本
  calculateCost(model, promptTokens, completionTokens) {
    const modelCost = this.costs[model] || this.costs['gpt-3.5-turbo'];
    return (promptTokens / 1000) * modelCost.prompt + 
           (completionTokens / 1000) * modelCost.completion;
  }

  // 智能LLM调用
  async generate(prompt, options = {}) {
    const { 
      model = this.selectModel(prompt), 
      temperature = 0.7,
      useCache = true 
    } = options;

    // 检查缓存
    const cacheKey = this.getCacheKey(prompt, model, temperature);
    if (useCache && this.cache.has(cacheKey)) {
      return { 
        ...this.cache.get(cacheKey), 
        cached: true 
      };
    }

    // 调用LLM
    const startTime = Date.now();
    const response = await this.openai.chat.completions.create({
      model,
      messages: [{ role: 'user', content: prompt }],
      temperature
    });
    const latency = Date.now() - startTime;

    const completion = response.choices[0].message.content;
    const promptTokens = response.usage.prompt_tokens;
    const completionTokens = response.usage.completion_tokens;
    const totalTokens = response.usage.total_tokens;
    const cost = this.calculateCost(model, promptTokens, completionTokens);

    const result = {
      completion,
      model,
      usage: { promptTokens, completionTokens, totalTokens },
      cost,
      latency,
      cached: false
    };

    // 缓存结果
    this.cache.set(cacheKey, result);

    return result;
  }

  // 获取使用统计
  getStats() {
    const keys = this.cache.keys();
    let totalCost = 0;
    let cacheHits = 0;
    let totalRequests = 0;

    keys.forEach(key => {
      const value = this.cache.get(key);
      totalCost += value.cost || 0;
      totalRequests++;
      if (value.cached) cacheHits++;
    });

    return {
      totalRequests,
      cacheHits,
      cacheHitRate: totalRequests ? (cacheHits / totalRequests).toFixed(2) : 0,
      totalCost
    };
  }
}

// 使用示例
async function demo() {
  const llmService = new SmartLLMService();

  const response1 = await llmService.generate('你好，请简单介绍自己');
  console.log('响应1:', response1);

  // 缓存命中
  const response2 = await llmService.generate('你好，请简单介绍自己');
  console.log('响应2（缓存）:', response2);

  const response3 = await llmService.generate('请详细分析RAG的工作原理');
  console.log('响应3:', response3);

  console.log('统计:', llmService.getStats());
}

demo();
```

---

## 安全性篇

### 一、选择题

**1. 以下哪个不是LLM应用的常见安全风险？**
A. Prompt注入
B. 敏感信息泄露
C. 缓冲区溢出
D. 过度授权

> **答案：C**  
> 缓冲区溢出是传统软件的安全问题，不是LLM应用特有的。

---

**2. 防止Prompt注入最好的方法是？**
A. 输入长度限制
B. 输入过滤和验证
C. 不使用提示词
D. 直接返回固定内容

> **答案：B**  
> Prompt注入通过输入验证、限制提示词结构、输出过滤等方法防御。

---

**3. 对于LLM API密钥，最佳实践是？**
A. 硬编码在代码里
B. 提交到版本控制
C. 使用环境变量和密钥管理服务
D. 分享给同事

> **答案：C**  
> API密钥应该使用环境变量或密钥管理服务（如AWS Secrets Manager、HashiCorp Vault）存储。

---

### 二、简答题

**1. 请说明LLM应用中常见的安全风险和防护措施。**

> **答案：**  
> **常见风险**：
> 1. **Prompt注入**：恶意用户构造输入让模型执行非预期行为
> 2. **敏感信息泄露**：训练数据或输出包含敏感信息
> 3. **过度授权**：Agent调用工具权限过大
> 4. **内容合规**：生成不适当、违法内容
> 5. **速率限制**：API调用超出限额
> 6. **供应链安全**：第三方库安全漏洞
> 
> **防护措施**：
> - **输入验证**：过滤、清理用户输入
> - **输出过滤**：检查和过滤模型输出
> - **权限最小化**：工具调用权限最小化
> - **内容审核**：使用内容审核API
> - **速率限制**：用户级限流
> - **审计日志**：完整记录请求和响应
> - **Prompt工程**：安全的提示词设计
> 
> **示例防护**：
```javascript
// Prompt注入检测
function detectPromptInjection(input) {
  const patterns = [
    /ignore previous instructions/i,
    /system prompt/i,
    /you are a helper/i,
    /disregard earlier instructions/i
  ];
  return patterns.some(pattern => pattern.test(input));
}

// 输出过滤
function filterOutput(output) {
  const filtered = output
    .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]')
    .replace(/(?:\d{1,3}\.){3}\d{1,3}/g, '[IP]')
    .replace(/\d{4}-\d{4}-\d{4}-\d{4}/g, '[CREDIT_CARD]');
  return filtered;
}
```

---

**2. 如何确保AI系统中的数据隐私和合规？**

> **答案：**  
> **合规要求**：
> - **GDPR**：数据可删除、可访问、知情权
> - **CCPA/CPRA**：加州用户数据权利
> - **企业隐私策略**：内部数据治理
> 
> **隐私保护措施**：
> - **数据脱敏**：姓名、邮箱、电话等敏感信息脱敏
> - **PII检测**：自动检测和移除个人可识别信息
> - **端到端加密**：数据传输和存储加密
> - **数据最小化**：只收集必要数据
> - **数据保留策略**：定时删除不需要的数据
> - **用户同意**：明确告知数据用途
> 
> **技术实现**：
```javascript
// PII检测和脱敏
import { PIIRedactor } from 'ai-pii-redactor';

const redactor = new PIIRedactor();

function anonymizeText(text) {
  return redactor.redact(text, {
    entities: ['EMAIL', 'PHONE', 'PERSON', 'ADDRESS'],
    replacement: '[REDACTED]'
  });
}

// 使用示例
const original = "我的邮箱是test@example.com，电话是13800138000";
const anonymized = anonymizeText(original);
console.log(anonymized); 
// "我的邮箱是[REDACTED]，电话是[REDACTED]"
```

---

### 三、编程题

**1. 实现一个安全的中间件，包括身份验证、速率限制、输入验证。**

> **参考答案：**
```javascript
// security-middleware.js
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import jwt from 'jsonwebtoken';
import redis from 'redis';

const client = redis.createClient();

// 身份验证中间件
export function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: '未提供身份验证令牌' });
  }
  
  const token = authHeader.slice(7);
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: '无效的身份验证令牌' });
  }
}

// 速率限制中间件
export function createRateLimiter(windowMs, max) {
  return rateLimit({
    store: new RedisStore({ client }),
    windowMs,
    max,
    message: '请求过于频繁，请稍后再试',
    keyGenerator: (req) => {
      // 使用用户ID或IP作为限流键
      return req.user?.id || req.ip;
    },
    standardHeaders: true,
    legacyHeaders: false
  });
}

// 输入验证中间件
export function validateInput(validators) {
  return (req, res, next) => {
    const errors = {};
    
    for (const [field, validator] of Object.entries(validators)) {
      const value = req.body[field];
      
      if (validator.required && !value) {
        errors[field] = `${field} 是必填项`;
        continue;
      }
      
      if (validator.type && typeof value !== validator.type) {
        errors[field] = `${field} 必须是 ${validator.type} 类型`;
        continue;
      }
      
      if (validator.pattern && !validator.pattern.test(value)) {
        errors[field] = validator.message || `${field} 格式不正确`;
        continue;
      }
      
      // 检测Prompt注入
      if (validator.promptInjectionCheck && detectPromptInjection(value)) {
        errors[field] = '检测到潜在的安全风险，请重新输入';
        continue;
      }
    }
    
    if (Object.keys(errors).length > 0) {
      return res.status(400).json({ errors });
    }
    
    next();
  };
}

// Prompt注入检测
function detectPromptInjection(input) {
  const patterns = [
    /ignore previous instructions/i,
    /disregard all prior messages/i,
    /you are now/i,
    /forget everything/i,
    /system prompt/i,
    /you must/i,
    /do not/i,
    /never/i
  ];
  
  return patterns.some(pattern => pattern.test(input));
}

// 使用示例
import express from 'express';
const app = express();
app.use(express.json());

// 用户聊天API
app.post('/api/chat', 
  authenticate, 
  createRateLimiter(15 * 60 * 1000, 100), // 15分钟100次
  validateInput({
    message: { 
      required: true, 
      type: 'string',
      promptInjectionCheck: true 
    }
  }),
  async (req, res) => {
    // 安全的聊天逻辑
    try {
      const response = await safeChatCall(req.body.message, req.user);
      res.json(response);
    } catch (error) {
      console.error('聊天错误:', error);
      res.status(500).json({ error: '处理失败' });
    }
  }
);

async function safeChatCall(message, user) {
  // 1. 记录审计日志
  await auditLog(user.id, 'chat', { messageLength: message.length });
  
  // 2. 输入脱敏
  const sanitizedMessage = sanitizeInput(message);
  
  // 3. 调用LLM（带超时）
  const response = await chatWithLLM(sanitizedMessage);
  
  // 4. 输出过滤
  const filteredResponse = filterOutput(response);
  
  // 5. 内容审核
  const moderation = await moderateContent(filteredResponse);
  if (!moderation.approved) {
    return { error: '生成内容未通过审核' };
  }
  
  return { response: filteredResponse };
}

app.listen(3000, () => console.log('安全API服务运行中'));
```

---

## 项目实战篇

### 一、选择题

**1. 在AI项目开发中，什么是最优先考虑的？**
A. 使用最新技术
B. 实现所有功能
C. 快速迭代和验证
D. 完美的架构设计

> **答案：C**  
> AI项目不确定性高，快速迭代和验证最重要，避免过早优化。

---

**2. 以下哪个不是AI项目的常见评估指标？**
A. 用户满意度
B. 回答准确率
C. 代码行数
D. 响应时间

> **答案：C**  
> 代码行数不是项目评估指标，用户满意度、准确率、响应时间都是。

---

### 二、简答题

**1. 请分享一个完整的AI项目从0到1的开发流程，包括需求分析、技术选型、开发、测试、部署。**

> **答案：**  
> **项目开发流程**：
> 
> **1. 需求分析**
> - 明确用户痛点和使用场景
> - 定义核心功能和边界
> - 确定成功指标（准确率、满意度）
> - 技术可行性验证
> 
> **2. 技术选型**
> - 前端：React/Vue
> - 后端：Node.js/Python/FastAPI
> - AI框架：LangChain
> - 向量数据库：Pinecone/Weaviate
> - LLM：OpenAI/Anthropic
> 
> **3. 开发流程**
> - 原型验证：最快实现核心功能验证可行性
> - 迭代开发：MVP → 优化 → 高级功能
> - 数据准备：文档收集、清洗、标注
> 
> **4. 测试策略**
> - 单元测试：工具函数、服务模块
> - 集成测试：完整流程测试
> - 评估测试：回答质量评估
> - A/B测试：用户侧验证
> 
> **5. 部署上线**
> - CI/CD流程搭建
> - 监控告警配置
> - 灰度发布
> - 用户反馈收集
> 
> **6. 持续迭代**
> - 分析用户反馈
> - 优化模型和提示词
> - 新增功能
> 
> **代码示例**：
```javascript
// A/B测试示例
function assignABTestGroup(userId) {
  const hash = require('crypto