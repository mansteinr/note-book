"""
CrewAI 示例:研究 + 写作协作团队(DeepSeek + Bocha 国产组合版)
任务:针对某个技术话题,先调研、再撰写一篇简报

技术栈:
    - LLM:     DeepSeek API (deepseek-reasoner + deepseek-chat)
    - 搜索:    Bocha Web Search API
    - 框架:    CrewAI

依赖安装:
    pip install crewai requests

环境变量:
    export DEEPSEEK_API_KEY="sk-..."      # 从 platform.deepseek.com 申请
    export BOCHA_API_KEY="sk-..."         # 从 open.bochaai.com 申请
"""

import os
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool


# ============ 1. 自定义 Bocha 搜索工具 ============
# CrewAI 没有原生的 Bocha 工具,自己包一个 —— 30 行代码而已

class BochaSearchInput(BaseModel):
    """Bocha 搜索工具的输入参数"""
    query: str = Field(..., description="搜索关键词,使用自然语言")


class BochaSearchTool(BaseTool):
    # 注意:name 必须是 ASCII(字母、数字、下划线、连字符),
    # 否则 CrewAI 在转换 OpenAI function calling schema 时会过滤掉中文,
    # 导致 "function name cannot be empty" 错误。
    # 中文描述放在 description 字段里即可,LLM 完全能理解。
    name: str = "web_search"
    description: str = (
        "搜索互联网获取最新信息和资料。"
        "输入一个搜索关键词,返回搜索结果列表(标题、链接、摘要)。"
        "适合搜索技术资料、新闻、文档等任何公开信息。中文搜索效果优秀。"
    )
    args_schema: Type[BaseModel] = BochaSearchInput

    def _run(self, query: str) -> str:
        try:
            resp = requests.post(
                "https://api.bochaai.com/v1/web-search",
                headers={
                    "Authorization": f"Bearer {os.getenv('BOCHA_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "count": 10,           # 返回前 10 条结果
                    "summary": True,       # 让 Bocha 返回每条结果的摘要
                    "freshness": "noLimit" # 不限时间;可选 "oneDay"/"oneWeek"/"oneMonth"/"oneYear"
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            # 解析返回结构:data.webPages.value 是结果列表
            pages = data.get("data", {}).get("webPages", {}).get("value", [])
            if not pages:
                return "搜索没有返回任何结果,请尝试换个关键词。"

            # 拼成 LLM 易读的 Markdown 格式
            lines = []
            for i, p in enumerate(pages, 1):
                title = p.get("name", "")
                url = p.get("url", "")
                snippet = p.get("snippet", "") or p.get("summary", "")
                site = p.get("siteName", "")
                lines.append(
                    f"【{i}】{title}\n"
                    f"   来源:{site}\n"
                    f"   链接:{url}\n"
                    f"   摘要:{snippet}\n"
                )
            return "\n".join(lines)

        except requests.exceptions.RequestException as e:
            return f"搜索请求失败:{e}。请检查 BOCHA_API_KEY 和网络连接。"
        except Exception as e:
            return f"搜索结果解析失败:{e}"


# ============ 2. 配置 DeepSeek LLM ============
deepseek_reasoner = LLM(
    model="deepseek/deepseek-reasoner",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3,
    max_tokens=4000,
)

deepseek_chat = LLM(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.7,
    max_tokens=4000,
)


# ============ 3. 实例化工具 ============
search_tool = BochaSearchTool()


# ============ 4. 定义 Agent ============

researcher = Agent(
    role="资深技术研究员",
    goal="搜集关于 {topic} 的最新、最权威的技术资料,并提炼关键信息",
    backstory=(
        "你是一名拥有十年经验的技术研究员,擅长快速定位高质量信息源,"
        "能够从大量噪声中筛选出真正有价值的内容。你做事严谨,引用必有出处。"
        "你优先使用中文搜索,关注国内技术社区(知乎、CSDN、掘金、InfoQ 等)的高质量内容。"
    ),
    llm=deepseek_reasoner,
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
    max_iter=8,
)

writer = Agent(
    role="技术内容撰稿人",
    goal="基于研究员提供的资料,撰写一篇结构清晰、易读的技术简报",
    backstory=(
        "你是一名技术博客作者,擅长把复杂概念讲得通俗易懂。"
        "你的文章注重逻辑结构,语言简洁,从不堆砌术语。"
        "你写作的目标读者是中文技术圈的工程师。"
    ),
    llm=deepseek_chat,
    tools=[],
    verbose=True,
    allow_delegation=False,
    max_iter=5,
)


# ============ 5. 定义 Task ============

research_task = Task(
    description=(
        "针对话题「{topic}」进行深入调研,要求:\n"
        "1. 找到至少 5 个权威信息来源(官方文档、知名博客、论文、技术社区文章等)\n"
        "2. 总结当前的技术现状、主流方案、关键挑战\n"
        "3. 列出每个信息源的链接和核心观点\n"
        "4. 优先选择中文资料,但不排斥高质量英文来源"
    ),
    expected_output=(
        "一份结构化的调研笔记,包含:\n"
        "- 话题背景概述(约 200 字)\n"
        "- 5 个以上信息源 + 核心观点摘要\n"
        "- 3 个值得深入展开的子话题"
    ),
    agent=researcher,
)

writing_task = Task(
    description=(
        "基于研究员的调研笔记,撰写一篇面向中文技术读者的简报。\n"
        "要求:\n"
        "1. 800-1200 字\n"
        "2. 包含引言、核心内容、总结三部分\n"
        "3. 在引用观点时注明来源\n"
        "4. 避免堆砌术语,确保非专家也能读懂"
    ),
    expected_output="一篇 Markdown 格式的中文技术简报",
    agent=writer,
    context=[research_task],
    output_file="briefing.md",
)


# ============ 6. 组建 Crew ============
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True,
)


# ============ 7. 启动 ============
if __name__ == "__main__":
    # 前置检查
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY,从 platform.deepseek.com 申请")
    if not os.getenv("BOCHA_API_KEY"):
        raise RuntimeError("请先设置 BOCHA_API_KEY,从 open.bochaai.com 申请")

    result = crew.kickoff(
        inputs={"topic": "Multi-Agent 系统在 2026 年的工程实践"}
    )
    print("\n========== 最终产出 ==========\n")
    print(result)
