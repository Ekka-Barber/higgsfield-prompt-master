#!/usr/bin/env python3
"""
Intelligence Layers for Prompt Generation
==========================================
Three layers of domain expertise that transform a generic goal
into a professional-grade prompt:

1. PHOTOGRAPHY INTELLIGENCE — Camera bodies, lenses, lighting setups,
   color science, bokeh characteristics by shoot type

2. MARKETING INTELLIGENCE — AIDA framework, platform specs, demographic
   targeting, emotional triggers, competitive positioning

3. ART DIRECTION — Composition systems, color theory, visual hierarchy,
   contrast management, style references
"""

# ═══════════════════════════════════════════════════════════════════
# LAYER 1: PHOTOGRAPHY INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════

PHOTOGRAPHY = {
    "product": {
        "camera": "Phase One IQ4 150MP or Hasselblad X2D 100C",
        "lens": "80mm or 120mm macro f/2.8",
        "lighting": "Single softbox key light positioned 45° camera right at 3/4 power, large white fill card camera left at 1/4 intensity, subtle rim light from behind to separate product from background, acrylic diffusion sheet between key light and product for shadowless wrap",
        "color_science": "Color-calibrated for e-commerce, true-to-life ICC profile, neutral white balance at 5500K, no color cast, accurate fabric and material reproduction",
        "bokeh": "Tight depth of field on product label, smooth creamy background transition, focus stacked for full product sharpness",
        "post": "Frequency separation retouching for flawless surfaces, dust spot removal, subtle dodging on highlights, color-accurate proofing for print and web",
        "background": "Sweeping gradient from pure white to light gray (#FFFFFF to #F0F0F0), seamless paper sweep, no horizon line, product casts soft natural shadow",
    },
    "food": {
        "camera": "Canon EOS R5 or Sony A7RV",
        "lens": "100mm f/2.8 macro or 50mm f/1.2 for wider scenes",
        "lighting": "Large window light simulation from camera left at 90°, white bounce card camera right at 18 inches, backlit at 135° for steam and translucency, no front light to avoid flat reflections",
        "color_science": "Warm appetizing tones, enhanced reds and yellows for hunger response, slight saturation boost on greens, gold-tone white balance at 4800K",
        "bokeh": "Shallow depth of field on hero element, secondary items softly out of focus, circular specular highlights in background liquids",
        "post": "Enhanced steam and condensation, texture sharpening on crispy/grilled surfaces, glossy highlight enhancement on sauces, selective warmth on hero item",
        "background": "Rustic wooden table, marble surface, or dark slate, props blurred in background (ingredients, utensils, linen), negative space for text overlay",
    },
    "portrait": {
        "camera": "Sony A7IV or Canon R5",
        "lens": "85mm f/1.4 GM or 135mm f/1.8 for tighter compression",
        "lighting": "Rembrandt lighting pattern — key light at 45° camera left slightly above eye level, white reflector fill at camera right below chin, optional hair light from behind for separation from background",
        "color_science": "Warm natural skin tones, Kodak Portra 400 film emulation, slight orange-teal split tone, preserved skin texture and pore detail",
        "bokeh": "Extremely shallow at f/1.4, creamy circular bokeh, subject isolation with smooth background melt, eyes tack sharp",
        "post": "Natural frequency separation preserving skin texture, subtle dodge on iris catchlights, gentle burn on cheekbones for sculpting, no plastic skin",
        "background": "Complementary tone to subject wardrobe, mottled bokeh pattern from foliage or city lights, sufficient negative space for editorial text",
    },
    "fashion": {
        "camera": "Hasselblad X2D 100C or Phase One IQ4",
        "lens": "80mm f/2.8 or 50mm f/2.8 for environmental fashion",
        "lighting": "Beauty dish key light centered slightly above with diffusion sock, two strip softboxes as rim lights at 135° left and right, silver reflector below for fill, wind machine for fabric movement",
        "color_science": "Editorial color grade — muted shadows with vibrant midtones, fashion magazine emulation (Vogue/Harper's Bazaar), calibrated for CMYK print output",
        "bokeh": "Medium depth of field at f/4-f/5.6 for full outfit sharpness, location background recognizable but softened",
        "post": "High-end fashion retouching, D&B (dodge and burn) body sculpting, fabric texture enhancement, skin smoothing with visible pore preservation",
        "background": "Studio cyc wall in neutral gray (#7A7A7A), or environmental location — brutalist architecture, minimalist interior, or natural landscape",
    },
    "beauty": {
        "camera": "Canon R5 with MP-E 65mm macro for extreme detail",
        "lens": "100mm f/2.8 macro or 85mm f/1.2 for beauty portraits",
        "lighting": "Ring light or beauty dish dead-center for shadowless wrap, clamshell lighting with key above and reflector below, polarization filter to eliminate skin glare",
        "color_science": "Flawless skin reproduction, accurate cosmetic color rendering, pink-warm skin undertones, dewy highlight reproduction",
        "bokeh": "Tight focus on eyes or product, extreme macro detail on skin texture and product particles",
        "post": "Pixel-level skin retouching, frequency separation, luminosity masking for highlight control, cosmetic shimmer enhancement",
        "background": "Pure white or soft pastel gradient, clean and minimal, product or face fills 70%+ of frame",
    },
    "lifestyle": {
        "camera": "Sony A7IV or Fujifilm X-T5 for organic film look",
        "lens": "35mm f/1.4 or 24mm f/1.4 for environmental context",
        "lighting": "Natural window light or golden hour outdoor, no artificial light, reflector for gentle fill, overcast sky as natural softbox",
        "color_science": "Candid film emulation — Fuji Pro 400H or Kodak Gold 200 look, warm midtones, slightly lifted blacks for filmic feel",
        "bokeh": "Moderate depth of field, environmental context visible but soft, storytelling background elements",
        "post": "Film grain overlay, light leak simulation, subtle cross-processing, natural color grading with lifted shadows",
        "background": "Real environment — coffee shop, home interior, urban street, nature — reflecting authentic lifestyle context",
    },
    "automotive": {
        "camera": "Phase One IQ4 or Hasselblad H6D-100c",
        "lens": "40mm or 50mm f/2.8 for full car, 120mm for detail",
        "lighting": "Large 20x20ft overhead silk diffusion for sky reflection control, multiple strip lights along the car's body line for sculpted reflections, polarized light to control paint glare",
        "color_science": "Accurate metallic and pearl paint reproduction, deep blacks in shadows, controlled specular highlights on chrome and glass",
        "bokeh": "Wide depth of field for full car sharpness at f/8-f/11, controlled background that doesn't distract from vehicle",
        "post": "Paint enhancement — frequency separation on body panels, reflection management, wheel and rim detailing, pano stitch for wide automotive",
        "background": "Seamless studio cove in gradient gray, or cinematic location — tunnel, mountain road, urban nightscape with controlled reflections",
    },
    "architectural": {
        "camera": "Phase One IQ4 with Schneider 28mm or 40mm leaf shutter",
        "lens": "Tilt-shift 24mm or 17mm for perspective control",
        "lighting": "Available light only — blue hour or golden hour, multiple exposures blended for interior/exterior balance, no artificial supplemental light",
        "color_science": "Architectural accuracy, neutral color reproduction, true material colors — wood, concrete, steel, glass — no artistic color cast",
        "bokeh": "Deep depth of field at f/8-f/11, everything sharp from foreground to infinity, hyperfocal focusing",
        "post": "HDR blend for dynamic range, perspective correction, vertical alignment, window pull for exterior view retention",
        "background": "The architecture IS the subject — context includes sky, landscaping, and surrounding environment",
    },
}

