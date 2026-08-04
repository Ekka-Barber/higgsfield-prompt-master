# Branded Social Media Invitation — Prompt Template

Reusable template for generating branded invitation cards for businesses (Instagram Story, posts, etc.) using GPT Image 2 with multi-reference images.

## When to use
- Business owner asks for an Instagram Story/post invitation
- Eid, Ramadan, National Day, anniversary, or any celebration
- Needs to match real brand assets (logo, products, packaging)

## Pre-generation checklist
1. [ ] Business researched (Google Maps, website, reviews)
2. [ ] Brand colors extracted from logo/photos (hex if possible)
3. [ ] All reference images uploaded to Higgsfield (logo, products, etc.)
4. [ ] Arabic text confirmed exactly as user wrote it
5. [ ] Religious imagery constraints confirmed (many Saudi businesses want "no Islamic gestures")
6. [ ] Aspect ratio confirmed (Instagram Story = 9:16, Post = 4:5 or 1:1)

## Prompt structure

```
Instagram Story invitation card (9:16 vertical, 1080x1920px) for a [BUSINESS_TYPE] called [BUSINESS_NAME]. [OCCASION] celebration invitation.

IMPORTANT: All reference images must be used. [IMAGE_1_DESCRIPTION], [IMAGE_2_DESCRIPTION], [IMAGE_3_DESCRIPTION]. Replicate these items accurately.

DESIGN LAYOUT (top to bottom):

TOP SECTION (12%): [LOGO_PLACEMENT_DESCRIPTION] — describe the logo shape, colors, text exactly as it appears.

UPPER CENTER (20%): [GREETING_TEXT] in [COLOR] using [FONT_STYLE] Arabic typography. [SUB_TEXT] below in [ACCENT_COLOR]. [SPACING/WHITESPACE NOTES]. [IMAGERY_CONSTRAINTS — e.g., NO Islamic symbols].

MIDDLE (40%): Hospitality/product spread on [SURFACE] with [LIGHTING]. Items:
- [ITEM_1]: [DETAILED_DESCRIPTION including reference to uploaded photo]
- [ITEM_2]: [DETAILED_DESCRIPTION]
- [ITEM_3]: [DETAILED_DESCRIPTION]
- [ITEM_4]: [DETAILED_DESCRIPTION]
[TABLE_GARNISH_DESCRIPTION]

BOTTOM (28%): [BRAND_COLOR] background panel. [SUBHEADING_TEXT]. Menu listing:
• [MENU_ITEM_1]
• [MENU_ITEM_2]
• [MENU_ITEM_3]
• [MENU_ITEM_4]

[BOTTOM_CORNER_NOTE if applicable]: Small text at bottom left: '[NOTE_TEXT]'

COLOR PALETTE: [PRIMARY_COLOR], [SECONDARY_COLOR], [ACCENT_COLORS]. [NATURAL_FOOD_COLORS if applicable].

STYLE: Modern minimalist, editorial, luxury hospitality. [LIGHTING_NOTES]. [IMAGERY_CONSTRAINTS repeated]. Contemporary and sophisticated.

TYPOGRAPHY: Arabic text must be pixel-perfect, right-to-left, properly connected letterforms. Modern clean Arabic fonts.
```

## Lighting correction clause
When a reference photo has bad lighting (flash, night, fluorescent), add to the relevant item description:

```
IMPORTANT: Relight this [ITEM] from the reference photo to match soft diffused studio lighting — remove the harsh flash, add soft diffused ambient light with subtle warm tones. The [ITEM] should look like it was shot in a professional studio, not with a phone flash at night.
```

## Arabic text notes
- GPT Image 2 renders Arabic reasonably well but may have issues with diacritics (tashkeel)
- Transliterated brand names (e.g., بلوكبز for "bluecups") should be noted as transliterations
- Always quote exact Arabic strings in the prompt — don't paraphrase
- Common corrections to watch for: انت vs انتم, صلاة vs صلاعة (typos user will catch)

## Model settings
- **Model:** gpt_image_2 (required for Arabic text + branded graphics)
- **Aspect ratio:** 9:16 (Story), 4:5 (Post), 1:1 (Square post)
- **Count:** 2 (gives user a choice)
- **Quality:** default (low at 1k resolution)
