import html
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


BASE = "https://alte.edu.ge"
OUT_DIR = Path("alte_knowledge_base")
OUT_JSONL = OUT_DIR / "alte_knowledge_base_ka.jsonl"
OUT_MD = OUT_DIR / "alte_knowledge_base_index.md"
OUT_URLS = OUT_DIR / "alte_source_urls.txt"


PRIORITY_PATHS = {
    "/ka/",
    "/ka/universitetis-shesakheb",
    "/ka/universiteti-erti-shekhedvit",
    "/ka/akademiuri-programebi",
    "/ka/sabakalavro-programebi",
    "/ka/samagistro-programebi",
    "/ka/erttsikliani-sameditsino-programebi",
    "/ka/stsavla",
    "/ka/migheba",
    "/ka/abiturientebistvis",
    "/ka/bakalavriatistvis",
    "/ka/magistraturistvis",
    "/ka/saertashoriso-studentebistvis",
    "/ka/khshirad-dasmuli-kitkhvebi",
    "/ka/faq",
    "/ka/kontaqti",
    "/ka/akademiuri-informatsia",
    "/ka/akademiuri-kalendari",
    "/ka/gamotsdebis-shesakheb",
    "/ka/studentis-gzamkvlevi",
    "/ka/studentebis-sakonsultatsio-saatebi",
    "/ka/biblioteka",
    "/ka/servisebi",
    "/ka/sametsniero-baza",
    "/ka/bibliotekis-tsesebi",
    "/ka/studenturi-servisebi",
    "/ka/studentis-ketildgheobis-mrcheveli-da-warmatebis-qouchi",
    "/ka/karieruli-ganvitareba",
    "/ka/ombudsmeni",
    "/ka/relokatsiis-servisebi",
}

PROGRAM_HINTS = {
    "biznesis-administrirebis",
    "biznesis",
    "samartlis",
    "samartali",
    "fsiqologia",
    "saertashoriso-urtiertobebi",
    "turizmis",
    "turizmi",
    "kompiuteruli-metsniereba",
    "kompiuteruli-metsnierebis",
    "ai-da-monatsemta-analitika",
    "xelovnuri-inteleqti",
    "zhurnalistika",
    "meditsinis",
    "medicine",
    "sazogadoebrivi-jandatsva",
    "stomatologia",
}

EXCLUDE_HINTS = {
    "news",
    "event",
}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"p", "br", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        data = html.unescape(data).strip()
        if data:
            self.parts.append(data)

    def text(self):
        value = " ".join(self.parts)
        value = re.sub(r"[ \t]+", " ", value)
        value = re.sub(r"\s*\n\s*", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def strip_html(value):
    if not value:
        return ""
    parser = TextExtractor()
    parser.feed(str(value))
    return parser.text()


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Codex knowledge-base extraction for Alte chatbot planning",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace")


def sitemap_urls():
    xml = fetch(f"{BASE}/sitemap-ka.xml")
    root = ET.fromstring(xml)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for url_node in root.findall("sm:url", ns):
        loc = url_node.findtext("sm:loc", namespaces=ns)
        lastmod = url_node.findtext("sm:lastmod", namespaces=ns)
        if loc:
            urls.append((loc, lastmod or ""))
    return urls


def should_fetch(url):
    path = urlparse(url).path
    slug = path.lower()
    if path in PRIORITY_PATHS:
        return True
    if any(hint in slug for hint in PROGRAM_HINTS):
        return True
    if any(x in slug for x in ["/ka/for-", "/ka/admission", "/ka/academic", "/ka/student"]):
        return True
    return False


def next_data(html_text):
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_text, re.S)
    if not match:
        return None
    return json.loads(html.unescape(match.group(1)))


def get_page_payload(data):
    props = data.get("props", {})
    page_props = props.get("pageProps", {})
    return page_props.get("data") or page_props.get("post") or page_props


def flatten_page(payload):
    chunks = []

    def add(title, text, kind="section"):
        clean = strip_html(text)
        if len(clean) >= 30:
            chunks.append({"section": strip_html(title) or kind, "text": clean, "kind": kind})

    def walk(obj, context=""):
        if isinstance(obj, dict):
            title = obj.get("title") or obj.get("banner_title") or context
            if obj.get("description"):
                add(f"{title} - აღწერა", obj.get("description"), "description")
            if obj.get("text"):
                add(title, obj.get("text"), "body")
            locale_additional = obj.get("locale_additional")
            if isinstance(locale_additional, dict):
                for key, value in locale_additional.items():
                    if key == "sidebar_menu" and isinstance(value, list):
                        for item in value:
                            add(item.get("title") or title, item.get("text", ""), "sidebar")
                    elif isinstance(value, str):
                        add(key, value, "additional")
                    else:
                        walk(value, key)
            for key, value in obj.items():
                if key in {"description", "text", "locale_additional"}:
                    continue
                if key in {"translations", "breadcrumb", "slugs"}:
                    continue
                if isinstance(value, (dict, list)):
                    walk(value, title or context or key)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, context)

    walk(payload)
    seen = set()
    unique = []
    for chunk in chunks:
        key = (chunk["section"], chunk["text"][:200])
        if key not in seen:
            seen.add(key)
            unique.append(chunk)
    return unique


