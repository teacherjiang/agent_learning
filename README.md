# Agent Learning Repo

这是一个长期演进的 Agent 学习仓库，用来系统记录从“手写最小 Agent”到后续多阶段工程化能力的学习过程。

## 仓库目标

1. 作为专用 Agent 学习代码库
2. 每个阶段都有可运行、可复盘的代码与文档
3. 当前完成阶段 2：手写最小 Agent
4. 后续阶段在同一仓库持续迭代

## 当前进度

- 已完成：**Stage 2 - Hand-Written Minimal Agent**

## Stage 2 学什么

- 最小闭环：模型、工具列表、循环、停止条件
- 工具 schema
- 状态 / scratchpad
- 重试与错误处理
- 日志记录
- 结构化输出
- 工具结果回灌模型上下文

## 这个最小 Agent Demo 演示了什么

- 模型输出结构化动作：`final_answer` 或 `tool_call`
- Agent loop 根据动作决定是否调用工具
- 工具调用前做参数校验，异常可重试
- 工具结果写入 state/scratchpad 后再次调用模型
- 显式 stop condition 防止无限循环

## 如何运行

1. 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

2. 运行示例

```bash
PYTHONPATH=src python3 -m agent_learning.main "What's the weather in Tokyo?"
PYTHONPATH=src python3 -m agent_learning.main "Hello"
PYTHONPATH=src python3 -m agent_learning.main "What's the weather in Mars?"
```

3. 运行测试

```bash
PYTHONPATH=src pytest -q
```

## 项目结构

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── roadmap.md
│   └── stage2_minimal_agent.md
├── src/
│   └── agent_learning/
│       ├── __init__.py
│       ├── main.py
│       ├── agent.py
│       ├── llm.py
│       ├── tools.py
│       ├── schemas.py
│       ├── state.py
│       ├── logger.py
│       └── utils.py
├── examples/
│   └── stage2_demo_inputs.txt
└── tests/
    └── test_stage2_basic.py
```

## 后续如何扩展

后续阶段会在当前结构上演进，而不是推倒重来：

- `llm.py`：替换 mock 为真实 LLM API 客户端
- `tools.py`：扩展更多工具与 schema
- `state.py`：增加更完整的会话记忆和任务状态
- `agent.py`：从单 Agent loop 扩展到 workflow / orchestration / multi-agent
