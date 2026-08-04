# Interior Design Prompting Reference

## Egger Chipboard — Solid Colour Quick Reference

Egger (egger.com) is a major Austrian chipboard manufacturer. Their solid colour range
uses U-codes (uni colours) and W-codes (whites). When a user says "Egger chipboard",
they mean melamine-faced chipboard panels (Eurodekor).

### Key Solid Colours (for interior cabinetry)

| Code | Name | Visual Description | Best Texture | RAL Approx |
|------|------|--------------------|--------------|------------|
| W1000 | Premium White | Pure bright white | ST9 Matt | RAL 9016 |
| W911 | Cream White | Warm soft cream | ST15 Linear | — |
| U104 | Alabaster White | Warm ivory/cream | ST9 Matt | — |
| U108 | Vanilla | Warm yellow-cream | ST9 Matt | — |
| U156 | Sand Beige | Warm beige | ST9 Matt | — |
| U702 | Cashmere Grey | Warm medium grey | ST9 Matt, PM | — |
| U727 | Stone Grey | Warm mid-grey | ST9 Matt | — |
| U732 | Dust Grey | Cool light grey | ST9 Matt | — |
| U963 | Diamond Grey | Light silver-grey | ST9 Matt | — |
| U899 | Soft Black | Near-black, slightly soft | ST9 Matt | — |
| U999 | Black | Pure black | ST7 Pearl, ST9 Matt, PM | RAL 9011 |
| U599 | Indigo Blue | Deep navy | — | — |

### Texture Codes (how to describe in prompts)

| Code | Name | Prompt Description |
|------|------|-------------------|
| ST9 | Smoothtouch Matt | "smooth velvety matte finish, soft to touch" |
| PM | PerfectSense Super Matt | "ultra-matte anti-fingerprint finish, deep matt" |
| ST7 | Fine Pearl | "subtle pearlescent matte finish" |
| ST10 | Reproduction Texture | "textured realistic surface" |
| ST15 | Linear | "subtle linear grooved texture" |

### User Preferences
- User said "exclude all wooden look ones, need solid gestures" — no wood-grain decors
- User has the full PDF catalogue but it's image-heavy with minimal text extraction
- The PDF is useful for user reference but NOT for uploading to GPT Image 2 (it can't read PDFs)

---

## Prompt Templates for Interior Design Edits

### Template: Single Material Both Sides
```
EDIT this photo of my real [room type]. Do NOT change the [marble wall, walls,
ceiling, floor] — keep them EXACTLY as photographed. The central [marble/stone]
feature wall is the hero and must remain completely untouched. Only ADD new
elements to the LEFT and RIGHT sides:
LEFT SIDE: [TV console description] in [material]. [TV mount details].
[LED/lighting details]. [Cabinet details or "no upper cabinets"].
RIGHT SIDE: [Cabinet description] in same [material]. [Display niche details].
[Hardware: handleless push-to-open].
[Design principle: cabinetry frames/supports the hero marble wall].
Preserve all original photo elements. Photorealistic photo editing.
```

### Template: Two-Tone Split
```
EDIT this photo of my real [room type]. Do NOT change [preserve list].
Only ADD elements LEFT and RIGHT of the [hero element].
BOTH SIDES use a two-tone split:
UPPER ZONE: [light material] that blends with ceiling/upper wall.
LOWER ZONE: [dark material].
A crisp horizontal line separates light upper from dark lower.
Thin LED strip along the horizontal seam.
LEFT: [TV details per zone]. RIGHT: [cabinet details per zone].
Preserve all original photo elements. Photorealistic photo editing.
```

### Template: Minimal Gallery
```
EDIT this photo of my real [room type]. Do NOT change [preserve list].
LEFT SIDE: Maximum restraint. No upper cabinets. Just [slim console].
RIGHT SIDE: Full-height flush cabinets in [neutral material]. Handleless.
Special detail: [marble channel / connecting element between hero wall and cabinets].
Museum-like: hero material is artwork, cabinetry is gallery wall.
Preserve all original photo elements. Photorealistic photo editing.
```

---

## Session Learnings (2026-06-05)

### What worked
- Uploading both reference images as medias[] with each generation call
- Using "EDIT this photo" language vs "Interior design of..." — completely different results
- Emphasizing the hero element preservation twice in the prompt
- Describing Egger colours by visual appearance + texture, not just codes

### What failed
- First attempt used "Interior design visualization" → GPT Image 2 created entirely new rooms with different marble, different proportions
- User frustration: "I asked you only to use my main photo 1 as the one all edits on... editing not creating new marble walls"
- The PDF catalogue couldn't be extracted meaningfully (vector graphics, minimal text layer)
