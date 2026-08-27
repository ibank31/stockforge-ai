#!/data/data/com.termux/files/usr/bin/bash
# StockForge read-only readiness audit. Does not generate, submit, upload, or print secrets.
set +e
repo="${HOME}/stockforge-ai"
backlog="${HOME}/stockforge-backlog-v2/StockForge_Backlog_v2_2026-08-27.json"
log="${HOME}/stockforge-readiness-$(date -u +%Y%m%dT%H%M%SZ).log"
exec > >(tee "$log") 2>&1

pass(){ printf 'PASS  %s\n' "$1"; }
fail(){ printf 'FAIL  %s\n' "$1"; }
info(){ printf 'INFO  %s\n' "$1"; }

printf '%s\n' '=== StockForge Termux readiness (read-only) ==='
printf 'UTC: '; date -u +%Y-%m-%dT%H:%M:%SZ
printf 'HOME: %s\n' "$HOME"

if [ -d "$repo/.git" ]; then pass 'repo exists'; else fail "repo missing: $repo"; exit 1; fi
cd "$repo" || exit 1

printf '%s\n' '--- git ---'
printf 'branch: '; git branch --show-current
printf 'head: '; git rev-parse --short HEAD 2>/dev/null
printf 'origin-main: '; git rev-parse --short origin/main 2>/dev/null
if [ "$(git branch --show-current)" = "main" ]; then pass 'on main branch'; else fail 'not on main branch'; fi
if [ -z "$(git status --porcelain)" ]; then pass 'working tree clean'; else fail 'working tree has changes'; git status --short; fi

printf '%s\n' '--- runner files ---'
for f in scripts/run_backlog_preview_batch.py docs/BATCH_PREVIEW_RUNNER.md tests/test_backlog_preview_runner.py; do
  if [ -f "$f" ]; then pass "$f present"; else fail "$f missing"; fi
done

printf '%s\n' '--- runtime ---'
printf 'python: '; python3 --version 2>&1
if command -v python3 >/dev/null 2>&1; then pass 'python3 available'; else fail 'python3 missing'; fi
if [ -f "$HOME/.stockforge/config.json" ]; then pass 'STOCKFORGE_HOME config exists'; else fail "config missing at $HOME/.stockforge/config.json"; fi
export PYTHONPATH="$repo/src${PYTHONPATH:+:$PYTHONPATH}"
export STOCKFORGE_HOME="${STOCKFORGE_HOME:-$HOME/.stockforge}"
python3 -m py_compile scripts/run_backlog_preview_batch.py src/stockforge/cli.py && pass 'python compile' || fail 'python compile'

printf '%s\n' '--- backlog ---'
if [ -f "$backlog" ]; then
  python3 - "$backlog" <<'PY'
import json, sys
p=sys.argv[1]
d=json.load(open(p, encoding='utf-8'))
assert d.get('status') == 'research_ready_no_generation'
assert d.get('generation_performed') is False
assert d.get('total_candidates') == 30
assert d.get('format_counts') == {'JPEG': 15, 'PNG': 15}
print('PASS  backlog has 30 candidates (15 JPEG + 15 PNG)')
PY
else
  fail "backlog missing: $backlog"
fi

printf '%s\n' '--- local control-plane checks ---'
providers=$(python3 -m stockforge.cli provider list 2>&1)
provider_rc=$?
printf '%s\n' "$providers"
if [ "$provider_rc" -eq 0 ] && printf '%s\n' "$providers" | grep -qE '(^|[^a-z])(zerogpu|huggingface-zerogpu)([^a-z]|$)'; then pass 'ZeroGPU provider configured'; else fail 'ZeroGPU provider missing or unreadable'; fi
if command -v termux-wake-lock >/dev/null 2>&1; then pass 'termux-wake-lock available'; else fail 'termux-wake-lock missing (background run may be interrupted)'; fi
python3 -m stockforge.cli kaggle-finalizer test 2>&1 && pass 'JPEG finalizer local bundle' || fail 'JPEG finalizer local bundle'
python3 -m stockforge.cli kaggle-png-finalizer test 2>&1 && pass 'PNG finalizer local bundle' || fail 'PNG finalizer local bundle'
python3 scripts/run_backlog_preview_batch.py --backlog "$backlog" --project stock-assets --daily-cap 4 --dry-run 2>&1 && pass 'batch dry-run (no provider call)' || fail 'batch dry-run'

printf '%s\n' '--- Kaggle read-only checks ---'
if command -v kaggle >/dev/null 2>&1; then pass 'kaggle CLI available'; else fail 'kaggle CLI missing'; fi
if [ -s "$HOME/.kaggle/access_token" ] || [ -s "$HOME/.kaggle/kaggle.json" ]; then pass 'Kaggle auth file exists (value not printed)'; else fail 'Kaggle auth file missing'; fi
python3 -m stockforge.cli kaggle-finalizer status --kernel iqbalteguh/stockforge-finalizer 2>&1 && pass 'Kaggle JPEG status read' || fail 'Kaggle JPEG status read'

printf '%s\n' '--- Android visual folders ---'
android_root="${HOME}/storage/shared/Download/MACHINE STOCKFORGE"
for d in "$android_root/PREVIEW_TO_MANUS" "$android_root/READY_UPLOAD_ADOBE"; do
  if [ -d "$d" ]; then pass "folder exists: $d"; else fail "folder missing: $d"; fi
done
if [ -d "$android_root" ]; then
  bad=$(find "$android_root" -maxdepth 2 -type f \( ! -iname '*.webp' ! -iname '*.jpg' ! -iname '*.jpeg' ! -iname '*.png' ! -iname '*.svg' \) -print 2>/dev/null)
  if [ -z "$bad" ]; then pass 'visual root contains only allowed visual extensions'; else fail 'non-visual files found under visual root'; printf '%s\n' "$bad"; fi
fi

printf '%s\n' '--- protected worker hashes (informational) ---'
sha256sum deploy/kaggle-finalizer/worker.py deploy/kaggle-png-finalizer/worker.py 2>/dev/null || true
printf '%s\n' '=== End audit; no generation, Kaggle submit, upload, or quota-consuming operation was requested. ==='
printf 'LOG_FILE=%s\n' "$log"
