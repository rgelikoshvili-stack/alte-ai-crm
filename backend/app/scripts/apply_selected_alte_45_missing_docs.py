from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

from google.cloud.sql.connector import create_async_connector
from google.oauth2.credentials import Credentials
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import KnowledgeSnippet, KnowledgeSource


DEFAULT_PACKAGE_DIR = Path(
    r"C:\Users\Acer\Documents\Codex\2026-05-19\unexpected-status-403-forbidden-detail-code\alte_documents"
)
DEFAULT_INSTANCE_CONNECTION_NAME = "project-1e145fd0-c30e-4aac-a34:europe-west1:alte-ai-crm-db"
OWNER = "phase_9aa_selected_alte_45_missing_docs"
SOURCE_DOMAIN = "alte.edu.ge"


SELECTED_DOCUMENTS = [
    {
        "number": 10,
        "requested_title": "ინდივიდუალური სასწავლო გეგმის შემუშავების მეთოდოლოგია",
        "local_path": r"alte_documents\files\063_RRPR4gLRZ4.pdf",
        "category": "academic_registry",
        "department": "academic_registry",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "conservative_for_personal_cases",
    },
    {
        "number": 11,
        "requested_title": "სტუდენტთა ინდივიდუალური სასწავლო გეგმის შემუშავების მეთოდოლოგია",
        "local_path": r"alte_documents\files\098_q1YQAQhajF.pdf",
        "category": "academic_registry",
        "department": "academic_registry",
        "language": "en",
        "sensitivity": "medium",
        "answer_policy": "conservative_for_personal_cases",
    },
    {
        "number": 12,
        "requested_title": "ელექტრონული სწავლების ადმინისტრირების წესი",
        "local_path": r"alte_documents\files\058_lCBeyC0gSb.pdf",
        "category": "student_services",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_technical",
    },
    {
        "number": 14,
        "requested_title": "Examination Regulations",
        "local_path": r"alte_documents\files\076_ExaminationRegulations.pdf",
        "category": "exams",
        "department": "academic_registry",
        "language": "en",
        "sensitivity": "medium",
        "answer_policy": "conservative_for_personal_cases",
    },
    {
        "number": 15,
        "requested_title": "პლაგიატი, მისი ფორმები, პრევენციის საშუალებები და სანქციები",
        "local_path": r"alte_documents\files\065_QlAZe56OHS.pdf",
        "category": "academic_integrity",
        "department": "academic_registry",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_case",
    },
    {
        "number": 16,
        "requested_title": "ეთიკის კოდექსი",
        "local_path": r"alte_documents\files\074_vQyJ19AYWH.pdf",
        "category": "ethics",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_case",
    },
    {
        "number": 18,
        "requested_title": "სტუდენტთა უფლებებისა და კანონიერი ინტერესების დაცვის მექანიზმები",
        "local_path": r"alte_documents\files\095_LHzTgcc2Rc.pdf",
        "category": "student_rights",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_complaint",
    },
    {
        "number": 19,
        "requested_title": "სტუდენტური ომბუდსმენის დებულება",
        "local_path": r"alte_documents\files\080_73ut09R5Pa.pdf",
        "category": "ombudsman",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_complaint",
    },
    {
        "number": 20,
        "requested_title": "ომბუდსმენი",
        "local_path": r"alte_documents\files\030_F9yutbkbxH.pdf",
        "category": "ombudsman",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_complaint",
    },
    {
        "number": 21,
        "requested_title": "თვითმმართველობის დებულება",
        "local_path": r"alte_documents\files\082_6tvL7mhYc7.pdf",
        "category": "student_self_government",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 22,
        "requested_title": "სტუდენტების არჩევის წესი",
        "local_path": r"alte_documents\files\007_yfZG9xzy2l.pdf",
        "category": "student_governance",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 23,
        "requested_title": "სკოლის საბჭოებში მონაწილეობის წესი",
        "local_path": r"alte_documents\files\008_lg07GuicOD.pdf",
        "category": "student_governance",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 24,
        "requested_title": "ბიბლიოთეკის დებულება",
        "local_path": r"alte_documents\files\068_TRphmMn9Xg.pdf",
        "category": "library",
        "department": "library",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 25,
        "requested_title": "ბიბლიოთეკით სარგებლობის წესები",
        "local_path": r"alte_documents\files\086_e1Y852YO2T.pdf",
        "category": "library",
        "department": "library",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 26,
        "requested_title": "ბიბლიოთეკის წესები DOCX",
        "local_path": r"alte_documents\files\087_uLr992q8e0.docx",
        "category": "library",
        "department": "library",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 27,
        "requested_title": "კარიერული განვითარებისა და კურსდამთავრებულთა მომსახურების წესი",
        "local_path": r"alte_documents\files\092_UM4rez8Sgq.pdf",
        "category": "career",
        "department": "career",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 28,
        "requested_title": "Rules of Career Development of Students and Services of Alumni",
        "local_path": r"alte_documents\files\093_jHEsy8iDO8.pdf",
        "category": "career",
        "department": "career",
        "language": "en",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 29,
        "requested_title": "სპეციალური საჭიროების მქონე პირთა მომსახურების წესი",
        "local_path": r"alte_documents\files\088_Wmnayjohgb.pdf",
        "category": "special_needs",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_personal",
    },
    {
        "number": 30,
        "requested_title": "სსმ პირთა მომსახურების წესი",
        "local_path": r"alte_documents\files\089_fI35AQtlhc.pdf",
        "category": "special_needs",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_personal",
    },
    {
        "number": 32,
        "requested_title": "დაფინანსების წესი",
        "local_path": r"alte_documents\files\114_D87lOzA1tj.pdf",
        "category": "finance",
        "department": "finance",
        "language": "ka",
        "sensitivity": "high",
        "answer_policy": "conservative_handover_for_eligibility",
    },
    {
        "number": 33,
        "requested_title": "აკადემიური მიღწევებისთვის დეკანის გრანტის დანიშვნის წესი",
        "local_path": r"alte_documents\files\096_au4xEQ3RLj.pdf",
        "category": "finance",
        "department": "finance",
        "language": "ka",
        "sensitivity": "high",
        "answer_policy": "conservative_handover_for_eligibility",
    },
    {
        "number": 34,
        "requested_title": "Dean's List Award Terms and Conditions",
        "local_path": r"alte_documents\files\097_jTV38r4nF8.pdf",
        "category": "finance",
        "department": "finance",
        "language": "en",
        "sensitivity": "high",
        "answer_policy": "conservative_handover_for_eligibility",
    },
    {
        "number": 36,
        "requested_title": "გენერაციული ხელოვნური ინტელექტის გამოყენების პოლიტიკა",
        "local_path": r"alte_documents\files\131_yM6EMjQz9I.pdf",
        "category": "ai_policy",
        "department": "academic_registry",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_case",
    },
    {
        "number": 37,
        "requested_title": "Generative Artificial Intelligence Usage Policy",
        "local_path": r"alte_documents\files\132_UPP7tK2imL.pdf",
        "category": "ai_policy",
        "department": "academic_registry",
        "language": "en",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_case",
    },
    {
        "number": 38,
        "requested_title": "ინფორმაციული ტექნოლოგიების მართვის პოლიტიკა და ინფრასტრუქტურა",
        "local_path": r"alte_documents\files\106_3cvbwTPgx5.pdf",
        "category": "it_policy",
        "department": "it_support",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_technical",
    },
    {
        "number": 39,
        "requested_title": "IRO Policy",
        "local_path": r"alte_documents\files\115_C8hEJJ7ftX.pdf",
        "category": "iro_policy",
        "department": "international",
        "language": "en",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_personal",
    },
    {
        "number": 40,
        "requested_title": "IRO Policy Annex",
        "local_path": r"alte_documents\files\116_iz3giyVdLF.pdf",
        "category": "iro_policy",
        "department": "international",
        "language": "en",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_personal",
    },
    {
        "number": 41,
        "requested_title": "მდგრადი განვითარების სტრატეგია",
        "local_path": r"alte_documents\files\119_Gjvu8QaVrf.pdf",
        "category": "sustainability",
        "department": "student_services",
        "language": "ka",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 42,
        "requested_title": "Alte Sustainability Strategy",
        "local_path": r"alte_documents\files\120_kyxH61FeCu.pdf",
        "category": "sustainability",
        "department": "student_services",
        "language": "en",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 43,
        "requested_title": "Sustainability Report 2024",
        "local_path": r"alte_documents\files\121_KBTF24F2Dw.pdf",
        "category": "sustainability",
        "department": "student_services",
        "language": "en",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 44,
        "requested_title": "EDI Policy",
        "local_path": r"alte_documents\files\122_vj966IoEsX.pdf",
        "category": "edi_policy",
        "department": "student_services",
        "language": "en",
        "sensitivity": "low",
        "answer_policy": "direct_general",
    },
    {
        "number": 45,
        "requested_title": "კვლევითი კომპონენტის დაგეგმვის/განხილვის/შეფასების მექანიზმები",
        "local_path": r"alte_documents\files\112_9NYXk63jy8.pdf",
        "category": "research_component",
        "department": "academic_registry",
        "language": "ka",
        "sensitivity": "medium",
        "answer_policy": "direct_general_handover_case",
    },
]


