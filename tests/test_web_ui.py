from pathlib import Path

HTML = Path("frontend/index.html").read_text(encoding="utf-8")


def test_reference_driven_opportunity_ui_has_no_hardcoded_tumbler():
    assert "reusable insulated drink tumbler" not in HTML
    assert "proposed_subject" not in HTML
    assert "proposed_composition" not in HTML
    assert "differentiation_rationale" not in HTML


def test_reference_driven_opportunity_ui_selects_server_candidate():
    assert "sfCandidates" in HTML
    assert "selectedIndex" in HTML
    assert "opportunity_index:selectedIndex" in HTML
    assert "Select this opportunity" in HTML
    assert "Build Synchronized Plan" in HTML


def test_browser_flow_keeps_single_job_generation():
    assert "Generate 1 Asset" in HTML
    assert "exactly one generation job" in HTML
    assert "Tidak ada batch generation" in HTML


def test_generation_releases_gpu_before_separate_finalization():
    assert "Finalize 4×" in HTML
    assert "queueUpscale()" in HTML
    assert "/api/jobs/'+jobId+'/upscale" in HTML
    assert "Raw intermediate" in HTML
    assert "finalisasi 4× belum dijalankan" in HTML
