# Awesome GPT Image 2 Prompt Library Analysis

**Source:** https://github.com/YouMind-OpenLab/awesome-gpt-image-2
**Gallery:** https://youmind.com/gpt-image-2-prompts
**Stats (as of 2026-09-07):** 17,019 prompts, 9,767 stars, 880 forks (growing ~60-120 prompts and ~10-20 stars per day)
**Update cadence:** Every 4 hours via GitHub Actions (bot auto-commits `docs: auto-update README [skip ci]` — these are noise from CMS syncs, not real technique changes)
**License:** CC BY 4.0
**Public README:** 120 curated prompts with full text (capped by GitHub content-length limits); remaining 15,950+ behind private Payload CMS but **fully accessible** via youmind.com gallery pages at predictable URLs: `https://youmind.com/prompts/{any-slug}-{ID}`. GPT Image 2 prompts are at IDs ~13440–26917. See `references/gpt-image2-prompt-database.md` for scraping approach and scripts.

## youmind.com Gallery Structure (discovered via investigation)

- **URL pattern:** `/prompts/{slug}-{numericID}` — the slug is ignored; only the numeric ID resolves the prompt
- **ID ranges by model:** IDs 101-1000 = Nano Banana Pro; 1000-5000 = Seedream 4.5; 5000-13400 = Nano Banana Pro; 13440-26917 = GPT Image 2 (our target); 25000+ = some claude-fable mixed in
- **Prompt text location:** Rendered in DOM (Next.js RSC flight data). The `.whitespace-pre-wrap` CSS selector contains the full prompt text. Server-side RSC chunks (T-chunks) are unreliable for extraction — use CloakBrowser CDP DOM extraction instead.
- **Meta tags reliable via curl:** `<title>` contains prompt name + model + category. `<meta name="keywords">` contains category taxonomy. These extract reliably without a browser.

## Key Prompting Techniques Discovered

### 1. JSON-Structured Prompts (top featured technique)
GPT Image 2 parses JSON objects with high fidelity. Keys like `type`, `subject`, `style`, `background`, `layout`, `header`, `footer` map directly to generated elements. Best for posters, UI mockups, exploded diagrams, infographics.

### 2. Goal + Canvas + Sections Pattern
```
Goal: [One sentence]
Canvas: [Dimensions, background]
[Section]: [Elements with exact counts]
Visual style: [Closing style guard paragraph]
```

### 3. Exact Counting
Always specify element counts: "exactly 4 image cards", "exactly 8 rows". Prevents GPT Image 2 from adding/removing elements.

### 4. Spatial Anchoring
Name positions explicitly: "top-left header", "bottom-right product card", "arranged in two columns and three rows".

### 5. Visual Style Guard
End complex prompts with a closing paragraph summarizing the complete aesthetic. Prevents style drift across multi-element designs.

### 6. Face Lock / Identity Preservation
```
face lock: maintain exact facial structure, proportions, skin tone, hairstyle,
and identity from reference with 100% accuracy. Preserve micro-details and
natural imperfections, no beautification.
```

### 7. Cross-Reference Mapping
Number references explicitly: "Using REFERENCE_1 as the current thumbnail and REFERENCE_0 as the identity reference"

### 8. Negative Prompts
For photorealistic work: `negative prompt: distorted face, changed identity, altered hairstyle, flat lighting, plastic skin, beauty filter effect`

### 9. Detailed Color Science
`color science: ultra-clean cinematic color grading with high color separation, natural saturation, deep contrast, HDR dynamic range`

### 10. Layered Composition
Break UI mockups into named layers: `top_header → mid_left → bottom_left → bottom_right → bottom_bar`. Describe each independently.

### 11. Physics-Causality VFX (new, Aug 15 2026 — No. 89 "Luxury Desert Air Conditioner Ad" by Loriel.AI)
Instead of describing an effect as a static overlay, describe it as a physical action with a starting point, weight, and landing point, plus *selective environmental reaction*:
> "depict the cold air as an action with a starting point, weight, and a landing point… fan-shaped icy airflow starting dense at the vent, widening diagonally downward, diffusing softly around the subject… brighter and denser near the air outlet, then softens when it lands on people or animals… The overall environment remains hot, but only the area blown by the wind turns blue, frosts, and reflects light."

Why it works: the audience reads cause → effect, so the VFX reads as physics, not a floating blue overlay. Generalizes to smoke, light beams, splashes, magic.

### 12. Percentage-Grid Coordinates + Color Budget (new, observed in No. 109 "Stewed Pear Dessert Poster")
Pin object placement and text zones with percentage boxes instead of vague terms:
> "The center of the pot is at 62% horizontal and 64% vertical, occupying about 38% of the frame width. The area from 7% to 42% horizontal and 9% to 47% vertical on the left remains a warm white text zone."

Also specifies a **color budget** as percentages: "52% warm white background, 18% transparent light-gold syrup, 20% pear milk white, 5% glass gray, 5% dark brown text" — controls overall palette balance, not just hue choices. Includes macro photography specs (camera 12cm above pot, 90mm macro, 14° off-axis from 72cm, 5500K window light).

### 13. Adjacent-Genre Exclusion (new, observed in No. 94 "Rose-Pink Studio Fashion Portrait")
A closing sentence that names the *adjacent genres* the image must not drift toward — distinct from defect-based negative prompts (which list artifacts like "plastic skin"):
> "The final photograph should feel like a romantic independent beauty-studio portrait: feminine, composed, softly theatrical, floral, slightly formal, and physically grounded—not a bedroom scene, bridal portrait, flower field, or luxury campaign composite."

Pattern: `[intended genre adjectives] — not [adjacent genre 1], [genre 2], [genre 3], or [genre 4]`.

