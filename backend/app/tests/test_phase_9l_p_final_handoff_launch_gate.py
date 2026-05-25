from app.scripts import build_widget_asset_manifest, verify_phase_9l_p_final_handoff_launch_gate


def test_build_widget_asset_manifest_importable():
    manifest = build_widget_asset_manifest.build_manifest()

    assert "Widget Asset Manifest" in manifest
    assert "DATABASE_URL absent" in manifest


def test_phase_9l_p_verifier_importable():
    assert verify_phase_9l_p_final_handoff_launch_gate.DECISION_STATE.endswith("SITE_EMBED_AND_SMOKE")


def test_final_handoff_docs_exist():
    required = [
        verify_phase_9l_p_final_handoff_launch_gate.APPROVAL_RECORD,
        verify_phase_9l_p_final_handoff_launch_gate.HANDOFF_PACKAGE,
        verify_phase_9l_p_final_handoff_launch_gate.ALTE_SNIPPET,
        verify_phase_9l_p_final_handoff_launch_gate.JOIN_SNIPPET,
        verify_phase_9l_p_final_handoff_launch_gate.ASSET_MANIFEST,
        verify_phase_9l_p_final_handoff_launch_gate.ASSET_HANDOFF_RESULT,
        verify_phase_9l_p_final_handoff_launch_gate.SITE_EMBED_DECISION,
        verify_phase_9l_p_final_handoff_launch_gate.SITE_EMBED_CHECKLIST,
        verify_phase_9l_p_final_handoff_launch_gate.SMOKE_RESULT,
        verify_phase_9l_p_final_handoff_launch_gate.PUBLIC_LAUNCH_DECISION,
    ]

    assert all(path.exists() for path in required)


def test_asset_manifest_exists():
    assert verify_phase_9l_p_final_handoff_launch_gate.ASSET_MANIFEST.exists()


def test_actual_embed_not_executed():
    text = verify_phase_9l_p_final_handoff_launch_gate.SITE_EMBED_DECISION.read_text(encoding="utf-8")

    assert "ACTUAL_SITE_EMBED_EXECUTION_STATUS=NOT_EXECUTED_PENDING_FINAL_CONFIRMATION" in text
    assert verify_phase_9l_p_final_handoff_launch_gate.actual_embed_not_complete().passed is True


def test_real_domain_smoke_not_executed():
    text = verify_phase_9l_p_final_handoff_launch_gate.SMOKE_RESULT.read_text(encoding="utf-8")

    assert "REAL_DOMAIN_SMOKE_STATUS=NOT_EXECUTED_SITE_NOT_EMBEDDED" in text
    assert verify_phase_9l_p_final_handoff_launch_gate.real_domain_smoke_not_passed().passed is True


def test_public_launch_no_go():
    text = verify_phase_9l_p_final_handoff_launch_gate.PUBLIC_LAUNCH_DECISION.read_text(encoding="utf-8")

    assert "PUBLIC_LAUNCH_DECISION=NO_GO_PENDING_SITE_EMBED_AND_REAL_DOMAIN_SMOKE" in text
    assert verify_phase_9l_p_final_handoff_launch_gate.public_launch_not_complete().passed is True


def test_final_decision_state_exists():
    assert verify_phase_9l_p_final_handoff_launch_gate.docs_record_decision_state().passed is True


def test_production_widget_dist_assets_have_no_direct_anthropic_endpoint():
    assert verify_phase_9l_p_final_handoff_launch_gate.production_assets_are_safe().passed is True


def test_no_forbidden_secret_patterns():
    assert verify_phase_9l_p_final_handoff_launch_gate.production_assets_are_safe().passed is True


def test_phase_9l_p_all_checks_pass():
    checks = verify_phase_9l_p_final_handoff_launch_gate.run_checks()

    assert all(check.passed for check in checks)