def tags_for(url, title, breadcrumb):
    text = " ".join([url, title or "", breadcrumb or ""]).lower()
    tags = []
    for label, hints in {
        "program": ["პროგრამ", "program", "sabakalavro", "samagistro", "meditsinis", "samartlis", "biznesis", "kompiuteruli", "zhurnalistika", "turiz"],
        "admission": ["migheba", "abiturient", "ბაკალავრ", "მაგისტრ", "admission"],
        "student_services": ["student", "სტუდენტ", "biblioteka", "library", "ombudsmen", "karier"],
        "contact": ["kontaqti", "contact", "საკონტაქტ"],
        "faq": ["faq", "khshirad", "ხშირად"],
        "about": ["universitet", "about", "შესახებ"],
    }.items():
        if any(h in text for h in hints):
            tags.append(label)
    return sorted(set(tags))


def main():
    OUT_DIR.mkdir(exist_ok=True)
    candidates = [(u, lm) for u, lm in sitemap_urls() if should_fetch(u)]
    # Keep the crawl focused on chatbot-relevant university/program pages.
    candidates = sorted(set(candidates), key=lambda x: x[0])

    records = []
    errors = []
    for idx, (url, lastmod) in enumerate(candidates, start=1):
        try:
            html_text = fetch(url)
            data = next_data(html_text)
            if not data:
                continue
            payload = get_page_payload(data)
            title = strip_html(payload.get("title") if isinstance(payload, dict) else "")
            desc = strip_html(payload.get("description") if isinstance(payload, dict) else "")
            breadcrumb = ""
            if isinstance(payload, dict) and isinstance(payload.get("breadcrumb"), list):
                breadcrumb = " > ".join(strip_html(x.get("title", "")) for x in payload["breadcrumb"])
            chunks = flatten_page(payload)
            if desc and not any(c["text"] == desc for c in chunks):
                chunks.insert(0, {"section": "აღწერა", "text": desc, "kind": "description"})
            page_tags = tags_for(url, title, breadcrumb)
            for chunk_index, chunk in enumerate(chunks):
                records.append(
                    {
                        "source_url": url,
                        "lastmod": lastmod,
                        "locale": "ka",
                        "title": title,
                        "breadcrumb": breadcrumb,
                        "section": chunk["section"],
                        "chunk_index": chunk_index,
                        "kind": chunk["kind"],
                        "tags": page_tags,
                        "text": chunk["text"],
                    }
                )
            print(f"[{idx}/{len(candidates)}] {len(chunks):02d} chunks - {url}")
            time.sleep(0.15)
        except Exception as exc:
            errors.append((url, repr(exc)))
            print(f"ERROR {url}: {exc}")

    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with OUT_URLS.open("w", encoding="utf-8") as f:
        for url, lastmod in candidates:
            f.write(f"{url}\t{lastmod}\n")

    pages = {}
    for rec in records:
        pages.setdefault(rec["source_url"], {"title": rec["title"], "tags": rec["tags"], "chunks": 0, "lastmod": rec["lastmod"]})
        pages[rec["source_url"]]["chunks"] += 1

    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Alte chatbot knowledge-base index\n\n")
        f.write("ეს ფაილი არის წყაროების ინდექსი chatbot knowledge-base-ისთვის. სრული chunk-ები წერია `alte_knowledge_base_ka.jsonl`-ში.\n\n")
        f.write(f"- წყარო გვერდები: {len(pages)}\n")
        f.write(f"- knowledge chunks: {len(records)}\n")
        f.write(f"- crawl errors: {len(errors)}\n\n")
        f.write("## Answering policy\n\n")
        f.write("- ბოტმა უნდა უპასუხოს მხოლოდ active source/chunk-იდან.\n")
        f.write("- ფასები, მიღების ვადები, გრანტები, მოთხოვნები და ოფიციალური წესები source-ის გარეშე არ გამოიგონოს.\n")
        f.write("- თუ confidence დაბალია ან source არ მოიძებნა, შესთავაზოს human handover.\n")
        f.write("- admission/program interest + contact data -> CRM lead; general info -> conversation only.\n\n")
        f.write("## Sources\n\n")
        for url, meta in sorted(pages.items()):
            tags = ", ".join(meta["tags"]) if meta["tags"] else "general"
            f.write(f"- [{meta['title'] or url}]({url}) - chunks: {meta['chunks']}; tags: {tags}; lastmod: {meta['lastmod']}\n")
        if errors:
            f.write("\n## Errors\n\n")
            for url, err in errors:
                f.write(f"- {url}: `{err}`\n")

    print(f"\nWrote {OUT_JSONL.resolve()}")
    print(f"Wrote {OUT_MD.resolve()}")
    print(f"Wrote {OUT_URLS.resolve()}")
    print(f"Pages: {len(pages)}; chunks: {len(records)}; errors: {len(errors)}")


if __name__ == "__main__":
    main()