### 14. Selective Colorization (new, observed in No. 93 "Japanese Glamour Typography Poster")
Base monochrome/B&W frame with exactly one element colorized as the accent:
> "Use a mostly monochrome black-and-white photographic look with only the camisole softly colorized in muted rose and the jeans lightly warm beige."

### 15. Degraded-Reference Identity Extraction (new, observed in No. 2 "Y2K Pop Portrait Stickers", Aug 18 2026)
Face Lock variant for low-quality references. Instead of demanding a clean reference, enumerate the exact identity features to extract and continue, and explicitly license degraded input:
> "Even if the original is a childhood photo, low-res, blurry, or old, prioritize extracting and continuing the person's most recognizable features: face shape ratio, eye shape and distance, eyebrow shape, nose structure, mouth shape, ear contours, hairline, facial fleshiness, expressions, and personal temperament; while enhancing clarity and detail completeness, maintain the original identity so the result is clearly the same person as in the photo."

Why it works: naming the feature list gives the model a checklist to match against, and pre-authorizing degraded inputs prevents it from abandoning the reference. Also ends with an identity-priority clause: "character identity features always remain the highest priority for consistency" — useful whenever stylization (stickers, chibi, toys) competes with likeness.

### 16. Anti-Shortcut / Output Exclusions (new, observed in No. 1 "Vintage Halftone Portrait Poster" & No. 111 "Premium Energy Drink Branding", Aug 14-18 2026)
A third negative-prompt tier. Defect negatives block artifacts ("plastic skin"); adjacent-genre exclusion blocks wrong genres ("not a bridal portrait"); **output exclusions block the model's lazy default solution**. Two forms:

JSON key (inside the prompt object):
```json
"output_exclusions": ["Do NOT include a small circular/rounded-corner inset photo of the real reference image in the corner of the poster — the final output is the illustration ONLY, full-bleed, no reference thumbnail overlay."]
```

Prose form (transformation prompts):
> "Do not simply place the logo on a generic can. Reimagine the identity into a distinctive energy drink with a custom can silhouette, intelligent label system, signature energy graphics..."

Why it works: GPT Image 2 has recognizable fallback behaviors (inset reference thumbnails, paste-logo-on-product). Naming the shortcut explicitly and pairing it with the *desired* alternative ("Reimagine... into") forces full reinterpretation.

### 17. Split-Frame Analytical Deconstruction (new, observed in No. 37 "Watercolor Isometric Deconstruction Poster" & No. 38 "Da Vinci Isometric Structural Poster", Aug 22 2026)
A photo-transform prompt that splits the canvas into two fixed halves with different jobs:
- **Top 50%:** preserve the uploaded photo — subject identity, structure, proportions, perspective, natural lighting, original color atmosphere. Only "slight high-end photographic color grading" allowed; sky/ground may extend to fit the ratio but the subject must not be stretched or replaced.
- **Bottom 50%:** extract the subject and redraw it as a structural deconstruction study under isometric/axonometric logic (watercolor study, Da Vinci-style manuscript marks, Japanese clear colors, etc.).

The distinctive craft is in the constraints:
- **Extraction checklist:** "first identify the core subject, main axes, original observation direction, foreground/midground/background relationships, 3–7 most important identifying features, 4–6 primary colors, and environmental cues that reflect scale"
- **Subject-type-aware decomposition:** buildings/vessels split along roofs, floors, shells, frames, bases, modules; landscapes unfold by depth layers; **"humans, animals, or plants should remain physically whole — dismemberment, dissection, or mechanical partitioning is prohibited"**, expressed only through overlapping outlines, pose layers, and color blocks
- **Anti-collage ban:** "Do not paste the photo directly, and do not create before-and-after comparisons, collages, or photographic slices"
- **Anchor layer:** retain "one complete, stable, most detailed base or anchor area so the audience can reassemble the subject in their mind"
- **Anti-template clause:** "Avoid templated exploded views... and unfounded structural fabrications" — the deconstruction method must grow from the subject's own structure

Why it works: the fixed 1:1 split plus per-half rule sets makes the output predictable while the extraction checklist forces genuine analysis of the reference rather than a generic exploded view.

### 18. Medium-Partition Hybrid (new, observed in No. 24 "Anime Doodle and Real Photo Fusion", Aug 22 2026)
Assign a different medium to each region of the image and explicitly forbid medium bleed:
> "The character should look like a 2D ink illustration placed physically inside the real-world scene... Do not make the entire image cartoon-like. Only the character should be illustrated; everything else must remain photorealistic."

Key clauses: character rendered as clean black ink line art with white interior and "clearly visible black outline around the entire character, like a hand-cut sticker" + "slightly imperfect hand-drawn lines for an authentic sketchbook feel"; background locked with "Use the uploaded photo as the exact background reference. Preserve the original... perspective, lighting, colors, shadows, and camera composition"; integration cues make the mix physical — "Make her feet properly contact the ground/stairs", "Add realistic interaction with the environment through natural shadows and overlapping perspective".

Why it works: without the medium-bleed ban, GPT Image 2 tends to blend styles globally (whole image goes anime or whole image stays photo). Region-scoped style assignment + physical contact cues keep the hybrid crisp. Generalizes to any two-medium mix (cel character + photo world, watercolor sky + photo city).

### 19. Chained Retrieval-Transform Steps (new, observed in No. 33 "Movie Scene Character Swap Prompt", Aug 22 2026)
A two-step workflow where Step 1 delegates reference *retrieval* to the model itself instead of uploading references:
> "Step 1: Search for the 10 most classic stills from [movie]. Use each classic still as a reference image. Step 2: Replace the main characters with [targets]. Be careful to maintain the characters' emotions, the screen grain texture, and the color texture. All stills should maintain their original texture, creativity, and compositional characteristics, just like the original film frames. Please output each image."