# ═══════════════════════════════════════════════════════════════════
# LAYER 2: MARKETING INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════

MARKETING = {
    "instagram_feed": {
        "framework": "AIDA",
        "ratio": "4:5",
        "attention": "Bold hero element in upper third — the scroll-stopper. High contrast, vibrant color, or unexpected composition that stands out in a feed of thumbnails",
        "interest": "Middle third shows product in context — lifestyle usage, before/after, or detail shot that answers 'what is this?'",
        "desire": "Lower third shows aspirational outcome — the transformed self, the status symbol, the emotional payoff",
        "action": "Bottom 10% reserved for CTA overlay zone — 'Swipe', 'Link in bio', or 'Shop now' — high contrast against background",
        "safe_zones": "Avoid placing critical text in the right 15% (Instagram UI overlay), bottom 20% (caption overlay), top 5% (status bar)",
        "color_strategy": "Brand-dominant palette with one complementary accent for the CTA — 70/20/10 rule (primary/secondary/accent)",
        "tone": "Aspirational but authentic — polished but not sterile, lifestyle-driven",
    },
    "instagram_story": {
        "framework": "FOMO",
        "ratio": "9:16",
        "attention": "Full-bleed hero image, text overlay in top third within 2 seconds of tap — Stories are glanced at for 1-3 seconds",
        "interest": "Sticker-poll or question overlay to drive engagement, swipe-up link indicator",
        "desire": "Countdown timer, limited-time offer, or exclusive access messaging",
        "action": "Bottom 25% reserved for 'Swipe up' or link sticker — must be tappable zone",
        "safe_zones": "Top 15% (profile name + timestamp), bottom 25% (link sticker + reply bar), right 10% (report/more)",
        "color_strategy": "High contrast for text legibility — dark overlay on bright image or vice versa, minimum 4.5:1 contrast ratio",
        "tone": "Urgent, exclusive, real-time — behind-the-scenes or flash sale energy",
    },
    "youtube_thumbnail": {
        "framework": "Curiosity Gap",
        "ratio": "16:9",
        "attention": "Emotional face in left or right third at 3x normal size — human faces drive 38% higher CTR. Expression must match video emotion",
        "interest": "Visual contrast between left and right halves — before/after, problem/solution, or unexpected juxtaposition",
        "desire": "Large bold text MAX 5 words in complementary color — readable at 120x68px (mobile thumbnail size)",
        "action": "Arrow, circle, or highlight pointing to the curiosity element — visual finger-pointing",
        "safe_zones": "Bottom 8% (progress bar), bottom-right corner (timestamp), right 15% (YouTube UI)",
        "color_strategy": "Maximum 3 colors — background, text, and one accent. High saturation for small-size visibility. Avoid white backgrounds (blend with YouTube dark mode)",
        "tone": "Clickable energy — excitement, surprise, or intrigue. NOT clickbait — deliver on the promise",
    },
    "linkedin_post": {
        "framework": "Authority",
        "ratio": "1.91:1 or 1:1",
        "attention": "Professional hero image — clean, corporate, aspirational. No stock-photo clichés",
        "interest": "Data visualization, infographic element, or professional context (office, conference, product in use)",
        "desire": "Growth, efficiency, or success metrics implied visually — charts, upward arrows, team collaboration",
        "action": "Minimal — LinkedIn audience prefers value over CTA. Subtle logo placement bottom-right",
        "safe_zones": "Standard banner zones apply. Avoid bottom 10% (article preview overlay)",
        "color_strategy": "Corporate palette — blues, grays, whites. One accent color for data highlight. Professional, restrained",
        "tone": "Authoritative, data-driven, professional. No exclamation marks. Value-first",
    },
    "poster": {
        "framework": "Visual Hierarchy",
        "ratio": "2:3 or 3:4",
        "attention": "Hero visual occupies 50-60% of poster area — must be visible from 10 feet away (poster is meant to be read across a room)",
        "interest": "Headline in largest type — 30% of poster width minimum, readable at 3 meters",
        "desire": "Supporting details in clear hierarchy — date, venue, call to action — decreasing type sizes guide the eye down",
        "action": "QR code, URL, or contact info in bottom 10% — don't make people search for how to act",
        "safe_zones": "Bleed zone: keep critical elements 0.25 inch from edges. Trim zone varies by printer",
        "color_strategy": "Limited palette — 2-3 colors maximum for screen printing cost. CMYK conversion for print. High contrast for distance readability",
        "tone": "Event-appropriate — formal for conferences, energetic for concerts, informative for educational",
    },
    "ecommerce": {
        "framework": "Conversion",
        "ratio": "1:1 or 4:5",
        "attention": "Product centered, fills 80%+ of frame, pure white background (#FFFFFF) for marketplace compliance (Amazon, Google Shopping)",
        "interest": "Product shown from most flattering angle — 3/4 view for 3D objects, flat-lay for flat items, model for wearables",
        "desire": "Lifestyle/infographic images as 2nd-6th images in carousel — product in use, size comparison, material detail",
        "action": "Price, rating stars, and 'Add to Cart' are handled by the platform UI — image must make product desirable enough to click",
        "safe_zones": "Product must not touch edges. 5% margin minimum. No text overlays on main image (marketplace rules)",
        "color_strategy": "Pure white background mandatory for main image. Brand colors in secondary images only. Color-accurate product reproduction (returns prevention)",
        "tone": "Clean, trustworthy, aspirational. Product is the hero — no distractions",
    },
    "billboard": {
        "framework": "3-Second Rule",
        "ratio": "16:9 or 2:1",
        "attention": "ONE core message — maximum 7 words. Drivers have 3 seconds to read it at 60mph",
        "interest": "Single powerful image — recognizable from 100+ feet. No complex scenes or fine detail",
        "desire": "Emotional trigger — humor, fear, aspiration, or curiosity. The feeling IS the message",
        "action": "URL or phone number only — no QR codes (nobody stops on a highway). Maximum 1 action element",
        "safe_zones": "All text within center 70% of canvas. 10% bleed for physical installation variance",
        "color_strategy": "High contrast — maximum 3 colors. Warm colors advance (red, orange), cool colors recede (blue, green). Bold sans-serif type only",
        "tone": "Bold, simple, memorable. If you can't read it in 3 seconds, it failed",
    },
}

