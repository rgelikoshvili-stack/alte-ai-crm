from app.scripts import (
    build_widget_asset_manifest,
    validate_final_launch_approvals,
    verify_phase_9l_m_n_final_launch_package,
)


def test_final_launch_approval_validator_importable():
    result = validate_final_launch_approvals.evaluate_approvals()

    assert "approval_status" in result
    assert "go_allowed" in result


def test_widget_asset_manifest_builder_importable():
    manifest = build_widget_asset_manifest.build_manifest()

    assert "Widget Asset Manifest" in manifest
    assert "dist/widget/alte-ai-chat-widget.js" in manifest


def test_final_launch_package_verifier_importable():
    assert verify_phase_9l_m_n_final_launch_package.NO_GO_DECISION.endswith("SITE_EMBED")


def test_final_docs_exist():
    required = [
        verify_phase_9l_m_n_final_launch_package.APPROVAL_INTAKE,
        verify_phase_9l_m_n_final_launch_package.HANDOFF_PACKAGE,
        verify_phase_9l_m_n_final_launch_package.ASSET_MANIFEST,
        verify_phase_9l_m_n_final_launch_package.ACTUAL_EMBED_RESULT,
        verify_phase_9l_m_n_final_launch_package.REAL_DOMAIN_SMOKE_PLAN,
        verify_phase_9l_m_n_final_launch_package.REAL_DOMAIN_SMOKE_RESULT,
        verify_phase_9l_m_n_final_launch_package.PUBLIC_LAUNCH_DECISION,
    ]

    assert all(path.exists() for path in required)


def test_no_go_status_valid_when_approvals_or_site_embed_missing():
    result = validate_final_launch_approvals.evaluate_approvals()

    assert result["approval_status"] == "NO_GO"
    assert result["go_allowed"] is False
    assert result["missing_blockers"]


def test_public_launch_not_marked_go_without_required_evidence():
    decision = verify_phase_9l_m_n_final_launch_package.PUBLIC_LAUNCH_DECISION.read_text(encoding="utf-8")
    evidence_check = verify_phase_9l_m_n_final_launch_package.go_has_required_evidence()

    assert "PUBLIC_LAUNCH_DECISION=GO_APPROVED_FOR_PUBLIC_LAUNCH" not in decision
    assert evidence_check.passed is True


def test_widget_assets_have_no_direct_anthropic_endpoint():
    assert verify_phase_9l_m_n_final_launch_package.production_assets_are_safe().passed is True


def test_widget_assets_have_backend_chat_routes():
    assert verify_phase_9l_m_n_final_launch_package.production_assets_have_backend_routes().passed is True


def test_no_forbidden_secret_patterns_in_production_assets():
    assert verify_phase_9l_m_n_final_launch_package.production_assets_are_safe().passed is True


def test_final_launch_package_all_checks_pass():
    checks = verify_phase_9l_m_n_final_launch_package.run_checks()

    assert all(check.passed for check in checks)
