from __future__ import annotations

import hashlib
import ipaddress
import re
import socket
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from app.schemas.knowledge import (
    WebsiteApprovedChunkRead,
    WebsiteSyncApproveResponse,
    WebsiteSyncChunkPreview,
    WebsiteSyncDiffRead,
    WebsiteSyncPreviewRequest,
    WebsiteSyncPreviewRunRead,
    WebsiteSyncRejectResponse,
    WebsiteSyncRollbackResponse,
    WebsiteSyncSourceCreate,
    WebsiteSyncSourceRead,
)

APPROVED_WEBSITE_HOSTS = {"alte.edu.ge", "www.alte.edu.ge", "join.alte.edu.ge"}
BLOCKED_PATH_PREFIXES = ("/admin", "/login", "/wp-admin", "/dashboard", "/api")
MAX_PREVIEW_BYTES = 750_000
DEFAULT_CHUNK_CHARS = 900
SAFE_USER_AGENT = "AlteAI-WebsiteSyncPreview/10M draft-only"
OFFICIAL_WEBSITE_SOURCE_LABEL = "\u10d0\u10da\u10e2\u10d4\u10e1 \u10dd\u10e4\u10d8\u10ea\u10d8\u10d0\u10da\u10e3\u10e0\u10d8 \u10d5\u10d4\u10d1\u10d2\u10d5\u10d4\u10e0\u10d3\u10d8"

FIXTURE_HTML: dict[str, str] = {
    "fixture://admissions-deadlines": """
      <html lang="ka"><head><title>Admissions deadlines</title><link rel="canonical" href="https://alte.edu.ge/ka/admissions" /></head>
      <body><header>Menu</header><nav>Home Admissions</nav><main>
      <h1>მიღების ვადები</h1>
      <p>2026 წლის მიღების ბოლო ვადა და რეგისტრაცია გამოქვეყნდება ოფიციალურ გვერდზე.</p>
      <p>ჩარიცხვა და განაცხადის deadline უკავშირდება მიმდინარე მიღების სტატუსს.</p>
      </main><footer>Contact footer</footer><script>bad()</script></body></html>
    """,
    "fixture://program-stable": """
      <html lang="en"><head><title>Computer Science Program</title></head>
      <body><main><h1>Computer Science</h1>
      <p>The Computer Science bachelor program is a higher education program. The program level is bachelor and the volume is 240 ECTS credits.</p>
      <p>Students study software engineering, databases, algorithms, and computer systems.</p>
      </main></body></html>
    """,
    "fixture://tuition": """
      <html lang="ka"><head><title>Tuition fees</title></head><body><main>
      <h1>სწავლის საფასური</h1><p>მედიცინის პროგრამის საფასური არის 12000 GEL წელიწადში. გადახდის პირობები განახლებულია.</p>
      </main></body></html>
    """,
    "fixture://noisy": """
      <html><head><title>Noisy page</title><style>.x{display:none}</style></head><body>
      <header>Header menu should disappear</header><nav>Navigation should disappear</nav>
      <main><h1>Library rules</h1><p>Library users may access reading spaces and general student services.</p></main>
      <footer>Footer should disappear</footer><script>console.log("remove")</script></body></html>
    """,
}

FIXTURE_HTML["fixture://tuition-en"] = """
  <html lang="en"><head><title>Medicine tuition fee</title></head><body><main>
  <h1>Medicine tuition fee</h1>
  <p>The Medicine/MD program tuition fee is 12000 GEL per academic year. Payment terms are current website information.</p>
  </main></body></html>
"""

FIXTURE_HTML["fixture://admissions-deadlines-updated"] = """
  <html lang="en"><head><title>Admissions deadlines</title><link rel="canonical" href="https://alte.edu.ge/ka/admissions" /></head>
  <body><main>
  <h1>Admissions deadlines</h1>
  <p>The 2027 admissions deadline and registration schedule will be published on the official page.</p>
  <p>Application deadline details depend on the current admissions status and applicant category.</p>
  </main></body></html>
"""