# ═══════════════════════════════════════════════════════════════════
# LAYER 3: ART DIRECTION
# ═══════════════════════════════════════════════════════════════════

ART_DIRECTION = {
    "composition": {
        "rule_of_thirds": "Primary subject at upper-right or upper-left third intersection. Horizon line on upper or lower third. Creates dynamic tension and natural eye flow",
        "golden_ratio": "Subject positioned at golden spiral focal point (0.618 from any edge). Spiral flow guides eye through frame. More organic and pleasing than rule of thirds",
        "centered_symmetry": "Subject dead-center with mirror symmetry left/right. Conveys formality, power, and stability. Use for hero products and authoritative portraits",
        "leading_lines": "Converging lines (roads, architecture, shadows, perspective) draw eye from edges to subject at vanishing point. Creates depth and guides attention",
        "negative_space": "60-70% of frame is empty space, subject occupies 30-40%. Creates breathing room, elegance, and space for text overlay. Essential for editorial and advertising",
        "fill_the_frame": "Subject fills 90%+ of frame, edges cropped. Creates intimacy, intensity, and detail focus. Use for beauty close-ups and product hero shots",
        "diagonal_dynamism": "Subjects positioned along diagonal axes (corner to corner). Creates energy, movement, and visual interest. Breaks static feel of horizontal/vertical compositions",
        "frame_within_frame": "Architectural or environmental elements create a natural frame around subject (doorway, window, arch). Adds depth, context, and focuses attention",
    },
    "color_theory": {
        "complementary": "Opposite colors on wheel — blue/orange, red/green, purple/yellow. Maximum contrast and vibrancy. Use for attention-grabbing ads and energetic designs",
        "analogous": "Adjacent colors — blue/teal/green or red/orange/yellow. Harmonious, calming, natural. Use for lifestyle, wellness, and organic brands",
        "triadic": "Evenly spaced colors — red/yellow/blue or orange/green/purple. Vibrant but balanced. Use for playful brands and children's content",
        "monochromatic": "Single hue in varying lightness/saturation. Sophisticated, minimalist, brand-focused. Use for luxury and premium positioning",
        "split_complementary": "Base color plus two adjacent to its complement. Less tension than complementary, more nuanced. Use for refined commercial work",
    },
    "contrast": {
        "high_key": "Bright, airy, predominantly light tones (80%+ highlights). Conveys optimism, purity, cleanliness. Use for beauty, wellness, minimalist product shots",
        "low_key": "Dark, moody, predominantly shadow tones (70%+ darks). Conveys drama, mystery, luxury. Use for automotive, spirits, high-end fashion",
        "full_range": "Full tonal range from deep blacks to bright whites. Maximum impact and realism. Use for editorial, documentary, and commercial photography",
        "flat_design": "Reduced tonal range, minimal shadows, uniform lighting. Conveys modern, clean, digital-native aesthetic. Use for UI/UX and tech brands",
    },
    "style_references": {
        "minimalist": "Negative space, limited palette, single focal point, clean sans-serif type. Apple, Muji, Kinfolk magazine aesthetic",
        "brutalist": "Raw materials, exposed structure, high contrast, oversized type. Balenciaga, Off-White, underground music aesthetic",
        "art_deco": "Geometric patterns, gold accents, symmetrical layout, luxurious materials. Great Gatsby, vintage travel posters",
        "bauhaus": "Form follows function, primary colors, geometric shapes, grid-based. Modernist design school aesthetic",
        "memphis": "Bold patterns, squiggles, bright contrasting colors, playful shapes. 80s postmodern, contemporary fashion campaigns",
        "y2k": "Chrome, metallic, futuristic, cyber elements, iridescent. Late 90s/early 2000s nostalgia, tech branding",
        "editorial": "Magazine-quality, high production value, storytelling composition. Vogue, Monocle, Kinfolk",
        "cinematic": "Film still quality, anamorphic lens flare, teal-orange grade, shallow depth of field. Roger Deakins, Emmanuel Lubezki inspired",
    },
}

