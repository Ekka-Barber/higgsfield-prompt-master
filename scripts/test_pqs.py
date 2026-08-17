"""US-014 adversarial checks (research/prompt-quality-evaluation.md §8.3):
  1. padding without new atoms DECREASES the score
  2. swapping the goal drops >= 25 points (goal-fidelity collapse)
  3. goals 'x' and 'analytics dashboard' score differently
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))

from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()
GOAL = "analytics dashboard with charts and KPI metrics"
CAT = "App / Web Design"

r = hpm.generate_prompt(GOAL, CAT, "Template")
prompt = r["prompt"]
s0 = hpm._quality_score(prompt, CAT, GOAL)

# 1. padding: double the text with filler, no new distinct atoms
filler = (" Additionally, the overall scene includes various beautiful "
          "elements with amazing details and professional high quality "
          "finish for a nice look. ") * 6
s_pad = hpm._quality_score(prompt + filler, CAT, GOAL)

# 2. goal swap: same prompt, unrelated goal
s_swap = hpm._quality_score(prompt, CAT, "vintage postage stamp collection")

# 3. goal discrimination
s_x = hpm._quality_score(prompt, CAT, "x")
s_dash = hpm._quality_score(prompt, CAT, "analytics dashboard")

failures = []
if not s_pad["total"] < s0["total"]:
    failures.append(f"padding increased score: {s0['total']} -> {s_pad['total']}")
drop = s0["total"] - s_swap["total"]
if drop < 25:
    failures.append(f"goal-swap drop {drop} < 25 ({s0['total']} -> {s_swap['total']})")
if s_x["total"] == s_dash["total"]:
    failures.append(f"goals 'x' and 'analytics dashboard' scored identically "
                    f"({s_x['total']})")

print(f"original  : {s0['total']:>3} ({s0['grade']}, p{s0['percentile']})  "
      f"factors={s0['factors']}")
print(f"padded    : {s_pad['total']:>3} ({s_pad['grade']})")
print(f"goal swap : {s_swap['total']:>3} ({s_swap['grade']})  drop={drop}")
print(f"goal 'x'  : {s_x['total']:>3}   goal 'analytics dashboard': {s_dash['total']}")

if failures:
    for f in failures:
        print(f"❌ {f}")
    sys.exit(1)
print("✅ US-014: PQS adversarial checks passed")
