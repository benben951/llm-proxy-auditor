from __future__ import annotations

import argparse
import os
from pathlib import Path

from .client import OpenAICompatClient
from .probes import PROBE_NAMES, run_all_probes
from .report import write_json_report, write_markdown_report
from .scoring import score_results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="proxy-auditor", description="Audit OpenAI-compatible LLM proxies.")
    sub = parser.add_subparsers(dest="command", required=True)

    list_probes = sub.add_parser("list-probes", help="List probes included in this version.")
    list_probes.set_defaults(handler=run_list_probes)

    audit = sub.add_parser("audit", help="Run proxy trust probes.")
    audit.add_argument("--base-url", required=True, help="OpenAI-compatible base URL, for example https://host/v1")
    audit.add_argument("--api-key", default=os.getenv("PROXY_API_KEY"), help="API key. Defaults to PROXY_API_KEY.")
    audit.add_argument("--model", required=True, help="Model name to test.")
    audit.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    audit.add_argument("--out", default="trust_report.md", help="Markdown report path.")
    audit.add_argument("--json-out", default="trust_report.json", help="JSON report path.")
    audit.add_argument(
        "--fail-on",
        choices=["medium", "high", "critical", "never"],
        default="high",
        help="Exit non-zero at or above this risk level. Defaults to high.",
    )
    audit.add_argument("--reference-base-url", help="Optional reference OpenAI-compatible base URL.")
    audit.add_argument("--reference-api-key", default=os.getenv("REFERENCE_API_KEY"), help="Reference API key.")
    audit.add_argument("--reference-model", help="Reference model. Defaults to --model.")
    audit.set_defaults(handler=run_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def run_list_probes(args: argparse.Namespace) -> int:
    del args
    for name in PROBE_NAMES:
        print(name)
    return 0


def run_audit(args: argparse.Namespace) -> int:
    if not args.api_key:
        raise SystemExit("--api-key is required or set PROXY_API_KEY.")

    client = OpenAICompatClient(args.base_url, args.api_key, args.model, timeout=args.timeout)
    reference_client = None
    if args.reference_base_url:
        if not args.reference_api_key:
            raise SystemExit("--reference-api-key is required when --reference-base-url is set.")
        reference_client = OpenAICompatClient(
            args.reference_base_url,
            args.reference_api_key,
            args.reference_model or args.model,
            timeout=args.timeout,
        )

    results = run_all_probes(client, reference_client)
    summary = score_results(results)
    write_markdown_report(Path(args.out), base_url=args.base_url, model=args.model, results=results, summary=summary)
    write_json_report(Path(args.json_out), base_url=args.base_url, model=args.model, results=results, summary=summary)

    print(f"Overall risk: {summary.level} ({summary.score}/{summary.max_score})")
    print(f"Agent recommendation: {summary.agent_recommendation}")
    print(f"Markdown report: {args.out}")
    print(f"JSON report: {args.json_out}")
    return 1 if _should_fail(summary.level, args.fail_on) else 0


def _should_fail(level: str, fail_on: str) -> bool:
    if fail_on == "never":
        return False
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    threshold = order[fail_on.upper()]
    return order[level] >= threshold


if __name__ == "__main__":
    raise SystemExit(main())
