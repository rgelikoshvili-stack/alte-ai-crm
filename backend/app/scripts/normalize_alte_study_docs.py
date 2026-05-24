from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "knowledge_evidence" / "alte_study_docs"
SEED_DIR = BACKEND_ROOT / "app" / "knowledge_seed" / "alte_study_docs"
REPORTS_DIR = BACKEND_ROOT / "reports"
SEED_PATH = SEED_DIR / "alte_study_docs_seed_v1.json"
SUMMARY_JSON = REPORTS_DIR / "alte_study_docs_normalization_summary.json"
SUMMARY_MD = REPORTS_DIR / "alte_study_docs_normalization_summary.md"

SOURCE_FILES = [
    "AI_CRM_Needs_Detailed.txt",
    "Alte_AI_CRM_Chatbot_Codex_Master_Plan_GEO.txt",
    "Alte_AI_CRM_Chatbot_Complete_Master_Plan_GEO.txt",
    "Alte_AI_CRM_Master_Plan_v3_FINAL.txt",
    "Alte_AI_CRM_v2_Additions.txt",
]


def build_seed_records() -> list[dict[str, Any]]:
    return [
        {
            "source_key": "alte_study_programs_overview_v1",
            "title": "Study programs overview - KA",
            "language": "ka",
            "category": "program_overview",
            "department": "Admissions",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "ალტეს ჩათბოტმა სასწავლო პროგრამების კითხვებზე უნდა უპასუხოს Knowledge Base-ზე დაყრდნობით. "
                "სასწავლო მიმართულებების კონტექსტში ფაილებში ნახსენებია საბაკალავრო, სამაგისტრო და ერთსაფეხურიანი "
                "სამედიცინო პროგრამები, ასევე Business, Law, Psychology, International Relations, Tourism, "
                "Computer Science, AI & Data Analytics და Journalism. კონკრეტული პროგრამის დეტალები, ენა, ხანგრძლივობა "
                "ან მიღების პირობა უნდა დადასტურდეს აქტიური ოფიციალური წყაროდან ან კონსულტანტთან."
            ),
            "keywords": [
                "სასწავლო პროგრამები",
                "პროგრამები",
                "ბაკალავრიატი",
                "მაგისტრატურა",
                "Business",
                "Law",
                "Psychology",
                "Tourism",
                "Computer Science",
                "AI",
                "Journalism",
            ],
            "sensitivity": "medium",
            "stale_after_days": 90,
        },
        {
            "source_key": "alte_study_programs_overview_v1",
            "title": "Study programs overview - EN",
            "language": "en",
            "category": "program_overview",
            "department": "Admissions",
            "source_domain": "join.alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "For study program questions, the chatbot should answer only from active Knowledge Base sources. "
                "The study documents mention bachelor, master and one-step medical programs, including Business, "
                "Law, Psychology, International Relations, Tourism, Computer Science, AI & Data Analytics and "
                "Journalism. Exact program requirements, language, duration or admission rules must be confirmed "
                "from an active official source or by an admissions consultant."
            ),
            "keywords": [
                "study programs",
                "programs",
                "bachelor",
                "master",
                "business",
                "law",
                "psychology",
                "tourism",
                "computer science",
                "medicine",
            ],
            "sensitivity": "medium",
            "stale_after_days": 90,
        },
        {
            "source_key": "alte_study_admissions_rules_v1",
            "title": "Admissions interest without contact - KA",
            "language": "ka",
            "category": "admissions_general",
            "department": "Admissions",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": False,
            "content": (
                "თუ მომხმარებელი დაინტერესებულია პროგრამით, ჩარიცხვით ან კონსულტაციით, მაგრამ არ ტოვებს ტელეფონს "
                "ან ელფოსტას, ბოტმა უნდა სთხოვოს საკონტაქტო მონაცემები და არ უნდა შექმნას lead/task. საუბარი და "
                "AI summary შეიძლება შეინახოს."
            ),
            "keywords": ["ჩარიცხვა", "მიღება", "კონსულტაცია", "საკონტაქტო", "lead"],
            "sensitivity": "medium",
            "stale_after_days": 120,
        },
        {
            "source_key": "alte_study_admissions_rules_v1",
            "title": "Admissions interest with contact - EN",
            "language": "en",
            "category": "admissions_general",
            "department": "Admissions",
            "source_domain": "join.alte.edu.ge",
            "status": "approved",
            "review_required": False,
            "content": (
                "Admission, program or consultation interest should create or update a customer, lead and follow-up "
                "task only after phone or email exists. Without contact data, the chatbot should ask for the missing "
                "contact fields and keep the interaction as conversation context."
            ),
            "keywords": ["admission", "apply", "consultation", "phone", "email", "lead"],
            "sensitivity": "medium",
            "stale_after_days": 120,
        },
        {
            "source_key": "alte_study_required_documents_v1",
            "title": "Required documents safe answer - KA",
            "language": "ka",
            "category": "required_documents",
            "department": "Admissions",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "საბუთების ზუსტი სია არ უნდა გამოიგონოს ბოტმა. შეუძლია თქვას, რომ საჭირო დოკუმენტები დამოკიდებულია "
                "პროგრამაზე და აპლიკანტის სტატუსზე, ხოლო საბოლოო სია უნდა დადასტურდეს Admissions გუნდთან ან აქტიურ "
                "ოფიციალურ წყაროსთან."
            ),
            "keywords": ["საბუთები", "დოკუმენტები", "ჩარიცხვა", "მიღება", "Admissions"],
            "sensitivity": "high",
            "stale_after_days": 30,
        },
        {
            "source_key": "alte_study_finance_policy_v1",
            "title": "Tuition and fees safe answer - KA",
            "language": "ka",
            "category": "finance_tuition",
            "department": "Finance",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "სწავლის საფასურის, გადასახადის, გრანტის ან დაფინანსების ზუსტი თანხა ბოტმა არ უნდა გამოიგონოს. "
                "თუ აქტიური ოფიციალური წყარო არ არის, პასუხი უნდა იყოს კონსერვატიული: ზუსტი თანხა უნდა დადასტურდეს "
                "Finance ან Admissions გუნდთან."
            ),
            "keywords": ["სწავლის საფასური", "საფასური", "გადასახადი", "გრანტი", "დაფინანსება", "tuition"],
            "sensitivity": "high",
            "stale_after_days": 30,
        },
        {
            "source_key": "alte_study_deadline_policy_v1",
            "title": "Deadlines safe answer - KA",
            "language": "ka",
            "category": "deadlines_calendar",
            "department": "Academic Registry",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "ჩარიცხვის, განაცხადის, გამოცდის ან აკადემიური კალენდრის ზუსტი ვადები ბოტმა არ უნდა გამოიგონოს. "
                "თუ აქტიური ოფიციალური წყარო არ არის, ბოტმა უნდა გადაამისამართოს Admissions ან Academic Registry გუნდთან."
            ),
            "keywords": ["ვადა", "ვადები", "კალენდარი", "გამოცდა", "ჩარიცხვა", "deadline"],
            "sensitivity": "high",
            "stale_after_days": 30,
        },
        {
            "source_key": "alte_study_international_admissions_v1",
            "title": "International admissions routing - EN",
            "language": "en",
            "category": "international_admissions",
            "department": "International Admissions",
            "source_domain": "join.alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "International student questions should route to International Admissions. Country, city, interested "
                "program and intake should be preserved in the conversation analysis. Exact document, visa, relocation, "
                "deadline, eligibility or tuition requirements must not be invented and require official confirmation."
            ),
            "keywords": ["international", "join.alte.edu.ge", "country", "visa", "documents", "admission"],
            "sensitivity": "high",
            "stale_after_days": 60,
        },
        {
            "source_key": "alte_study_medicine_md_v1",
            "title": "Medicine MD routing - EN",
            "language": "en",
            "category": "medicine_md",
            "department": "International Admissions",
            "source_domain": "join.alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "program_name": "Medicine / MD",
            "content": (
                "Medicine or MD interest should be treated as a separate medical track and routed to the Medicine "
                "pipeline or International Admissions. Without phone or email, no lead/task should be created; the bot "
                "should ask for contact details. Exact MD requirements, documents, tuition and deadlines require an "
                "approved official source."
            ),
            "keywords": ["medicine", "MD", "medical", "India", "international", "pipeline"],
            "sensitivity": "high",
            "stale_after_days": 60,
        },
        {
            "source_key": "alte_study_contact_v1",
            "title": "Alte contact from study docs - KA",
            "language": "ka",
            "category": "general_contact",
            "department": "General",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": True,
            "content": (
                "სწავლის დოკუმენტებში მითითებულია საკონტაქტო ინფორმაცია: Tbilisi, University St. N10, ZIP 0177; "
                "(+995 32) 2 40 29 46/48; info@alte.edu.ge. საჯარო პასუხისთვის ეს ინფორმაცია მაინც უნდა "
                "გადამოწმდეს ოფიციალურ წყაროსთან, თუ stale ან source missing მდგომარეობაა."
            ),
            "keywords": ["კონტაქტი", "მისამართი", "ტელეფონი", "ელფოსტა", "info@alte.edu.ge"],
            "sensitivity": "low",
            "stale_after_days": 90,
        },
        {
            "source_key": "alte_study_handover_policy_v1",
            "title": "Fallback and human handover policy - KA",
            "language": "ka",
            "category": "handover",
            "department": "Admissions",
            "source_domain": "alte.edu.ge",
            "status": "approved",
            "review_required": False,
            "content": (
                "თუ confidence ნაკლებია 0.70-ზე, აქტიური წყარო არ მოიძებნა, ან კითხვა ეხება ფასს, ვადას, გრანტს, "
                "საბუთებს ან ოფიციალურ მოთხოვნებს წყაროს გარეშე, ბოტმა უნდა გამოიყენოს fallback პასუხი და შესთავაზოს "
                "ადამიანთან გადამისამართება."
            ),
            "keywords": ["handover", "ადამიანი", "ოპერატორი", "confidence", "fallback"],
            "sensitivity": "medium",
            "stale_after_days": 120,
        },
    ]