# ═══════════════════════════════════════════════════════════════════
# CATEGORY → INTELLIGENCE MAPPING
# ═══════════════════════════════════════════════════════════════════

CATEGORY_PHOTO_MAP = {
    "Product Marketing": "product",
    "E-commerce Main Image": "product",
    "Social Media Post": "lifestyle",
    "Profile / Avatar": "portrait",
    "Portrait / Selfie": "portrait",
    "Poster / Flyer": "product",
    "App / Web Design": None,  # Not photography
    "Comic / Storyboard": None,
    "Game Asset": None,
    "Infographic / Edu Visual": None,
    "YouTube Thumbnail": None,
    "Architecture / Interior": "architectural",
    "Cinematic / Film Still": None,
}

CATEGORY_MARKETING_MAP = {
    "Social Media Post": "instagram_feed",
    "Product Marketing": "ecommerce",
    "E-commerce Main Image": "ecommerce",
    "Poster / Flyer": "poster",
    "YouTube Thumbnail": "youtube_thumbnail",
    "App / Web Design": None,
    "Profile / Avatar": None,
}

def get_photo_intelligence(category: str, goal: str = "") -> dict:
    """Get photography settings for a category, with goal-based override."""
    photo_key = CATEGORY_PHOTO_MAP.get(category)
    if not photo_key:
        # Try to infer from goal keywords
        goal_lower = goal.lower()
        if any(w in goal_lower for w in ["food", "restaurant", "dish", "meal", "recipe"]):
            photo_key = "food"
        elif any(w in goal_lower for w in ["car", "automotive", "vehicle", "truck"]):
            photo_key = "automotive"
        elif any(w in goal_lower for w in ["building", "architecture", "interior", "room"]):
            photo_key = "architectural"
        elif any(w in goal_lower for w in ["fashion", "clothing", "outfit", "runway", "apparel"]):
            photo_key = "fashion"
        elif any(w in goal_lower for w in ["beauty", "cosmetic", "makeup", "skincare"]):
            photo_key = "beauty"
        elif any(w in goal_lower for w in ["product", "bottle", "package", "device"]):
            photo_key = "product"
        else:
            photo_key = "lifestyle"
    return PHOTOGRAPHY.get(photo_key, PHOTOGRAPHY["lifestyle"])

def get_marketing_intelligence(category: str, goal: str = "") -> dict:
    """Get marketing framework for a category."""
    mkt_key = CATEGORY_MARKETING_MAP.get(category)
    if not mkt_key:
        goal_lower = goal.lower()
        if any(w in goal_lower for w in ["instagram", "social", "facebook", "twitter"]):
            mkt_key = "instagram_feed"
        elif any(w in goal_lower for w in ["story", "reel", "tiktok"]):
            mkt_key = "instagram_story"
        elif any(w in goal_lower for w in ["youtube", "video", "thumbnail"]):
            mkt_key = "youtube_thumbnail"
        elif any(w in goal_lower for w in ["linkedin", "professional", "b2b"]):
            mkt_key = "linkedin_post"
        elif any(w in goal_lower for w in ["poster", "flyer", "event", "concert"]):
            mkt_key = "poster"
        elif any(w in goal_lower for w in ["shop", "store", "amazon", "product listing"]):
            mkt_key = "ecommerce"
        elif any(w in goal_lower for w in ["billboard", "outdoor", "transit"]):
            mkt_key = "billboard"
    return MARKETING.get(mkt_key) if mkt_key else None

def infer_mood(style: str, goal: str) -> str:
    """Infer mood/atmosphere from style and goal keywords."""
    text = f"{style} {goal}".lower()
    if any(w in text for w in ["luxury", "premium", "elegant", "sophisticated"]):
        return "refined, aspirational, exclusive — quiet confidence and understated power"
    elif any(w in text for w in ["vibrant", "energetic", "bold", "dynamic"]):
        return "high-energy, attention-grabbing, confident — bold and unapologetic"
    elif any(w in text for w in ["minimalist", "clean", "simple", "modern"]):
        return "calm, clear, focused — intentional minimalism where every element earns its place"
    elif any(w in text for w in ["cinematic", "dramatic", "moody", "dark"]):
        return "dramatic, atmospheric, cinematic — deep shadows and directional light creating narrative tension"
    elif any(w in text for w in ["playful", "fun", "colorful", "cheerful"]):
        return "joyful, approachable, warm — inviting and human with genuine emotion"
    elif any(w in text for w in ["corporate", "professional", "business"]):
        return "trustworthy, authoritative, competent — professional credibility without coldness"
    elif any(w in text for w in ["natural", "organic", "earthy", "rustic"]):
        return "grounded, authentic, warm — natural materials and honest imperfection"
    elif any(w in text for w in ["futuristic", "tech", "digital", "cyber"]):
        return "innovative, sleek, forward-looking — precision engineering meets aspirational technology"
    else:
        return "polished, professional, purposeful — every detail deliberately crafted for impact"


# Source: Ekka-Barber/higgsfield-prompt-master corpus analysis + freestylefly/awesome-gpt-image-2 (MIT)
# ═══════════════════════════════════════════════════════════════════
# LAYER 4: GPT_IMAGE_2 MODEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
# Model-specific guidance for prompts routed to gpt_image_2. Unlike the
# photography/marketing layers (generic camera + platform specs), this layer
# encodes what GPT Image 2 actually does well: JSON-fidelity layout parsing,
# exact element counting, spatial anchoring by name, reliable text rendering,
# and multi-zone composition. Derived from analysis of the 8,596-prompt
# corpus (54% JSON-structured) + awesome-gpt-image-2 community patterns.

