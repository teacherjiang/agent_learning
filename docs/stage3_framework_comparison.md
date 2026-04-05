# Stage 3: Single-Agent Framework Comparison

目标：在保留 Stage 2 手写实现的前提下，用同一任务实现 1~2 个框架版本，做结构化对比。

## 本阶段核心原则

- Stage 2 baseline 不删除、不覆盖
- 对比任务保持一致（同一输入、同一工具、同一输出目标）
- 不追求大而全，先做最小可对比版本

## 建议对比对象

- Baseline: hand-written minimal agent (Stage 2)
- Candidate A: LangChain
- Candidate B: OpenAI Agents SDK

## 统一对比任务

使用相同任务：
- 输入：天气问题 / 普通问候 / 未知城市
- 工具：`get_weather(city: str)`
- 目标：能够完成工具调用并输出最终答案

## 目录建议

```text
src/stage3/
  baseline_adapter.py
  framework_langchain.py
  framework_openai_agents.py
  run_comparison.py
```

当前状态：
- baseline 已可运行
- LangChain 版本已可运行（使用 `@tool + RunnableLambda`，无真实 LLM API）
- OpenAI Agents SDK 版本仍是占位（下一步实现）

## 对比维度（必须记录）

- 代码量（LOC）
- 可读性（主流程是否直观）
- 可控性（重试、错误处理、状态可见性）
- 可扩展性（新增工具/新增流程的改动成本）
- 调试体验（日志、可观测、定位问题难度）

## 完成标准（Definition of Done）

- 至少 1 个框架版本可以跑通同任务
- 产出对比表（见 `docs/templates/stage3_comparison_matrix.md`）
- 形成结论：框架帮你封装了什么，代价是什么
