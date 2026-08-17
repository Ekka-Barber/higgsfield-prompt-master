---
name: hf-social
description: >
  Social media image prompts with correct ratios and safe zones — Instagram,
  Snapchat, TikTok, X, LinkedIn, YouTube. Arabic-first. Use for /hf-social,
  "ستوري", "بوست انستقرام", "سناب", "تيك توك", "instagram post", "story",
  "reel cover", "youtube thumbnail", "linkedin banner".
---

# /hf-social — social formats, safe zones, Arabic-first

Social kills designs by cropping them. This command gets the ratio and the
**safe zone** right before anything else.

Read `../_shared/arabic-rules.md` and `../_shared/model-routing.md`.
Also read `../_shared/typography.md` — font names are style hints,
descriptors are the real control.

## Formats

| Surface | Ratio | Pixels | Watch out |
|---|---|---|---|
| IG / FB feed square | 1:1 | 1080×1080 | safest default |
| IG feed portrait | 4:5 | 1080×1350 | best feed real-estate |
| IG / FB story, Reel cover | 9:16 | 1080×1920 | see safe zone below |
| Snapchat snap / ad | 9:16 | 1080×1920 | heavy top+bottom chrome |
| TikTok | 9:16 | 1080×1920 | right rail + bottom caption |
| X / Twitter post | 16:9 | 1600×900 | crops to ~2:1 in timeline |
| LinkedIn post | 1:1 or 4:5 | 1200×1200 | text-heavy performs |
| LinkedIn banner | ~4:1 | 1584×396 | avatar covers lower-left |
| YouTube thumbnail | 16:9 | 1280×720 | duration chip lower-right |

## Safe zones — state these in the prompt

**9:16 vertical (Story / Reel / TikTok / Snap):** keep all text and the logo
inside the middle ~70%. Reserve **~250px top** and **~350px bottom**; TikTok
also eats the **right ~120px** with its action rail.

> "Keep all text and the logo within the central safe area, clear of the top
> 250px and bottom 350px."

**YouTube thumbnail:** keep the lower-right corner clear for the timestamp.
**LinkedIn banner:** keep the lower-left clear for the profile photo.

## Arabic on social

- **Story headlines: 2–5 Arabic words.** Vertical formats tempt long copy; the
  error rate does not care.
- RTL clause still applies — right-aligned, entry top-right.
- Snapchat/TikTok skew Gulf-casual (خليجي); LinkedIn skews MSA (فصحى). Ask if
  you are drafting the copy.
- Prices and dates: confirm Western `0-9` vs Arabic-Indic `٠-٩`.

## Routing

- Arabic text on the image → **Nano Banana Pro** (`gemini-3-pro-image`).
- English text-dense (dense infographic carousel, data thumbnail) →
  **GPT Image 2** (`gpt-image-2`), `quality: high`.
- Mood-led lifestyle plate with no text → **Nano Banana Pro**.

## Grill

1. Which platform *and* placement (feed vs story vs ad)?
2. Verbatim headline text?
3. Photo-real or graphic/flat?
4. Brand colours / logo to respect?

Follow-up: single asset, or a set that must look like a series? A series
changes the approach — lock one composition and vary only the subject.

## Close with

Ratio + exact pixels, the safe-zone clause used, model + id, Arabic checklist
if Arabic, and one next lever.