GPT_IMAGE_2 = {
    "strengths": [
        "High-fidelity JSON layout parsing — keys like layout.centerpiece / left_section / right_section / footer render as placed",
        "Exact element counting — 'exactly 4 cards' / 'exactly 8 rows' is honored, preventing arbitrary additions",
        "Spatial anchoring by name — 'top-left header', 'bottom-right product card' positions elements deterministically",
        "Reliable text rendering — UI labels, headlines, callouts, and short body copy render legibly without garbling",
        "Multi-zone composition — complex layouts (dashboards, broadcast UI, recipe cards) hold together coherently",
        "Exploded/labeled diagrams — centerpiece + callout_labels split left/right produce clean technical illustrations",
        "Cross-reference image mapping — REFERENCE_0 as identity / REFERENCE_1 as layout disambiguates multi-image edits",
        "Face lock edits — 'maintain exact facial structure from reference with 100% accuracy' preserves identity on edits",
    ],
    "weaknesses": [
        "Long unstructured prose drifts — flat paragraphs lose element discipline on complex scenes (prefer JSON for layouts)",
        "Without exact counts, model tends to add extra items (more cards, more rows) to fill space",
        "Body text beyond ~12 words per block starts to garble or hallucinate characters",
        "Fine print / disclaimers / legal-sized text renders poorly — keep text blocks short",
        "Left unspecified, layout zones get reshuffled or merged on regeneration",
        "Reference images without explicit REFERENCE_N numbering get applied ambiguously",
        "Negative constraints buried in prose are ignored — 'negative prompt:' must be a labeled closing block",
    ],
    "preferred_structures": {
        "json_object": {
            "when": "PRIMARY structure — 54% of corpus. Use for UI mockups, exploded diagrams, infographics, posters, any multi-zone layout",
            "keys": "type, subject, style, background, header, layout {centerpiece, left_section, right_section, footer}, callout_labels",
            "rule": "Every named region in JSON becomes a placed region in the image. Be explicit — undefined regions get filled arbitrarily",
        },
        "flat_paragraph": {
            "when": "46% of corpus. Single-subject, single-composition — portraits, cinematic shots, simple illustrations",
            "pattern": "[SUBJECT] [STYLE] [TECHNICAL] [COMPOSITION] [BACKGROUND] [DETAILS] [CONSTRAINTS]",
            "rule": "Reserve for ONE subject in ONE composition. Switch to JSON the moment a second zone appears",
        },
        "goal_canvas_sections": {
            "when": "Niche — complex multi-zone designs (dashboards, broadcast UI, recipe cards) needing element counts per region",
            "pattern": "Goal: <intent> | Canvas: <size> | named sections with element counts | closing 'Visual style:' paragraph as guard",
            "rule": "Always close with a Visual style paragraph summarizing the full aesthetic — it prevents style drift across zones",
        },
    },
    "text_rendering": {
        "general_rule": "Keep text blocks SHORT — headlines <= 6 words, labels <= 3 words, body <= 12 words per block. Longer copy garbles",
        "ui_labels": "Short UI strings render reliably: button labels, nav items, badges, tab names, status indicators, metric values",
        "headlines": "Large bold headlines <= 6 words render crisply. Use explicit font-weight and size hints ('bold 48px sans-serif headline')",
        "body_copy": "Limit to ~12 words per block. For longer copy, break into multiple discrete labeled blocks rather than one paragraph",
        "numbers_metrics": "Numeric values (prices, stats, counts, percentages) render accurately — ideal for dashboards and infographics",
        "multilingual": "Latin-script languages render well. Non-Latin scripts (Arabic, CJK) need explicit script + direction hints and shorter strings",
        "typography_hints": "Specify family (sans/serif/mono), weight (bold/regular/light), and size tier explicitly. 'clean sans-serif typography' alone is too vague",
    },
    "quality_modifiers": {
        "ui_screenshot": {
            "structure": "JSON object with layout.centerpiece + named zones (top_header, left_sidebar, main_panel, bottom_bar)",
            "counting": "State exact element counts: 'exactly 6 nav items', 'exactly 4 cards in main grid', 'exactly 3 tabs'",
            "anchoring": "Anchor by name: 'top-left logo', 'bottom-right CTA button', 'center hero card'",
            "text": "Short UI labels only — button text, nav labels, metric values. No long body copy in mockups",
            "style_guard": "Close with Visual style paragraph: clean modern SaaS aesthetic, generous whitespace, consistent 8px spacing grid, subtle shadows",
        },
        "infographic": {
            "structure": "JSON with header + layout (centerpiece chart/data viz + left_section legend + right_section callouts) or Goal/Canvas/Sections",
            "counting": "'exactly 5 data points', 'exactly 4 stat blocks', 'exactly 3 icon rows' — prevents filler additions",
            "anchoring": "'top-center title', 'center hero chart', 'bottom legend bar'",
            "text": "Title + short stat labels + numeric values. Numbers render accurately — lean on metrics",
            "style_guard": "Editorial infographic aesthetic, limited palette of 3 colors, clear typographic hierarchy, data-first composition",
        },
        "ecommerce_pdp": {
            "structure": "JSON with centerpiece (product hero) + callout_labels (feature callouts split left/right) + footer (price/CTA zone)",
            "counting": "'exactly 4 feature callouts', 'exactly 3 thumbnail variants', 'exactly 1 price block'",
            "anchoring": "'center hero product', 'top-left brand mark', 'bottom-right price + CTA'",
            "text": "Product name + short feature labels + price. Keep feature copy <= 6 words each",
            "style_guard": "Clean e-commerce PDP aesthetic, pure white background, soft natural shadow under product, color-accurate material reproduction",
        },
        "exploded_diagram": {
            "structure": "JSON with layout.centerpiece: 'vertically stacked exploded view' + callout_labels split into left_section/right_section arrays",
            "counting": "'exactly 7 component layers', 'exactly 7 callout labels matching components'",
            "anchoring": "Each component gets a numbered callout — 'component 1: ...', with leader lines implied",
            "text": "Numbered component labels + short technical names. No descriptions in the callouts",
            "style_guard": "Technical illustration aesthetic, isometric or orthographic projection, neutral background, precise line work",
        },
        "cinematic": {
            "structure": "Flat paragraph with labeled sections: Shot Type / Subject + Face Lock / Setting / Action / Attire / Lighting & Color / Technical / negative prompt",
            "counting": "Single subject, single composition — flat structure is correct here, do NOT use JSON",
            "anchoring": "Subject placement via shot type ('centered medium shot', 'rule-of-thirds wide shot')",
            "text": "Minimal diegetic text only. This is not a layout category",
            "style_guard": "Camera spec depth: name the lens (e.g. 'Panavision anamorphic 70mm'), shallow DoF, cinematic color grade (teal-orange / deep contrast / HDR dynamic range)",
        },
        "portrait_edit": {
            "structure": "Flat paragraph with explicit Face Lock clause + cross-reference mapping (REFERENCE_0 as identity)",
            "counting": "One face, preserved exactly",
            "anchoring": "Face lock: 'maintain exact facial structure from reference with 100% accuracy, preserve micro-details, no beautification'",
            "text": "N/A",
            "style_guard": "Subsurface scattering: 'soft natural skin with visible pores, smooth tonal transitions, subtle subsurface scattering'. Always pair with a negative prompt block",
        },
    },
    "negative_prompt_library": {
        "ui_screenshot": "negative prompt: overlapping elements, misaligned grid, broken layout, illegible labels, placeholder lorem ipsum text, inconsistent spacing, clipped text, distorted buttons",
        "infographic": "negative prompt: misaligned data, illegible numbers, extra unlabeled elements, cluttered composition, inconsistent chart styling, garbled axis labels, color confusion",
        "ecommerce_pdp": "negative prompt: distorted product, wrong proportions, color-inaccurate material, cluttered callouts, overlapping labels, illegible price, shadow artifacts",
        "exploded_diagram": "negative prompt: misaligned components, mismatched callout numbering, distorted proportions, floating unanchored parts, garbled technical labels",
        "cinematic": "negative prompt: distorted face, plastic skin, beauty filter effect, oversharpened texture, washed-out colors, banding, noisy shadows, anamorphic distortion errors",
        "portrait_edit": "negative prompt: distorted face, plastic skin, beauty filter effect, altered facial structure, lost likeness, over-smoothed pores, uncanny valley, changed identity",
        "general": "negative prompt: distorted elements, illegible text, garbled characters, overlapping zones, misaligned layout, extra unrequested elements, inconsistent styling",
    },
    "token_budget_guidance": {
        "principle": "GPT Image 2 rewards detailed structured prompts but loses discipline past a threshold. Budget by structure, not by word count",
        "json_layout": "Aim 200-450 tokens. Every named region earns its tokens — undefined space gets filled. More zones = more JSON keys, not more prose per key",
        "flat_cinematic": "Aim 150-350 tokens. Camera + lighting + color + action + negative prompt. Beyond ~400 tokens the scene starts to drift and add unrequested elements",
        "goal_canvas_sections": "Aim 300-600 tokens. Justified by explicit per-section element counts. The closing Visual style paragraph is ~50-80 tokens and is NOT optional trim",
        "over_budget_warning": "If a prompt exceeds ~650 tokens, the model tends to: add extra unrequested elements, drift on style, garble longer text blocks. Split into focused regions instead",
        "minimum_viable": "Below ~80 tokens the image is under-specified and the model improvises. Even simple shots need subject + style + composition + background minimum",
        "negative_prompt_cost": "The 'negative prompt:' block is ~20-40 tokens and pays for itself — always include one for layout and portrait categories",
    },
}


