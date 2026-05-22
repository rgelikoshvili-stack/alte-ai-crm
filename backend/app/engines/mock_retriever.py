from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KnowledgeSnippet, KnowledgeSource, RetrievalResult


async def retrieve_snippets(
    db: AsyncSession,
    *,
    query: str,
    language: str | None = None,
    category: str | None = None,
    source_domain: str | None = None,
    sensitivity: str | None = None,
    program_name: str | None = None,
    approved_only: bool = True,
    include_stale: bool = False,
    limit: int = 3,
) -> list[RetrievalResult]:
    rows = (
        await db.execute(
            select(KnowledgeSnippet, KnowledgeSource)
            .join(KnowledgeSource, KnowledgeSnippet.source_id == KnowledgeSource.id)
            .where(KnowledgeSource.status != "archived")
        )
    ).all()
    results: list[RetrievalResult] = []
    query_tokens = tokenize(query)
    today = date.today()

    for snippet, source in rows:
        if approved_only and (source.status != "approved" or snippet.status != "approved"):
            continue
        if language and snippet.language != language:
            continue
        if category and snippet.category != category:
            continue
        explicit_domains = {item for item in {snippet.source_domain, source.source_domain} if item}
        if source_domain and explicit_domains and source_domain not in explicit_domains:
            continue
        if sensitivity and sensitivity not in {snippet.sensitivity, source.sensitivity}:
            continue
        if program_name and snippet.program_name and snippet.program_name.lower() != program_name.lower():
            continue

        score = score_snippet(snippet, source, query_tokens, language, category, program_name)
        if score <= 0:
            continue
        source_status = "answered_from_approved_source"
        stale = is_stale_snippet(snippet, today)
        if stale:
            source_status = "source_stale"
            if not include_stale:
                continue
        results.append(RetrievalResult(snippet, source, score, source_status, is_stale=stale))

    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]


def score_snippet(
    snippet: KnowledgeSnippet,
    source: KnowledgeSource,
    query_tokens: set[str],
    language: str | None,
    category: str | None,
    program_name: str | None,
) -> int:
    haystack = " ".join(
        [
            snippet.title,
            snippet.content,
            snippet.category,
            snippet.source_key or "",
            snippet.source_domain or "",
            snippet.sensitivity or "",
            snippet.program_name or "",
            snippet.keywords or "",
            source.title,
            source.source_key or "",
            source.source_domain or "",
            source.category or "",
            source.sensitivity or "",
        ]
    ).lower()
    score = sum(10 for token in query_tokens if token and token in haystack)
    if language and snippet.language == language:
        score += 8
    if category and snippet.category == category:
        score += 12
    if program_name and snippet.program_name and snippet.program_name.lower() == program_name.lower():
        score += 20
    return score


def is_stale_snippet(snippet: KnowledgeSnippet, today: date) -> bool:
    if snippet.effective_to and snippet.effective_to < today:
        return True
    if snippet.stale_after_days is None:
        return False
    baseline = snippet.effective_from or as_date(snippet.updated_at) or as_date(snippet.created_at)
    return bool(baseline and baseline + timedelta(days=snippet.stale_after_days) < today)


def as_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def tokenize(text: str) -> set[str]:
    normalized = text.lower().replace(",", " ").replace("?", " ").replace(".", " ")
    tokens = {token.strip() for token in normalized.split() if len(token.strip()) >= 3}
    keyword_map = {
        "ღირს": "tuition",
        "საფასური": "tuition",
        "ფასი": "tuition",
        "გადასახადი": "tuition",
        "tuition": "tuition",
        "fee": "tuition",
        "fees": "tuition",
        "price": "tuition",
        "deadline": "deadline",
        "ვადა": "deadline",
        "ჩარიცხვა": "admission",
        "მიღება": "admission",
        "admission": "admission",
        "apply": "admission",
        "application": "admission",
        "ბიზნესი": "business",
        "business": "business",
        "სამართალი": "law",
        "law": "law",
        "მედიცინა": "medicine",
        "medicine": "medicine",
        "md": "medicine",
        "სტიპენდია": "scholarship",
        "scholarship": "scholarship",
        "მისამართი": "contact",
        "ტელეფონი": "contact",
        "კონტაქტი": "contact",
        "contact": "contact",
        "address": "contact",
        "კომპიუტერული": "computer",
        "computer": "computer",
        "ხელოვნური": "ai",
        "international": "international",
        "visa": "visa",
        "relocation": "relocation",
        "library": "library",
        "ბიბლიოთეკა": "library",
    }
    tokens.update(value for key, value in keyword_map.items() if key in normalized)
    return tokens