_sources: dict[str, WebsiteSyncSourceRead] = {}
_runs: dict[str, WebsiteSyncPreviewRunRead] = {}
_approved_chunks: dict[str, WebsiteApprovedChunkRead] = {}


@dataclass
class ExtractedPage:
    title: str | None
    canonical_url: str | None
    text: str


def reset_website_sync_preview_state() -> None:
    _sources.clear()
    _runs.clear()
    _approved_chunks.clear()


class ReadableHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.title_depth = 0
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.canonical_url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {key.lower(): value for key, value in attrs if key}
        if tag in {"script", "style", "nav", "footer", "header", "noscript"}:
            self.skip_depth += 1
            return
        if tag == "title":
            self.title_depth += 1
            return
        if tag == "link" and attrs_dict.get("rel") == "canonical" and attrs_dict.get("href"):
            self.canonical_url = attrs_dict["href"]
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "br"} and not self.skip_depth:
            self.text_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "nav", "footer", "header", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
            return
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3"} and not self.skip_depth:
            self.text_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_parts.append(data)
        elif not self.skip_depth:
            self.text_parts.append(data)


def create_website_source(payload: WebsiteSyncSourceCreate) -> WebsiteSyncSourceRead:
    validate_source_config(payload)
    now = datetime.now(UTC)
    source = WebsiteSyncSourceRead(
        id=str(uuid4()),
        name=payload.name.strip(),
        base_url=canonicalize_url(payload.base_url),
        allowed_paths=normalize_allowed_paths(payload.allowed_paths),
        source_group_hint=payload.source_group_hint,
        enabled=payload.enabled,
        created_at=now,
        updated_at=now,
    )
    _sources[source.id] = source
    return source


def list_website_sources() -> list[WebsiteSyncSourceRead]:
    return sorted(_sources.values(), key=lambda item: item.created_at)


def list_website_runs() -> list[WebsiteSyncPreviewRunRead]:
    return sorted(_runs.values(), key=lambda item: item.created_at, reverse=True)


def get_website_diff(run_id: str) -> WebsiteSyncDiffRead | None:
    run = _runs.get(run_id)
    if not run:
        return None
    old_content = approved_chunks_for_run_scope(run, include_archived=True)
    active_old_content = [chunk for chunk in old_content if chunk.status == "approved" and chunk.public_usable]
    old_text = "\n".join(chunk.chunk_text for chunk in active_old_content)
    diff = build_text_diff(old_text, run.extracted_text_preview)
    conflicts = conflict_flags_for_run(run, active_old_content)
    return WebsiteSyncDiffRead(
        run=run,
        run_id=run.run_id,
        source_url=run.source_url,
        canonical_url=run.canonical_url,
        page_title=run.page_title,
        status=run.status,
        detected_changes=diff["detected_changes"],
        conflicts=conflicts,
        approval_status=run.status,
        approval_allowed=run.status == "draft",
        rejection_allowed=run.status == "draft",
        archive_available=any(chunk.status == "approved" and chunk.public_usable for chunk in old_content),
        risk_flags=run.risk_flags,
        freshness_class=run.freshness_class,
        source_group_guess=run.source_group_guess,
        public_usable=run.public_usable,
        chunks_preview=run.chunks,
        old_approved_content=old_content,
        added_lines=diff["added_lines"],
        removed_lines=diff["removed_lines"],
        unchanged_summary=diff["unchanged_summary"],
        content_hash_changed=diff["content_hash_changed"],
    )