def get_gpt_image_2_intelligence(category: str, goal: str = "") -> dict:
    """Get GPT Image 2 model-specific guidance for a category.

    Returns the quality_modifiers + negative_prompt + text_rendering slice
    relevant to the category/goal, plus the always-on structure/budget/strengths
    context. Falls back to goal-keyword inference, then to the general slice.
    """
    cat_to_modifier = {
        "App / Web Design": "ui_screenshot",
        "Infographic / Edu Visual": "infographic",
        "E-commerce Main Image": "ecommerce_pdp",
        "Product Marketing": "ecommerce_pdp",
        "Game Asset": "exploded_diagram",
        "Cinematic / Film Still": "cinematic",
        "Portrait / Selfie": "portrait_edit",
        "Profile / Avatar": "portrait_edit",
    }
    modifier_key = cat_to_modifier.get(category)

    if not modifier_key:
        g = goal.lower()
        if any(w in g for w in ["ui", "dashboard", "mockup", "interface", "app screen", "web page"]):
            modifier_key = "ui_screenshot"
        elif any(w in g for w in ["infographic", "chart", "data viz", "diagram", "stat"]):
            modifier_key = "infographic"
        elif any(w in g for w in ["product page", "pdp", "e-commerce", "ecommerce", "product detail", "shop"]):
            modifier_key = "ecommerce_pdp"
        elif any(w in g for w in ["exploded", "technical illustration", "breakdown", "components"]):
            modifier_key = "exploded_diagram"
        elif any(w in g for w in ["cinematic", "film still", "movie", "shot on", "anamorphic"]):
            modifier_key = "cinematic"
        elif any(w in g for w in ["portrait", "face", "headshot", "selfie", "avatar", "identity"]):
            modifier_key = "portrait_edit"
        else:
            modifier_key = "ui_screenshot"  # GPT Image 2's dominant use case in the corpus

    neg_key = modifier_key if modifier_key in GPT_IMAGE_2["negative_prompt_library"] else "general"

    return {
        "modifier": GPT_IMAGE_2["quality_modifiers"][modifier_key],
        "negative_prompt": GPT_IMAGE_2["negative_prompt_library"][neg_key],
        "text_rendering": GPT_IMAGE_2["text_rendering"],
        "preferred_structures": GPT_IMAGE_2["preferred_structures"],
        "token_budget_guidance": GPT_IMAGE_2["token_budget_guidance"],
        "modifier_key": modifier_key,
    }


