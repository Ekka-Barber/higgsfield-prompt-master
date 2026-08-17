---
name: rasm-edit
description: >
  Editing existing images — reference workflows, face/identity preservation,
  style transfer, object removal, background swaps, and translating text inside
  an image to Arabic. Use for /rasm-edit, "عدل الصورة", "غير الخلفية", "احتفظ
  بالوجه", "edit this image", "change background", "face lock", "style transfer",
  "keep the same person", "translate text in image".
---

# /rasm-edit — edits, references & identity

Editing has its own grammar. The two rules that matter most are *name every
reference by ordinal and role*, and *state what must not change*.

Read `../_shared/model-routing.md`.

## Never write `REFERENCE_0`

That syntax appears in no vendor documentation. Address references in natural
language:

> "In the first image (the product), keep the label unchanged. Use the second
> image for lighting and colour mood only."

**Always state the reference's job.** A reference with no stated role competes
with your text and usually wins on Nano Banana Pro.

## The preserve list — the core of every edit

Both vendors document the same pattern: **"change only X" + "keep everything
else the same"**, and **repeat the preserve list on every iteration** or the
image drifts.

> "Change only the background to a warm sand-toned studio sweep. Keep the
> product, its label, the camera angle, the lighting direction, and the shadow
> exactly as they are."

For surgical edits, also pin: saturation, contrast, layout, labels, and
surrounding objects.

## Identity / face preservation

Never write "100% accuracy" — it is not a control, it is a wish. Write what to
preserve:

> "Preserve her exact facial features, bone structure, skin tone and texture,
> hairstyle, expression and proportions. Do not beautify, slim, smooth, or
> alter the face in any way. Change only the clothing."

**Nano Banana Pro** is the identity model: up to **5 characters** with
consistency, and it holds a reference's character better. Do not exceed 5.

## Model split for edits

| Edit | Model | Why |
|---|---|---|
| Style / colour / mood transfer | **Nano Banana Pro** | takes grade from a reference willingly |
| Keep layout & pose, change content | **GPT Image 2** | holds structure tightly |
| Face / character consistency | **Nano Banana Pro** | typed character slots |
| Translate text inside the image | **Nano Banana Pro** | documented localisation strength |
| Object removal, surgical | **GPT Image 2** | more literal about "change only" |
| Multi-image compositing | **Nano Banana Pro** | 6 objects / 5 chars / 3 styles |

When a reference and the text disagree: **GPT Image 2 trusts the text, Nano
Banana Pro trusts the image.** If your written instruction is being ignored on
Nano Banana Pro, that is why — scope the reference, don't rewrite the text.

## Localisation — English image → Arabic

A genuine strength of Nano Banana Pro, and a real use case for Saudi marketing.

> "Replace the English headline with the Arabic text '...' set in a modern
> Kufi style. Keep the photograph, layout, colours and logo completely
> unchanged. Right-align the new Arabic text and mirror the text block to the
> right side. Fully connected cursive letterforms, no tashkeel, no Latin text."

**Note the layout consequence:** swapping LTR copy for Arabic usually means the
text block, alignment and any arrows must mirror too. Ask whether they want a
true RTL relayout or a drop-in text swap.

## Object removal — positive phrasing

Negation summons. Instead of "remove the car, no car":

> "The street is empty and clear, bare asphalt where the car was, with the
> building line and shadows continuing naturally."

## Grill

1. What exactly changes, and what must stay identical?
2. How many reference images, and what is each one *for*?
3. Is a face/identity involved?
4. Is this a text swap, and to Arabic?

Follow-up: one-off edit, or a repeatable recipe for a batch? A batch needs a
locked preserve list you can paste every time.
