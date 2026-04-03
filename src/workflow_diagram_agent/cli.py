from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .generator import build_executive_workflow_diagram


def _read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.input_file:
        return Path(args.input_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide --text, --input-file, or pipe text over stdin.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an executive-level Mermaid workflow diagram from pasted text."
    )
    parser.add_argument("--text", help="Raw workflow description text.")
    parser.add_argument("--input-file", help="Path to a text file containing workflow notes.")
    parser.add_argument("--max-steps", type=int, default=6, help="Maximum number of executive steps.")
    args = parser.parse_args()

    text = _read_input_text(args).strip()
    if not text:
        raise SystemExit("Input text is empty.")

    diagram = build_executive_workflow_diagram(text=text, max_steps=args.max_steps)
    print(diagram)


if __name__ == "__main__":
    main()
