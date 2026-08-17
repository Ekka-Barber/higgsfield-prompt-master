---
name: hf-brief
description: >
  Interrogation-only mode — grills the user into a complete, locked design brief
  and outputs the spec without generating a prompt. Use for /hf-brief, "اسألني",
  "حدد المطلوب", "grill me", "build a brief", "what do you need to know", or when
  a request is too vague to design against.
---

# /hf-brief — grill first, spec out, no generation

Produces a **locked brief**, not a prompt. Use it when the request is vague,
when several people must agree before work starts, or when the user wants to
think before generating.

**Read `../_shared/grill-protocol.md`.** This command is that protocol run to
completion and stopped at the spec.

## How this differs from `/hf`

`/hf` asks the minimum and generates. `/hf-brief` goes deeper — it is allowed
to spend more questions, and it deliberately **stops** at the spec so the user
can review, edit, or hand it to someone else.

## The interrogation

**Round 1 — 3–4 questions** on the highest-leverage unknowns:

1. **Exact text** — the verbatim Arabic (or English) string. Nothing matters
   more; wrong copy makes a perfect image useless.
2. **Purpose & surface** — where does this live? Story, print A3, menu board,
   shopfront, in-app banner.
3. **Audience & register** — luxury vs everyday, government vs startup,
   family vs youth.
4. **Photographic or graphic** — photo-real plate or flat vector/illustration.

**Round 2 — one confirmation follow-up.** Play back the answers and ask the one
question they opened. Examples:
- "Ramadan" → which moment: the crescent announcement, iftar, or Eid?
- "menu" → full menu board, single hero dish, or a story-format teaser?
- "logo" → wordmark only, or lockup with an icon?

**Round 3 — only if a contradiction surfaced.** Otherwise stop.

## Arabic slots to lock

- Verbatim string, and who wrote it (user-supplied vs you drafted it)
- MSA (فصحى) / Gulf (خليجي) / Egyptian register
- Numerals: `0-9` or `٠-٩`
- Script style: calligraphic vs modern sans
- Arabic-only or bilingual, and which language leads
- Tashkeel: yes/no (default no)

## Output — the locked brief

```
BRIEF · <short name>

Language    Arabic only · MSA
Text        "..." (verbatim, user-supplied)
            no tashkeel · Western numerals
Purpose     Instagram story announcing a soft opening
Audience    Riyadh, 25-40, premium casual
Surface     9:16 · 1080×1920 · screen only
Register    Calm, confident, understated
Visual      Photographic plate, desert-neutral palette
Type        Geometric Kufi wordmark, right-aligned
Layout      RTL · entry top-right · logo top-right
Brand       #1B4332 primary · existing wordmark supplied
Model       Nano Banana Pro (gemini-3-pro-image)
Excluded    No people, no Latin text
Risks       Headline is 6 words — near the reliable Arabic limit
```

Close with: **"Run `/hf` to generate from this brief, or `/hf-arabic` if the
lettering is the hero."**

## Flag risks in the brief, do not bury them

- Arabic string long enough that letter errors are likely
- Sacred text or the Saudi flag involved
- Exact counts above ~5
- Internal contradictions ("minimal" + eleven required elements)
