from agent_learning.agent import MinimalAgent


def run_baseline(user_input: str) -> dict:
    """Adapter to run the Stage 2 baseline with a Stage 3-compatible output shape."""
    result = MinimalAgent().run(user_input)
    return {
        "variant": "stage2_baseline",
        "success": result.success,
        "final_answer": result.final_answer,
        "end_reason": result.end_reason,
        "loops": result.loops,
    }