def approve_website_run(run_id: str, *, approved_by: str = "local_admin") -> WebsiteSyncApproveResponse:
    run = _runs.get(run_id)
    if not run:
        raise ValueError("Website sync preview run not found")
    if run.status != "draft":
        raise ValueError("Only draft website sync runs can be approved")
    now = datetime.now(UTC)
    version = f"website_sync:{run.run_id}"
    source_labels: list[str] = []
    for chunk in run.chunks:
        label = clean_source_label(run)
        if label not in source_labels:
            source_labels.append(label)
        approved = WebsiteApprovedChunkRead(
            approved_chunk_id=str(uuid4()),
            run_id=run.run_id,
            source_id=run.source_id,
            source_url=run.source_url,
            canonical_url=run.canonical_url,
            page_title=run.page_title,
            language=run.language,
            content_hash=chunk.content_hash,
            approved_at=now,
            approved_by=approved_by or "local_admin",
            version=version,
            source_group=run.source_group_guess,
            freshness_class=run.freshness_class,
            priority=100,
            status="approved",
            chunk_text=chunk.text,
            chunk_index=chunk.index,
            risk_flags=[flag for flag in run.risk_flags if flag != "draft_not_public_usable"],
            public_usable=True,
            clean_source_label=label,
        )
        _approved_chunks[approved.approved_chunk_id] = approved
    _runs[run_id] = run.model_copy(update={"status": "approved", "public_usable": False})
    return WebsiteSyncApproveResponse(
        run_id=run_id,
        status="approved",
        approved_count=len(run.chunks),
        public_usable=True,
        source_labels=source_labels,
    )


def reject_website_run(run_id: str) -> WebsiteSyncRejectResponse:
    run = _runs.get(run_id)
    if not run:
        raise ValueError("Website sync preview run not found")
    if run.status != "draft":
        raise ValueError("Only draft website sync runs can be rejected")
    _runs[run_id] = run.model_copy(update={"status": "rejected", "public_usable": False})
    return WebsiteSyncRejectResponse(run_id=run_id, status="rejected", public_usable=False)


def list_approved_website_chunks(*, include_archived: bool = False) -> list[WebsiteApprovedChunkRead]:
    chunks = [
        chunk
        for chunk in _approved_chunks.values()
        if include_archived or (chunk.status == "approved" and chunk.public_usable)
    ]
    return sorted(chunks, key=lambda item: (item.approved_at, item.chunk_index), reverse=True)


def archive_approved_website_version(version_id: str) -> WebsiteSyncRollbackResponse:
    archived_count = 0
    for chunk_id, chunk in list(_approved_chunks.items()):
        if chunk.version == version_id or chunk.run_id == version_id:
            _approved_chunks[chunk_id] = chunk.model_copy(update={"status": "archived", "public_usable": False})
            archived_count += 1
    if archived_count == 0:
        raise ValueError("Approved website version not found")
    return WebsiteSyncRollbackResponse(
        version_id=version_id,
        status="archived",
        archived_count=archived_count,
        public_usable=False,
    )


def approved_website_answer_for_question(
    question: str,
    *,
    language: str | None = None,
    source_group: str | None = None,
) -> dict | None:
    result = search_approved_website_knowledge(question, language=language, source_group=source_group, limit=1)
    if not result:
        return None
    chunk, score = result[0]
    if score < 2 and classify_freshness(question) != "variable":
        return None
    return {
        "answer": chunk.chunk_text,
        "status": "answered",
        "source_group": chunk.source_group or "approved_website_sync",
        "public_source_label": chunk.clean_source_label,
        "confidence": min(0.98, 0.72 + (score / 20)),
        "freshness_class": chunk.freshness_class,
        "chunk": chunk,
    }


