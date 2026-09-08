from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from cc3d.core.CompiledSteppableAutoCompiler import (
    compile_project_steppables,
    format_compiled_steppable_summary,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile C++ steppables declared by a CompuCell3D .cc3d project."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to the .cc3d project file.",
    )
    parser.add_argument(
        "--result-json",
        required=True,
        help="Path where the structured compile result should be written.",
    )
    parser.add_argument(
        "--build-type",
        choices=("Debug", "Release", "RelWithDebInfo"),
        default="RelWithDebInfo",
        help="Compiler configuration. Default: RelWithDebInfo.",
    )
    return parser


def _write_result(result_path: Path, result: dict) -> None:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    result_path = Path(args.result_json)

    try:
        summary = compile_project_steppables(args.project, build_type=args.build_type)
        result = {
            "success": summary.success,
            "summary": summary.to_dict(),
            "formatted_summary": format_compiled_steppable_summary(summary),
        }
    except BaseException as e:
        result = {
            "success": False,
            "summary": None,
            "formatted_summary": traceback.format_exc(),
            "error": str(e),
        }

    _write_result(result_path, result)
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