# Source: Google Cloud Nano Banana guide + kingbootoshi/nano-banana-2-skill (MIT) + ZeroLu/awesome-nanobanana-pro (MIT)
# ═══════════════════════════════════════════════════════════════════
# LAYER 5: NANO_BANANA MODEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
# Model-specific guidance for prompts routed to nano_banana_2. Nano Banana
# (Gemini Flash Image / Gemini 3 Pro Image) is the photography & reference-
# image model: 1,329 NB prompts in the corpus, heavily skewed to Social
# Media (46%), Profile/Avatar (12%), camera-spec prose (62%), and lighting
# directives (63%). Unlike GPT Image 2 (layout/JSON-first), NB rewards
# camera-metadata vocabulary, face-lock clauses, and multi-image reference
# composition (up to 14 inputs). Derived from the corpus model-comparison
# (Section 12) + the photo-editing/avatar NB master prompts + community
# skill specs. NOT derived from GPT_IMAGE_2 guidance — distinct strengths.

NANO_BANANA = {
    "models": {
        # "flash" alias = Nano Banana 2 = Gemini 3.1 Flash Image
        "nb2": {
            "alias": "flash",
            "engine": "Gemini 3.1 Flash Image",
            "input_tokens": 131072,
            "output_tokens": 32768,
            "cost_per_1k": "lowest tier — fast, cheap, default for high-volume photo + edit tasks",
            "strength": "speed and cost efficiency for photorealistic generation + reference-image edits; the workhorse for avatars, portraits, social, product restage",
        },
        # "pro" alias = Nano Banana Pro = Gemini 3 Pro Image
        "nb_pro": {
            "alias": "pro",
            "engine": "Gemini 3 Pro Image",
            "input_tokens": 65536,
            "output_tokens": 32768,
            "cost_per_1k": "premium tier — higher fidelity, reserved for hero/brand/photographic-detail work",
            "strength": "maximum photoreal fidelity, finer skin/material texture, better long-range coherence; use when nb2 output undersells the subject",
        },
    },
    "strengths": [
        "Photorealistic camera output — 62% of NB corpus leads with camera body, lens, focal length, aperture (vs 45% for GPT Image 2)",
        "Lighting directives render faithfully — 63% of NB corpus specifies lighting setup (Rembrandt, three-point, window, golden hour)",
        "Reference-image editing & identity preservation — face-lock clauses hold likeness across restyle/background/wardrobe swaps",
        "Up to 14 reference images per request — multi-image composition, style transfer, and subject-to-scene mapping",
        "Natural skin texture with visible pores and subsurface scattering — no plastic-skin default",
        "Shorter, prose-driven prompts succeed (avg 1,267 chars vs 1,634 for GPT Image 2) — camera vocabulary over layout scaffolding",
        "JSON compartmentalization works (19.6% of NB corpus) for multi-element scenes that need zone discipline",
        "Web-grounded generation — can ground entity/brand/place accuracy against live web context when factual fidelity matters",
    ],
    "weaknesses": [
        "Layout/UI/diagram work is weaker than GPT Image 2 (Layout/Comp 47% vs 71%) — switch models for dashboards, infographics, exploded diagrams",
        "Long body text and dense UI labels garble — keep text blocks short, prefer diegetic/minimal text",
        "Without an explicit face-lock clause, identity drifts on edits (beautification, altered bone structure)",
        "Without an explicit 'Do NOT change ...' closing clause, the model tends to over-edit (modernize vintage, alter features)",
        "Aspect ratio is not reliably inferred from prose — supply ratio or a dimension-locking reference",
        "Reference images beyond the supported MIME set or exceeding 14 inputs are ignored or merged ambiguously",
        "Negative prompts buried in prose are ignored — put constraints in a labeled closing clause",
    ],
    "frameworks": {
        # Framework 1 — pure text-to-image (no reference inputs)
        "T2I": {
            "name": "Text-to-Image (camera-spec prose)",
            "formula": "[SUBJECT] + [CAMERA: body + lens + aperture] + [LIGHTING setup] + [SETTING/BACKGROUND] + [STYLE/MOOD] + [COMPOSITION + ratio] + [TECHNICAL: 8k, color grade] + [CONSTRAINTS clause]",
            "when": "Fresh generation with no reference image — avatars, portraits, social, product, food. The dominant NB pattern (camera-spec prose)",
            "rule": "Lead with subject, then camera metadata. NB rewards photographic vocabulary far more than layout scaffolding",
        },
        # Framework 2 — reference-image-driven (edit / restyle / compose)
        "Multimodal": {
            "name": "Multimodal reference composition",
            "formula": "[FACE-LOCK clause on uploaded image] + [TRANSFORM: restyle/background/wardrobe] + [PRESERVE: identity, lighting direction, color temperature] + [OUTPUT camera/style] + [Do NOT ... clause]",
            "when": "1-14 reference images attached — headshot makeover, background replacement, style transfer, restoration, multi-image composition",
            "rule": "First reference = primary subject/style. State exactly what to preserve and what to change. Always close with a 'Do NOT alter identity' clause",
        },
        # Framework 3 — factually grounded generation
        "Web-grounded": {
            "name": "Web-grounded factual generation",
            "formula": "[ENTITY/BRAND/PLACE subject] + [ground: live web context for accuracy] + [CAMERA + LIGHTING] + [COMPOSITION] + [ACCURACY clause: true-to-life details, real proportions, correct branding]",
            "when": "Output must be factually faithful to a real entity — brand product, public figure, landmark, recognized IP",
            "rule": "Reserve for when factual accuracy (correct logo, real architecture, accurate likeness) matters more than stylization. Pair with a face-lock or accuracy clause",
        },
    },
    "reference_image_rules": {
        "max_images": "Up to 14 reference images per request",
        "mime_types": "png, jpeg, webp, heic, heif (unsupported types are ignored or merged ambiguously)",
        "first_reference": "The FIRST reference image sets the primary subject + style — treat it as the identity/style anchor",
        "last_reference": "The LAST reference image can lock output dimensions/aspect ratio (blank-image dimension trick: attach a blank canvas of the target ratio to force the output shape)",
        "ordering": "Order matters: identity/style refs first, layout/composition refs middle, dimension-lock ref last",
        "numbering": "When referencing specific inputs in prose, number them (uploaded image / first reference) — unnumbered refs get applied ambiguously",
    },
    "face_lock_phrasings": [
        "Keep the facial features of the person in the uploaded image exactly consistent",
        "Preserve original facial features and expressions exactly",
        "Maintain identical lighting direction and color temperature on subject",
        "preserving the person's facial identity and expression exactly",
        "Keep the subject in the uploaded image exactly unchanged",
        "Do NOT change facial identity / Do NOT alter the subject in any way",
        "maintain exact facial structure from reference with 100% accuracy, preserve micro-details, no beautification",
    ],
    "studio_controls": {
        "sizes": "512 / 1K / 2K / 4K on the long edge — pick by use case (512 for thumbnails/avatars, 1K for social, 2K for hero/web, 4K for print/brand)",
        "aspect_ratios": "1:1 (avatar/square), 2:3 & 3:2 (portrait), 4:5 (IG feed), 9:16 (story/reel), 16:9 (landscape/YouTube), 3:4 & 2:1 (poster/banner)",
        "ratio_specification": "75%+ of corpus has no explicit --ar flag — embed ratio in prose ('vertical 9:16', 'square 1:1 composition') or lock via a dimension reference",
        "camera_vocabulary": "Body (Sony A7IV/R5, Hasselblad X2D, Phase One) + lens + focal length + aperture + ISO/shutter hints — this metadata drives NB output more than any other signal",
        "lighting_vocabulary": "Three-point studio, Rembrandt, clamshell, window light, golden hour, ring light, beauty dish — explicit lighting setup renders faithfully",
    },
    "green_screen_workflow": {
        "trick": "Chroma-key isolation: provide/generate the subject on a flat green (or solid chroma) background, then prompt NB to replace ONLY the green with [NEW BACKGROUND] while preserving subject edge detail, lighting, and shadows",
        "steps": [
            "1. Subject on green/solid chroma background (shot or generated)",
            "2. Prompt: 'Replace only the green background with [NEW BACKGROUND]. Keep the subject exactly unchanged. Maintain identical lighting direction and color temperature. Seamless edge blending with zero haloing. Natural shadow casting on new background.'",
            "3. Pair with a face-lock clause for portrait subjects",
            "4. Close with: 'Do NOT alter the subject in any way.'",
        ],
        "blank_image_dimension_trick": "Attach a BLANK reference image of the target dimensions/aspect ratio as the last reference to lock the output shape — NB treats the last reference's canvas geometry as an output constraint, forcing the generation into that ratio without relying on a --ar flag",
        "when": "Subject isolation + background swap, product restage onto a new set, composite work where edge fidelity matters",
    },
    "do_donts": {
        "do": [
            "Lead with camera body + lens + aperture for photographic work — it is the strongest signal NB responds to",
            "Specify the lighting setup explicitly (Rembrandt, three-point, window, golden hour)",
            "State an explicit aspect ratio or lock it via a dimension reference",
            "Use a face-lock clause for any portrait/avatar/edit touching a real face",
            "Close edit prompts with a 'Do NOT ...' clause naming what must not change",
            "Number reference images when more than one is attached (uploaded image / first reference / last reference)",
            "Keep text blocks short and diegetic — NB garbles dense UI copy",
            "Use JSON compartmentalization only when a scene has multiple distinct zones that need discipline",
        ],
        "dont": [
            "Don't route layout/UI/dashboard/infographic work to NB — use GPT Image 2 (Layout 71% vs 47%)",
            "Don't exceed 14 reference images — extras are ignored or merged",
            "Don't supply reference images outside png/jpeg/webp/heic/heif",
            "Don't omit the face-lock clause on identity-preserving edits — likeness will drift",
            "Don't bury constraints in prose — put them in a labeled closing clause",
            "Don't over-specify layout scaffolding at the expense of camera vocabulary — NB is camera-first, not layout-first",
            "Don't modernize vintage or alter historical character without an explicit instruction to preserve era",
        ],
    },
}


