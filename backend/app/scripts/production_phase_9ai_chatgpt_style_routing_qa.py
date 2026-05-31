from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from app.scripts.production_phase_9ai_clarification_routing_qa import (
    BACKEND_URL,
    CASES,
    ORIGIN,
    run_case,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = PROJECT_ROOT / "docs" / "evaluation" / "PHASE_9AI_CHATGPT_STYLE_ROUTING_QA_RESULT.md"


def write_report(results: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for item in results if item["passed"])
    lines = [
        "# Phase 9AI ChatGPT-Style Routing QA Result",
        "",
        f"Backend URL: {BACKEND_URL}",
        f"Origin: {ORIGIN}",
        f"Total: {len(results)}",
        f"Passed: {passed}",
        f"Failed: {len(results) - passed}",
        "No real contact details sent: YES",
        "Lead/task/customer created intentionally: NO",
        "",
        "| Case | Route | Source group | Clarification | Answer status | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in results:
        lines.append(
            f"| {item['name']} | {item.get('route')} | {item.get('source_group')} | "
            f"{item.get('clarification_needed')} | {item.get('answer_status')} | "
            f"{'PASS' if item['passed'] else 'FAIL'} |"
        )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results = []
    for case in CASES:
        results.append(run_case(case))
        time.sleep(0.1)
    write_report(results)
    payload = {
        "status": "PASSED" if all(item["passed"] for item in results) else "FAILED",
        "total": len(results),
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
        "report": str(REPORT_PATH),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
