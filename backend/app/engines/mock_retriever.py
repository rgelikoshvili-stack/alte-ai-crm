from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KnowledgeSnippet, KnowledgeSource, RetrievalResult


async def retrieve_snippets(
    db: AsyncSession,
    *,
    query: str,
    language: str | None = None,
    category: str | None = None,
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
        if program_name and snippet.program_name and snippet.program_name.lower() != program_name.lower():
            continue

        score = score_snippet(snippet, source, query_tokens, language, category, program_name)
        if score <= 0:
            continue
        source_status = "answered_from_approved_source"
        if snippet.effective_to and snippet.effective_to < today:
            source_status = "source_stale"
            if not include_stale:
                continue
        results.append(RetrievalResult(snippet, source, score, source_status))

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
            snippet.program_name or "",
            snippet.keywords or "",
            source.title,
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


def tokenize(text: str) -> set[str]:
    normalized = text.lower().replace(",", " ").replace("?", " ").replace(".", " ")
    tokens = {token.strip() for token in normalized.split() if len(token.strip()) >= 3}
    keyword_map = {
        "ღირს": "tuition",
        "ფასი": "tuition",
        "გადასახადი": "tuition",
        "მიღება": "admission",
        "ჩარიცხვა": "admission",
        "ბიზნეს": "business",
        "სტიპენდია": "scholarship",
    }
    tokens.update(value for key, value in keyword_map.items() if key in normalized)
    return tokens
