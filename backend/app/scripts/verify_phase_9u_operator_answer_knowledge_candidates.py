from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def is_tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def assert_contains(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"{label} missing marker: {marker}")


def assert_not_contains(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"{label} contains forbidden marker: {marker}")


def run_checks() -> dict:
    required_files = [
        "backend/app/services/knowledge_service.py",
        "backend/app/api/routes_knowledge.py",
        "backend/app/schemas/knowledge.py",
        "backend/app/tests/test_phase_9u_operator_answer_knowledge_candidates.py",
        "frontend/app.js",
        "docs/deployment/PHASE_9U_OPERATOR_ANSWER_KNOWLEDGE_CANDIDATES_RESULT.md",
    ]
    for path in required_files:
        if not (PROJECT_ROOT / path).exists():
            raise AssertionError(f"Missing required file: {path}")

    service = read("backend/app/services/knowledge_service.py")
    routes = read("backend/app/api/routes_knowledge.py")
    schemas = read("backend/app/schemas/knowledge.py")
    result_doc = read("docs/deployment/PHASE_9U_OPERATOR_ANSWER_KNOWLEDGE_CANDIDATES_RESULT.md")
    docs = "\n".join(
        read(path)
        for path in [
            "docs/NEXT_PHASES.md",
            "docs/deployment/PHASE_9P_PUBLIC_LAUNCH_DECISION.md",
            "docs/deployment/PHASE_9U_OPERATOR_ANSWER_KNOWLEDGE_CANDIDATES_RESULT.md",
        ]
    )
    frontend = "\n".join(
        read(path)
        for path in [
            "frontend/app.js",
            "frontend/index.html",
            "widget/pro-v2.html",
            "widget/variants/pro-v2-chat.jsx",
            "widget/variants/pro-v2-modals.jsx",
        ]
        if (PROJECT_ROOT / path).exists()
    )

    for marker in [
        "create_operator_reply_knowledge_candidate",
        "operator_reply_knowledge_candidate_created",
        "review_required=review_required",
        'status="draft"',
        'source_type="faq"',
        "operator_reply:",
    ]:
        assert_contains(service, marker, "knowledge service")
    assert_contains(routes, "/operator-reply-candidates/{message_id}", "knowledge route")
    assert_contains(schemas, "OperatorReplyKnowledgeCandidateCreate", "knowledge schema")
    assert_contains(schemas, "OperatorReplyKnowledgeCandidateRead", "knowledge schema")
    assert_contains(frontend, "/knowledge/operator-reply-candidates/", "operator frontend")
    assert_contains(frontend, "source_key: `operator_reply:${messageId}`", "operator frontend")
    assert_contains(frontend, "knowledge-candidate-btn", "operator frontend")
    assert_contains(frontend, "Create knowledge candidate", "operator frontend")
    assert_contains(frontend, "open-knowledge-candidate-btn", "operator frontend")
    assert_contains(frontend, "candidate-status", "operator frontend")
    assert_contains(frontend, "Open review", "operator frontend")
    assert_contains(frontend, "showOperatorAnswerDrafts", "operator frontend")
    assert_contains(frontend, "operatorKnowledgeFilterBtn", "operator frontend")
    assert_contains(frontend, "approveKnowledgeSnippet", "operator frontend")
    assert_contains(frontend, "archiveKnowledgeSnippet", "operator frontend")
    assert_contains(frontend, "saveKnowledgeSnippetDraft", "operator frontend")
    assert_contains(frontend, "knowledge-edit-textarea", "operator frontend")
    assert_contains(frontend, "knowledge-meta-grid", "operator frontend")
    assert_contains(frontend, "snippet-category-", "operator frontend")
    assert_contains(frontend, "snippet-sensitivity-", "operator frontend")
    assert_contains(frontend, "snippet-language-", "operator frontend")
    assert_contains(frontend, "/knowledge/sources/${sourceId}", "operator frontend")
    assert_contains(frontend, "Save draft", "operator frontend")
    assert_contains(frontend, "/knowledge/snippets/${snippetId}", "operator frontend")
    assert_contains(frontend, "renderKnowledgeReviewItem", "operator frontend")
    assert_contains(frontend, "/knowledge/review-queue", "operator frontend")
    assert_contains(
        result_doc,
        "PHASE_9U_OPERATOR_ANSWER_KNOWLEDGE_STATUS=OPERATOR_ANSWERS_TO_DRAFT_REVIEW_QUEUE_READY",
        "result doc",
    )
    assert_contains(
        docs,
        "BACKEND_LOCAL_OPERATOR_ANSWER_REVIEW_LEARNING_READY_PENDING_UI_REVIEW_AND_APPROVAL",
        "status docs",
    )
    assert_contains(docs.lower(), "automatic learning from operator replies: no", "status docs")
    for marker in [
        "PUBLIC_LAUNCH_DECISION=GO",
        "public launch complete",
        "ACTUAL_SITE_EMBED_EXECUTION_STATUS=EXECUTED",
        "REAL_DOMAIN_SMOKE_STATUS=PASSED",
    ]:
        assert_not_contains(docs, marker, "status docs")
    for marker in ["api.anthropic.com", "ANTHROPIC_API_KEY", "sk-ant-", "DATABASE_URL"]:
        assert_not_contains(frontend, marker, "frontend widget")
    for path in [".env", ".local-secrets"]:
        if is_tracked(path):
            raise AssertionError(f"{path} must not be tracked")

    return {
        "status": "PASS",
        "checked_files": len(required_files),
        "decision_state": "BACKEND_LOCAL_OPERATOR_ANSWER_REVIEW_LEARNING_READY_PENDING_UI_REVIEW_AND_APPROVAL",
    }


def main() -> None:
    print(run_checks())


if __name__ == "__main__":
    main()
