from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
VISUAL_QA_DIR = PROJECT_ROOT / "docs" / "deployment" / "visual_qa"
DEFAULT_URL = "https://nimble-croissant-2f66e8.netlify.app/join.html"
GEORGIAN_TEST_QUESTION = "როგორ ჩავაბარო ბაკალავრიატზე?"


def _safe_name(label: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label.lower())


def _load_playwright():
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, exc
    return sync_playwright, None


def _write_result(result: dict[str, Any]) -> None:
    url = str(result.get("url") or "")
    stem = "phase_9ab_visual_qa_result_local" if "127.0.0.1" in url or "localhost" in url else "phase_9ab_visual_qa_result_netlify"
    target = VISUAL_QA_DIR / f"{stem}.json"
    latest = VISUAL_QA_DIR / "phase_9ab_visual_qa_result.json"
    try:
        payload = json.dumps(result, indent=2)
        for path in [target, latest]:
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(payload, encoding="utf-8")
            tmp.replace(path)
    except OSError as exc:  # pragma: no cover - local environment dependent
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
            const sidebar = doc && doc.querySelector('.cw-side');
            const header = doc && doc.querySelector('.cw-hdr');
            const composer = doc && doc.querySelector('.cw-comp');
            const launcher = doc && doc.querySelector('.alte-launcher, .cw-win');
            const sidebarStyle = sidebar ? win.getComputedStyle(sidebar) : null;
            inner = {
              windowInnerWidth: win ? win.innerWidth : null,
              windowInnerHeight: win ? win.innerHeight : null,
              documentScrollWidth: doc ? doc.documentElement.scrollWidth : null,
              bodyScrollWidth: doc && doc.body ? doc.body.scrollWidth : null,
              modalVisible: modal ? modal.getBoundingClientRect().width > 0 : false,
              modalWidth: modal ? modal.getBoundingClientRect().width : null,
              modalRight: modal ? modal.getBoundingClientRect().right : null,
              modalLeft: modal ? modal.getBoundingClientRect().left : null,
              sidebarVisible: sidebar
                ? sidebarStyle.display !== 'none'
                  && sidebarStyle.visibility !== 'hidden'
                  && sidebar.getBoundingClientRect().width > 1
                : false,
              headerVisible: header ? header.getBoundingClientRect().height > 0 : false,
              composerVisible: composer ? composer.getBoundingClientRect().height > 0 : false,
              launcherOrModalVisible: launcher ? launcher.getBoundingClientRect().width > 0 : false,
            };
          } catch (err) {
            inner = { error: 'iframe_inaccessible' };
          }
          return { outer, inner };
        }
        """
    )


def _run_georgian_encoding_check(page: Any) -> dict[str, Any]:
    try:
        page.evaluate(
            """
            (question) => {
              const iframe = document.querySelector('iframe[title="Alte AI Chatbot"]');
              const doc = iframe && iframe.contentDocument;
              const textarea = doc && doc.querySelector('textarea');
              const send = doc && doc.querySelector('button.send');
              if (!textarea || !send) throw new Error('composer_not_found');
              textarea.focus();
              textarea.value = question;
              textarea.dispatchEvent(new Event('input', { bubbles: true }));
              send.click();
            }
            """,
            GEORGIAN_TEST_QUESTION,
        )
        page.wait_for_function(
            """
            () => {
              const iframe = document.querySelector('iframe[title="Alte AI Chatbot"]');
              const doc = iframe && iframe.contentDocument;
              const text = doc && doc.body ? doc.body.innerText || '' : '';
              return text.includes('როგორ') && (text.match(/[\u10A0-\u10FF]/g) || []).length >= 10;
            }
            """,
            timeout=45_000,
        )
        text = page.evaluate(
            """
            () => {
              const iframe = document.querySelector('iframe[title="Alte AI Chatbot"]');
              const doc = iframe && iframe.contentDocument;
              return doc && doc.body ? doc.body.innerText || '' : '';
            }
            """
        )
        has_mojibake = "áƒ" in text
        georgian_count = len([ch for ch in text if "\u10a0" <= ch <= "\u10ff"])
        return {
            "ran": True,
            "passed": not has_mojibake and georgian_count >= 10,
            "hasMojibake": has_mojibake,
            "georgianCharacterCount": georgian_count,
            "containsQuestion": GEORGIAN_TEST_QUESTION in text,
            "visibleTextExcerpt": text[:500],
        }
    except Exception as exc:  # pragma: no cover - browser/runtime dependent
        return {
            "ran": True,
            "passed": False,
            "error": str(exc)[:240],
        }


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
    modal_right = inner.get("modalRight")
    modal_left = inner.get("modalLeft")
    inner_ok = (
        inner.get("documentScrollWidth", 999999) <= inner_width + 1
        and inner.get("bodyScrollWidth", 999999) <= inner_width + 1
        and inner.get("launcherOrModalVisible") is True
        and inner.get("headerVisible") is True
        and inner.get("composerVisible") is True
        and (modal_left is None or modal_left >= -1)
        and (modal_right is None or modal_right <= inner_width + 1)
    )
    return bool(outer_ok and inner_ok)


def _mobile_passes(metrics: dict[str, Any]) -> bool:
    inner = metrics.get("inner") or {}
    return _passes(metrics) and inner.get("sidebarVisible") is False


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
        ("mobile_390x844", 390, 844),
        ("mobile_375x667", 375, 667),
    ]
    artifact_prefix = "local_widget" if "127.0.0.1" in url or "localhost" in url else "netlify_widget"
    result: dict[str, Any] = {"status": "PASSED", "url": url, "checks": []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for label, width, height in viewports:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(url, wait_until="networkidle", timeout=60_000)
                page.wait_for_selector("iframe[title='Alte AI Chatbot']", timeout=30_000)
                page.wait_for_timeout(3_000)
                screenshot = VISUAL_QA_DIR / f"{artifact_prefix}_{_safe_name(label)}_phase_9ab.png"
                page.screenshot(path=str(screenshot), full_page=True)
                metrics = _evaluate_page(page)
                encoding_check = None
                if label in {"desktop_1440x900", "mobile_430x932"}:
                    encoding_check = _run_georgian_encoding_check(page)
                passed = _mobile_passes(metrics) if label.startswith("mobile_") else _passes(metrics)
                if encoding_check is not None:
                    passed = passed and encoding_check.get("passed") is True
                result["checks"].append(
                    {
                        "label": label,
                        "viewport": {"width": width, "height": height},
                        "passed": passed,
                        "screenshot": str(screenshot.relative_to(PROJECT_ROOT)),
                        "metrics": metrics,
                        "georgianEncodingCheck": encoding_check,
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
