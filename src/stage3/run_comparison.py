import json
import sys

from .baseline_adapter import run_baseline
from .framework_langchain import run_langchain_variant
from .framework_openai_agents import run_openai_agents_variant


SUPPORTED = {
    "baseline": run_baseline,
    "langchain": run_langchain_variant,
    "openai_agents": run_openai_agents_variant,
}


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "Usage: python -m stage3.run_comparison "
            "<baseline|langchain|openai_agents> \"<input>\""
        )
        raise SystemExit(1)

    variant = sys.argv[1]
    user_input = sys.argv[2]

    if variant not in SUPPORTED:
        print(f"Unsupported variant: {variant}")
        raise SystemExit(1)

    output = SUPPORTED[variant](user_input)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
