# Stage 3 学习指南：框架到底帮你省了什么

这份文档不是 API 手册，而是“怎么学”的路线。

目标：
- 看清楚框架做了哪些封装
- 看清楚它省了你哪些手写代码
- 看清楚代价（黑盒程度、可控性、调试成本）

## 先对齐对比对象

当前仓库里有三种实现路径：

1. Stage 2 Baseline（手写）
- 代码位置：`src/agent_learning/*`
- 特点：所有机制都能直接看到

2. LangChain 版本
- 代码位置：`src/stage3/framework_langchain.py`
- 关键抽象：`@tool`、`RunnableLambda`

3. OpenAI Agents SDK 版本
- 代码位置：`src/stage3/framework_openai_agents.py`
- 关键抽象：`Agent`、`Runner.run_sync`、`@function_tool`

## 框架“用了什么”

### LangChain 版用了什么

- `@tool`
  - 把普通函数包装成工具对象，自动生成工具描述与参数结构
- `RunnableLambda`
  - 用统一 Runnable 接口承载 planner/decision 步骤

你省下了：
- 工具包装样板代码
- 工具调用接口统一的胶水层

你付出的代价：
- 需要理解 Runnable 抽象
- 出问题时要沿着框架对象定位

### OpenAI Agents SDK 版用了什么

- `Agent`
  - 把指令、工具、模型绑定成一个可运行 Agent
- `Runner.run_sync`
  - 负责多轮运行与工具回灌循环
- `@function_tool`
  - 把 Python 函数显式注册成工具

你省下了：
- 手写 loop 中的部分编排细节
- 工具调用/回灌的一部分样板控制代码

你付出的代价：
- 需要 API key 与模型可用性
- 运行过程部分细节由 SDK 管理，透明度低于手写 baseline

## “怎么学”建议顺序（务必按顺序）

1. 先用 baseline 复盘一次 loop
- 命令：`PYTHONPATH=src python3 -m stage3.run_comparison baseline "What's the weather in Tokyo?"`
- 你要回答：每轮状态如何变化？什么时候 stop？

2. 再看 LangChain
- 命令：`PYTHONPATH=src python3 -m stage3.run_comparison langchain "What's the weather in Tokyo?"`
- 你要回答：哪些代码不见了？是被谁封装了？

3. 再看 OpenAI Agents SDK
- 命令：`PYTHONPATH=src python3 -m stage3.run_comparison openai_agents "What's the weather in Tokyo?"`
- 如果未配置 key，会得到学习提示；配置后可跑真实调用
- 你要回答：Runner 帮你管理了哪些循环细节？你还能控制哪些边界？

4. 填对比矩阵
- 文件：`docs/templates/stage3_comparison_matrix.md`
- 至少填：可读性、可控性、调试体验三列

## 一条非常实用的判断标准

当你考虑“要不要上框架”时，先问三件事：

1. 当前团队更缺“开发速度”还是“透明可控”？
2. 这个阶段主要是“验证想法”还是“做稳定系统”？
3. 出问题时，你能不能快速定位到哪一层？

如果你还在学习阶段：
- 永远先保留 baseline
- 再把框架版本当作“增量层”去理解

## 本仓库当前结论（阶段性）

- Baseline：最透明，最适合理解机制
- LangChain：上手快，适合快速组织流程
- OpenAI Agents SDK：Agent 原语更聚焦，适合后续接真实模型与策略控制

下一步推荐：
- 先把 OpenAI Agents SDK 跑通真实 key
- 然后开始 Stage 4（workflow/orchestration）

## 常见易混点（基于本仓库实战）

1. `tool schema` 不在 `schemas.py`
- 在本仓库里，工具参数 schema 在 `src/agent_learning/tools.py`（`parameters_schema`）。
- `schemas.py` 主要定义模型动作和运行结果的数据结构。

2. `scratchpad` 不只是“中间结果”
- 概念上它是可被后续轮次读取的工作记忆区。
- 当前示例只写了 `last_tool_result`，是最小实现，不是能力上限。

3. “未知工具是否会直接崩溃？”
- 不会。主循环会先按未知工具分支记录失败，再进入下一轮决策。
- 即便异常抛出也在主循环 `try/except` 中被接住并写入 state。