def search_approved_website_knowledge(
    question: str,
    *,
    language: str | None = None,
    source_group: str | None = None,
    limit: int = 3,
) -> list[tuple[WebsiteApprovedChunkRead, int]]:
    query = normalize_text(question).lower()
    if not query:
        return []
    query_freshness = classify_freshness(query)
    query_tokens = search_tokens(query)
    scored: list[tuple[WebsiteApprovedChunkRead, int]] = []
    for chunk in _approved_chunks.values():
        if chunk.status != "approved" or not chunk.public_usable:
            continue
        if language and chunk.language not in {language, "unknown"}:
            continue
        if source_group and chunk.source_group and source_group != chunk.source_group:
            continue
        if query_freshness == "variable" and chunk.freshness_class != "variable":
            continue
        text = f"{chunk.page_title or ''} {chunk.chunk_text}".lower()
        score = sum(1 for token in query_tokens if token in text)
        if query_freshness == "variable" and chunk.freshness_class == "variable":
            score += 3
        if chunk.source_group and source_group and chunk.source_group == source_group:
            score += 2
        if score > 0:
            scored.append((chunk, score))
    return sorted(scored, key=lambda item: (item[1], item[0].priority, item[0].approved_at), reverse=True)[:limit]


def search_tokens(value: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[\w\u10a0-\u10ff]+", value.lower())
        if len(token) >= 3 and token not in {"the", "and", "what", "when", "how", "does", "this"}
    ]


def clean_source_label(run: WebsiteSyncPreviewRunRead) -> str:
    return OFFICIAL_WEBSITE_SOURCE_LABEL


def approved_chunks_for_run_scope(
    run: WebsiteSyncPreviewRunRead,
    *,
    include_archived: bool = False,
) -> list[WebsiteApprovedChunkRead]:
    canonical = canonical_scope(run.canonical_url or run.source_url)
    source_group = run.source_group_guess
    return sorted(
        [
            chunk
            for chunk in _approved_chunks.values()
            if canonical_scope(chunk.canonical_url or chunk.source_url) == canonical
            and (not source_group or chunk.source_group == source_group)
            and (include_archived or (chunk.status == "approved" and chunk.public_usable))
        ],
        key=lambda item: (item.approved_at, item.chunk_index),
        reverse=True,
    )


def canonical_scope(value: str | None) -> str:
    return canonicalize_url(value or "").rstrip("/")


def build_text_diff(old_text: str, new_text: str) -> dict:
    old_lines = comparable_lines(old_text)
    new_lines = comparable_lines(new_text)
    old_set = set(old_lines)
    new_set = set(new_lines)
    added = [line for line in new_lines if line not in old_set]
    removed = [line for line in old_lines if line not in new_set]
    unchanged_count = len([line for line in new_lines if line in old_set])
    if not old_lines:
        detected = ["No previous approved website content for this canonical URL/source group."]
    elif added or removed:
        detected = ["Draft content differs from currently approved website content."]
    else:
        detected = ["Draft content matches currently approved website content."]
    return {
        "detected_changes": detected,
        "added_lines": added[:20],
        "removed_lines": removed[:20],
        "unchanged_summary": f"{unchanged_count} unchanged line(s), {len(added)} added, {len(removed)} removed.",
        "content_hash_changed": hash_text(old_text) != hash_text(new_text) if old_lines else True,
    }


