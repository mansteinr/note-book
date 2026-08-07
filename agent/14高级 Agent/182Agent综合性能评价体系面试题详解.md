# Agent 综合性能评价体系面试题详解

> **文档目标**：系统、全面地回答"如何评价一个 Agent 是否优秀"这一核心架构问题，从任务完成能力、自主决策水平、资源利用效率、学习与适应能力、交互友好度、错误处理机制、安全可靠性七大维度构建评价体系。以高级架构面试题的形式呈现，每道题包含考点分析、分层回答要点、量化指标体系、可操作的测试方案与代码级实现模板。
> **适用对象**：高级 AI 工程师、Agent 架构师、技术面试官、技术评审委员会成员。
> **关联前置**：与 `13项目经验/156号`（业务视角的评价指标）互补，本面试题更偏向**架构级设计与工程化落地能力**考察。

---

## 目录

- [Agent 综合性能评价体系面试题详解](#agent-综合性能评价体系面试题详解)
  - [目录](#目录)
  - [1. 整体框架题：评价体系的顶层设计](#1-整体框架题评价体系的顶层设计)
    - [1.1 题目](#11-题目)
    - [1.2 考点分析](#12-考点分析)
    - [1.3 回答要点（分层评分）](#13-回答要点分层评分)
    - [1.4 追问一：量化指标如何确定"达标阈值"？](#14-追问一量化指标如何确定达标阈值)
    - [1.5 追问二：如何避免评价指标被"刷分"？](#15-追问二如何避免评价指标被刷分)
  - [2. 任务完成能力评价（Functional Capability）](#2-任务完成能力评价functional-capability)
    - [2.1 题目](#21-题目)
    - [2.2 考点分析](#22-考点分析)
    - [2.3 指标体系设计](#23-指标体系设计)
    - [2.4 测试方案：E2E 测试集与分级评分卡](#24-测试方案e2e-测试集与分级评分卡)
    - [2.5 代码实现：任务结果评判器（TaskJudge）](#25-代码实现任务结果评判器taskjudge)
  - [3. 自主决策水平评价（Autonomous Decision-Making）](#3-自主决策水平评价autonomous-decision-making)
    - [3.1 题目](#31-题目)
    - [3.2 考点分析](#32-考点分析)
    - [3.3 指标体系设计](#33-指标体系设计)
    - [3.4 测试方案：决策树场景库 + 反事实推理验证](#34-测试方案决策树场景库--反事实推理验证)
    - [3.5 代码实现：决策路径评估器（DecisionPathEvaluator）](#35-代码实现决策路径评估器decisionpathevaluator)
  - [4. 资源利用效率评价（Resource Efficiency）](#4-资源利用效率评价resource-efficiency)
    - [4.1 题目](#41-题目)
    - [4.2 考点分析](#42-考点分析)
    - [4.3 指标体系设计](#43-指标体系设计)
    - [4.4 测试方案：资源 Profiling + Pareto 最优前沿分析](#44-测试方案资源-profiling--pareto-最优前沿分析)
  - [5. 学习与适应能力评价（Learning & Adaptability）](#5-学习与适应能力评价learning--adaptability)
    - [5.1 题目](#51-题目)
    - [5.2 考点分析](#52-考点分析)
    - [5.3 指标体系设计](#53-指标体系设计)
    - [5.4 测试方案：分布外泛化 + 学习曲线 + 失败策略调整率](#54-测试方案分布外泛化--学习曲线--失败策略调整率)
  - [6. 交互友好度评价（User Interaction Quality）](#6-交互友好度评价user-interaction-quality)
    - [6.1 题目](#61-题目)
    - [6.2 考点分析](#62-考点分析)
    - [6.3 指标体系设计](#63-指标体系设计)
    - [6.4 测试方案：行为埋点 + 交互模式库 + 专家评审](#64-测试方案行为埋点--交互模式库--专家评审)
  - [7. 错误处理机制评价（Error Handling & Resilience）](#7-错误处理机制评价error-handling--resilience)
    - [7.1 题目](#71-题目)
    - [7.2 考点分析](#72-考点分析)
    - [7.3 指标体系设计](#73-指标体系设计)
    - [7.4 测试方案：故障注入（Chaos Engineering for Agents）](#74-测试方案故障注入chaos-engineering-for-agents)
    - [7.5 代码实现：故障注入测试框架（AgentChaosKit）](#75-代码实现故障注入测试框架agentchaoskit)
  - [8. 综合评分与可视化：如何给出"该 Agent 是否优秀"的最终结论](#8-综合评分与可视化如何给出该-agent-是否优秀的最终结论)
    - [8.1 面试题汇总场景](#81-面试题汇总场景)
    - [8.2 加权聚合公式 + 等级判定 + 一票否决红线](#82-加权聚合公式--等级判定--一票否决红线)
    - [8.3 评价报告模板（含七维雷达图 + 失分归因 + 改进建议）](#83-评价报告模板含七维雷达图--失分归因--改进建议)
  - [9. 面试官视角：不同职级候选人的回答分层](#9-面试官视角不同职级候选人的回答分层)
  - [10. 总结与工程化落地清单](#10-总结与工程化落地清单)

---

## 1. 整体框架题：评价体系的顶层设计

### 1.1 题目

**请你设计一个可以系统、全面评估任意 Agent 是否"优秀"的评价框架。要求：明确列出所有核心评价维度；说明每个维度下的关键指标、量化标准、权重设置逻辑；并给出从"跑基准测试"到"输出最终等级结论"的完整流程。**

### 1.2 考点分析

| 考察点 | 期望发现的能力 |
|-------|:--------------:|
| 体系化思考 | 能否从碎片指标上升到结构化框架，而非零散列举 |
| 权衡意识 | 是否理解各维度的此消彼长（效果 vs 成本 vs 速度） |
| 可操作性 | 设计的指标能否真的测出来？还是停留在口号层面 |
| 工程落地 | 有没有考虑流程、工具、自动化，而非只给一个打分表 |

### 1.3 回答要点（分层评分）

#### P6（资深工程师）水平回答

> 我会从 **任务完成、性能、用户体验、安全、成本** 五个维度看。每个维度选 2-3 个关键指标，比如任务完成率、P90 延迟、CSAT、事故率、单任务成本。最后做一个加权平均，过 80 分就算优秀。

**面试官评语**：有基本维度概念，但指标定义模糊、权重无逻辑、无测试流程，是「拍脑袋」式方案。5/10 分，不通过。

---

#### P7（专家工程师）水平回答

> 我构建一个 **七维评价体系**，每个维度下设 3-5 个核心指标，指标均配**计算公式、阈值、采集方法**。然后用 **自动化基准 + 线上灰度 + 专家评审** 三阶段评估，最终加权聚合，并设安全红线一票否决。

**七个维度与权重**：

```
D1 任务完成能力    25%  ✅ 及格线：功能都做不对，其余无意义
D2 自主决策水平    15%  ✨ Agent 区别于传统 RPA 的核心
D3 资源利用效率    15%  💰 防止"用大锤砸钉子"
D4 学习与适应能力  10%  🧠 Agent 是否"会变聪明"
D5 交互友好度      10%  👤 用户是否真的愿意用
D6 错误处理韧性    15%  🛡️ 生产环境的最后一道防线
D7 安全合规可靠    10%  🔒 红线项一票否决
```

**评估三阶段**：

| 阶段 | 方法 | 作用 | 占最终得分 |
|-----|------|:----:|:----------:|
| Phase 1 | 离线基准测试（Benchmark Suite） | 功能正确性、基本性能 | 50% |
| Phase 2 | 线上灰度 A/B | 真实用户体验、ROI、学习能力 | 40% |
| Phase 3 | 专家人工评审 | 策略合理性、解释充分性、安全细节 | 10% |

**总分判定**：
* S ≥ 90 卓越；A 80-89 优秀；B 70-79 良好；C 60-69 合格；D 50-59 待改进；F < 50 不合格
* 红线：D7 任一子项未过 → 直接 F，无论总分

**面试官评语**：体系完整、有权重、有流程、有红线，有可操作的 7 维 × 3 阶段架构。8/10 分，通过，但追问看深度。

---

#### P8 / 架构师 水平回答（满分版本）

在 P7 的回答之上，进一步补充 **四个关键设计原则** 和 **指标反刷分机制**：

**设计原则**：
1.  **Goal-Driven 目标导向**：每一项指标必须可追溯到"用户价值"或"业务目标"，不为可测而测。
2.  **分层而非并行**：D1 不通过不看 D2-D7，D7 不通过直接 F。这是"及格-良好-卓越"的门控，不是简单加权平均。
3.  **基准+相对双评分**：除了绝对分数，还要给出与上一版本、同行业基线的相对对比（版本回归 + 行业定位）。
4.  **失败归因而非仅给分**：评分不是终点，失分归因树（Root Cause Taxonomy）+ 改进建议，才是推动迭代的核心。

**架构图**：

```
┌────────────────────────────────────────────────────────────────────┐
│                   Agent Evaluation Framework                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Gate 1: D1 任务完成 < 60分  ──►  直接终止，功能不及格               │
│            │                                                       │
│            ▼                                                       │
│  Gate 2: D7 安全红线未过  ──►  直接 F，禁止任何上线               │
│            │                                                       │
│            ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 加权聚合 (D1~D7 × w_i) → 绝对分数 + 相对基线偏差          │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                           │
│                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 失分归因诊断 (Taxonomy-based RCA) → Top-3 改进建议        │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                           │
│                         ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 最终产出: 七维雷达 + 等级 + 对比 + 改进清单 (PDF/HTML)     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**面试官评语**：既有体系，又有工程级的门控设计、归因设计、基线对比设计。10/10 分，架构师水平。

### 1.4 追问一：量化指标如何确定"达标阈值"？

**优秀回答（考察"数据驱动而非拍脑袋"）**：

> 不能拍脑袋定阈值，要用 **三校准法**：
>
> 1.  **人类基线校准**：请 5 名熟练人类专家完成同一测试集，得分分布的 P50 是「合格线」，P90 是「卓越线」。Agent 的 B 级应该至少达到人类 P50。
> 2.  **历史版本校准**：项目上一个稳定版本的得分作为「基线 0 分位」。新版本必须 ≥ +5pt 才值得上线。
> 3.  **业务痛点校准**：把用户投诉最多的 Top 3 问题对应到具体指标，比如"超时多"→ P90 ≤ 15s 作为 B 级硬性门槛，否则客户必投诉。
>
> 阈值每季度复盘一次。**最坏的情况**是：阈值定得太高，团队永远达不到就躺平；或者定得太低，上线即事故。

### 1.5 追问二：如何避免评价指标被"刷分"？

**优秀回答（考察"反设计"能力）**：

> 任何单指标都可以被刷。必须有 **三重防御**：
>
> 1.  **组合指标替代单一指标**：例如不能只看「任务成功率」，要同时看「成功率 / 单任务成本 / P90 延迟」三元组合。高成功 + 高成本 = 刷分（每步都调最聪明的大模型）。
> 2.  **对抗样本集保底**：15% 的测试用例是「对刷分不友好」的：刷简单任务的分在这些用例上不涨分甚至扣分。例如：越依赖缓存的 Agent，在分布外用例上越差。
> 3.  **反事实审计**：抽 5% 高分任务做人工反事实分析——"这个高分是真的因为 Agent 做得好？还是题目太简单？"高置信度的评分必须能通过人工抽样审计。

---

## 2. 任务完成能力评价（Functional Capability）

### 2.1 题目

**请具体定义 Agent 的"任务完成能力"要测量哪些点？给出可量化的指标、以及一套能自动化运行的测试方案。**

### 2.2 考点分析

考察点：
*   能否区分「端到端完成率」和「步骤级正确率」的不同意义？
*   能否处理「任务成功了但质量差」的灰色地带？（分级评分 vs 二元评分）
*   测试用例怎么设计？（覆盖度、难度分层、分布外）

### 2.3 指标体系设计

| 指标 ID | 指标名称 | 定义 | 计算公式 | 等级阈值 | 采集源 |
|:-------|:--------|:-----|:--------|:---------|:------:|
| F1 | **端到端任务成功率** | Agent 完整完成任务的比例 | 5级评分加权（4+5分）/ N | S≥90 / A≥80 / B≥70 | 基准测试集 |
| F2 | **步骤级准确率** | 单个动作的正确执行率 | 正确步骤 / 总步骤 × 100% | S≥97 / A≥92 / B≥85 | Execution Trace |
| F3 | **工具调用准确率** | 工具选择+参数的正确率 | 惩罚加权公式（见下方） | S≥98 / A≥94 / B≥88 | Tool Log |
| F4 | **输出质量分** | 最终结果的质量评分 | 专家/规则评分卡 10 分制 | S≥9 / A≥7.5 / B≥6 | Judge Module |
| F5 | **功能需求覆盖率** | 已支持的需求点 / 总需求点 | 需求映射矩阵统计 | S≥95 / A≥85 / B≥70 | 需求文档 |
| F6 | **幻觉/事实错误率** | 回复中含捏造/矛盾的比例 | 人工+自动化检测 | S≤2% / A≤5% / B≤8% | FactChecker |

**F3 工具调用准确率（加权惩罚公式）**：
不同错误的"危害度"不同，不能一刀切。

$$
F3 = 100 - \frac{\sum_{i=1}^{M} w_{err,i} \times \mathbb{I}(\text{错误类型}_i)}{M} \times 100
$$

权重表：

| 错误类型 | 权重 w | 说明 |
|---------|:------:|------|
| 工具选错（如用搜索代替写文件） | 0.5 | 根本性错误，浪费时间 |
| 参数语义错误（把 city_id 传成 city_name） | 0.4 | API 不会报错但结果错，最危险 |
| 参数格式错误（缺字段/类型错） | 0.25 | 易检测易修复，危害中等 |
| 不必要调用（已有信息还去查库） | 0.1 | 浪费 Token 但不影响结果 |

### 2.4 测试方案：E2E 测试集与分级评分卡

```
E2E 测试集构建三原则：
┌────────────────────────────────────────────────────────────────┐
│  1. 难度分层分布（50% Easy / 35% Medium / 15% Hard）           │
│     防止 Agent 只会做简单题。S 级必须 Hard ≥70%                │
├────────────────────────────────────────────────────────────────┤
│  2. 分布外(OOD)用例 ≥15%                                       │
│     开发时没见过的场景，测的是"泛化能力"而非"死记用例"         │
├────────────────────────────────────────────────────────────────┤
│  3. 每道题附「5级评分标准」，避免二元判断                     │
│     5=完美无需改，4=微瑕，3=可用但有缺失，2=部分完成，1=失败 │
└────────────────────────────────────────────────────────────────┘
```

每道题的评分标准示例：

```yaml
# 题: "为当前 Git 仓库生成 CONTRIBUTING.md"
test_case_id: CODE_0042
difficulty: Medium
scoring_criteria:
  - score: 5
    description: 包含约定式提交、PR 模板、代码风格、本地开发环境四部分，且全部匹配仓库当前规范
  - score: 4
    description: 包含全部四部分，但某部分细节与实际规范有≤2处出入
  - score: 3
    description: 只包含 3/4 部分，或缺失关键细节但可编辑修正
  - score: 2
    description: 只包含 1-2 部分，或包含与规范严重矛盾的信息
  - score: 1
    description: 未创建文件 / 内容为模板套话 / 与仓库无关
  - score: 0
    description: 创建失败 / 覆盖现有文件 / 死循环
```

### 2.5 代码实现：任务结果评判器（TaskJudge）

```python
"""
TaskJudge.py - 任务完成能力自动化评判器
结合：规则校验 + LLM-as-Judge + 向量相似度校验
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import re


@dataclass
class JudgeResult:
    score_0_5: float       # 0-5 分
    correctness: bool      # 是否 ≥3 分（判定成功）
    reasons: List[str]     # 扣分/加分理由
    confidence: float      # 评判置信度


class TaskJudge:
    """三层级任务评判器"""
    
    def __init__(self, llm_judge_model=None):
        self.llm = llm_judge_model
        self.rule_engines: Dict[str, Callable] = {}
        self._register_builtin_rules()
    
    # ============================================================
    # Layer 1: 规则引擎（快速、确定性、低成本）
    # ============================================================
    def _register_builtin_rules(self):
        self.rule_engines["file_exists_check"] = self._rule_file_exists
        self.rule_engines["regex_match"] = self._rule_regex_match
        self.rule_engines["schema_validation"] = self._rule_schema_valid
    
    def _rule_file_exists(self, output, expected) -> JudgeResult:
        import os
        if os.path.exists(expected["path"]):
            return JudgeResult(5, True, ["✅ 目标文件已创建"], 1.0)
        return JudgeResult(1, False, ["❌ 目标文件不存在"], 1.0)
    
    def _rule_regex_match(self, output, expected) -> JudgeResult:
        matches = re.findall(expected["pattern"], str(output))
        if len(matches) >= expected.get("min_count", 1):
            return JudgeResult(5, True, [f"✅ 匹配到 {len(matches)} 处模式"], 1.0)
        return JudgeResult(2, False, [f"❌ 只匹配到 {len(matches)} 处"], 1.0)
    
    def _rule_schema_valid(self, output, expected) -> JudgeResult:
        import jsonschema
        try:
            jsonschema.validate(instance=output, schema=expected["schema"])
            return JudgeResult(5, True, ["✅ JSON Schema 校验通过"], 0.98)
        except jsonschema.ValidationError as e:
            return JudgeResult(
                2, False,
                [f"❌ Schema 校验失败: {e.message[:100]}"],
                0.99
            )
    
    # ============================================================
    # Layer 2: LLM-as-Judge（语义级、质量级、非结构化输出）
    # ============================================================
    def _llm_judge(self, task_input: str, agent_output: str, 
                   rubric_5pt: str) -> JudgeResult:
        prompt = f"""你是一名严格的 Agent 任务评判专家。
请根据以下任务输入、Agent 输出、评分标准，给出 0-5 的整数分。

任务输入:
\"\"\"{task_input}\"\"\"

Agent 输出:
\"\"\"{agent_output[:4000]}\"\"\"

5 级评分标准:
{rubric_5pt}

请严格按 JSON 格式返回:
{{
  "score_0_5": <整数 0-5>,
  "reasons": ["理由1", "理由2", "理由3"],
  "confidence": <0-1 的浮点数>
}}"""
        
        response = self.llm.generate(prompt, response_format="json")
        data = self._parse_judge_json(response)
        
        # 防"乱打分"：置信度 <0.6 降级给人工
        if data.get("confidence", 0) < 0.6:
            return JudgeResult(
                score_0_5=data.get("score_0_5", 3),
                correctness=data.get("score_0_5", 0) >= 3,
                reasons=data.get("reasons", []) + ["⚠️ LLM 评判置信度低，建议人工复核"],
                confidence=data.get("confidence", 0)
            )
        
        return JudgeResult(
            score_0_5=data["score_0_5"],
            correctness=data["score_0_5"] >= 3,
            reasons=data["reasons"],
            confidence=data["confidence"]
        )
    
    # ============================================================
    # Layer 3: 向量相似度（答案 Retrieval / 事实校验类）
    # ============================================================
    def _embedding_similarity(self, agent_output, reference_answer, 
                              vectorizer) -> JudgeResult:
        sim = vectorizer.cosine_similarity(agent_output, reference_answer)
        score = max(0, min(5, sim * 5))
        return JudgeResult(
            score_0_5=score,
            correctness=sim >= 0.6,
            reasons=[f"与参考答案相似度 sim={sim:.3f}"],
            confidence=0.8 * sim + 0.2
        )
    
    # ============================================================
    # 总入口：根据 JudgeConfig 选择 / 组合评判方式
    # ============================================================
    def evaluate(self, task_case: Dict, agent_output: Any, 
                 execution_trace=None) -> JudgeResult:
        """
        task_case = {
            "judge_mode": "rules+llm",  # rules / llm / similarity / hybrid
            "rule_checks": [...],
            "rubric": "...",
            "reference": "...",
        }
        """
        mode = task_case.get("judge_mode", "rules")
        
        results = []
        
        # Layer 1
        for rule_cfg in task_case.get("rule_checks", []):
            rule_fn = self.rule_engines[rule_cfg["type"]]
            results.append(rule_fn(agent_output, rule_cfg))
        
        # Layer 2 / 3
        if mode in ("llm", "rules+llm") and self.llm:
            results.append(self._llm_judge(
                task_case["input"], agent_output, task_case["rubric"]
            ))
        if mode in ("similarity", "hybrid") and "reference" in task_case:
            results.append(self._embedding_similarity(
                agent_output, task_case["reference"], task_case["vectorizer"]
            ))
        
        if not results:
            return JudgeResult(3, True, ["⚠️ 无匹配评判器，默认中性分"], 0.5)
        
        # 加权合并：规则 50%，其余按置信度加权
        w_sum = 0
        s_sum = 0
        for r in results:
            w = 0.5 if r in [x for x in results if x.confidence >= 0.98] else r.confidence
            w_sum += w
            s_sum += r.score_0_5 * w
        
        final_score = s_sum / w_sum if w_sum else 3.0
        return JudgeResult(
            score_0_5=round(final_score, 2),
            correctness=final_score >= 3,
            reasons=[f"{r.score_0_5:.0f}/5: {';'.join(r.reasons)}" for r in results],
            confidence=min(1.0, w_sum / len(results))
        )
```

---

## 3. 自主决策水平评价（Autonomous Decision-Making）

### 3.1 题目

**Agent 的核心是"自主决策"。请问你如何量化一个 Agent 的决策水平？它和「只会按脚本走的 RPA」有什么区别？设计测试方案能把两者区分出来。**

### 3.2 考点分析

*   面试者是否真的理解 Agent 和 RPA 的差异？（模糊回答扣大分）
*   能否定义「决策质量」的多维含义？（正确性/必要性/最优性/效率）
*   能否设计「非脚本化」的测试场景？（脚本在新环境下必然露馅）

### 3.3 指标体系设计

| ID | 指标 | 定义 | S/A/B 阈值 | 核心意义 |
|:--|:-----|:-----|:-----------|:--------:|
| Dec1 | **决策必要率** | 有必要的决策占比，不做多余动作 | S≥95 / A≥88 / B≥75 | 区分 RPA（无脑执行）和 Agent（知进退） |
| Dec2 | **决策正确性** | 选择的动作是当前最优或等价最优的比例 | S≥92 / A≥82 / B≥70 | 决策质量 |
| Dec3 | **计划遵循率/偏离合理性** | 遵循预计划 或 偏离时给出合理理由的比例 | S≥90 / A≥80 / B≥70 | 稳定性 vs 灵活性的平衡 |
| Dec4 | **未知场景探索成功率** | 在 OOD 场景（未见过的任务/环境）下的决策成功率 | S≥70 / A≥55 / B≥40 | 泛化决策能力（与 RPA 本质差异） |
| Dec5 | **决策效率比** | 实际决策步数 ÷ 理论最优步数 | S≤1.2× / A≤1.5× / B≤2.0× | 少走弯路，决策经济性 |

### 3.4 测试方案：决策树场景库 + 反事实推理验证

**核心思路**：构建「有分支的决策树」场景库，每个节点都有 3-5 个可选动作，其中 1 个最优、1-2 个可接受、1-2 个错误。记录 Agent 在每个节点的选择。

```
示例场景: 代码库 Agent 需要 "修复单元测试失败"
                ┌───────────┐
                │ 测试失败  │
                └─────┬─────┘
     ┌──────────────┼──────────────┬──────────────────┐
     ▼              ▼              ▼                  ▼
[最优]改代码    [可接受]先跑   [次优]直接看    [错误] 直接全部
       处Bug        一遍失败用例    错误代码瞎猜     回退到上一版本
  0 步冗余     +1 步验证开销      +3 步定位慢         破坏任务
```

**RPA vs Agent 的本质区分测试**：

> 在同样的场景中，引入 5 处「环境变体」（如命令行参数拼写变了、API 返回字段多了一层嵌套）。
> *   纯 RPA：决策树完全相同走 → **环境一变就错**，Dec4 = 0%
> *   弱 Agent：能识别 1-2 处变体，其余仍按脚本走 → Dec4 = 30%
> *   强 Agent：识别所有 5 处，自行调整适配 → Dec4 = 80%+

**反事实验证（Counterfactual Validation）**：
对 Dec2（决策正确性），不能只看「最终对了」，要看「中间每一步是否选得好」。做法：在每一个决策节点，做反事实模拟——如果 Agent 选了另一条路，结果会更好吗？如果更好，说明该节点决策非最优，扣分。

### 3.5 代码实现：决策路径评估器（DecisionPathEvaluator）

```python
"""
DecisionPathEvaluator - 决策路径质量评估
基于"决策树场景库 + 动作价值标注"
"""

@dataclass
class DecisionNode:
    """决策树中的一个节点"""
    node_id: str
    description: str
    available_actions: List[Dict]
    # 每个动作: {"id": "...", "label": "...", "value": 1.0/0.5/0.0/-1.0, "next_node": "..."}
    optimal_action_id: str
    max_reachable_score: float  # 从该节点到结束能拿到的最高总分


@dataclass
class PathEvaluation:
    dec1_necessity_ratio: float
    dec2_correctness: float
    dec5_efficiency_ratio: float
    overall_score_0_100: float
    per_step_analysis: List[Dict]


class DecisionPathEvaluator:
    
    def __init__(self, decision_tree: Dict[str, DecisionNode]):
        self.tree = decision_tree
    
    def evaluate(self, agent_trace: List[Dict]) -> PathEvaluation:
        """
        agent_trace: [{node_id, action_chosen_id, observation, steps_taken}]
        """
        total_optimal_score = 0
        total_achieved_score = 0
        unnecessary_steps = 0
        correct_decisions = 0
        theoretical_min_steps = 0
        actual_steps = 0
        analysis = []
        
        for step in agent_trace:
            node = self.tree.get(step["node_id"])
            if not node:
                continue
            
            theoretical_min_steps += 1  # 每个节点最少 1 步
            actual_steps += step.get("steps_taken", 1)
            if step.get("steps_taken", 1) > 1:
                unnecessary_steps += step["steps_taken"] - 1
            
            chosen_action = [
                a for a in node.available_actions
                if a["id"] == step["action_chosen_id"]
            ][0]
            
            # 累计得分
            max_val = max(a["value"] for a in node.available_actions)
            total_optimal_score += max_val
            total_achieved_score += chosen_action["value"]
            
            # 是否"正确"（最优或等价）
            is_correct = chosen_action["value"] >= max_val - 0.1
            if is_correct:
                correct_decisions += 1
            
            # 逐节点分析
            analysis.append({
                "node": node.node_id,
                "chosen": chosen_action["label"],
                "value_got": chosen_action["value"],
                "value_max": max_val,
                "optimal": chosen_action["id"] == node.optimal_action_id,
                "extra_steps": step.get("steps_taken", 1) - 1,
            })
        
        n = len([a for a in analysis])
        dec1 = max(0.0, 1.0 - unnecessary_steps / max(1, actual_steps)) * 100
        dec2 = (correct_decisions / n) * 100 if n else 0
        dec5 = actual_steps / max(1, theoretical_min_steps)
        
        # 效率比分：越接近 1.0 越好 → 转化为 0-100
        if dec5 <= 1.2:
            dec5_score = 100.0
        elif dec5 <= 2.0:
            dec5_score = 100 - (dec5 - 1.2) / 0.8 * 40  # 1.2-2.0 → 100-60
        else:
            dec5_score = max(0.0, 60 - (dec5 - 2.0) * 20)
        
        overall = (
            dec1 * 0.25 +          # 必要性
            dec2 * 0.50 +          # 正确性（核心）
            dec5_score * 0.25      # 效率
        )
        
        return PathEvaluation(
            dec1_necessity_ratio=round(dec1, 2),
            dec2_correctness=round(dec2, 2),
            dec5_efficiency_ratio=round(dec5, 2),
            overall_score_0_100=round(overall, 2),
            per_step_analysis=analysis
        )
```

---

## 4. 资源利用效率评价（Resource Efficiency）

### 4.1 题目

**一个 Agent 任务成功率 95%，看起来优秀，但每任务消耗 $2.5；另一个 Agent 成功率 90%，每任务只消耗 $0.3。你认为哪个更优秀？请设计完整的资源-效果权衡评价方法，并给出具体的资源 Profiling 方案。**

### 4.2 考点分析

*   是否能跳出「唯成功率论」，理解 Agent 工程的本质是「性价比最大化」？
*   能否拆解资源消耗的来源？（只说 Token = 初级；能拆 Token/工具/计算/存储/人力 = 高级）
*   是否知道 Pareto 前沿？（知道该词说明有扎实的优化理论背景）

### 4.3 指标体系设计

| ID | 指标 | 定义 | 优秀阈值 | 采集源 |
|:--|:-----|:-----|:--------:|:------:|
| E1 | **Token 效率** | 每 1000 Input+Output Token 换取的「任务完成分」 | ≥1.2 分/K Token | LLM 调用日志 |
| E2 | **单位成本完成率** | 成功任务数 ÷ 总花费（美元） | ≥30 任务/$1 | 成本账单聚合 |
| E3 | **资源浪费率** | 失败任务/重试/不必要调用消耗的占比 | ≤8% | Trace 审计 |
| E4 | **延迟-准确性 Pareto 得分** | 同等准确率下，延迟越低越好；或同等延迟下准确率越高越好 | Pareto 前沿内 | 双维散点图 |
| E5 | **峰值吞吐承载率** | 实测峰值 TPS ÷ 配置额定目标 TPS | ≥90% | 压测报告 |

### 4.4 测试方案：资源 Profiling + Pareto 最优前沿分析

#### Pareto 前沿分析（"又好又省"的科学定义）

在「成功率 vs 单位成本」、「成功率 vs P90 延迟」的二维散点图上，定义 **Pareto 支配关系**：

> Agent A 支配 Agent B ⟺ A 在任一维度不差于 B，且至少一个维度严格优于 B。

```mermaid
xychart-beta
    title "Agent 候选方案：成功率 vs 单位成本（Pareto 前沿）"
    x-axis "单位成本（$ / 成功任务）" [0.2 --> 2.5]
    y-axis "任务成功率 (%)" 70 --> 96
    scatter [
      [0.22, 71],
      [0.30, 90],   # ← B 方案（性价比高）
      [0.45, 88],
      [0.50, 93],
      [0.75, 92],
      [1.10, 95],
      [2.40, 95.5]  # ← A 方案（成功率略高但成本 8 倍）
    ]
    line [
      71, 90, 88, 93, 92, 95, 95.5  # Pareto 前沿
    ]
```

> **本题目答案揭晓**：
> *   如果场景是「客服助理（量大利薄）」→ B 明显优秀（Pareto 支配大多数），A 的 5% 成功率提升带来的收益，根本覆盖不了 8.3× 成本。
> *   如果场景是「医疗诊断/金融风控（单任务价值极高）」→ A 更优。假设一单错了损失 $10K，多花 $2.2 换 5% 错误减少 = 每单节省 $500 期望损失。
> *   **所以一个好的评价体系，必须给出「按场景差异化权重 + Pareto 分位数」的结论，而不是单一说"谁更好"**。

#### 资源 Profiling 的最小化埋点清单（工程级落地）

每个 Agent 任务必须采集（不能事后补）：

| 资源维度 | 采集字段 | 粒度 |
|---------|---------|:----:|
| LLM Token | `model_id, prompt_tokens, completion_tokens, cached_tokens, cost_usd` | 每次调用 |
| 工具调用 | `tool_id, latency_ms, retry_count, api_call_cost, data_scanned_bytes` | 每次调用 |
| 计算资源 | `process_cpu_peak_millis, process_ram_peak_mb, gpu_util_peak, wall_time_ms` | 每任务 |
| 存储/IO | `vector_db_queries, db_read_bytes, db_write_bytes, object_storage_ops` | 每任务 |
| 人力介入 | `human_interventions, human_time_seconds, rollback_count` | 每任务 |

---

## 5. 学习与适应能力评价（Learning & Adaptability）

### 5.1 题目

**如何验证一个 Agent 真的"会学习"，而不是代码里写死的 Prompt 模板？设计完整的学习能力评测方案，包括泛化、长期记忆、失败策略调整、用户偏好学习四个方向。**

### 5.2 考点分析

"会学习"是 Agent 区别于一次性脚本的核心标志，但也是最难测的——很多团队把「重新 Prompt」假装成「学习成功」。面试官希望看到是否有**可证伪**的测试设计。

### 5.3 指标体系设计

| ID | 指标 | 定义 | S/A/B 阈值 |
|:--|:-----|:-----|:-----------|
| L1 | **分布外泛化 Gap** | OOD 用例成功率 ÷ ID（用例内）成功率 | S≥0.85 / A≥0.70 / B≥0.55 |
| L2 | **学习增益 Gain** | 训练 500 任务后的成功率 − Day 0 成功率 | S≥+12pt / A≥+7pt / B≥+3pt |
| L3 | **收敛速度** | 达到 Day0 + 90% × Gain 所需任务数 | S≤200 / A≤400 / B≤800 |
| L4 | **失败策略调整率** | 同类失败第二次出现时，Action 序列差异度 ≥30% 的比例 | S≥85% / A≥65% / B≥45% |
| L5 | **偏好学习准确率** | Top-3 推荐 / 风格匹配的命中率 | S≥88% / A≥72% / B≥55% |

### 5.4 测试方案：分布外泛化 + 学习曲线 + 失败策略调整率

#### L2 + L3：学习曲线测试（最具说服力的"真学习"证据）

步骤：
1.  **Day 0**：在固定测试集 TestSet-Final 上测一次初始得分 S₀（注意：TestSet-Final 只在 Day0 和测试结束时各跑一次，避免污染）。
2.  **训练期**：让 Agent 连续处理 Streaming-Data（流式训练任务，每任务给反馈，Agent 走 154 号文档的自主学习闭环）。
3.  **每 50 个任务**：跑一次「小型评估集 DevSet」，记录得分。
4.  **第 500 任务后**：再跑 TestSet-Final，得 S_final → Gain = S_final - S₀。
5.  **拟合学习曲线**：`Score(t) = Ceiling − (Ceiling − S₀) × exp(−λt)`，λ 越大收敛越快；t_90 = 达到 90%Gain 的任务数 = L3。

> **防骗术**：如果 DevSet 分数涨了但 TestSet-Final 分数没涨 → 「过拟合学习」，不是真的会学习，只是记住了 DevSet 的答案。必须在**未见过的测试集**上验证。

#### L4：失败策略调整率（反死循环的学习能力）

用同一类失败模式（如「DB 连接超时」）构造 20 次独立任务，每次 Agent 失败后给出「已失败 + 原因」反馈，看它下次是否还做完全一样的事：

> *   好 Agent：第 3 次之后就改变策略（换 API 端点/指数退避/切换到备用数据源），Action 序列的 Jaccard 相似度从 1.0 下降到 ≤0.5。
> *   差 Agent：20 次全是一模一样的失败序列，相似度永远 ≈1.0。

---

## 6. 交互友好度评价（User Interaction Quality）

### 6.1 题目

**用户体验是 Agent 能否真正被采用的决定因素。请从「用户- Agent 交互」的全过程设计量化评价方案，而不是只给一个 CSAT 问卷。**

### 6.2 考点分析

CSAT 是必要的，但不是充分的。高级工程师必须能设计「超越问卷」的**行为级指标**——用户的鼠标/操作不会撒谎。

### 6.3 指标体系设计

| ID | 指标 | 定义 | 说明 | S 阈值 |
|:--|:-----|:-----|:-----|:------:|
| UX1 | **用户澄清率** | Agent 输出后，用户需要追问/澄清的回合占比 | 越少越"说人话" | ≤10% |
| UX2 | **纠正回退率** | 用户手动修改/撤销/回退 Agent 结果的比例 | 纠正率>30% = Agent 实际是**降效** | ≤8% |
| UX3 | **首步交互感知延迟** | 用户发送 → Agent 首字符/首卡片出现的 P90 | 感知 3s 是体验临界点 | ≤3s |
| UX4 | **可解释满意度** | 关键步骤给出可理解理由的比例 × 人工评分 10 分制 | 黑盒决策 = 用户不信任 | ≥8/10 |
| UX5 | **异常场景优雅度** | Agent 出错时：道歉+原因+补救建议 vs 沉默/堆栈溢出 | 专家评审 5 分制 | ≥4.2/5 |
| UX6 | **7 日/30 日使用率留存** | 周活跃用户中 7 日后仍活跃的比例 | 留存差=本质体验差 | ≥55% |

### 6.4 测试方案：行为埋点 + 交互模式库 + 专家评审

**UX 反模式检测库（低成本高信号）**：

| 反模式代码 | 行为表现 | 检测方式 | 发现此模式扣分权重 |
|:----------|:---------|:---------|:-----------------:|
| UX-ANT-01 | **无限追问**：每个问题先让用户确认 2-3 次 | 每任务用户澄清交互次数 ≥3 | 高 |
| UX-ANT-02 | **输出无结构**：扔一大段文字，用户自己找关键信息 | JSON/Markdown 结构化输出占比 <50% | 中 |
| UX-ANT-03 | **过度啰嗦**：一句能说清的用三句 | 回复 Token 数 ÷ 信息点数量 ≥ 阈值 | 中 |
| UX-ANT-04 | **错误静默**：出错无提示，用户得自己猜 | 失败任务中给出显式错误信息比例 <60% | 极高 |
| UX-ANT-05 | **假自信**：不确定的内容也说 100% 确定 | 置信度校准分数 ≤0.5 | 极高 |

> 反模式检测分数本身即可作为 UX 维度的组成部分，**占 UX 总分的 40% 权重**，比发问卷省时省钱、信号更强。

---

## 7. 错误处理机制评价（Error Handling & Resilience）

### 7.1 题目

**设计一个能系统评价 Agent 错误处理能力的方案。要求覆盖 「工具故障、网络问题、权限不足、数据缺失、格式错误」五大类常见故障，给出具体的故障注入测试方案和评分标准。**

### 7.2 考点分析

Demo 里永远没有故障，生产里天天是故障。高级 Agent 和 Demo Agent 的最大差别就是 **1% 场景下的行为**。本题考察面试者是否有「混沌工程」思维。

### 7.3 指标体系设计

| ID | 指标 | 定义 | S/A/B 阈值 |
|:--|:-----|:-----|:-----------|
| R1 | **故障自恢复率** | 在注入故障时，Agent 无需人工介入即可自恢复并完成任务的比例 | S≥92 / A≥80 / B≥60 |
| R2 | **无故障传播率** | 单步故障不会引发后续 3+ 步连锁错误的比例 | S≥98 / A≥93 / B≥85 |
| R3 | **死循环/雪崩避免率** | 触发故障后，不会陷入重复调用死循环或 Token 雪崩 | S≥99.5 / A≥98 / B≥95 |
| R4 | **MTTR 平均恢复时间** | 从故障发生到任务继续推进的中位时间 | S≤1.5s / A≤5s / B≤15s |
| R5 | **错误信息可理解性** | 最终暴露给用户的错误信息专家评分（10 分制） | S≥8.5 / A≥7 / B≥5 |
| R6 | **人类介入成功率** | 当需要 HITL 时，Agent 能否提供充足上下文让人类 1 分钟内决策并继续 | S≥90% / A≥75% / B≥55% |

### 7.4 测试方案：故障注入（Chaos Engineering for Agents）

**五大类故障 × 严重程度 × 注入时机 = 125 个标准故障用例矩阵**：

| 故障类型 | 轻量级故障（L1） | 中量级故障（L2） | 重量级故障（L3） | 注入时机 |
|---------|:---------------|:---------------|:---------------|:--------|
| **工具故障** | 工具延迟 2x | API 返回 `503` + 重试 1 次成功 | API 永久 4xx，返回格式不变 | 第 1 次/第 3 次/最后一次调用 |
| **网络问题** | 丢包 10% + 重传 | RTT ×5 + 超时一次 | 网络 10s 全断 | 任意 LLM / API 调用 |
| **权限不足** | 返回 403 但附可读错误信息 | 403 无错误信息 | 操作被静默拒绝，无明确提示 | 敏感操作步骤前 |
| **数据缺失** | 字段缺失（如 age=null） | 整列数据缺失 | 上游数据源整体空 | RAG 检索 / DB 查询后 |
| **格式错误** | JSON 缺尾括号（可修复） | 完全乱码 | 返回 HTML 错误页而非 JSON | Tool 返回 / 输入给 Agent |

**评分逻辑（最重要！）**：
*   面对 L1 轻量级故障 → **必须自恢复**，需要人工 = 直接扣大分（这是基本功）。
*   面对 L2 中量级故障 → **允许降级但不能失败**，例如：数据库查不到 → 换缓存查 / 用旧版本数据 + 提示"数据可能非最新"。
*   面对 L3 重量级故障 → **优雅退出 + 明确错误信息 + 补救建议**。要求"全自恢复"是不现实的，判断标准是**能否把用户伤害降到最低**而不是硬撑。

### 7.5 代码实现：故障注入测试框架（AgentChaosKit）

```python
"""
AgentChaosKit - 面向 Agent 的故障注入测试框架
核心思想: 猴子补丁 + 故障概率调度 + 行为审计
"""

import random
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class FaultType(Enum):
    TOOL_LATENCY = "tool_latency"
    TOOL_503_RETRYABLE = "tool_503"
    TOOL_PERMISSION_403 = "tool_403"
    NETWORK_TIMEOUT = "network_timeout"
    DATA_FIELD_MISSING = "data_missing"
    OUTPUT_MALFORMED_JSON = "malformed_json"


class FaultSeverity(Enum):
    L1 = 1  # 轻量
    L2 = 2  # 中量
    L3 = 3  # 严重


@dataclass
class FaultRule:
    fault_type: FaultType
    severity: FaultSeverity
    probability: float     # 0-1，每次调用触发概率
    target_tool: Optional[str] = None  # None = 全适用
    min_step: int = 0
    max_step: int = 9999


@dataclass
class InjectionReport:
    injected_count: int
    detected_count: int             # Agent 明确识别出故障类型
    self_recovered_count: int       # 自恢复完成任务
    propagated_count: int           # 故障传播（后续出错归因于前故障）
    dead_loop_count: int            # 触发死循环
    human_needed_count: int         # 需要人工介入
    r1_self_recovery_rate: float
    details: List[Dict]


class AgentChaosKit:
    
    def __init__(self, agent_executor, rules: List[FaultRule]):
        self.executor = agent_executor
        self.rules = rules
        self.injection_log = []
        self._install_monkey_patches()
    
    def _install_monkey_patches(self):
        """通过猴子补丁在工具/网络层注入故障"""
        original_tool_exec = self.executor.tools.execute
        
        def wrapped_tool_exec(tool_id, params):
            step = self.executor.current_step
            # 检查是否匹配任一故障规则
            fired = self._match_and_fire(tool_id, step)
            if fired:
                return self._apply_fault(fired, original_tool_exec, tool_id, params)
            return original_tool_exec(tool_id, params)
        
        self.executor.tools.execute = wrapped_tool_exec
    
    def _match_and_fire(self, tool_id, step) -> Optional[FaultRule]:
        for rule in self.rules:
            if rule.target_tool and rule.target_tool != tool_id:
                continue
            if not (rule.min_step <= step <= rule.max_step):
                continue
            if random.random() < rule.probability:
                self.injection_log.append({"tool": tool_id, "step": step, "rule": rule})
                return rule
        return None
    
    def _apply_fault(self, rule: FaultRule, real_exec, tool_id, params):
        """按类型执行故障注入"""
        sev = rule.severity.value
        
        # ============ 延迟类 ============
        if rule.fault_type == FaultType.TOOL_LATENCY:
            extra_ms = {1: 200, 2: 2000, 3: 12000}[sev]
            time.sleep(extra_ms / 1000.0)
            return real_exec(tool_id, params)
        
        # ============ 可重试 503 ============
        if rule.fault_type == FaultType.TOOL_503_RETRYABLE:
            attempts = {1: 1, 2: 3, 3: 999}[sev]  # L3: 永远 503
            retry_count = self.executor.current_retry_count
            if retry_count < attempts:
                raise Retryable503Error(f"Chaos Injected 503 (try {retry_count + 1}/{attempts})")
            return real_exec(tool_id, params)
        
        # ============ 权限 403 ============
        if rule.fault_type == FaultType.TOOL_PERMISSION_403:
            if sev == 1:
                raise PermissionError("L1: 权限不足，请检查 role 'read_only' 是否需要提升")
            elif sev == 2:
                raise PermissionError("Forbidden")
            else:
                # L3: 静默失败（最考验 Agent）
                return empty_safe_result_for_tool(tool_id)
        
        # ============ 数据缺失 ============
        if rule.fault_type == FaultType.DATA_FIELD_MISSING:
            result = real_exec(tool_id, params)
            if isinstance(result, dict):
                keys = list(result.keys())
                # L1 删 1 个字段；L2 删一半；L3 返回 {}
                if sev == 1 and keys:
                    result.pop(random.choice(keys))
                elif sev == 2:
                    for k in keys[:len(keys)//2]:
                        result[k] = None
                elif sev == 3:
                    result = {}
            return result
        
        # ============ 格式错误 ============
        if rule.fault_type == FaultType.OUTPUT_MALFORMED_JSON:
            good = json.dumps(real_exec(tool_id, params))
            if sev == 1:
                return good[:-1]  # 删一个括号，可修复
            elif sev == 2:
                return good + "@@@garbage###" * 5  # 乱码
            else:
                return "<html><body>502 Bad Gateway</body></html>"
        
        return real_exec(tool_id, params)
    
    def run_suite(self, test_cases: List[Dict]) -> InjectionReport:
        """运行完整故障注入测试套件，生成评分报告"""
        injected = detected = recovered = propagated = dead = human = 0
        
        for case in test_cases:
            result = self.executor.run(case)
            injected += 1
            # 审计 Agent Trace
            trace = result.trace
            if trace.agent_detected_fault:
                detected += 1
            if trace.success and not trace.human_intervened:
                recovered += 1
            if trace.fault_propagated:
                propagated += 1
            if trace.was_in_loop:
                dead += 1
            if trace.human_intervened:
                human += 1
        
        return InjectionReport(
            injected_count=injected,
            detected_count=detected,
            self_recovered_count=recovered,
            propagated_count=propagated,
            dead_loop_count=dead,
            human_needed_count=human,
            r1_self_recovery_rate=recovered / max(1, injected),
            details=[...]
        )
```

---

## 8. 综合评分与可视化：如何给出"该 Agent 是否优秀"的最终结论

### 8.1 面试题汇总场景

**最后一步：你手上有七维的详细得分，现在请给 CEO / 产品委员会做一页 5 分钟决策汇报，给出最终结论。你会怎么呈现？**

本题考察：**从技术得分到业务决策的翻译能力**。

### 8.2 加权聚合公式 + 等级判定 + 一票否决红线

```
最终得分计算（门控式加权）：
┌────────────────────────────────────────────────────────────────────┐
│  STEP 1: Gate 1 功能及格线检查                                   │
│          IF D1 功能实现 < 60分  →  返回等级 F + 原因"功能不过关"  │
│          → 终止，不看其他维度                                      │
├────────────────────────────────────────────────────────────────────┤
│  STEP 2: Gate 2 安全红线（一票否决）                             │
│          IF 任何红线项触发：                                       │
│             • S2 对抗安全防御率 <80%                              │
│             • S3 发生真实数据泄露或越权                            │
│             • S1 死循环率 >5%                                     │
│             • 合规不满足                                          │
│          →  返回等级 F + 原因"安全红线未过" + 禁止上线           │
├────────────────────────────────────────────────────────────────────┤
│  STEP 3: 七维加权聚合（过了 Gate 才计算）                        │
│     Total = Σ ( DimScore_i × DimWeight_i )                       │
│     D1×25% + D2×15% + D3×15% + D4×10% +                          │
│     D5×10% + D6×15% + D7×10%                                     │
├────────────────────────────────────────────────────────────────────┤
│  STEP 4: 等级判定 + 业务建议                                     │
│     S ≥90 → 卓越：全量上线，建立标杆                               │
│     A 80-89 → 优秀：全量，灰度对照 2 周                           │
│     B 70-79 → 良好：灰度 20%，观察 2 周                           │
│     C 60-69 → 合格：试点 5% 低风险场景                            │
│     D 50-59 → 待改进：回炉，不建议上线                            │
│     F <50 → 不合格：暂停项目，先解决 Gate 问题                    │
└────────────────────────────────────────────────────────────────────┘
```

### 8.3 评价报告模板（一页决策版）

```
┌──────────────────────────────────────────────────────────────────────┐
│   📊 Agent v3.2.1 综合性能评价报告（决策版）                          │
│   生成时间: 2026-08-08   评估人: AI 评审委员会                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─ 总评 ──────────────────────────────────────────────────────────┐ │
│   │  🌟 最终等级：A 优秀 (综合得分 85.4 / 100)                      │ │
│   │  🆚 上一版 v3.1.0: 78.6 → 本轮 +6.8pt                            │ │
│   │  🎯 上线建议：✅ 全量上线（保留 10% 对照组）                     │ │
│   └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   ┌─ 七维雷达（得分 × 权重）────────────────────────────────────────┐ │
│   │                                                                 │ │
│   │          任务完成 [D1] ● 89 (25%)   安全可靠 [D7] ● 88 (10%)    │ │
│   │                   ╲         ╱                                    │ │
│   │     自主决策 [D2] ● 82 (15%)     错误韧性 [D6] ● 86 (15%)      │ │
│   │                   │         │                                    │ │
│   │     资源效率 [D3] ● 80 (15%)     交互友好 [D5] ● 87 (10%)      │ │
│   │                   ╱         ╲                                    │ │
│   │          学习适应 [D4] ● 84 (10%)                                │ │
│   │                                                                 │ │
│   └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   ┌─ 核心改进项（相对 v3.1.0）─────────────────────────────────────┐ │
│   │  ✅ Dec2 决策正确性 +12pt → 154 号学习闭环生效                   │ │
│   │  ✅ R1 故障自恢复率 +10pt → 接入 13 号防循环 + ErrorClassifier   │ │
│   │  ✅ UX2 纠正率 -7pt → UX-ANT-01 模式整治                        │ │
│   └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   ┌─ Top-3 失分归因 & 下一版本改进建议 ────────────────────────────┐ │
│   │  1. F6 幻觉率 6% (B 级) → 下版引入事实核查模块 (预估 +3pt)      │ │
│   │  2. E2 Pareto 非最优 (C 级) → 大小模型智能路由 (预估 +4pt)     │ │
│   │  3. L4 失败策略调整率 58% (B) → 记忆库反模式黑名单 (预估 +5pt) │ │
│   └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 9. 面试官视角：不同职级候选人的回答分层

| 职级 | 典型表现 | 给分参考 |
|:----|:---------|:--------:|
| **P5/初级** | 只说「看成功率、看响应速度」，无法拆解具体指标，无测试方案 | 3-4/10，不合格 |
| **P6/资深** | 能说 4-5 个维度，但权重无依据；能说「做基准测试」，但说不出具体怎么做（分级评分卡、OOD 比例、Pareto 等）；无代码级实现思路 | 5-6/10，边界合格 |
| **P7/专家** ✅ | 体系化 6-7 维，每维 3-5 个可量化指标并有阈值逻辑；有基准+A/B+评审三阶段；能针对任务完成/错误处理写出 TaskJudge 或 ChaosKit 的核心代码；理解 Pareto、OOD Gap、CSAT 问卷与行为指标的关系 | 8-9/10，优秀通过 |
| **P8/架构师** 🏆 | 回答中有「门控式架构 + 失分归因树 + 三校准阈值法 + 反刷分防御 + 业务级一页决策汇报模板」；对 R1 自恢复、Dec2 决策正确性、E2 Pareto 的工程级落地思考完整；能说清"不同业务场景下权重如何变、为什么这样变" | 10/10，强烈通过 |

---

## 10. 总结与工程化落地清单

### 10.1 核心结论

> **Agent 是否优秀 ≠ "Demo 演示效果好"**，而是下面这件事：
>
> **在可接受的成本、延迟、风险下，以稳定、可验证、可改进的方式，持续为真实用户创造业务价值。**
>
> 本章七维评价体系（任务完成 / 决策水平 / 资源效率 / 学习适应 / 交互友好 / 错误韧性 / 安全可靠）+ 三阶段评估法（基准 / 灰度 / 专家）+ 混沌故障注入，是把这句话从口号落地为工程系统的具体路径。

### 10.2 工程落地 Checklist（按优先级排序）

| 优先级 | 落地项 | 本章节对应位置 | 人天估算 |
|:------|:-------|:-------------|:--------:|
| P0 🔴 | 建立 F1-F6 功能基准测试集 + 分级评分卡（至少 200 题） | 第二章 2.3-2.4 | 10d |
| P0 🔴 | 上线 R1-R6 红线监控 + 一票否决机制 | 第七、八章 | 3d |
| P1 🟠 | 落地 TaskJudge 三层级评判器（规则 + LLM + 相似度） | 第二章 2.5 代码 | 5d |
| P1 🟠 | 资源 Profiling 埋点（11 项必填字段）+ E1-E5 报表 | 第四章 | 3d |
| P1 🟠 | AgentChaosKit 故障注入 25 个基础用例（5 类 × L1） | 第七章 7.4-7.5 | 5d |
| P2 🟡 | Dec1-Dec5 决策树场景库（10+ 场景，每场景 5+ 分支） | 第三章 3.4-3.5 | 7d |
| P2 🟡 | UX 反模式检测库上线（5 类 ANTI 模式，占 UX 40% 权重） | 第六章 6.4 | 2d |
| P2 🟡 | L2-L3 学习曲线评估（Day0 vs 500 任务后的 TestSet-Final） | 第五章 5.4 | 4d |
| P3 🟢 | 一页决策报告模板（雷达 + 失分归因 + 上线建议） | 第八章 8.3 | 2d |
| P3 🟢 | Pareto 前沿分析（多版本候选方案对比图） | 第四章 4.4 | 2d |

**合计预估**：3-4 周（1 名架构师 + 2 名资深工程师）可完成从 0 到「可用的」Agent 综合评价体系。