def source_key_for(doc: dict) -> str:
    file_stem = Path(doc["local_path"]).stem.lower().replace(" ", "_")
    return f"selected_alte_45_doc_{doc['number']:02d}_{file_stem}"[:160]


def snippet_key_for(doc: dict, chunk_index: int) -> str:
    return f"{source_key_for(doc)}_chunk_{chunk_index:03d}"[:160]


def load_selected_chunks(package_dir: Path) -> tuple[list[dict], list[dict]]:
    chunks_path = package_dir / "alte_documents_chunks.jsonl"
    if not chunks_path.exists():
        raise FileNotFoundError(f"Missing chunks JSONL: {chunks_path}")
    wanted = {doc["local_path"]: doc for doc in SELECTED_DOCUMENTS}
    found_paths: set[str] = set()
    rows: list[dict] = []
    with chunks_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            doc = wanted.get(row.get("local_path"))
            if doc is None:
                continue
            found_paths.add(doc["local_path"])
            rows.append({**row, "selected_doc": doc})
    missing = [doc for doc in SELECTED_DOCUMENTS if doc["local_path"] not in found_paths]
    return rows, missing


def summarize(rows: list[dict], missing: list[dict]) -> dict:
    by_doc = defaultdict(lambda: {"chunks": 0, "source_title": None, "source_filename": None})
    for row in rows:
        doc = row["selected_doc"]
        item = by_doc[doc["requested_title"]]
        item["chunks"] += 1
        item["source_title"] = row.get("title") or doc["requested_title"]
        item["source_filename"] = Path(doc["local_path"]).name
    return {
        "selected_documents": len(SELECTED_DOCUMENTS),
        "processable_documents": len(by_doc),
        "total_chunks": len(rows),
        "chunks_by_requested_title": dict(sorted(by_doc.items())),
        "missing_local_documents": [
            {"number": doc["number"], "requested_title": doc["requested_title"], "local_path": doc["local_path"]}
            for doc in missing
        ],
    }


