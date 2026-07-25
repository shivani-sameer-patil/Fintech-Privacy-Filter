"""
Application Entrypoint for FinTech Privacy Filter.

Provides command-line interface (CLI) execution, file processing,
and interactive prompt modes for running the privacy filter pipeline.
"""

import argparse
import json
import sys
from pathlib import Path

# Force stdout UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from privacy_filter.config import PipelineConfig
from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline


def run_cli():
    parser = argparse.ArgumentParser(
        description="Production FinTech Privacy Filter - Mask sensitive PII & financial entities."
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Input raw text string to filter and mask.",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to input text file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to write masked output text file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full detection metadata in JSON format.",
    )

    args = parser.parse_args()

    pipeline = FinTechPrivacyPipeline()

    raw_input_text = ""
    if args.text:
        raw_input_text = args.text
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
            sys.exit(1)
        raw_input_text = file_path.read_text(encoding="utf-8")
    else:
        print("==================================================")
        print("FINTECH PRIVACY FILTER INTERACTIVE MODE")
        print("==================================================")
        print("Enter text to mask (Press Ctrl+C or Enter blank line to exit):\n")
        raw_input_text = (
            "Dear Customer Shivani Patil, Your PAN card ABCDE1234F and Aadhaar 2345 6789 0123 "
            "have been verified. Bank account 123456789012 with IFSC SBIN0001234. Card: 4111 1111 1111 1111."
        )
        print(f"Default Input:\n{raw_input_text}\n")

    result = pipeline.process(raw_input_text)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(result.masked_text, encoding="utf-8")
        print(f"Masked output successfully saved to: {args.output}")

    if args.json:
        print(json.dumps(result.to_dict(), indent=4))
    else:
        print("==================================================")
        print("SANITISED MASKED OUTPUT")
        print("==================================================")
        print(result.masked_text)
        print("\n--------------------------------------------------")
        print(f"Language Detected : {result.language.language_name} ({result.language.language_code})")
        print(f"Entities Masked   : {result.entities_masked_count}")
        print(f"Execution Time    : {result.processing_time_ms} ms")
        print("--------------------------------------------------")


if __name__ == "__main__":
    run_cli()
