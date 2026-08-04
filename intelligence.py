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
