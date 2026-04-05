# Stage 2: Minimal Agent (Hand-Written)

## 什么是最小 Agent 闭环

最小闭环可以概括为：

1. 接收用户输入
2. 调用模型获取下一步动作
3. 若动作为工具调用，则执行工具并回灌结果
4. 再次调用模型
5. 直到得到最终答案或触发停止条件

这套机制就是后续大型框架封装的核心。

## 代码映射

- 模型：`src/agent_learning/llm.py`
- 工具列表与 schema：`src/agent_learning/tools.py`
- 结构化动作 schema：`src/agent_learning/schemas.py`
- Agent loop：`src/agent_learning/agent.py`
- stop condition：`src/agent_learning/agent.py`
- state / scratchpad：`src/agent_learning/state.py`
- error handling / retry：`src/agent_learning/agent.py`
- logging：`src/agent_learning/logger.py`

## 本阶段如何体现关键学习点

1. 模型输出结构化结果
- `action="final_answer"`：直接结束
- `action="tool_call"`：触发工具执行

2. 工具 schema
- `get_weather(city: str)` 的 schema 显式定义在工具注册表中。

3. 状态推进而非“失忆”
- `AgentState` 保存轮次、步骤、工具调用记录、工具结果与最终回答。

4. 停止条件
- 得到最终答案则停止
- 超过最大循环次数则停止
- 工具失败次数超过上限则停止

5. 错误处理与重试
- 工具名不存在
- 参数校验失败
- 工具执行异常
- 限制最大重试次数，防止无限重试

6. 日志
- 每轮记录 action 类型
- 记录工具调用及结果
- 记录结束原因

## 为什么这还不是生产级 Agent

- 使用 mock LLM，不具备真实模型能力
- 只有单工具和简单 schema
- 无并发、无权限隔离、无外部可观测平台
- 测试覆盖有限，缺乏评估数据集与回归基线

## 后续最自然升级方向

1. 替换真实 LLM API（保留相同动作结构）
2. 增加多工具与更严格参数 schema
3. 引入更完整的 tracing 与评估
4. 从单 loop 发展到 workflow / orchestration
5. 再进入多 Agent 与协议层实践
