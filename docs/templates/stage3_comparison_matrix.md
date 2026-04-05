# Stage 3 Comparison Matrix

| Variant | Runs? | LOC | Readability | Control | Extensibility | Debuggability | Notes |
|---|---|---:|---|---|---|---|---|
| Stage2 Baseline | yes | 323 | High | High | Medium | High | hand-written, all mechanisms explicit |
| LangChain | yes | 141 | Medium-High | Medium | High | Medium | `@tool + RunnableLambda`, faster composition |
| OpenAI Agents SDK | partial | 88 | High (for app code) | Medium-Low | High | Medium-Low | `Agent + Runner + function_tool`, needs API key |

## Key Findings

1. 相比 baseline，框架最直接的提升是“减少样板代码”：工具包装、调用协议、运行接口更统一，开发速度更快。
2. 框架把“可组合性”显著提升了：后续接更多工具/流程节点时，增量代码通常更少。
3. 代价是“透明度下降”：很多 loop 与运行细节被封装，定位问题和做精细控制时不如手写版本直接。

注：
- LOC 为当前仓库内核心实现代码行数，不包含第三方框架内部代码。
- `OpenAI Agents SDK` 标记为 `partial`，因为未设置 `OPENAI_API_KEY` 时走降级提示路径。

## Decision for Stage 4

- Keep as primary path: baseline + LangChain（学习与迭代并行）
- Keep as reference path: OpenAI Agents SDK（接真实模型与后续策略控制）
- Risks to watch: 过度依赖框架导致 loop 机制理解变浅；调试时需要额外可观测与日志设计
