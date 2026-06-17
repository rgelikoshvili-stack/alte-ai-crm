from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx


BASE_URL = "https://alte-ai-crm-backend-226875230147.europe-west1.run.app"


def _safe_keys(payload: dict[str, Any]) -> list[str]:
    return sorted(str(key) for key in payload.keys())


async def main() -> int:
    session_payload = {
        "source_domain": "join.alte.edu.ge",
        "language": "en",
        "channel": "website_chat",
        "widget_variant": "pro_v2_safe",
    }
    messages = [
        "Hello, can you help me?",
        "What documents do international students need?",
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            session_response = await client.post(f"{BASE_URL}/chat/session/start", json=session_payload)
        except httpx.RequestError as exc:
            print(f"session_start_request_error={exc.__class__.__name__}")
            print("contact_details_sent=NO")
            print("handover_called=NO")
            print("intentional_lead_task_customer_creation=NO")
            print("production_chat_message_smoke=FAIL")
            return 1
        print(f"session_start_status={session_response.status_code}")
        if session_response.status_code != 200:
            print("session_start_failed")
            print("contact_details_sent=NO")
            print("handover_called=NO")
            print("intentional_lead_task_customer_creation=NO")
            print("production_chat_message_smoke=FAIL")
            return 1
        session_data = session_response.json()
        print("session_start_keys=" + json.dumps(_safe_keys(session_data)))

        conversation_id = session_data.get("conversation_id")
        session_id = session_data.get("session_id")
        if not conversation_id or not session_id:
            print("session_ids_missing")
            return 1

        for index, text in enumerate(messages, start=1):
            message_payload = {
                "conversation_id": conversation_id,
                "session_id": session_id,
                "message": text,
                "language": "en",
                "source_domain": "join.alte.edu.ge",
                "selected_department": "international",
                "selected_topic": "international_admissions",
                "page_url": "https://nimble-croissant-2f66e8.netlify.app/join.html",
                "widget_variant": "pro_v2_safe",
            }
            try:
                response = await client.post(f"{BASE_URL}/chat/message", json=message_payload)
            except httpx.RequestError as exc:
                print(f"message_{index}_request_error={exc.__class__.__name__}")
                print("contact_details_sent=NO")
                print("handover_called=NO")
                print("intentional_lead_task_customer_creation=NO")
                print("production_chat_message_smoke=FAIL")
                return 1
            print(f"message_{index}_status={response.status_code}")
            if response.status_code != 200:
                print(f"message_{index}_failed")
                print("contact_details_sent=NO")
                print("handover_called=NO")
                print("intentional_lead_task_customer_creation=NO")
                print("production_chat_message_smoke=FAIL")
                return 1
            data = response.json()
            print(f"message_{index}_keys=" + json.dumps(_safe_keys(data)))
            if not data.get("reply"):
                print(f"message_{index}_reply_missing")
                return 1

    print("contact_details_sent=NO")
    print("handover_called=NO")
    print("intentional_lead_task_customer_creation=NO")
    print("production_chat_message_smoke=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