Why it works: the model pulls its own training-data knowledge of iconic compositions instead of depending on user-supplied references; the texture/grain/color preservation clause keeps the character swap diegetic (a film frame, not a collage). Use when you want "X franchise scene but with Y characters" without sourcing stills. Variant flags: language-hinted output language via argument slots.

### 20. Ultra-Minimal Two-Slot Templates (new, observed in No. 27 "Laughter on the Veranda" & No. 29 "Blue Mosaic Garden Bath", Aug 22 2026)
A whole prompt of the form `{style} of the {location}`:
> "Blue mosaic of the hot spring garden" / "Laughter overflowing on the veranda"

Why it works (sometimes): for atmospheric/conceptual images, two nouns do the composition work and the model fills the rest — a deliberate minimalism at the opposite end from JSON. Low control, high serendipity. Useful for mood boards and style studies, not for text/counts. Worth knowing as the floor of the prompt-length spectrum.

### 21. Source-Look Preservation / Anti-Upgrade Clause (new, observed in No. 31 "Identity Swap Image Consistency Prompt", Aug 23 2026)
An identity-swap edit prompt whose key craft is forbidding the model's beautify default:
> "Image editing task. Use Image 1 as the base image. Reproduce the same scene, pose, camera angle, framing, lighting, outfit style and background. Change only the person identity to match the attached AI model reference images. Keep the same body orientation, hand position, facial direction and composition. Preserve the raw phone-photo look: slight motion blur, JPEG compression, sensor noise, imperfect crop, real shadows, uneven indoor light and natural skin texture. Do not make it look like a studio render."

Why it works: GPT Image 2's edit default is to "improve" the frame (cleaner light, sharper render), which instantly betrays the edit. Enumerating the *flaws to keep* (compression, noise, motion blur, imperfect crop, uneven light) plus an explicit anti-studio clause locks the output to the source's authenticity level. Inverts the usual negative-prompt logic: the "defects" are the spec. Use for undetectable face swaps, texture-matched restyles, and "same photo, different person" tasks.

### 22. Element-Scoped Negatives (new, observed in No. 27 "Woman in White Lace Dress at Sunset Beach" & No. 115 "Ancient Chinese Fantasy Game Poster", Aug 23 2026)
Negatives that name specific elements of your own composition instead of generic artifacts. Two flavors:
- **Fragile-detail protection** (No. 27): `Negative: Do not make the front leg small; Do not omit the sheer hem of the white lace.` — defends the exact details the model tends to shrink or drop (extended limbs, sheer fabric, small props).
- **Focus-stealing prevention** (No. 115): `avoid ... title engulfing the subject, and background props becoming the protagonist` — caps decorative/text/background elements from overwhelming the subject.

Why it works: generic negatives ("no watermark, no extra fingers") are static hygiene; element-scoped negatives encode *predicted failure modes for this specific layout*. Review the prompt, find the 1-2 elements most likely to be lost or overgrown, and ban exactly that.

### 23. Enumerated Prop-List Inventory (new, observed in No. 21 "Backlit Sunrise Couple Picnic", Aug 24 2026)
Instead of describing a scene's props loosely, list every visible object as a numbered inventory with count + position + micro-description:
> "Include exactly 14 visible prop groups: 1 beige blanket spread across the ground, 1 light pillow at far left, 1 open sketchbook or magazine near the woman's left hand, 1 black camera at the lower left edge, 1 plate of fruit with green grapes and small oranges in front of the couple, 1 black notebook labeled 'Lam & Ty / HELLO JOURNEY'…"

Why it works: this is Exact Counting applied to a whole scene rather than a single layout grid — the enumeration doubles as spatial anchoring (each item carries its position) and as a text-rendering manifest (labeled props get their exact strings). Use for flat-lay, picnic/desk/table scenes, and any "casual lifestyle photo" where GPT Image 2 otherwise over- or under-populates the environment.

### 24. Recontextualized Reference Transformation (new, observed in No. 93 "Red Spiked Mask Cabinet Still Life", Aug 24 2026)
Take a single reference object and move it into an entirely new genre/scene as multiple physical instances, with the wear carried over:
> "Using the provided reference image as the design source for the red spiked leather helmet/mask, transform it into a grounded photorealistic still-life scene instead of an action portrait. Remove the wearer and motion trails. Show the mask design as a collection of exactly 7 physical helmets stored in an old teal wooden cabinet: 1 main helmet on the upper shelf, 1 partial helmet cropped at the far upper-left edge… Preserve the red leather, black eye openings, metal studs, silver side fins, cracked seams, and worn handcrafted look from the reference, but make all helmets tangible objects with realistic scuffs and damage."

Why it works: it names the *source-genre clichés to strip* ("remove the wearer and motion trails"), re-instances the design as N physical objects each with a slot in the composition, and preserves a material checklist from the reference. The anti-portrait pivot ("instead of an action portrait") prevents GPT Image 2 from defaulting to a character render of the reference. Use for product-line visualization, collection shots, and "museum display" treatments of a single design.