def database_parts() -> tuple[str, str, str]:
    raw_url = os.environ.get("DATABASE_URL")
    if not raw_url:
        raise RuntimeError("DATABASE_URL must be set without printing it")
    url = make_url(raw_url)
    if not url.username or not url.password or not url.database:
        raise RuntimeError("DATABASE_URL is missing required connection fields")
    return url.username, url.password, url.database


def connector_credentials() -> Credentials:
    token = os.environ.get("GCLOUD_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("GCLOUD_ACCESS_TOKEN must be set without printing it")
    return Credentials(token=token)


async def apply_rows(rows: list[dict]) -> dict:
    user, password, db_name = database_parts()
    instance_connection_name = os.environ.get("CLOUD_SQL_INSTANCE_CONNECTION_NAME", DEFAULT_INSTANCE_CONNECTION_NAME)
    connector = await create_async_connector(credentials=connector_credentials())

    async def getconn():
        return await connector.connect_async(
            instance_connection_name,
            "asyncpg",
            user=user,
            password=password,
            db=db_name,
        )

    engine = create_async_engine("postgresql+asyncpg://", async_creator=getconn, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["selected_doc"]["local_path"]].append(row)

    summary = Counter()
    async with session_factory() as db:
        for doc_path, doc_rows in grouped.items():
            doc = doc_rows[0]["selected_doc"]
            source_key = source_key_for(doc)
            source = await db.scalar(select(KnowledgeSource).where(KnowledgeSource.source_key == source_key))
            source_values = {
                "title": doc["requested_title"][:255],
                "source_type": "official_alte_document_package",
                "status": "approved",
                "language": doc["language"],
                "source_url": doc_rows[0].get("source_url"),
                "source_domain": SOURCE_DOMAIN,
                "category": doc["category"],
                "sensitivity": doc["sensitivity"],
                "review_required": False,
                "stale_after_days": 365,
                "owner": OWNER,
            }
            if source is None:
                source = KnowledgeSource(source_key=source_key, **source_values)
                db.add(source)
                await db.flush()
                summary["sources_created"] += 1
            else:
                changed = False
                for field, value in source_values.items():
                    if getattr(source, field) != value:
                        setattr(source, field, value)
                        changed = True
                summary["sources_updated"] += int(changed)

            for row in doc_rows:
                chunk_index = int(row.get("chunk_index") or 0)
                snippet_key = snippet_key_for(doc, chunk_index)
                content = "\n\n".join(
                    [
                        f"Source title: {doc['requested_title']}",
                        f"Source file: {Path(doc_path).name}",
                        f"Answer policy: {doc['answer_policy']}",
                        str(row.get("text") or "").strip(),
                    ]
                ).strip()
                content_hash = sha256(content.encode("utf-8")).hexdigest()
                snippet = await db.scalar(select(KnowledgeSnippet).where(KnowledgeSnippet.source_key == snippet_key))
                snippet_values = {
                    "source_id": source.id,
                    "title": f"{doc['requested_title']} c.{chunk_index}"[:255],
                    "content": content,
                    "category": doc["category"],
                    "source_domain": SOURCE_DOMAIN,
                    "sensitivity": doc["sensitivity"],
                    "review_required": False,
                    "stale_after_days": 365,
                    "content_hash": content_hash,
                    "program_name": None,
                    "keywords": build_keywords(doc, row),
                    "status": "approved",
                    "language": doc["language"],
                }
                if snippet is None:
                    snippet = KnowledgeSnippet(source_key=snippet_key, **snippet_values)
                    db.add(snippet)
                    summary["snippets_created"] += 1
                else:
                    changed = False
                    for field, value in snippet_values.items():
                        if getattr(snippet, field) != value:
                            setattr(snippet, field, value)
                            changed = True
                    summary["snippets_updated"] += int(changed)

        source_count = await db.scalar(select(func.count(KnowledgeSource.id)).where(KnowledgeSource.owner == OWNER))
        snippet_count = await db.scalar(select(func.count(KnowledgeSnippet.id)).where(KnowledgeSnippet.source_domain == SOURCE_DOMAIN, KnowledgeSnippet.source_key.like("selected_alte_45_doc_%")))
        approved_snippet_count = await db.scalar(
            select(func.count(KnowledgeSnippet.id)).where(
                KnowledgeSnippet.source_domain == SOURCE_DOMAIN,
                KnowledgeSnippet.source_key.like("selected_alte_45_doc_%"),
                KnowledgeSnippet.status == "approved",
            )
        )
        await db.commit()

    await engine.dispose()
    await connector.close_async()
    return {
        **summary,
        "production_selected_source_count": source_count,
        "production_selected_snippet_count": snippet_count,
        "production_selected_approved_snippet_count": approved_snippet_count,
    }


def build_keywords(doc: dict, row: dict) -> str:
    values = [
        doc["requested_title"],
        doc["category"],
        doc["department"],
        row.get("title") or "",
        row.get("category") or "",
        row.get("section") or "",
        Path(doc["local_path"]).name,
    ]
    return " ".join(item for item in values if item)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply selected missing Alte official documents from local documentation package.")
    parser.add_argument("--package-dir", default=str(DEFAULT_PACKAGE_DIR))
    parser.add_argument("--apply", action="store_true", help="Write selected sources/snippets to production KB.")
    args = parser.parse_args()

    rows, missing = load_selected_chunks(Path(args.package_dir))
    summary = summarize(rows, missing)
    if not args.apply:
        print(json.dumps({"mode": "dry-run", "would_write": False, **summary}, ensure_ascii=False, indent=2))
        return
    result = asyncio.run(apply_rows(rows))
    print(json.dumps({"mode": "apply", "would_write": True, **summary, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
