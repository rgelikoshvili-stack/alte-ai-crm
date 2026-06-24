from app.services.website_sync_preview_service import reset_website_sync_preview_state


def add_source(client, **overrides):
    payload = {
        "name": "Official Alte website",
        "base_url": "https://alte.edu.ge",
        "allowed_paths": ["/ka", "/en"],
        "source_group_hint": "admissions_rules",
        "enabled": True,
        **overrides,
    }
    response = client.post("/api/knowledge/sync/website/sources", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def preview(client, source_id: str, url: str = "fixture://admissions-deadlines", **overrides):
    response = client.post(
        "/api/knowledge/sync/website/preview",
        json={
            "source_id": source_id,
            "url": url,
            "mode": "single_url",
            "limit": 5,
            "dry_run": True,
            **overrides,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_phase_10o_diff_endpoint_returns_review_shape_for_draft_run(client):
    reset_website_sync_preview_state()
    source = add_source(client)
    run = preview(client, source["id"])

    response = client.get(f"/api/knowledge/sync/website/diff/{run['run_id']}")
    assert response.status_code == 200, response.text
    diff = response.json()

    assert diff["run_id"] == run["run_id"]
    assert diff["source_url"] == "fixture://admissions-deadlines"
    assert diff["canonical_url"] == "https://alte.edu.ge/ka/admissions"
    assert diff["page_title"] == "Admissions deadlines"
    assert diff["status"] == "draft"
    assert diff["freshness_class"] == "variable"
    assert diff["source_group_guess"] == "admissions_rules"
    assert diff["approval_allowed"] is True
    assert diff["rejection_allowed"] is True
    assert diff["archive_available"] is False
    assert diff["public_usable"] is False
    assert diff["chunks_preview"]
    assert diff["old_approved_content"] == []
    assert diff["added_lines"]
    assert diff["removed_lines"] == []
    assert diff["content_hash_changed"] is True
    assert "No previous approved website content" in diff["detected_changes"][0]


def test_phase_10o_diff_detects_changed_hash_against_existing_approved_content(client):
    reset_website_sync_preview_state()
    source = add_source(client, source_group_hint="admissions_rules")
    first = preview(client, source["id"], url="fixture://admissions-deadlines")
    approve = client.post(f"/api/knowledge/sync/website/approve/{first['run_id']}", json={})
    assert approve.status_code == 200

    second = preview(client, source["id"], url="fixture://admissions-deadlines-updated")
    diff = client.get(f"/api/knowledge/sync/website/diff/{second['run_id']}").json()

    assert diff["approval_allowed"] is True
    assert diff["archive_available"] is True
    assert diff["content_hash_changed"] is True
    assert diff["added_lines"]
    assert diff["removed_lines"]
    assert "differs" in diff["detected_changes"][0]


def test_phase_10o_high_risk_flags_cover_deadline_tuition_and_stable_content(client):
    reset_website_sync_preview_state()
    admissions_source = add_source(client, source_group_hint="admissions_rules")
    admissions = preview(client, admissions_source["id"], url="fixture://admissions-deadlines")
    assert "high_risk_year_specific" in admissions["risk_flags"]
    assert "high_risk_deadlines" in admissions["risk_flags"]
    assert "high_risk_fixture_test_input" in admissions["risk_flags"]

    finance_source = add_source(client, name="Official finance", source_group_hint="finance_sources")
    tuition = preview(client, finance_source["id"], url="fixture://tuition")
    assert "high_risk_tuition_fees" in tuition["risk_flags"]
    assert "price_detected" in tuition["risk_flags"]
    assert "high_risk_fixture_test_input" in tuition["risk_flags"]

    program_source = add_source(client, name="Official programs", source_group_hint="program_catalog_sources")
    program = preview(client, program_source["id"], url="fixture://program-stable")
    assert program["freshness_class"] == "stable"
    assert "high_risk_ects_credits" in program["risk_flags"]
    assert "high_risk_deadlines" not in program["risk_flags"]
    assert "high_risk_tuition_fees" not in program["risk_flags"]


def test_phase_10o_archive_excludes_archived_by_default_and_blocks_retrieval(client):
    reset_website_sync_preview_state()
    source = add_source(client, source_group_hint="finance_sources")
    run = preview(client, source["id"], url="fixture://tuition-en")
    approve = client.post(f"/api/knowledge/sync/website/approve/{run['run_id']}", json={})
    assert approve.status_code == 200

    ask_before = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask_before.status_code == 200
    assert "12000 GEL" in ask_before.json()["answer"]

    rollback = client.post(f"/api/knowledge/sync/website/rollback/website_sync:{run['run_id']}", json={})
    assert rollback.status_code == 200
    assert rollback.json()["archived_count"] == run["chunks_count"]

    assert client.get("/api/knowledge/sync/website/approved").json() == []
    archived = client.get("/api/knowledge/sync/website/approved?include_archived=true").json()
    assert archived
    assert all(chunk["status"] == "archived" for chunk in archived)
    assert all(chunk["public_usable"] is False for chunk in archived)

    ask_after = client.post("/api/knowledge/ask", json={"question": "What is the Medicine tuition fee?", "language": "en"})
    assert ask_after.status_code == 200
    assert "12000 GEL" not in ask_after.json()["answer"]
