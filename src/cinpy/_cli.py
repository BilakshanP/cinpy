"""CLI entry point for running examples."""

import runpy
import sys
from pathlib import Path


def run_example() -> None:
    if len(sys.argv) < 2:
        examples_dir = Path(__file__).parent.parent.parent / "examples"
        if not examples_dir.exists():
            examples_dir = Path("examples")
        available = sorted(f.stem for f in examples_dir.glob("*.py"))
        print("Usage: cinpy-example <name>")
        print(f"Available: {', '.join(available)}")
        sys.exit(1)

    name = sys.argv[1].removesuffix(".py")
    examples_dir = Path(__file__).parent.parent.parent / "examples"
    if not examples_dir.exists():
        examples_dir = Path("examples")

    target = examples_dir / f"{name}.py"
    if not target.exists():
        print(f"Example '{name}' not found in {examples_dir}")
        sys.exit(1)

    sys.argv = sys.argv[1:]
    runpy.run_path(str(target), run_name="__main__")