def summarize_source_files() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for name in SOURCE_FILES:
        path = EVIDENCE_DIR / name
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        items.append(
            {
                "file": name,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
                "lines": len(text.splitlines()) if text else 0,
            }
        )
    return items


def main() -> None:
    missing = [name for name in SOURCE_FILES if not (EVIDENCE_DIR / name).exists()]
    if missing:
        raise SystemExit(f"Missing study evidence files: {', '.join(missing)}")

    SEED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    records = build_seed_records()
    SEED_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_dir": str(EVIDENCE_DIR.relative_to(PROJECT_ROOT)),
        "source_files": summarize_source_files(),
        "records": len(records),
        "approved_status_records": sum(1 for item in records if item["status"] == "approved"),
        "review_required_records": sum(1 for item in records if item["review_required"]),
        "high_sensitivity_records": sum(1 for item in records if item["sensitivity"] == "high"),
        "seed_path": str(SEED_PATH.relative_to(PROJECT_ROOT)),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SUMMARY_MD.write_text(render_summary_markdown(summary), encoding="utf-8")

    print(
        json.dumps(
            {
                "records": summary["records"],
                "review_required_records": summary["review_required_records"],
                "high_sensitivity_records": summary["high_sensitivity_records"],
                "seed_path": summary["seed_path"],
                "summary_path": str(SUMMARY_JSON.relative_to(PROJECT_ROOT)),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Alte Study Docs Knowledge Normalization Summary",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "## Source Files",
        "",
    ]
    for item in summary["source_files"]:
        lines.append(f"- `{item['file']}`: exists={item['exists']}, bytes={item['bytes']}, lines={item['lines']}")
    lines.extend(
        [
            "",
            "## Output",
            "",
            f"- Seed path: `{summary['seed_path']}`",
            f"- Records: {summary['records']}",
            f"- Review-required records: {summary['review_required_records']}",
            f"- High-sensitivity records: {summary['high_sensitivity_records']}",
            "",
            "Sensitive facts such as tuition, deadlines, required documents, Medicine/MD, international admissions,",
            "visa/relocation and official requirements remain review-required and must not be treated as final public",
            "launch approval.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