def comparable_lines(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", normalized)
    return [part.strip() for part in parts if part.strip()]


def conflict_flags_for_run(run: WebsiteSyncPreviewRunRead, old_content: list[WebsiteApprovedChunkRead]) -> list[str]:
    if not old_content:
        return []
    conflicts = []
    old_hashes = {chunk.content_hash for chunk in old_content}
    new_hashes = {chunk.content_hash for chunk in run.chunks}
    if old_hashes and old_hashes != new_hashes:
        conflicts.append("approved_content_hash_changed")
    risky = sorted({flag for flag in run.risk_flags if flag.startswith("high_risk_")})
    conflicts.extend(risky)
    return conflicts


def run_preview_sync(payload: WebsiteSyncPreviewRequest) -> WebsiteSyncPreviewRunRead:
    source = _sources.get(payload.source_id)
    if not source:
        raise ValueError("Website sync source not found")
    if not source.enabled:
        raise ValueError("Website sync source is disabled")
    if payload.mode != "single_url":
        raise ValueError("Only single_url preview mode is supported")
    if not payload.dry_run:
        raise ValueError("Website sync preview must be dry_run=true in Phase 10M")

    validate_preview_url(payload.url, source)
    html = load_preview_html(payload.url)
    extracted = extract_readable_html(html, base_url=payload.url)
    text = extracted.text
    if not text:
        raise ValueError("No readable page text extracted")
    chunks = chunk_text(text, limit=payload.limit or 5)
    freshness_class = classify_freshness(text)
    risk_flags = high_risk_flags_for_text(text, payload.url)
    source_group_guess = guess_source_group(text, source.source_group_hint)
    now = datetime.now(UTC)
    run = WebsiteSyncPreviewRunRead(
        run_id=str(uuid4()),
        source_id=source.id,
        status="draft",
        source_url=payload.url,
        canonical_url=extracted.canonical_url or canonicalize_url(payload.url),
        page_title=extracted.title,
        language=detect_language(text),
        content_hash=hash_text(text),
        extracted_text_preview=text[:1000],
        chunks_count=len(chunks),
        chunks=[
            WebsiteSyncChunkPreview(index=index, text=chunk, content_hash=hash_text(chunk))
            for index, chunk in enumerate(chunks)
        ],
        source_group_guess=source_group_guess,
        freshness_class=freshness_class,
        risk_flags=risk_flags,
        public_usable=False,
        created_at=now,
    )
    _runs[run.run_id] = run
    updated = source.model_copy(update={"last_preview_run_id": run.run_id, "last_preview_at": now, "updated_at": now})
    _sources[source.id] = updated
    return run


def validate_source_config(payload: WebsiteSyncSourceCreate) -> None:
    if not payload.name.strip():
        raise ValueError("Source name is required")
    parsed = parse_http_url(payload.base_url)
    if parsed.hostname not in APPROVED_WEBSITE_HOSTS:
        raise ValueError("Website source domain is not approved")
    if parsed.path and is_blocked_path(parsed.path):
        raise ValueError("Website source base path is blocked")
    normalize_allowed_paths(payload.allowed_paths)


def validate_preview_url(url: str, source: WebsiteSyncSourceRead) -> None:
    if url.startswith("fixture://"):
        if url not in FIXTURE_HTML:
            raise ValueError("Unknown website sync fixture")
        return
    parsed = parse_http_url(url)
    if parsed.hostname not in APPROVED_WEBSITE_HOSTS:
        raise ValueError("Preview URL domain is not approved")
    source_host = urlparse(source.base_url).hostname
    if source_host != parsed.hostname:
        raise ValueError("Preview URL must match the configured source host")
    if is_blocked_path(parsed.path):
        raise ValueError("Preview URL path is blocked")
    if parsed.query and len(parsed.query) > 80:
        raise ValueError("Query-heavy preview URLs are blocked")
    if source.allowed_paths and not any(parsed.path.startswith(path) for path in source.allowed_paths):
        raise ValueError("Preview URL path is outside configured allowed paths")
    reject_private_host(parsed.hostname or "")


def parse_http_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are allowed")
    if not parsed.hostname:
        raise ValueError("URL host is required")
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Localhost URLs are not allowed outside fixture mode")
    return parsed


def reject_private_host(hostname: str) -> None:
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            resolved = socket.gethostbyname(hostname)
        except OSError:
            return
        address = ipaddress.ip_address(resolved)
    if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
        raise ValueError("Private or local network hosts are not allowed")


def is_blocked_path(path: str) -> bool:
    lowered = (path or "/").lower()
    return any(lowered == prefix or lowered.startswith(f"{prefix}/") for prefix in BLOCKED_PATH_PREFIXES)


def normalize_allowed_paths(paths: list[str]) -> list[str]:
    normalized = []
    for path in paths:
        value = (path or "").strip()
        if not value:
            continue
        if not value.startswith("/"):
            value = f"/{value}"
        if is_blocked_path(value):
            raise ValueError("Allowed paths cannot include admin/login/private paths")
        normalized.append(value)
    return normalized


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    if url.startswith("fixture://"):
        return url
    path = parsed.path or "/"
    return f"{parsed.scheme}://{parsed.hostname}{path}"


def load_preview_html(url: str) -> str:
    if url.startswith("fixture://"):
        return FIXTURE_HTML[url]
    request = Request(url, headers={"User-Agent": SAFE_USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=5) as response:  # nosec B310 - URL is validated against approved domains first.
        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            raise ValueError("Preview URL did not return HTML")
        data = response.read(MAX_PREVIEW_BYTES + 1)
    if len(data) > MAX_PREVIEW_BYTES:
        raise ValueError("Preview HTML exceeds size limit")
    return data.decode("utf-8", errors="replace")


def extract_readable_html(html: str, *, base_url: str | None = None) -> ExtractedPage:
    parser = ReadableHTMLExtractor()
    parser.feed(html or "")
    title = normalize_text(" ".join(parser.title_parts)) or None
    text = normalize_text(" ".join(parser.text_parts))
    canonical = parser.canonical_url
    if canonical and base_url and not canonical.startswith(("http://", "https://", "fixture://")):
        canonical = urljoin(base_url, canonical)
    return ExtractedPage(title=title, canonical_url=canonical, text=text)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def chunk_text(text: str, *, limit: int) -> list[str]:
    limit = max(1, min(limit, 20))
    chunks = []
    remaining = text
    while remaining and len(chunks) < limit:
        chunk = remaining[:DEFAULT_CHUNK_CHARS].strip()
        chunks.append(chunk)
        remaining = remaining[DEFAULT_CHUNK_CHARS:].strip()
    return chunks


def hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def detect_language(text: str) -> str:
    georgian = sum(1 for char in text if "\u10a0" <= char <= "\u10ff")
    latin = sum(1 for char in text if "a" <= char.lower() <= "z")
    if georgian > latin:
        return "ka"
    if latin:
        return "en"
    return "unknown"


VARIABLE_MARKERS = [
    "როდის",
    "ვადა",
    "ბოლო ვადა",
    "რეგისტრაცია",
    "ჩარიცხვა",
    "მიღება",
    "სემესტრი",
    "კალენდარი",
    "გამოცდა",
    "საფასური",
    "ფასი",
    "რა ღირს",
    "გრანტი",
    "დაფინანსება",
    "სტიპენდია",
    "when",
    "deadline",
    "application deadline",
    "admission deadline",
    "registration",
    "semester",
    "calendar",
    "exam",
    "tuition",
    "fee",
    "cost",
    "scholarship",
    "grant",
    "funding",
    "latest",
    "updated",
    "current",
]

STABLE_MARKERS = [
    "program description",
    "program level",
    "bachelor program",
    "master program",
    "ects",
    "credits",
    "academic integrity",
    "library users",
    "student services",
    "ombudsman",
    "policy",
    "ზოგადი",
    "პროგრამა",
    "კრედიტ",
    "კეთილსინდისიერება",
    "ბიბლიოთეკ",
]


def classify_freshness(text: str) -> str:
    lowered = (text or "").lower()
    if any(marker.lower() in lowered for marker in VARIABLE_MARKERS):
        return "variable"
    if re.search(r"\b20(2[6-9]|3[0-5])\b", lowered):
        return "variable"
    if re.search(r"\b\d{1,2}[./-]\d{1,2}([./-]\d{2,4})?\b", lowered):
        return "variable"
    if re.search(r"\b\d+\s*(gel|lari|usd|eur)\b|₾\s*\d+", lowered):
        return "variable"
    if any(marker in lowered for marker in ["schedule", "period", "office hours", "contact", "განრიგ", "პერიოდ", "საკონტაქტ", "საათ"]):
        return "variable"
    if any(marker.lower() in lowered for marker in STABLE_MARKERS):
        return "stable"
    return "unknown"


def guess_source_group(text: str, hint: str | None = None) -> str | None:
    if hint:
        return hint
    lowered = (text or "").lower()
    if any(marker in lowered for marker in ["tuition", "fee", "cost", "საფასური", "ფასი", "გრანტ", "დაფინანს"]):
        return "finance_sources"
    if any(marker in lowered for marker in ["admission", "deadline", "მიღება", "ჩარიცხვა", "ვადა"]):
        return "admissions_rules"
    if any(marker in lowered for marker in ["calendar", "semester", "exam", "კალენდარი", "სემესტრი", "გამოცდა"]):
        return "academic_calendar_2025_2026"
    if any(marker in lowered for marker in ["program", "ects", "credits", "პროგრამ", "კრედიტ"]):
        return "program_catalog_sources"
    if any(marker in lowered for marker in ["library", "ბიბლიოთეკ"]):
        return "library_sources"
    return None


def risk_flags_for_text(text: str, url: str) -> list[str]:
    flags = ["preview_only", "draft_not_public_usable"]
    freshness = classify_freshness(text)
    if freshness == "variable":
        flags.append("freshness_sensitive")
    if re.search(r"\b20(2[6-9]|3[0-5])\b", text or ""):
        flags.append("year_specific")
    if re.search(r"\b\d+\s*(gel|lari|usd|eur)\b|₾\s*\d+", (text or "").lower()):
        flags.append("price_detected")
    if url.startswith("fixture://"):
        flags.append("fixture_input")
    return flags


def high_risk_flags_for_text(text: str, url: str) -> list[str]:
    flags = risk_flags_for_text(text, url)
    lowered = (text or "").lower()
    if re.search(r"\b20(2[6-9]|3[0-5])\b", text or ""):
        flags.append("high_risk_year_specific")
    if re.search(r"\b\d{1,2}[./-]\d{1,2}([./-]\d{2,4})?\b", lowered):
        flags.extend(["date_detected", "high_risk_dates"])
    if any(marker in lowered for marker in ["deadline", "application deadline", "admission deadline", "ბოლო ვადა", "ვადა"]):
        flags.append("high_risk_deadlines")
    if re.search(r"\b\d+\s*(gel|lari|usd|eur)\b|₾\s*\d+|â‚¾\s*\d+", lowered):
        flags.extend(["price_detected", "high_risk_tuition_fees"])
    if any(marker in lowered for marker in ["tuition", "fee", "cost", "price", "საფასური", "ფასი", "რა ღირს"]):
        flags.append("high_risk_tuition_fees")
    if any(marker in lowered for marker in ["grant", "scholarship", "funding", "გრანტ", "დაფინანს", "სტიპენდ"]):
        flags.append("high_risk_grants_scholarships")
    if any(marker in lowered for marker in ["admission", "admissions", "enrollment", "მიღება", "ჩარიცხვა"]):
        flags.append("high_risk_admissions_rules")
    if any(marker in lowered for marker in ["calendar", "semester", "exam", "schedule", "კალენდარი", "სემესტრი", "გამოცდა"]):
        flags.append("high_risk_academic_calendar")
    if any(marker in lowered for marker in ["requirement", "prerequisite", "program requirement", "მოთხოვნ"]):
        flags.append("high_risk_program_requirements")
    if any(marker in lowered for marker in ["ects", "credit", "credits", "კრედიტ"]):
        flags.append("high_risk_ects_credits")
    if any(marker in lowered for marker in ["privacy", "legal", "personal data", "confidential", "პირად", "კონფიდენცი"]):
        flags.append("high_risk_legal_privacy")
    if any(marker in lowered for marker in ["contact", "phone", "email", "office hours", "address", "საკონტაქტ", "ტელეფონ", "ელფოსტ", "მისამართ"]):
        flags.append("high_risk_contact_details")
    if url.startswith("fixture://"):
        flags.append("high_risk_fixture_test_input")
    return list(dict.fromkeys(flags))
