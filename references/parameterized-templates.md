# Parameterized Template Prompts (`{argument}` Syntax)

> **Discovered:** August 2026 corpus harvest
> **Prevalence:** 91% of new prompts (1,157 out of 1,276) use this syntax
> **Status:** Major paradigm shift in how GPT Image 2 prompts are structured

## Overview

A new dominant pattern has emerged in the GPT Image 2 prompt ecosystem: **parameterized templates** using `{argument}` syntax. Instead of writing a single static prompt, creators now build reusable templates with variable placeholders that can be customized per generation.

This is the single biggest structural change since the original "Goal + Canvas + Sections" pattern identified in the first corpus analysis.

## Syntax

```
{argument name="DESCRIPTIVE_NAME" default="DEFAULT_VALUE"}
```

### Components
- **`name`**: A human-readable identifier for the variable (e.g., `"artistic style"`, `"shading"`, `"color palette"`)
- **`default`**: The fallback value used if no custom value is provided

### Example

```
Ultra-detailed monochrome graphite portrait illustration, contemporary fine-art 
sketch aesthetic, hyper-realistic facial rendering blended with {argument name="artistic 
style" default="expressive loose construction lines"}, premium pencil-on-smooth-paper 
texture, {argument name="shading" default="soft charcoal shading, refined graphite 
gradients, delicate cross-hatching"}, painterly tonal transitions...
```

When the template is used:
- With no customization → generates with the default values
- With `artistic style="bold ink wash strokes"` → swaps in the custom value

## Why this matters

1. **Reusability** — One template can serve infinite variations. A single "Product Photography" template can generate hundreds of different product shots by varying 3-4 arguments.
2. **Consistency** — The base structure (lighting, composition, quality) stays fixed while only the variable parts change. This produces more consistent batch results.
3. **Community sharing** — Templates are designed to be shared and remixed. The `{argument}` syntax is human-readable, making templates self-documenting.

## Identified argument categories

From analyzing 1,157 parameterized prompts, these are the most common argument types:

| Argument Type | Example `name` | Example `default` | Frequency |
|---|---|---|---|
| **Artistic Style** | `"artistic style"` | `"expressive loose construction lines"` | Very High |
| **Color/Mood** | `"color palette"` / `"mood"` | `"warm golden hour tones"` | High |
| **Lighting** | `"lighting setup"` | `"soft diffused studio lighting"` | High |
| **Background** | `"background setting"` | `"minimalist concrete texture"` | Medium |
| **Camera/Lens** | `"camera specification"` | `"85mm f/1.4, shallow depth of field"` | Medium |
| **Subject Detail** | `"subject description"` | `"young woman with curly hair"` | Medium |
| **Typography** | `"font style"` / `"text overlay"` | `"bold sans-serif, white on dark"` | Medium |
| **Composition** | `"layout structure"` | `"rule of thirds, centered subject"` | Low |

## How to use this in generation

When generating prompts for users, the system should:

1. **Detect when a parameterized template is the best fit** — Use this pattern when the user wants a reusable, customizable prompt rather than a one-off generation.
2. **Insert 2-4 arguments** at natural variation points — style, color/mood, lighting are the most useful.
3. **Set intelligent defaults** based on the category's reference guide and the corpus data.
4. **Generate both versions** — Produce the expanded prompt (defaults filled in) AND the template (for reuse).

### Generation example

```python
# User request: "product photo for a skincare bottle"

# OLD approach (static):
prompt = "A luxury skincare bottle on a marble surface with soft lighting, 
          4k, photorealistic, studio quality..."

# NEW approach (parameterized template):
prompt = """Premium product photography of a skincare bottle, {argument name="product 
material" default="frosted glass with brushed aluminum cap"}, placed on {argument 
name="surface" default="polished white marble with subtle veining"}, {argument 
name="lighting" default="soft diffused studio lighting from the left creating gentle 
shadows"}, {argument name="background" default="seamless light gray gradient background"}, 
shot with {argument name="camera" default="100mm macro lens, f/4, shallow depth of field"}, 
ultra-detailed, photorealistic, commercial advertising quality, 4K resolution."""
```

## Impact on the skill

The `higgsfield_prompt.py` generator should be updated to:
1. Detect when a parameterized template is appropriate (user wants reusability or batch consistency)
2. Generate templates with 2-4 `{argument}` placeholders at intelligent variation points
3. Always provide filled-in defaults so the template works standalone
4. Allow the user to override specific arguments for variation
