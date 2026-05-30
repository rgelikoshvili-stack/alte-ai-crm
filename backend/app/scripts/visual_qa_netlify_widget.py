from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
VISUAL_QA_DIR = PROJECT_ROOT / "docs" / "deployment" / "visual_qa"
DEFAULT_URL = "https://nimble-croissant-2f66e8.netlify.app/join.html"


def _safe_name(label: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label.lower())


def _load_playwright():
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, exc
    return sync_playwright, None


def _write_result(result: dict[str, Any]) -> None:
    target = VISUAL_QA_DIR / "phase_9ab_visual_qa_result.json"
    try:
        target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except PermissionError as exc:  # pragma: no cover - local environment dependent
        result["artifact_write_status"] = "FAILED_PERMISSION_DENIED"
        result["artifact_write_error"] = str(exc)


def _evaluate_page(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """
        () => {
          const root = document.getElementById('alte-chat-widget-root')
            || document.getElementById('alte-chat-widget-container')
            || document.querySelector('[data-alte-widget-variant]');
          const iframe = document.querySelector('iframe[title="Alte AI Chatbot"]');
          const outer = {
            windowInnerWidth: window.innerWidth,
            documentScrollWidth: document.documentElement.scrollWidth,
            bodyScrollWidth: document.body ? document.body.scrollWidth : 0,
            rootScrollWidth: root ? root.scrollWidth : null,
            iframeVisible: !!iframe,
            iframeWidth: iframe ? iframe.getBoundingClientRect().width : null,
            rootVisible: root ? root.getBoundingClientRect().width > 0 : false,
          };
          let inner = null;
          try {
            const doc = iframe && iframe.contentDocument;
            const win = iframe && iframe.contentWindow;
            const modal = doc && doc.querySelector('.cw-win');
            const launcher = doc && doc.querySelector('.alte-launcher, .cw-win');
            inner = {
              windowInnerWidth: win ? win.innerWidth : null,
              documentScrollWidth: doc ? doc.documentElement.scrollWidth : null,
              bodyScrollWidth: doc && doc.body ? doc.body.scrollWidth : null,
              modalVisible: modal ? modal.getBoundingClientRect().width > 0 : false,
              modalWidth: modal ? modal.getBoundingClientRect().width : null,
              launcherOrModalVisible: launcher ? launcher.getBoundingClientRect().width > 0 : false,
            };
          } catch (err) {
            inner = { error: 'iframe_inaccessible' };
          }
          return { outer, inner };
        }
        """
    )


def _passes(metrics: dict[str, Any]) -> bool:
    outer = metrics.get("outer") or {}
    inner = metrics.get("inner") or {}
    outer_width = outer.get("windowInnerWidth") or 0
    outer_ok = (
        outer.get("documentScrollWidth", 999999) <= outer_width + 1
        and outer.get("bodyScrollWidth", 999999) <= outer_width + 1
        and outer.get("iframeVisible") is True
    )
    inner_width = inner.get("windowInnerWidth") or outer_width
    inner_ok = (
        inner.get("documentScrollWidth", 999999) <= inner_width + 1
        and inner.get("bodyScrollWidth", 999999) <= inner_width + 1
        and inner.get("launcherOrModalVisible") is True
    )
    return bool(outer_ok and inner_ok)


def run_visual_qa(url: str = DEFAULT_URL) -> dict[str, Any]:
    sync_playwright, import_error = _load_playwright()
    VISUAL_QA_DIR.mkdir(parents=True, exist_ok=True)
    if sync_playwright is None:
        result = {
            "status": "PLAYWRIGHT_UNAVAILABLE",
            "url": url,
            "reason": str(import_error),
            "manual_steps": [
                "Open the URL in desktop viewport 1440x900 and confirm no horizontal scroll.",
                "Open the URL in mobile viewport 430x932 and confirm no horizontal scroll or cropped right edge.",
                "Confirm header, messages, source chips/cards, and composer are visible.",
            ],
        }
        _write_result(result)
        print(json.dumps(result, indent=2))
        return result

    viewports = [
        ("desktop_1440x900", 1440, 900),
        ("mobile_430x932", 430, 932),
    ]
    result: dict[str, Any] = {"status": "PASSED", "url": url, "checks": []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for label, width, height in viewports:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(url, wait_until="networkidle", timeout=60_000)
                page.wait_for_selector("iframe[title='Alte AI Chatbot']", timeout=30_000)
                page.wait_for_timeout(3_000)
                screenshot = VISUAL_QA_DIR / f"netlify_widget_{_safe_name(label)}_phase_9ab.png"
                page.screenshot(path=str(screenshot), full_page=True)
                metrics = _evaluate_page(page)
                passed = _passes(metrics)
                result["checks"].append(
                    {
                        "label": label,
                        "viewport": {"width": width, "height": height},
                        "passed": passed,
                        "screenshot": str(screenshot.relative_to(PROJECT_ROOT)),
                        "metrics": metrics,
                    }
                )
                page.close()
        finally:
            browser.close()

    if not all(check["passed"] for check in result["checks"]):
        result["status"] = "FAILED"
    _write_result(result)
    print(json.dumps(result, indent=2))
    if result["status"] == "FAILED":
        raise SystemExit(1)
    return result


def main() -> None:
    run_visual_qa(os.environ.get("ALTE_WIDGET_QA_URL", DEFAULT_URL))


if __name__ == "__main__":
    main()