### 25. Normalized 100×100 Grid Series Contract (new, observed in No. 88 "3D Handcrafted Clay Destination Plaque", Aug 24 2026)
For multi-image consistent series, define every layout zone on a normalized 0–100 coordinate grid with numeric ranges, plus a landmark hierarchy by percentage height, then lock everything except the changing content:
> "COMPOSITION & GEOMETRY: Use a fixed horizontal framed layout on a normalized 100×100 grid. Frame: x=5–95, y=8–92. Landmark zone: y=18–58. Foreground: y=48–67. Location-name zone: y=68–88. Bottom margin: y=88–92. Keep these proportions identical for every location." … "SERIES CONSISTENCY: Keep the frame, composition, grid, typography, landmark scale, hierarchy, object density, materials, palette, lighting, camera angle, depth, shadows, and negative space identical across every location. Change only the landmarks, culturally/environmentally relevant details, and restrained location-specific accent colors."

Why it works: percentage coordinates (technique #12) applied to a *series* become a template contract — the enumerated "keep identical" list plus a "change only" whitelist makes every generated image structurally interchangeable while varying only the content. Closes with a "FINAL QUALITY CHECK" section restating acceptance criteria (recognizable, correctly spelled, visually balanced). Use for collectible sets, multi-city campaigns, deck card series, flag/poster series.

### 26. Anti-Cliché Cultural Adaptation Clause (new, observed in No. 92 "Contemporary Editorial Travel Artwork Template", Aug 24 2026)
For location/destination prompts, forbid generic landmark-poster tropes and force city-specific grounding:
> "Avoid anime aesthetics, excessive cultural symbols, clutter, photorealistic collage, generic stock imagery, oversized landmarks, excessive decoration and oversized typography." … "Important: Prioritize the authentic visual character of the chosen city. Do not force elements that do not belong there. Adapt the architecture, landscape, vegetation, atmosphere and color palette specifically to the city."

Why it works: adjacent-genre exclusion (#13) specialized for travel/place imagery — it bans the *stock-poster failure modes* (oversized landmarks, cultural-symbol soup, collage) and adds a positive "authenticity-first" mandate that overrides template defaults with location-specific research. Pairs well with a numbered-issue aesthetic ("No. 05 — 2026") for collectible-series feel.

### 27. Pseudo-Code DSL + Inference Delegation (new, observed in No. 26 "Calligraphic Sports Grid System" & No. 39 "Edible World Wonder Cakes" & No. 77 "Thematic Artistic Collage Template", Aug 25 2026)
A fourth prompt structure beyond JSON / flat / Goal+Canvas: write the prompt as a program the model executes. Three dialects observed:
- **Formal grammar** (No. 26, by Gadgetify): `INPUT ::= [TOPIC_OR_WORD]` `W := derive_word(INPUT)` `A := infer_actor_or_symbol(INPUT)` — typed variables with derivation functions; an ASCII `LAYOUT_SOLVER` box diagram of the canvas; `SEMANTIC_ASSIGNMENT ::` slot rules (BODY_SLOT := glyph whose counter/curve/stem best accommodates pose(A)); `FUSION ::` mapping lines (`A.body_part -> glyph_stroke`, `collision -> ink_burst`, `energy_propagation -> concentric_marks`); `BRUSH_PHYSICS ::` proportionalities (`stroke_width(t) ∝ pressure(t)`, `dryness(t) ∝ velocity(t)`, `splatter ∝ energy`).
- **AI_INFER calls in JSON** (No. 39, also Gadgetify): values like `"Textures": "AI_INFER(High contrast between glossy mirror glazes, porous aerated sponge, and crumbly sablé base matching the flavor)"` plus a leading clause "do this for 4 wonders of the world, ai picks the rest for flavor profile" — the JSON fixes structure while delegated slots let the model improvise.
- **DO/RULES variable blocks** (No. 77, by Kōda): `THEME = {} STYLE = {} PALETTE = {}` headers, then a `DO:` block of imperatives ("Derive subjects, environments, objects and visual events naturally from THEME", "Treat each scene as a distinct emotional fragment", "Avoid repeating the same rectangle size or alignment") and `CAMERA:` / `RULES:` closers ("Use STYLE as the authority for medium, linework, text").

Why it works: declarative slot-binding gives compositional guarantees where prose is ambiguous (which glyph absorbs the pose? where does impact land?), and inference delegation produces coherent novelty per item in a series without hand-writing every variant. Use for generative series systems, calligraphy/typographic fusion, and theme-driven collages. Risk: over-formalization can confuse the model — keep the grammar small and pair with one plain-language summary sentence.

### 28. Fixed-Anchor Campaign Grid (new, observed in No. 89 "Pho Republic Campaign Grid" & No. 94 "Rise Shot Commercial Coffee Poster", Aug 24-25 2026, both by Loriel.AI)
For 2×2 (or N-panel) campaign poster series: declare one immutable object anchor and govern variation with named meta-directives:
- **Fixed anchor:** "The pho bowl must remain the absolute visual hero in every panel... shown from the exact same slightly top-down camera angle. Bowl size, bowl height, bowl perspective, rim thickness, bowl diameter, and visual weight must be perfectly consistent across all four posters. The container must sit at an equal visual scale in every panel, acting as the fixed campaign anchor."
- **Style lock:** pins genre and medium — "high-end graphic food advertising... not illustration, not 3D render... Cannes-level print campaign execution."
- **Transit logic:** subtraction mandate — "Reduce small labels, reduce decorative callouts, shorten copy, preserve more clean negative space... Avoid flyer-like density."
- **Orbit logic:** the per-panel variation system — "Panel one uses a strong descending diagonal text flow, panel two uses a mirrored inward-driving diagonal, panel three uses a controlled circular orbit around the bowl, and panel four uses a tighter circular return path that visually resolves the campaign."

Why it works: it cleanly separates invariants (anchor object, scale, structure system) from movement (typographic trajectories), so the set reads as one campaign with four coordinated beats rather than four unrelated posters. "Transit/Orbit" is just named subtract/add dialectics — reusable vocabulary for any series brief ("merge Transit restraint with Orbit energy").

### 29. Protected Wardrobe Contract (new, observed in No. 92 "Cyberpunk Technical Bomber Jacket" by MoodLock_JP, Aug 24 2026)
For complex or asymmetric outfits, open with an immutability contract and scoped override semantics instead of trusting the model to track every garment detail:
- **Priority header:** "PROTECTED WARDROBE RULE — HIGHEST PRIORITY: Treat each garment description as immutable source identity. Preserve construction, parts, hardware, material, pattern, and every registered graphic or marking — its surface, side, orientation, scale, colors, content, spelling, and count — unless a later instruction explicitly changes color, material, or wearing state."
- **Scoped override semantics:** "A MATERIAL CHANGE substitutes only the explicitly scoped source material phrase and preserves every other garment attribute. FINAL WORN STATE overrides only the scoped item's use, position, side, orientation, fastening, layering, folds, tucks, knots, and drape. A SOURCE GARMENT label describes the unstyled item, never the completed silhouette. Do not redesign, add, remove, mirror, duplicate, relocate, or redraw protected details."
- **View-conditional side mapping:** "VIEW-CONDITIONAL BODY-SIDE MAP: front view — wearer-left is image-right; back view — wearer-left is image-left. In profiles, crossed limbs, or ambiguity, trace the named limb continuously from its shoulder or hip. Apply the state only to the named anatomical side; never mirror or duplicate it."

Why it works: two classic GPT Image 2 failures are garments quietly redesigned between description and render, and asymmetric details (one-sided panels, single stockings, unilateral straps) mirrored onto both sides. The contract makes identity vs. state explicit, and the body-side map resolves the wearer-vs-image left/right inversion that causes mirrored-side hallucinations. Use for technical fashion, character sheets with layered outfits, and any look with deliberate asymmetry.

### 30. Agency Creative Brief (new, observed in No. 21 "Premium Pizza Advertising Poster" by ᴍᴜʀᴘʜʏ, Aug 27 2026)
Instead of describing an image, write the prompt as an all-caps advertising agency brief with named sections:
- **CREATIVE DIRECTION** — visual-language sourcing plus anti-copy + anti-generic clauses: "Do not copy any specific reference composition. Extract the common principles and build an original execution. The poster must feel like a real global pizza campaign art-directed for Instagram… not a generic AI food poster." Plus the legibility law: "The visual must communicate the idea before the viewer reads the copy."
- **CAMPAIGN DNA** — Brand / Hero product / Campaign territory / Concept ("THE BOX IS THE WIN") / Personality ("hungry, playful, confident, fast, slightly cheeky"), and a **color system with roles**: "Dominant red (#E31837)… blue used only as logo, box accent, small graphic punctuation… The red must own the frame immediately."
- **BACKGROUND with Allowed/Forbidden lists** — "Allowed: extremely subtle blob pattern at very low contrast, restrained radial falloff… Forbidden: random restaurant interior as default, dirty kitchen, city street, collage clutter, extra brands."
- **HERO PRODUCT with frame-occupancy spec** — "Product occupies roughly 50–65% of the frame width unless the idea needs scale contrast"; material realism gates: "believable grease sheen, not plastic CGI"; brand-geometry lock: "Preserve recognizable box/logo geometry. Do not invent a new logo."
- **TYPOGRAPHIC SYSTEM** — "Headline: short, 3–6 words… Typography is hierarchy, not decoration. Do not flood the frame with copy."

Why it works: the section names double as quality gates the model understands (Allowed/Forbidden lists are sharper than prose bans; percentage frame occupancy beats "large product"); the DNA block (concept + personality) gives the model a campaign-level idea to execute rather than a layout to fill. Use for brand campaigns, ad posters, and any brief where strategy must drive the image. Also note the **Use:/Avoid: line pair** under CREATIVE EXECUTION ("Use: oversized short typography, product scale… Avoid environmental documentary") — a compact include/exclude dialect.

### 31. Timed Storyboard Script (new, observed in No. 41 "Educational Lightning Storyboard Infographic" by 𝐌, Aug 23 2026 — newly rotated into README Aug 26-27)
Encode motion inside a still image by writing a shot list with timecodes:
```
1 | 0:00–0:03 — STORM CLOUDS
Visual: Huge dark storm clouds forming above a landscape.
Action: Clouds grow rapidly with electric particles inside.
VO: "Lightning begins inside powerful storm clouds."
SFX: Wind and distant thunder.
Camera: Slow aerial push in.
Transition: Light Flash.
```
…repeated for exactly 5 scenes (15 seconds total), opened by format specs ("vertical 2:3, 5 horizontal scenes, cinematic realistic 3D science visualization, exactly like a professional educational video storyboard") and closed by a narrator spec ("NARRATOR (VO): Clear, calm, educational male voice").

Why it works: timecodes force one beat per panel (no panel tries to show two moments); each per-scene field maps to a concrete rendering instruction (VO → caption text, Camera → panel composition/angle, Transition → inter-panel energy or divider treatment, SFX → implied audio visualization). Produces animatic-grade storyboards from a single prompt. Use for explainers, ad storyboards, and sequential education content.

### 32. Named Effect Menu — one-of-N treatments (new, observed in No. 93 "Experimental Editorial Portrait Poster" by Saul Goodman, Aug 26 2026)
A customizable header block (Subject / Interference / Title / Palette / Mood) followed by a **dictionary of named, precisely-defined treatments**:
> "Color Split: Uneven translucent bands selectively shift, reveal, separate, or distort portions of the portrait. / Narrow Light Beam: A single controlled beam cuts across the face or body and continues naturally into the surrounding space. / Horizontal Cut: Bold horizontal bands interrupt selected areas of the portrait and interact with oversized typography. / Motion Veil: Keep the main portrait sharp while selected areas create subtle horizontal photographic motion trails."

…locked by "Use only one primary interference method" and grounded by a base-quality gate: "The portrait must work visually as a fashion photograph before the graphic intervention is applied."

Why it works: the menu decouples template from treatment — run the same template N times with different menu choices and you get a coherent series (the prompt itself generated 4 distinct outputs); the one-only rule prevents effect stacking, which GPT Image 2 drifts toward when multiple effects are merely listed. Typography is specified as a compositional actor ("allowing letters to crop beyond the frame, overlap the subject, disappear behind the body, or interact with the interference"). Use for poster series, A/B aesthetic tests, and any repeatable treatment family.

### 33. Pipeline Anchor Declaration (new, observed in No. 119 "Vermilion Sword Character Concept Art" by AIライフハック, Aug 26 2026)
A Step-1 prompt whose job is to manufacture the reference asset for later steps — and says so explicitly:
> "Without using reference images, generate a new single anchor image to serve as the protagonist for this video project. This image will be used as the sole design standard for character, costume, and sword for subsequent 'Design-focused Three-view' and 'Simple Three-view' sheets."

The design criteria are then optimized for **expandability rather than standalone beauty**: "clear facial features, hair, body type, proportions, clothing, sword, and color placement, making it easy to expand into front, side, and back views later"; hair "with clear shapes for bangs, sides, and the back of the head, creating a silhouette easily recognizable in a video"; costume "the front, side, and back structures can be naturally developed"; and a fit spec — "Fixed 1:1 square. Fit the protagonist from head to toe, including the entire sword, within the square without strain… not too small and not cut off at the edges." Written in a markdown-header DSL (`# CUSTOM_VERMILION_SWORD_ANCHOR`, `## [Purpose]`, `## [Aspect Ratio]`) — a fifth dialect of the pseudo-code DSL family (technique #27).

Why it works: declaring the downstream role changes what the model optimizes for (three-view-expandable design, uncluttered silhouette, full-body fit) versus a one-off illustration; the anchor image then acts as a Face-Lock/style-bible for the follow-up sheets, giving series consistency without any uploaded reference. Use for character pipelines, IP development, and multi-step workflows where step 1 must produce a canonical asset.

### 34. Split-Screen Controlled-Variable A/B (new, observed in No. 33 "Split Fantasy Portrait Comparison" by John Qiao, Aug 26 2026)
Render the *same* subject twice with exactly one named delta, plus one label box per panel:
> "Canvas is a horizontal 16:9 split-screen composition with a perfectly vertical divide down the center, no gap, left panel and right panel each occupying exactly half the image. In both panels, depict the same ethereal young woman… Make the left panel slightly more textured, crisp, and detailed in skin and fabric microtexture; make the right panel slightly smoother and more airbrushed, with softer pastel lighting… Add exactly 2 label boxes: one white rounded rectangle at the top left of the left panel reading 'OpenAI 官方', and one at the top left of the right panel reading 'Azure West US 3'."

Closed by a similarity band: "Keep both portraits similar enough to clearly compare rendering differences, but not identical."

Why it works: the single-variable delta + "similar but not identical" band keeps the comparison honest (GPT Image 2 either makes both panels identical, killing the comparison, or drifts on multiple axes, muddying it); split-frame + per-panel labels (which double as a text-rendering test) turn one image into an evidence artifact. Use for model/version face-offs, before/after showcases, and settings comparisons.

### 35. Rebus Visual-Word Substitution (new, observed in No. 38 "Rebus Style Visual Poetry Poster" by 小小东, Sep 1 2026)
A split-frame photo-transform (top 50% photo preserved, split-frame #17's canvas) whose lower half becomes a **visual sentence** — a rebus:
- **Sentence-first workflow:** "First, generate a short, imaginative, and slightly poetic or editorial sentence based on the photo's mood, action, relationships, location, memory, or metaphor. Then, select several nouns, action words, imagery words, or emotion words from the sentence that are best suited for visualization and replace them directly with corresponding image elements."
- **True substitution semantics (the core novelty):** "These images are not decorative illustrations; they must truly replace words in the sentence. Once a word is replaced by an image, the word must not be written in text again. The entire sentence must rely on the combination of 'text + images' to be fully understood." Forms a continuous "text → image-word → text → image-word → text" reading path, not drawings decorating a complete sentence.
- **Image-word craft:** each visual word sits in its own small colored block ("like a fragment cut from the memory of the original photo") with varied sizes, aspect ratios, and crops; blocks are *redrawn in a unified hand-drawn editorial style* extracted from the photo — not crops or screenshots; size varies by semantic importance (word-sized vs. visual focal point).
- **Palette derivation:** block colors "extracted from the brightest, most vibrant, and most vital colors in the upper photo and then retuned" toward soft milk-blue/mint/cream/peach tones — not averaged.
- **Anti-failure bans:** sticker-wall aesthetics, card-list grids, regular grids, "including images without deleting the corresponding words in the sentence," commercial template styles, crowded layouts lacking white space.

Why it works: it forces genuine semantic parsing of the photo (mood → sentence → word selection → visualization) rather than generic decoration, and the substitution rule creates a puzzle-like reading engagement no other technique produces. Use for photo-to-art-journal transforms, memory/keepsake posters, and editorial zine pages. Related observed same-cycle: No. 39 "Documentary Photo Series of Grape-kun" (Sep 1) is a Timed Storyboard (#31) variant adding an **anti-fictionalization clause** ("Strictly based on real events, no fictionalization of [subject]'s psychology, dialogue, memories, or motives; 'love' is the interpretation *people* have for its behavior") — useful flavor for documentary-style series. No. 35 "Anime Lifestyle Portrait with Manga Shadows" is a Medium-Partition Hybrid (#18) variant (shadows become manga art).

### 36. Physical String Systems Map (new, observed in No. 45 "Handcrafted String Visualization Map" by 小小东, Aug 29 2026)
A split-frame photo-transform (top 50% photo preserved — split-frame #17/#35's canvas) whose bottom half translates the photo into a **tangible node-link diagram** built from real craft materials:
- **Subject-to-graph translation rule:** "extract the most recognizable subject, outline, structure, posture, and narrative relationship of the photo… Do not depict the original object directly, but disassemble the subject into a small number of meaningful nodes and relationships: key outlines, structural turns, movement directions, spatial positions, or environmental clues become pushpin-style Nodes, and real strings are used as Edges / Links between them."
- **Emergent-geometry mandate:** strings must follow the original image's direction, proportion, distance, and narrative logic — "some nodes form radial, convergent, triangular, polygonal, and cross-regional connections, causing a large number of simple relationships to naturally produce emergent geometry." Dense center, sparse periphery, generous negative space.
- **Material authenticity spec:** "small pushpins, stitches, cotton thread or twine, paper labels, handwritten marks, and a real cardboard surface, retaining slight string tension differences, node heights, cross-shading, stitch shadows, and manual errors… not a computer-drawn network diagram, nor cyber UI, digital glowing lines, or cheap detective board effects."
- **Color logic:** one sharp but restrained line color (vermilion/coral red) as the primary relationship color against warm-white/light-grey backgrounds; pushpins and tags may echo local colors from the photo above in small areas.
- **Free-annotation clause:** text intervenes as Hand-lettered Annotation *without preset content* — "freely generate a few keywords, short sentences, arrows, circled notes… based on the subject, action, position, emotion, relationship, or metaphor in the photo" near nodes and string intersections, in a small research-note-like handwritten font.
- **Anti-failure bans:** random red lines, meaningless nodes, full-page chaos, horror crime boards, digital network UI, cartoon pushpins, templated mind maps, ordinary flowcharts.

Why it works: same forced semantic parsing as the Rebus technique (#35) but mapping to *structure* (nodes/edges) instead of *words* — the model must decide what the subject's parts are and how they relate before drawing. The material-physicality spec defeats the model's default of rendering digital network graphics. Use for research-wall aesthetics, system-design experiments, and information-art installations from photos.

### 37. Ownable Super-Symbol (Brand Codes + Eye-Loop) (new, observed in No. 92 "Electric Energy Drink Poster" by Loriel.AI, Sep 1 2026)
A brand-hero-product prompt that designs for *repeatability across future campaigns* rather than one poster:
- **Port logic (brand codes):** "turn this exact visual into the unmistakable super-symbol of VOLTERRA. The permanent identity must be built from four fixed codes: one grounded transparent blue glass bottle, one dominant high-voltage orbital ring around the bottle body, one deep blue-black void background with rear lightning activity, and one wet reflective floor catching the electric glow. The image should feel instantly ownable, repeatable, and scalable across future flavor and campaign extensions."
- **Orbit logic (eye-loop path):** an explicit viewing circulation — "build a strong closed visual loop through the product. The eye should move from the cap highlight into the bottle neck, travel down the central label, continue through the main electric ring around the waist, drop into the bottle base and its mirrored floor reflection, then rise back through the outer bottle edge highlights and rear lightning into the cap again. The bottle tilt, ring placement, label position, floor reflection, and rear electrical branches must all reinforce one continuous circulation."

Why it works: "orbit logic" here goes beyond the Fixed-Anchor Campaign Grid (#28) typography trajectories — it scripts the *viewer's gaze path* as a closed loop and requires every element to reinforce it (gaze-guidance as a compositional contract). The enumerated "fixed codes" turn one image into a brand system spec: subsequent generations re-invoke the codes for campaign-wide visual consistency. Use for brand identity heroes, mascot/product super-symbols, and any asset meant to seed a repeatable visual system. (Related: No. 48 "Viral Mascot Reels Grid", Aug 28 — exact-count UI screenshot realism with exactly-N overlay labels "15K/989K/1.2M" — is Enumerated Inventory (#23) + exact counting applied to fake analytics UI; noted, not novel enough to promote.)

### 38. Field-Notes Archivist Transform (Content-Adaptive Panels + Compression Contract) (new, observed in No. 40 "Travel Observation Archive Poster" & No. 41 "Travel Rubber Stamp Poster", both by lovimg_com, Sep 3 2026)
A split-frame photo-transform family (top ~43-58% photo preserved — split-frame #17/#35/#36's canvas) whose second half translates the photo into an *archivist's field study*. Two variants share one novel mechanic:
- **Content-adaptive annotation panels** (No. 40): "Set up 5 small observation boards of uniform size at the bottom, automatically selected based on the photo content: Geographical location schematic / Terrain or skyline outline / Front or side view of the subject / Local structural section / Weather, water surface, cloud, vegetation, or road observation. All boards must come from the content of the original photo, and no unrelated structures should be added out of thin air." The model *chooses* the content of each panel per input photo — the template fixes the slots (count + size), the photo fills them.
- **Minimum-information compression contract** (No. 41): "Extract the most recognizable subject outlines, architectural structures, terrain trends… compressing them into a small multi-color rubber stamp image. Do not copy everything from the photo item by item. Retain only the minimum information necessary for someone to recognize the original location, subject, and scene relationships at a glance. Delete crowds, vehicles, dense windows, repetitive buildings, fine vegetation, decorative components, and irrelevant backgrounds." Plus a scale cap: the stamp occupies only 30-38% of its zone height and "cannot be enlarged into a common illustration, full landscape painting, or brand logo."
- **Auto-derived typography spec** (No. 40): the model generates a Chinese main title of 2-6 characters, numbering, a four-digit year, a short description, 3-4 scene info items, 4-6 structural observation labels — count ranges instead of fixed strings, keeping field-journal authenticity ("quiet, poetic, retaining a lot of white space"; explicitly not CAD/engineering drawing).

Why it works: unlike Fixed-Anchor series contracts (#25) where everything is pinned, this delegates *content selection* to the model while pinning *slot structure* (exactly N uniform panels, percentage zones) — the anti-fabrication clause ("no unrelated structures added out of thin air") keeps the adaptation honest. The compression contract inverts the usual detail-maximizing instinct: mandating *minimum viable recognition* defeats the model's tendency to over-render reference transforms. Use for travel/field-journal posters, logo/stamp extraction from photos, and any photo → distillation study.

Related same-cycle observations (already covered, not promoted): No. 76 "Poetic Wave of Departure Portrait" (Sep 3, Michael H. Lester) is an extreme ultra-minimal data point — the *entire prompt is a 5-line free-verse poem* ("in a rush / to get to her next stop / she departs / with a wave of her hand / and a throaty toodle-oo") — confirming technique #20's floor: poetic free verse works as a prompt form for low-intensity aesthetic images. No. 77 "Infrared Police Backseat Footage" (Sep 3) = Face Lock + Source-Look Preservation (#21) + exact-count overlay labels applied to surveillance-cam transformation.

### 39. Input-Conditional Fallback Clauses (new, observed in No. 76 "Multi-Angle Scene Reconstruction Grid" by M. Asif, Sep 4 2026)
A grid-of-shots prompt that branches explicitly on the *content of the input photo*, so one template survives any upload:
- **Core job:** "Using the attached image as the single source of truth, create ONE image that is a clean 3-column by 2-row grid of six photographs of the EXACT same scene, captured from six different camera positions, as if six cameras were placed around the room at the same instant." — a Multi-Angle variant of turnaround sheets, but scene-level (room + people + props), not character-level.
- **Scene lock:** "Lock everything from the attached image: the same people with the same faces, hair, skin tone, glasses, clothing and body proportions; the same furniture, props, walls, signage with the same text, lighting setup and color grade; the same time of day. Nothing is added, removed, or rearranged — only the camera position, lens and framing change between panels."
- **Per-panel lens spec:** each of the 6 panels names camera position + focal length + aperture (wide master 35mm; ceiling top-down 24mm; over-the-shoulder left 50mm f/2.0; reverse OTS right 50mm f/2.0; low-angle 28mm; tight close-up 85mm f/1.8 shallow DoF).
- **The novel mechanic — conditional fallbacks:** "If the scene contains only one person, apply the over-the-shoulder panels as a three-quarter side angle from the left and from the right of that person instead. If the scene contains no people, treat the main object or furniture group as the subject for panels 3, 4 and 6."
- **Grid rules closer:** equal panels, thin white gutters, no labels/numbers/captions, identical white balance/exposure/color grade/film grain across panels, consistent lighting direction.

Why it works: grid/turnaround templates normally break when the input doesn't match the assumed subject count; enumerating input-conditional branches keeps the template total (works on any photo) instead of average. Generalizes to any reference-based template: write the happy path, then "if [input condition], do [adaptation] instead" clauses for the common input shapes. Use for multi-angle coverage, virtual camera-array shots, and reusable client-facing templates that must survive arbitrary uploads.

Also observed this cycle: the **`{argument name="..." default="..."}` Raycast slot syntax** is now pervasive across README entries (No. 13, 20, 48, 50, 52, etc.) — inline fill-in slots that make prompts reusable templates. Syntax note only, not a technique; worth using when authoring reusable template prompts.

## Featured Prompt Patterns (Reusable Templates)

### Exploded Product Diagram
```json
{
  "type": "exploded view product diagram poster",
  "subject": "[product]",
  "style": "clean high-tech 3D render, studio lighting, glowing accents",
  "layout": {
    "centerpiece": "vertically stacked exploded view showing [N] layers",
    "callout_labels": {
      "count": [N],
      "left_side": ["[feature]: [desc]"],
      "right_side": ["[feature]: [desc]"]
    }
  }
}
```

### Broadcast UI Mockup
```
Goal: Create a [clean] screenshot showing [purpose].
Canvas: [dimensions], [background], minimal modern UI.
Top [header]: [exact element counts]
Main [content]: [exact counts]
Bottom [bar]: [exact element counts]
Visual style: [complete aesthetic]
```

### Before/After + Face Correction
```
Using REFERENCE_1 as the current [design] and REFERENCE_0 as the identity reference,
regenerate with the same [layout], but [specific change].
Keep [preserved elements] unchanged. Preserve exactly [N] visible text areas.
Do not redesign; the only correction is [fix].
```

### Cinematic Action Portrait
```
[Shot type]: [Wide Cinematic Medium-Full Shot]
[Subject with face lock]: matching exact reference...
[Setting & Atmosphere]: [detailed environment]
[Lighting & Color]: [specific light sources, directions]
[Technical]: [camera, lens, film stock, grain, DoF]
negative prompt: [avoid list]
```

## Monitoring
Daily watchdog cron job (11am, job `26c2c68477b8`) checks for new commits and prompt count changes. Silent when no changes. Weekly system report also tracks this repo under "Remote Repos Monitored".
