def test_widget_session_start_accepts_channel_source_domain_and_language(client):
    response = client.post(
        "/chat/session/start",
        json={
            "channel": "website_chat",
            "source_domain": "join.alte.edu.ge",
            "language": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"]
    assert data["session_id"]
    assert data["source_domain"] == "join.alte.edu.ge"


def test_widget_message_accepts_source_domain_and_language(client):
    session = client.post(
        "/chat/session/start",
        json={
            "channel": "website_chat",
            "source_domain": "alte.edu.ge",
            "language": "ka",
        },
    ).json()

    response = client.post(
        "/chat/message",
        json={
            "conversation_id": session["conversation_id"],
            "session_id": session["session_id"],
            "message": "სად მდებარეობს უნივერსიტეტი?",
            "source_domain": "alte.edu.ge",
            "language": "ka",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == session["conversation_id"]
    assert data["reply"]
