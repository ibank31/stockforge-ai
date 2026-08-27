import json
from pathlib import Path

from scripts.run_backlog_preview_batch import make_plan, validate_plan


BACKLOG = Path('/home/ubuntu/stockforge-backlog-v2/StockForge_Backlog_v2_2026-08-27.json')


def load_backlog():
    return json.loads(BACKLOG.read_text(encoding='utf-8'))


def test_backlog_plan_preserves_prompt_contract_and_routes():
    backlog = load_backlog()
    plan = make_plan(backlog, 'test-batch')
    checks = validate_plan(plan)

    assert len(plan['briefs']) == 30
    assert sum(item['asset_spec']['delivery_format'] == 'jpeg' for item in plan['briefs']) == 15
    assert sum(item['asset_spec']['delivery_format'] == 'png' for item in plan['briefs']) == 15
    assert len(checks) == 30
    assert all(item['gpu_eligible'] for item in checks)
    assert plan['quality_policy']['batch_size'] == 1
    assert plan['quality_policy']['kaggle_auto_submit'] is False

    source_by_id = {item['id']: item for item in backlog['candidates']}
    for brief in plan['briefs']:
        source = source_by_id[brief['brief_id']]
        package = brief['prompt_package']
        assert package['prompt'] == source['generation_prompt']
        assert package['negative_prompt'] == source['negative_prompt']
        assert brief['metadata']['human_review_required'] is True
        assert brief['metadata']['status'] == 'human_review_required'


def test_png_route_is_true_alpha_trial_and_never_jpeg():
    plan = make_plan(load_backlog(), 'test-batch')
    png_briefs = [brief for brief in plan['briefs'] if brief['asset_spec']['delivery_format'] == 'png']
    assert len(png_briefs) == 15
    assert all(brief['asset_spec']['product_kind'] == 'transparent_cutout' for brief in png_briefs)
    assert all(brief['format_decision']['delivery_format'] == 'png' for brief in png_briefs)
    assert all(brief['format_decision']['trial_ready'] is True for brief in png_briefs)