def get_nano_banana_intelligence(model: str = "nb2", category: str = "", goal: str = "") -> dict:
    """Get Nano Banana model-specific guidance.

    model: 'nb2' (flash / Gemini 3.1 Flash Image) or 'nb_pro' (pro / Gemini 3 Pro Image).
    Returns the selected model spec plus the always-on NB context: strengths,
    weaknesses, frameworks, reference-image rules, face-lock phrasings, studio
    controls, green-screen workflow, and do/don'ts. The category/goal are
    accepted for parity with get_gpt_image_2_intelligence but NB guidance is
    model-first (not category-first) since NB's routing is photography/edit heavy.
    """
    model_key = model if model in NANO_BANANA["models"] else "nb2"
    return {
        "model": NANO_BANANA["models"][model_key],
        "model_key": model_key,
        "strengths": NANO_BANANA["strengths"],
        "weaknesses": NANO_BANANA["weaknesses"],
        "frameworks": NANO_BANANA["frameworks"],
        "reference_image_rules": NANO_BANANA["reference_image_rules"],
        "face_lock_phrasings": NANO_BANANA["face_lock_phrasings"],
        "studio_controls": NANO_BANANA["studio_controls"],
        "green_screen_workflow": NANO_BANANA["green_screen_workflow"],
        "do_donts": NANO_BANANA["do_donts"],
    }
