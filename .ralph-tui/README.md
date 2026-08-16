# ralph-tui workspace — higgsfield-prompt-master v2

## Files

- `prd.md` — the full PRD (33 user stories, P0→P3) from IMPROVEMENT_PLAN.md Rev 3
- `prd.json` — the tracker file ralph-tui executes (flat schema; regenerate via
  `python .ralph-tui/_gen_prd_json.py` after editing stories in that script)
- `config.toml` — project config (agent: opencode, tracker: json, 40 iterations)

## Run

```bash
# from the repo root
ralph-tui run --prd .ralph-tui/prd.json --agent opencode --model zai-coding-plan/glm-5.3
```

GLM-5.3 with max thinking is registered in `~/.config/opencode/opencode.json`
(`zai-coding-plan` provider, `reasoningEffort: "max"`).

Resume an interrupted session: `ralph-tui resume`
Status headless: `ralph-tui status`

## Quality gates (enforced on every story)

- `python -m py_compile <changed files>`
- `python -c "from higgsfield_prompt import HiggsfieldPromptMaster; HiggsfieldPromptMaster().stats()"`
- `python scripts/verify-generation-diversity.py` → exit 0
- `python demo.py` → no traceback

## DB safety rule

The 57MB corpus DB is gitignored (only backup: GitHub Release v2.1.1). Every
DB-mutating story runs on a copy via `HIGGSFIELD_DB` by default and needs an
explicit `--apply` flag to touch the live DB. Do not bypass this.

## Scope lock (owner directive)

Two models ONLY: `gpt-image-2` and `nano-banana-pro` (`gemini-3-pro-image`).
All model claims must trace to `research/SOURCE_TRUTH.md` — no folklore.

## Branch

Stories execute on `ralph/higgsfield-v2-rebuild` (set in prd.json). Merge to
main only when gates pass — the skill hub is a junction to this repo, so main
ships to all 5 agent installs instantly.
