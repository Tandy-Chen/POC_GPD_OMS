"""Command-line interface."""

from __future__ import annotations

import argparse
import sys

from .config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR
from .pipeline import run_process, run_validate
from .reader import SourceReadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scope3 GHG CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_cmd = sub.add_parser("validate", help="Validate source file and required columns")
    validate_cmd.add_argument("--input", default=None, help="Path to source Excel file (auto-locate if omitted)")
    validate_cmd.add_argument("--sheet", default="sheet1", help="Source sheet name")
    validate_cmd.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Input directory for auto-locate")

    process_cmd = sub.add_parser("process", help="Generate output workbook")
    process_cmd.add_argument("--input", default=None, help="Path to source Excel file (auto-locate if omitted)")
    process_cmd.add_argument("--sheet", default="sheet1", help="Source sheet name")
    process_cmd.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR), help="Input directory for auto-locate")
    process_cmd.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        try:
            summary = run_validate(input_path=args.input, sheet_name=args.sheet, input_dir=args.input_dir)
        except SourceReadError as exc:
            print(f"[ERROR] {exc}")
            return 2

        print("[OK] Source validation passed")
        print(f"source_rows={summary.source_rows}")
        print(f"valid_rows={summary.valid_rows}")
        return 0

    if args.command == "process":
        try:
            summary = run_process(
                input_path=args.input,
                sheet_name=args.sheet,
                input_dir=args.input_dir,
                output_dir=args.output_dir,
            )
        except SourceReadError as exc:
            print(f"[ERROR] {exc}")
            return 2

        print("[OK] Output workbook generated")
        print(f"source_path={summary['source_path']}")
        print(f"source_snapshot_sheet={summary['source_snapshot_sheet']}")
        print(f"output_file={summary['output_file']}")
        print(f"rows_processed={summary['rows_processed']}")
        print(f"sheet_names={','.join(summary['sheet_names'])}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
