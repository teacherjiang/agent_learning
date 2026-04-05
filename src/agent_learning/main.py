import json
import sys

from .agent import MinimalAgent


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m agent_learning.main "<your question>"')
        sys.exit(1)

    user_input = sys.argv[1]
    agent = MinimalAgent()
    result = agent.run(user_input)

    print(
        json.dumps(
            {
                "success": result.success,
                "final_answer": result.final_answer,
                "end_reason": result.end_reason,
                "loops": result.loops,
                "trace": result.trace,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
