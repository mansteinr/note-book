# Agent 工程师学习计划

## 学习目标
- 掌握 AI Agent 的核心概念和设计模式
- 能够独立开发和部署可落地的智能 Agent 系统
- 了解 Agent 在不同行业的应用案例

---

## 第一阶段：基础入门（1-2个月）

### 核心知识点
| 知识点 | 内容概述 |
|--------|----------|
| Agent 基础 | 什么是 AI Agent、Agent 的历史演进、Agent 的核心组件（感知、决策、执行） |
| AI/ML 基础 | 基础 ML 算法、深度学习基础、LLM 原理入门 |
| 编程基础 | Python 进阶、异步编程、API 开发 |
| 工具链入门 | Git、Docker、Linux 基础、Prompt 工程 |

### 学习资源
#### 文档/教程
1. **Agent 基础概念**
   - [OpenAI GPT 官方文档](https://platform.openai.com/docs/introduction/overview)
   - [《AI Agent 实战指南》](https://github.com/e2b-dev/awesome-ai-agents)
   - [LangChain 官方文档](https://python.langchain.com/v0.2/docs/introduction/)
2. **LLM 入门**
   - [斯坦福 CS224W 课程](https://web.stanford.edu/class/cs224w/)
   - [Hugging Face 入门教程](https://huggingface.co/docs/transformers/quicktour)
3. **编程工具**
   - [Python 官方教程](https://docs.python.org/3/tutorial/)
   - [Docker 入门到实践](https://yeasy.gitbook.io/docker_practice/)

#### 视频课程
1. [Coursera 机器学习专项课程](https://www.coursera.org/specializations/machine-learning-introduction)
2. [CS224W 图机器学习（YouTube）](https://www.youtube.com/playlist?list=PLoROMvodv4rPLKxIpqhjhPgdQy7imNkDn)
3. [LangChain 中文教程（Bilibili）](https://www.bilibili.com/video/BV1m5411H76Y/)

---

## 第二阶段：进阶开发（2-4个月）

### 核心知识点
| 知识点 | 内容概述 |
|--------|----------|
| Agent 框架 | LangChain、AutoGPT、CrewAI、AutoGen |
| 工具调用 | Function Calling、Tool Use、结构化输出 |
| 多Agent 协作 | 多Agent 架构、角色分工、通信机制 |
| Prompt 工程进阶 | 思维链（CoT）、反思、自动提示优化 |
| 数据与记忆 | Vector DB（Pinecone、Chroma、FAISS）、记忆管理策略 |

### 学习资源
#### 文档/教程
1. **框架官方文档**
   - [LangChain 完整文档](https://python.langchain.com/v0.2/docs/concepts/)
   - [AutoGen 官方教程](https://microsoft.github.io/autogen/)
   - [CrewAI 文档](https://docs.crewai.com/)
2. **工具与记忆**
   - [Pinecone 官方教程](https://www.pinecone.io/docs/quickstart/)
   - [Chroma DB 文档](https://docs.trychroma.com/)
3. **优秀开源项目**
   - [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
   - [BabyAGI](https://github.com/yoheinakajima/babyagi)
   - [ReAct Agent](https://github.com/ysymyth/ReAct)

#### 视频课程
1. [LangChain 深入实战（Bilibili）](https://www.bilibili.com/video/BV1q642137sS/)
2. [多Agent 系统实战（YouTube）](https://www.youtube.com/playlist?list=PLh3y3z067b926r03940m60v5f11n)
3. [OpenAI Function Calling 教程（Bilibili）](https://www.bilibili.com/video/BV16a411s7aC/)

---

## 第三阶段：高级与优化（2-3个月）

### 核心知识点
| 知识点 | 内容概述 |
|--------|----------|
| 性能优化 | Prompt 优化、降低 Token 消耗、调用延迟优化 |
| 安全与评估 | 安全防护、对抗测试、Agent 评估指标 |
| 工程化落地 | 部署架构、监控、日志、DevOps |
| 前沿方向 | 自主代理、多模态 Agent、终身学习 |

### 学习资源
#### 文档/论文
1. **核心论文**
   - [ReAct](https://arxiv.org/abs/2210.03629)
   - [Self-Refine](https://arxiv.org/abs/2303.17651)
   - [Tree-of-Thoughts](https://arxiv.org/abs/2305.10601)
2. **工程化**
   - [LangChain 生产环境部署指南](https://python.langchain.com/v0.2/docs/guides/deploying/)
   - [OpenAI Evals 评估框架](https://github.com/openai/evals)
3. **前沿研究**
   - [arXiv: CS.AI 最新论文](https://arxiv.org/list/cs.AI/recent)
   - [Agents 研究进展（OpenAI Blog）](https://openai.com/blog/agents)

#### 视频/讲座
1. [LLM 安全与对齐（Stanford CS221/CS229 补充）](https://www.youtube.com/playlist?list=PLoROMvodv4r)
2. [多模态 Agent 实战（Bilibili）](https://www.bilibili.com/video/BV1V4y21j7aK/)

---

## 项目实践列表
### 入门项目
1. **简易问答 Agent**：基于 LangChain 构建一个可以回答固定领域问题的 Agent
2. **知识库 Agent**：使用向量数据库构建一个基于自己文档库的 RAG 问答 Agent
3. **工具调用 Agent**：调用天气、搜索等外部 API 的助手 Agent

### 进阶项目
1. **多角色协作 Agent**：使用 CrewAI 或 AutoGen 构建团队协作完成任务
2. **代码生成 Agent**：能够辅助写代码、调试、解释代码的 Agent
3. **数据可视化 Agent**：根据自然语言生成图表和数据分析报告

### 高级项目
1. **行业解决方案**：如法律合同审查、医疗辅助、教育辅导 Agent
2. **自主评估系统**：自动评估 Agent 表现并优化 Prompt 的系统
3. **多模态 Agent**：结合视觉、音频的多模态智能助手

---

## 社区与平台推荐
| 类型 | 推荐平台 |
|------|----------|
| 资讯 | Hugging Face Blogs、OpenAI Blog、Machine Learning Street Talk |
| 代码平台 | GitHub（关注 awesome-ai-agents 等仓库） |
| 讨论社区 | Reddit: r/LocalLLaMA、Discord: LangChain 官方服务器 |
| 竞赛平台 | Kaggle（关注 LLM 相关竞赛） |

---

## 学习建议
1. **每周安排**：基础知识（3小时） + 项目实践（4小时） + 前沿资讯（1小时）
2. **学习路径**：框架 → 工具 → 简单项目 → 进阶项目 → 论文/研究
3. **保持实践**：边学边做，每学完一个模块就完成一个小项目
4. **关注社区**：加入相关技术群，参与讨论，了解最新动态
