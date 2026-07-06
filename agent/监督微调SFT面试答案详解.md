# 监督微调（SFT）面试答案详解

> 面试核心题目：什么是监督微调（SFT）？它的原理和实施流程是什么？
> 本文档系统覆盖 SFT 的定义、原理、数据、方法、挑战，适合中高级技术面试准备。

---

## 目录

- [一、SFT 的定义与定位](#一sft-的定义与定位)
- [二、核心原理](#二核心原理)
- [三、SFT 数据构建](#三sft-数据构建)
- [四、实施步骤](#四实施步骤)
- [五、关键微调方法](#五关键微调方法)
- [六、关键技术考量](#六关键技术考量)
- [七、常见挑战与解决方案](#七常见挑战与解决方案)
- [八、典型应用场景](#八典型应用场景)
- [九、面试高频追问](#九面试高频追问)
- [十、总结](#十总结)

---

## 一、SFT 的定义与定位

### 1.1 什么是监督微调

**监督微调（Supervised Fine-Tuning，简称 SFT）**，是指在大规模预训练模型（基座模型）的基础上，使用**人工标注的指令-回答对**数据进行有监督训练，使模型学会遵循人类指令、以对话格式输出。

### 1.2 SFT 在大模型训练流程中的位置

```
完整训练流程:

  预训练          SFT           RLHF/DPO         部署
  (Pre-training)  (Fine-tuning)  (Alignment)    (Deployment)
      │              │               │              │
      ▼              ▼               ▼              ▼
  学习语言能力  →  学会对话格式  →  对齐人类偏好  →  服务上线
  (Base Model)    (Chat Model)    (Aligned Model)  (Production)
      │              │               │
   自监督学习      有监督学习       强化学习
   无标注数据      人工标注数据     偏好排序数据
   成本90%+        成本~5%          成本~3%
```

### 1.3 为什么需要 SFT

```
预训练后的基座模型（Base Model）:

  输入: "请帮我写一首关于春天的诗"
  输出: "请帮我写一首关于夏天的诗\n请帮我写一首关于秋天的诗"
  → 只是做文本续写，不理解"指令"

  输入: "法国的首都是哪里？"
  输出: "日本的首都是哪里？\n德国的首都是哪里？"
  → 把问题当成陈述句在续写

SFT 后的对话模型（Chat Model）:

  输入: "请帮我写一首关于春天的诗"
  输出: "春风拂面花开早，\n燕子归来柳色新。\n万物复苏生机旺，\n人间四月最美时。"
  → 理解指令，给出正确回答

  输入: "法国的首都是哪里？"
  输出: "法国的首都是巴黎。巴黎位于法国北部塞纳河畔..."
  → 理解问题，给出准确答案
```

### 1.4 SFT 的核心目标

| 目标 | 说明 |
|------|------|
| **指令遵循** | 理解人类指令意图，按指令执行任务 |
| **对话格式** | 学会多轮对话的交互格式 |
| **角色区分** | 区分 user/assistant 角色，不越权 |
| **风格统一** | 输出风格一致（礼貌、专业、简洁） |
| **能力激活** | 激活预训练中已学到但未被"唤醒"的能力 |

---

## 二、核心原理

### 2.1 训练目标

SFT 本质上仍是**自回归语言建模**，但关键区别在于：**只对 assistant 的回答部分计算损失**。

```
训练样本:
  [user]   什么是递归？
  [assistant] 递归是一种编程技巧，函数在执行过程中调用自身...

Token 序列:
  [BOS] user: 什么是递归？ assistant: 递归是一种编程技巧...
  
Loss 计算:
  user: 什么是递归？  →  这部分不计入 loss（MASK）
  assistant: 递归是一种...  →  这部分计入 loss

  L = -Σ log P(token_i | token_{<i}),  只对 assistant 部分求和
```

### 2.2 与预训练的区别

| 维度 | 预训练 | SFT |
|------|--------|-----|
| **训练目标** | 预测所有 token | 只预测 assistant 部分 token |
| **数据量** | TB 级（万亿 token） | 万~百万条 |
| **学习率** | 3e-4 | 2e-5（小一个量级） |
| **训练轮数** | 通常 1 epoch | 2~5 epochs |
| **Batch Size** | 百万 token 级 | 128~1024 |
| **数据格式** | 纯文本续写 | 指令-回答对 |
| **目的** | 学语言和知识 | 学指令遵循和对话 |

### 2.3 损失函数详解

```python
import torch
import torch.nn.functional as F

def sft_loss(model, input_ids, labels, attention_mask):
    """
    SFT 损失计算
    
    Args:
        input_ids:     [B, L]  完整序列（prompt + response）
        labels:        [B, L]  目标序列（prompt 部分为 -100/MASK，response 部分为真实 token）
        attention_mask: [B, L]  注意力掩码
    
    Returns:
        loss: 标量
    """
    # 前向传播，获取 logits
    # logits: [B, L, V]  V 是词表大小
    logits = model(input_ids, attention_mask=attention_mask)
    
    # 移位：预测第 i+1 个 token
    # logits[:, :-1] 预测 labels[:, 1:]
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()
    
    # 交叉熵损失，ignore_index=-100 自动忽略 prompt 部分
    loss = F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_labels.view(-1),
        ignore_index=-100  # prompt 部分的 label 设为 -100
    )
    
    return loss


# ===== 数据构造示例 =====
def build_sft_sample(tokenizer, prompt, response, max_length=2048):
    """
    构造 SFT 训练样本
    
    prompt:   "什么是递归？"
    response: "递归是一种编程技巧，函数在执行过程中调用自身..."
    """
    # 拼接完整序列
    full_text = f"user: {prompt}\nassistant: {response}"
    prompt_text = f"user: {prompt}\nassistant: "
    
    # 编码
    full_ids = tokenizer.encode(full_text, max_length=max_length, truncation=True)
    prompt_ids = tokenizer.encode(prompt_text, max_length=max_length, truncation=True)
    
    # 构造 labels：prompt 部分设为 -100，只对 response 计算损失
    labels = full_ids.copy()
    for i in range(len(prompt_ids)):
        labels[i] = -100  # 屏蔽 prompt 部分
    
    return {
        "input_ids": full_ids,
        "labels": labels,
        "attention_mask": [1] * len(full_ids)
    }
```

### 2.4 SFT 的本质理解

```
SFT 不是让模型学习新知识，而是:

1. 激活已有能力
   ┌──────────────────────────────┐
   │   预训练模型已经"知道"答案    │
   │   SFT 教它"如何表达"答案     │
   │                              │
   │   类比: 学生已经读了所有课本  │
   │   SFT = 教他如何答题          │
   └──────────────────────────────┘

2. 格式对齐
   预训练: 自由文本续写 → SFT: 结构化问答格式

3. 行为塑造
   预训练: 无差别续写 → SFT: 只在 assistant 角色时回答
```

---

## 三、SFT 数据构建

### 3.1 数据格式

```json
// 格式1: Alpaca 格式（单轮）
{
  "instruction": "请解释什么是快速排序",
  "input": "",
  "output": "快速排序是一种分治算法，通过选择一个基准值..."
}

// 格式2: ShareGPT 格式（多轮对话）
{
  "conversations": [
    {"role": "user", "content": "用 Python 写一个快速排序"},
    {"role": "assistant", "content": "```python\ndef quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr)//2]\n    left = [x for x in arr if x < pivot]\n    mid = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + mid + quicksort(right)\n```"},
    {"role": "user", "content": "这个的时间复杂度是多少？"},
    {"role": "assistant", "content": "快速排序的平均时间复杂度为 O(n log n)，最坏情况为 O(n²)..."}
  ]
}

// 格式3: ChatML 格式
{
  "messages": [
    {"role": "system", "content": "你是一个专业的编程助手"},
    {"role": "user", "content": "解释什么是闭包"},
    {"role": "assistant", "content": "闭包是指有权访问另一个函数作用域中变量的函数..."}
  ]
}
```

### 3.2 数据来源

```
SFT 数据来源
│
├── 人工标注（质量最高，成本最高）
│   ├── 雇佣专业人员编写
│   ├── 每条数据需要: 编写问题 + 编写高质量回答
│   ├── 成本: $3~20/条
│   └── 代表: OpenAI 的 SFT 数据、Anthropic 的 HH 数据
│
├── 开源数据集
│   ├── Alpaca (52K 条，Stanford)
│   ├── ShareGPT (90K+ 条，用户分享)
│   ├── FLAN Collection (1.8M 条，Google)
│   ├── OpenAssistant (161K 条)
│   ├── Belle (3.5M 条中文)
│   └── Firefly (160K 条中文)
│
├── 自生成数据（Self-Instruct）
│   ├── 用强模型（GPT-4）生成指令-回答对
│   ├── 流程: 种子指令 → 扩展 → 生成回答 → 过滤
│   ├── 成本低，但质量参差不齐
│   └── 代表: Alpaca（用 text-davinci-003 生成）
│
├── Evol-Instruct（进化式生成）
│   ├── 从简单指令出发，逐步演化出更复杂的指令
│   ├── 增加深度（更复杂的问题）和广度（更多领域）
│   └── 代表: WizardLM
│
└── 领域专业数据
    ├── 医疗问答（真实病例+医生回答）
    ├── 法律咨询（真实案例+律师分析）
    ├── 代码问答（GitHub Issues + 解决方案）
    └── 数学推理（竞赛题+详细解题过程）
```

### 3.3 数据质量标准

```python
# SFT 数据质量评估维度
data_quality_criteria = {
    "正确性": "回答内容准确无误，不包含错误信息",
    "完整性": "回答全面覆盖问题，不遗漏关键点",
    "格式规范": "Markdown 格式正确，代码可运行，步骤清晰",
    "多样性": "覆盖多种任务类型和难度级别",
    "自然性": "语言流畅自然，不像机器生成",
    "安全性": "不包含有害、歧视、暴力内容",
    "一致性": "相似问题的回答风格一致",
    "长度适中": "回答长度与问题复杂度匹配",
}

# 数据质量过滤示例
def filter_sft_data(sample):
    # 1. 长度过滤
    if len(sample['response']) < 10:
        return False  # 回答太短
    if len(sample['response']) > 8000:
        return False  # 回答太长
    
    # 2. 重复检测
    if is_duplicate(sample, existing_samples):
        return False
    
    # 3. 质量检测
    if has_low_quality_markers(sample['response']):
        # 检测: "我不知道"、不完整句子、乱码等
        return False
    
    # 4. 安全检测
    if contains_harmful_content(sample):
        return False
    
    return True
```

### 3.4 数据配比策略

```yaml
# 典型的 SFT 数据配比
数据配比:
  通用对话: 30%       # 日常问答、闲聊
  代码生成: 15%       # 编程相关
  数学推理: 10%       # 数学问题
  写作创作: 15%       # 文案、文章、故事
  知识问答: 15%       # 百科、事实性知识
  逻辑推理: 5%        # 逻辑题、脑筋急转弯
  角色扮演: 5%        # 特定角色对话
  安全拒绝: 5%        # 拒绝有害请求的样本

# 配比影响:
#   代码数据多 → 编程能力强，但可能对话不够自然
#   数学数据多 → 推理能力强，但可能回答风格过于刻板
#   安全数据多 → 更安全，但可能过度拒绝
#   需要通过实验找到最佳平衡
```

---

## 四、实施步骤

### 4.1 完整 SFT 流程

```
┌─────────────────────────────────────────────────────────┐
│                   SFT 完整实施流程                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 准备基座模型                                    │
│  ├── 选择预训练模型（如 LLaMA-3-8B-Base）               │
│  ├── 确认模型架构和配置                                  │
│  └── 加载模型权重和 Tokenizer                            │
│                                                         │
│  Step 2: 数据准备                                        │
│  ├── 收集/生成 SFT 数据                                  │
│  ├── 数据清洗和质量过滤                                  │
│  ├── 格式转换（统一为训练格式）                          │
│  ├── 数据去重和平衡                                      │
│  └── 划分训练集/验证集                                   │
│                                                         │
│  Step 3: 训练配置                                        │
│  ├── 选择微调方法（全参数/LoRA/QLoRA）                   │
│  ├── 设置超参数（学习率/batch/epochs）                   │
│  ├── 配置分布式训练策略                                  │
│  └── 设置检查点和日志                                    │
│                                                         │
│  Step 4: 训练执行                                        │
│  ├── 加载模型和数据                                      │
│  ├── 前向传播 → 计算 loss → 反向传播 → 参数更新         │
│  ├── 定期在验证集上评估                                  │
│  ├── 监控训练指标（loss/梯度/学习率）                    │
│  └── 保存检查点                                         │
│                                                         │
│  Step 5: 模型评估                                        │
│  ├── 自动评估（Benchmark 测试）                          │
│  ├── 人工评估（回答质量评分）                            │
│  ├── 对比评估（与基座模型/SOTA 对比）                    │
│  └── 安全评估（越狱测试/有害内容检测）                   │
│                                                         │
│  Step 6: 模型迭代                                        │
│  ├── 分析弱点（哪类问题回答不好）                        │
│  ├── 补充数据（针对弱点增加训练数据）                    │
│  ├── 调整参数（学习率/数据配比/epoch）                   │
│  └── 重新训练                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 训练代码示例

```python
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType

# ===== Step 1: 加载模型和 Tokenizer =====
model_path = "meta-llama/Llama-3-8B"

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,    # 混合精度
    device_map="auto",             # 自动分配到多卡
    trust_remote_code=True
)

# ===== Step 2: 配置 LoRA（可选，全参数微调则跳过） =====
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=64,                          # LoRA 秩
    lora_alpha=128,                # 缩放因子
    lora_dropout=0.05,             # dropout
    target_modules=[               # 应用 LoRA 的模块
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ]
)
model = get_peft_model(model, lora_config)

# ===== Step 3: 数据预处理 =====
def format_and_tokenize(example):
    """将对话数据格式化为模型输入"""
    messages = example["conversations"]
    
    # 使用 ChatML 格式
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    
    # 找到 assistant 回答的起始位置
    prompt_text = tokenizer.apply_chat_template(
        messages[:-1],  # 只到 user 的最后一条
        tokenize=False,
        add_generation_prompt=True  # 添加 assistant: 前缀
    )
    
    # 编码
    full_ids = tokenizer(text, truncation=True, max_length=2048)["input_ids"]
    prompt_ids = tokenizer(prompt_text, truncation=True, max_length=2048)["input_ids"]
    
    # 构造 labels：prompt 部分设为 -100
    labels = full_ids.copy()
    for i in range(len(prompt_ids)):
        if i < len(labels):
            labels[i] = -100
    
    return {
        "input_ids": full_ids,
        "labels": labels,
        "attention_mask": [1] * len(full_ids)
    }

# 加载数据集
dataset = Dataset.from_json("sft_data.json")
dataset = dataset.map(format_and_tokenize, remove_columns=dataset.column_names)

# ===== Step 4: 训练配置 =====
training_args = TrainingArguments(
    output_dir="./sft_output",
    num_train_epochs=3,              # 训练轮数
    per_device_train_batch_size=4,   # 单卡 batch
    gradient_accumulation_steps=8,   # 梯度累积（等效 batch=32）
    
    learning_rate=2e-5,              # 学习率（比预训练小一个量级）
    warmup_ratio=0.03,               # 预热
    lr_scheduler_type="cosine",      # 余弦退火
    
    weight_decay=0.0,                # 权重衰减
    max_grad_norm=1.0,               # 梯度裁剪
    
    logging_steps=10,                # 日志频率
    save_strategy="epoch",           # 每轮保存
    save_total_limit=3,              # 最多保存3个检查点
    
    evaluation_strategy="epoch",     # 每轮评估
    load_best_model_at_end=True,     # 加载最优模型
    
    bf16=True,                       # 使用 bfloat16
    gradient_checkpointing=True,     # 梯度检查点（省显存）
    report_to="tensorboard",         # 日志到 TensorBoard
)

# ===== Step 5: 训练 =====
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    padding=True,
    return_tensors="pt"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator,
)

trainer.train()

# ===== Step 6: 保存模型 =====
trainer.save_model("./sft_model")
tokenizer.save_pretrained("./sft_model")
```

---

## 五、关键微调方法

### 5.1 全参数微调（Full Fine-Tuning）

```
特点:
  - 更新模型所有参数
  - 效果最好
  - 显存需求大（参数 + 梯度 + 优化器状态）
  - 7B 模型需要 ~120GB 显存（FP16）

显存计算（7B 模型）:
  模型参数:     7B × 2 bytes (FP16) = 14 GB
  梯度:        7B × 2 bytes = 14 GB
  优化器状态:    7B × 8 bytes (AdamW) = 56 GB  ← 最大开销
  激活值:       ~10 GB
  总计:        ~94 GB（需要多卡）

适用场景:
  - 有充足算力
  - 追求最佳效果
  - 大规模 SFT 数据
```

### 5.2 LoRA（Low-Rank Adaptation）

```
核心思想:
  不修改原始权重 W，而是添加一个低秩增量 ΔW = A × B

  原始: Y = W × X
  LoRA: Y = (W + α/r × A × B) × X

  W: 原始权重 (d × d)，冻结
  A: 降维矩阵 (d × r)，可训练
  B: 升维矩阵 (r × d)，可训练
  r: 秩（远小于 d，如 r=8/16/64）
  α: 缩放因子

参数量对比:
  原始: d × d = d²
  LoRA: d × r + r × d = 2dr  (r << d)
  
  示例: d=4096, r=8
  原始: 16,777,216 参数
  LoRA: 65,536 参数（减少 99.6%）

图示:
         原始权重 W (d×d)        LoRA 增量
         ┌───────────┐          ┌───┐   ┌───────────┐
输入 ──→ │    W      │ ──→  +   │ A │ × │     B     │ ──→ 输出
         │   (冻结)  │          │   │   │           │
         └───────────┘          └───┘   └───────────┘
                               (d×r)    (r×d)     r << d
                               可训练    可训练
```

```python
# LoRA 配置
lora_config = LoraConfig(
    r=64,                    # 秩，越大效果越好但参数越多
    lora_alpha=128,          # 缩放因子，通常为 r 的 2 倍
    lora_dropout=0.05,       # dropout 防过拟合
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",  # Attention 层
        "gate_proj", "up_proj", "down_proj"       # FFN 层
    ],
    task_type=TaskType.CAUSAL_LM
)
```

### 5.3 QLoRA（Quantized LoRA）

```
QLoRA = 量化基座模型 + LoRA 微调

原理:
  1. 将基座模型量化为 4-bit（NF4 格式）
  2. 在量化模型上应用 LoRA
  3. LoRA 参数保持 FP16/BF16 精度

显存对比（7B 模型）:
  全参数微调:  ~94 GB  → 需要 4×A100-80G
  LoRA:       ~28 GB  → 需要 1×A100-40G
  QLoRA:      ~10 GB  → 单卡 RTX 4090 可跑

优势:
  - 极大降低显存需求
  - 效果接近全参数微调
  - 适合资源有限的团队
```

### 5.4 方法对比

| 方法 | 参数量 | 显存(7B) | 效果 | 训练速度 | 适用场景 |
|------|--------|---------|------|---------|---------|
| 全参数微调 | 100% | ~94GB | 最好 | 慢 | 大厂、追求极致 |
| LoRA | 0.1~1% | ~28GB | 接近全参 | 快 | 主流选择 |
| QLoRA | 0.1~1% | ~10GB | 略低于LoRA | 中 | 资源有限 |
| Adapter | 1~5% | ~30GB | 略低于LoRA | 中 | 较少使用 |
| Prefix Tuning | <0.1% | ~20GB | 低于LoRA | 快 | 特定场景 |

---

## 六、关键技术考量

### 6.1 超参数选择

```python
# SFT 关键超参数推荐值
sft_hyperparams = {
    # 学习率
    "learning_rate": {
        "full_ft": 2e-5,      # 全参数微调
        "lora": 2e-4,          # LoRA（更大，因为只训练少量参数）
        "qlora": 2e-4,         # QLoRA
    },
    
    # 训练轮数
    "epochs": {
        "general": 2,          # 通用场景
        "domain": 3,           # 领域微调
        "small_data": 5,       # 数据量少时
    },
    
    # Batch Size
    "batch_size": {
        "global": 128,         # 全局 batch（tokens）
        "per_device": 4,       # 单卡 batch
        "gradient_accumulation": 32,  # 梯度累积
    },
    
    # 其他
    "warmup_ratio": 0.03,      # 预热比例
    "weight_decay": 0.0,       # 权重衰减
    "max_grad_norm": 1.0,      # 梯度裁剪
    "lr_scheduler": "cosine",  # 学习率调度
}
```

### 6.2 学习率策略

```
学习率
  ↑
  │     ┌──── 峰值 (2e-5)
  │    ╱  ╲
  │   ╱    ╲
  │  ╱      ╲──── 余弦衰减
  │ ╱            ╲
  │╱ Warmup       ╲──── 最低 (2e-6)
  └───────────────────────────→ 训练步数

关键原则:
  - SFT 学习率 << 预训练学习率（2e-5 vs 3e-4）
  - LoRA 学习率 > 全参数微调（2e-4 vs 2e-5）
    因为 LoRA 只训练少量参数，需要更大的步长
  - Warmup 防止初期训练不稳定
  - Cosine 衰减让后期精细调整
```

### 6.3 数据长度处理

```python
# 序列长度策略
length_strategy = {
    "max_length": 2048,        # 最大序列长度
    "truncation": True,        # 超长截断
    "padding": "longest",      # 填充到 batch 内最长
}

# 长度分布分析（重要！）
# 如果大部分数据 < 512，但少数数据 > 2048
# 策略1: 截断到 2048（可能丢失信息）
# 策略2: 按长度分组，减少 padding 浪费
# 策略3: 动态 batch（短序列用大 batch，长序列用小 batch）

from transformers import LengthGroupedSampler
# Trainer 内置了 length_grouped=True 选项
training_args = TrainingArguments(
    group_by_length=True,      # 按长度分组，减少 padding
    length_column_name="length",
)
```

---

## 七、常见挑战与解决方案

### 7.1 灾难性遗忘

```
问题:
  SFT 后模型"忘记"了预训练阶段学到的知识

  SFT 前: 精通英语、法语、德语、代码、数学...
  SFT 后（只用中文对话数据）: 中文很好，但英语能力下降

解决方案:

  1. 混合通用数据
     SFT 数据 = 50% 领域数据 + 50% 通用数据

  2. 使用 LoRA
     冻结原始权重，不破坏预训练知识
     
  3. 小学习率
     SFT 学习率 << 预训练学习率
     
  4. KL 约束（RLHF 阶段）
     限制模型不偏离 SFT 模型太远
```

### 7.2 过拟合

```
问题:
  SFT 数据量少（如只有几千条），模型记住训练数据但泛化差

  训练集 loss 持续下降，但验证集 loss 上升

解决方案:

  1. 早停（Early Stopping）
     监控验证集 loss，停止在最优点
     
  2. 减少 Epoch
     数据少时 2-3 轮即可，不要过多

  3. Dropout
     LoRA dropout = 0.05~0.1
     
  4. 数据增强
     同一问题多种表述方式
     
  5. 正则化
     Weight Decay + Label Smoothing
```

### 7.3 数据质量不一致

```
问题:
  开源数据集质量参差不齐，有的回答很好，有的很差

  低质量数据会"教坏"模型

解决方案:

  1. 用强模型过滤
     用 GPT-4 对每条数据打分，只保留高质量数据

  2. 多样性去重
     不只精确去重，还要语义去重

  3. 人工抽检
     随机抽取 5~10% 人工审核

  4. 数据清洗流程
     规则过滤 → 模型过滤 → 人工抽检
```

### 7.4 多轮对话训练

```
问题:
  多轮对话如何构造训练样本？

错误做法:
  只训练最后一轮的 assistant 回答

正确做法:
  多轮对话中每个 assistant 回答都应该被训练

  对话: [user1, assistant1, user2, assistant2, user3, assistant3]

  训练样本1: [user1, assistant1]              → 训练 assistant1
  训练样本2: [user1, assistant1, user2, assistant2] → 训练 assistant2
  训练样本3: [user1, assistant1, user2, assistant2, user3, assistant3]
                                           → 训练 assistant3

  或者更高效: 一次前向传播中，每个 assistant 部分都计算 loss
```

---

## 八、典型应用场景

### 8.1 通用对话助手

```yaml
场景: 训练一个通用对话助手（如 ChatGPT）
基座模型: LLaMA-3-8B-Base
SFT 数据: 10万条通用对话数据（多任务）
  - 日常问答: 30%
  - 代码生成: 15%
  - 写作创作: 15%
  - 知识问答: 15%
  - 数学推理: 10%
  - 角色扮演: 5%
  - 安全拒绝: 10%
微调方法: LoRA (r=64)
训练资源: 8×A100-80G
训练时间: ~3小时
```

### 8.2 领域专用模型

```yaml
场景: 训练一个医疗问答助手
基座模型: Qwen-7B-Base
SFT 数据: 5万条医疗问答数据
  - 真实病例问答: 40%
  - 医学知识问答: 30%
  - 用药咨询: 15%
  - 健康建议: 10%
  - 安全拒绝（非医疗问题）: 5%
数据来源:
  - 公开医疗问答数据集
  - 医生审核的人工标注
  - 医学教材内容转换
微调方法: 全参数微调
训练资源: 4×A100-80G
关键考量:
  - 准确性要求极高（错误建议可能危及生命）
  - 必须有医学专家参与数据标注和审核
  - 必须添加免责声明
```

### 8.3 代码助手

```yaml
场景: 训练一个编程助手（如 Copilot）
基座模型: DeepSeek-Coder-6.7B
SFT 数据: 20万条代码问答
  - Python: 30%
  - JavaScript: 25%
  - Java: 20%
  - Go: 10%
  - C++: 10%
  - 其他: 5%
数据特点:
  - 代码必须可运行
  - 包含错误代码 + 修复方案
  - 包含代码解释
  - 包含多文件项目场景
微调方法: LoRA (r=128)  # 代码需要更大的 LoRA rank
特殊处理:
  - 代码缩进必须严格保持
  - 特殊 token 处理（如 <code> </code>）
```

---

## 九、面试高频追问

### Q1: SFT 和 RLHF 的区别是什么？

```
SFT:
  - 数据: 标准问答对（一个正确答案）
  - 目标: 模仿标准回答
  - 方法: 监督学习（交叉熵）
  - 学会: 对话格式、指令遵循

RLHF:
  - 数据: 偏好排序（回答A比回答B好）
  - 目标: 优化人类偏好
  - 方法: 强化学习（PPO/DPO）
  - 学会: 更安全、更自然、更有用

关系: SFT 是 RLHF 的前提
  先 SFT 学会对话 → 再 RLHF 优化质量
```

### Q2: LoRA 的 rank（秩）选择有什么讲究？

```
rank r 的影响:
  r 越大 → 可训练参数越多 → 效果越好，但过拟合风险增加
  r 越小 → 参数越少 → 效果略差，但更高效

经验值:
  r = 8:   通用任务（简单问答）
  r = 16:  中等复杂度（多轮对话）
  r = 64:  复杂任务（代码生成、数学推理）
  r = 128: 高复杂度（需要大量知识修改）

alpha 的选择:
  通常 alpha = 2 × r
  alpha 控制 LoRA 增量的缩放
  更大的 alpha → LoRA 影响更大
```

### Q3: SFT 数据需要多少条才够？

```
经验值:
  1K~5K 条:   可以让模型学会基本对话格式
  10K~50K 条: 达到不错的对话效果
  50K~100K 条: 接近商用水平（如 Alpaca 52K）
  100K+ 条:   高质量模型（如 ChatGPT 估计用了 10万+条）

关键不是数量，而是质量:
  LIMA 论文证明: 1000 条高质量数据 > 52000 条低质量数据
  ("Less Is More for Alignment")

数据质量 > 数据数量
```

### Q4: 如何评估 SFT 的效果？

```
评估方法:
  1. 自动评估
     - 验证集 Loss / Perplexity
     - BLEU / ROUGE（生成质量）
     - Benchmark: MMLU, C-Eval, GSM8K
  
  2. 人工评估
     - 回答质量打分（1-5分）
     - A/B 测试（与基座模型对比）
     - 专家评估（领域准确性）
  
  3. 在线评估
     - 用户满意度（点赞/踩）
     - 留存率
     - 使用频率
```

### Q5: 为什么 SFT 学习率要比预训练小？

```
原因:
  1. 预训练阶段模型从零开始学习，需要大学习率快速收敛
  2. SFT 阶段模型已经学好基础知识，只需微调
     大学习率会破坏预训练学到的知识（灾难性遗忘）
  3. SFT 数据量远小于预训练，大学习率容易过拟合

  预训练 LR: 3e-4
  SFT 全参:  2e-5  （小 15 倍）
  SFT LoRA:  2e-4  （与预训练接近，因为只训练少量参数）
```

---

## 十、总结

### SFT 核心知识图谱

```
监督微调（SFT）
│
├── 定义
│   ├── 在预训练模型上用标注数据进行有监督训练
│   ├── 让模型学会指令遵循和对话格式
│   └── 从"文本补全器"变成"对话助手"
│
├── 原理
│   ├── 自回归语言建模（预测下一个token）
│   ├── 只对 assistant 回答部分计算 loss
│   ├── 学习率 << 预训练学习率
│   └── 本质是激活已有能力 + 格式对齐
│
├── 数据
│   ├── 格式: Alpaca / ShareGPT / ChatML
│   ├── 来源: 人工标注 / 开源 / 自生成 / 领域数据
│   ├── 质量 > 数量（LIMA: 1K高质量 > 52K低质量）
│   └── 配比: 多任务均衡覆盖
│
├── 方法
│   ├── 全参数微调: 效果最好，资源需求大
│   ├── LoRA: 冻结原权重+低秩增量，主流选择
│   └── QLoRA: 量化+LoRA，单卡可跑
│
├── 挑战
│   ├── 灾难性遗忘 → 混合数据 / LoRA / 小学习率
│   ├── 过拟合 → 早停 / Dropout / 少Epoch
│   ├── 数据质量 → 模型过滤 / 人工审核
│   └── 多轮对话 → 每轮assistant都训练
│
└── 应用
    ├── 通用对话助手（多任务SFT）
    ├── 领域专用模型（医疗/法律/金融）
    └── 代码助手（代码SFT）
```

### 面试回答模板（2分钟版）

> 监督微调（SFT）是大模型训练的第二阶段，在预训练基座模型上用人工标注的指令-回答对进行有监督训练，让模型学会遵循指令和对话格式。
>
> **核心原理**是自回归语言建模，但关键区别是只对 assistant 回答部分计算损失，不对用户指令部分计算。学习率通常设为 2e-5，比预训练小一个量级，避免破坏预训练知识。
>
> **数据构建**是 SFT 的关键，数据质量比数量更重要。LIMA 论文证明 1000 条高质量数据效果可以超过 52000 条低质量数据。数据需要覆盖多种任务类型，合理配比。
>
> **微调方法**主要有三种：全参数微调效果最好但资源需求大；LoRA 冻结原始权重只训练低秩增量，是主流选择；QLoRA 在 LoRA 基础上量化基座模型，单卡即可训练。
>
> **主要挑战**包括灾难性遗忘（用混合数据和 LoRA 解决）、过拟合（用早停和 Dropout 解决）、数据质量不一致（用模型过滤+人工审核解决）。
>
> SFT 后的模型已经具备对话能力，但还需要 RLHF/DPO 进一步对齐人类偏好，使其更安全、自然、有用。
