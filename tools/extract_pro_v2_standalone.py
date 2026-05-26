from __future__ import annotations

import base64
import gzip
import json
import re
import zlib
from html import unescape
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_pro_v2_widget" / "Alte_AI_Chat_Pro_v2_standalone.html"
OUT = PROJECT_ROOT / "docs" / "knowledge_evidence" / "uploaded_pro_v2_widget" / "extracted"


def extract_script(text: str, script_type: str) -> str | None:
    pattern = re.compile(
        rf"<script[^>]+type=[\"']{re.escape(script_type)}[\"'][^>]*>(.*?)</script>",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def safe_json_loads(raw: str | None, fallback: Any) -> Any:
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def decode_asset(entry: dict[str, Any]) -> bytes | None:
    for key in ["data", "content", "bytes", "source"]:
        value = entry.get(key)
        if isinstance(value, str):
            raw = value
            if "," in raw and raw[:80].lower().startswith("data:"):
                raw = raw.split(",", 1)[1]
            try:
                data = base64.b64decode(raw)
            except Exception:
                continue
            compression = str(entry.get("compression") or entry.get("encoding") or "").lower()
            if "deflate" in compression or "zlib" in compression:
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    pass
            if "gzip" in compression or data.startswith(b"\x1f\x8b"):
                try:
                    data = gzip.decompress(data)
                except (OSError, EOFError):
                    pass
            return data
    return None


def classify_asset(name: str, mime: str, text: str) -> str:
    lower = f"{name} {mime}".lower()
    if "css" in lower or re.search(r"\.[mc]?css($|\?)", lower):
        return "css"
    if "javascript" in lower or re.search(r"\.[mc]?[jt]sx?($|\?)", lower):
        return "js"
    if "<style" in text or "{--" in text:
        return "css"
    if "function " in text or "const " in text or "React" in text or "window." in text:
        return "js"
    return "text"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source_text = SOURCE.read_text(encoding="utf-8", errors="replace")
    manifest = safe_json_loads(extract_script(source_text, "__bundler/manifest"), {})
    template = safe_json_loads(extract_script(source_text, "__bundler/template"), "")
    ext_resources = safe_json_loads(extract_script(source_text, "__bundler/ext_resources"), [])

    extracted_assets: list[dict[str, Any]] = []
    text_chunks: list[str] = []
    css_chunks: list[str] = []
    js_chunks: list[str] = []

    if isinstance(template, str):
        (OUT / "extracted_template.html").write_text(template, encoding="utf-8")
        text_chunks.append(template)
    else:
        (OUT / "extracted_template.html").write_text("", encoding="utf-8")

    if isinstance(manifest, dict):
        for uuid, entry in manifest.items():
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name") or entry.get("filename") or uuid)
            mime = str(entry.get("type") or entry.get("mime") or entry.get("mimeType") or "")
            asset_bytes = decode_asset(entry)
            asset_info: dict[str, Any] = {
                "uuid": uuid,
                "name": name,
                "mime": mime,
                "keys": sorted(entry.keys()),
                "decoded": asset_bytes is not None,
                "size": len(asset_bytes) if asset_bytes else None,
            }
            if asset_bytes is not None:
                suffix = Path(name).suffix or ".bin"
                safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{uuid}_{Path(name).name}")[:140]
                if "." not in safe_name:
                    safe_name += suffix
                asset_path = OUT / "assets" / safe_name
                asset_path.parent.mkdir(exist_ok=True)
                asset_path.write_bytes(asset_bytes)
                asset_info["output"] = str(asset_path.relative_to(PROJECT_ROOT))
                try:
                    asset_text = asset_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    asset_text = ""
                if asset_text:
                    asset_kind = classify_asset(name, mime, asset_text)
                    asset_info["kind"] = asset_kind
                    text_chunks.append(f"\n\n===== ASSET {uuid} {name} =====\n{asset_text}")
                    if asset_kind == "css":
                        css_chunks.append(f"\n/* {uuid} {name} */\n{asset_text}")
                    elif asset_kind == "js":
                        js_chunks.append(f"\n/* {uuid} {name} */\n{asset_text}")
            extracted_assets.append(asset_info)

    text_index = "\n".join(text_chunks)
    (OUT / "extracted_text_index.txt").write_text(text_index, encoding="utf-8")
    (OUT / "extracted_styles.css").write_text("\n".join(css_chunks), encoding="utf-8")
    (OUT / "extracted_app.js").write_text("\n".join(js_chunks), encoding="utf-8")
    (OUT / "extracted_asset_list.json").write_text(json.dumps(extracted_assets, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "source": str(SOURCE.relative_to(PROJECT_ROOT)),
        "has_manifest": isinstance(manifest, dict) and bool(manifest),
        "has_template": isinstance(template, str) and bool(template),
        "manifest_asset_count": len(manifest) if isinstance(manifest, dict) else 0,
        "decoded_asset_count": sum(1 for item in extracted_assets if item.get("decoded")),
        "external_resource_count": len(ext_resources) if isinstance(ext_resources, list) else 0,
        "outputs": [
            "extracted_template.html",
            "extracted_app.js",
            "extracted_styles.css",
            "extracted_manifest_summary.json",
            "extracted_text_index.txt",
            "extracted_asset_list.json",
        ],
        "limitations": [
            "No uploaded JavaScript was executed.",
            "Some bundled assets may remain binary or minified.",
            "Functional behavior is inferred from extracted readable text and source scanning.",
        ],
    }
    (OUT / "extracted_manifest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
