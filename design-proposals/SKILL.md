---
name: design-proposals
description: "Use when the user must pick a visual direction before building or redesigning a product. Builds a decision booklet with 3 to 8 visual directions applied to the product's real screens, captured at real size, with a 16:9 PDF, a filterable gallery, a design.md and a tokens.css (shadcn/ui + Tailwind v4) per direction, measured checks (WCAG AA contrast, text of 12 px or more, no clipping) and one firm recommendation."
version: 0.4.0
author: satoshi-grm
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [design, proposals, decision, pdf, ui, saas, tokens]
---

# Design proposals: see, compare and choose

Builds a **decision booklet** with 3 to 8 visual directions applied to the product's real screens, captured at real size and at double resolution. The output is a 16:9 PDF (one screen per page), an `index.html` gallery with a filter per direction, and, for each direction, a `design.md` and a `tokens.css` ready to move into the repo. It closes with a comparison, a mixing guide and **one firm recommendation**.

## When to use
- The user must choose between visual directions before building: a new product, a redesign, or a project spec that reaches the visual section with no look chosen.
- The user asks for "proposals", "options", "visual directions" or "how could this look".
- Something existing looks "default" (untouched shadcn or Tailwind).
- Not for a patch, a single component, or when the user has already chosen.
- Count: 3 to 5 by default; 6 to 8 when the user asks for "more proposals".

## What the skill includes
| File | Purpose |
|---|---|
| `templates/components/` | "SaaS pro" library in HTML and CSS with shadcn-named tokens: app shell, ⌘K, table with bulk actions, empty states, skeletons, toasts, modal and sheet, forms, tabs, onboarding, settings, plans, SVG charts, avatars, badges, breadcrumbs, pagination and dark mode. `catalog.html` shows them all per theme. See its `README.md`. |
| `templates/example/` | Starter project to copy: Nocturne, an independent cinema, with three directions (Marquee, Ticket Stub, Projector) and three screens (programming dashboard 1440×900, mobile ticket + seat picker 390×844, lobby TV 1920×1080). |
| `scripts/render.sh <folder>` | One command: fonts, 2x screens, catalog per theme, measured limits, contrast, `design.md`, `tokens.css`, PDF, gallery and review sheets. Exits with 1 if something fails. |
| `scripts/build.py` | What `render.sh` runs; `--only screens --dir x` to iterate on one direction. |
| `scripts/booklet.py` | Builds the booklet HTML and PDF pages. |
| `scripts/fonts.py` | Downloads Google Fonts locally (captures do not depend on the network). |
| `scripts/contrast.py` | WCAG 2.x contrast for loose pairs or for a JSON file. |
| `references/review.md` | Criteria for the visual review, page by page. |
| `references/handoff.md` | How the chosen direction moves into the product repo. |
| `references/legacy.md` | Old Spanish keys and folder names, still accepted. |

## Requirements
- Python 3.10 or later, standard library only.
- System Chrome or Chromium, or Playwright's `chrome-headless-shell` (`python3 -m playwright install chromium-headless-shell`). `CHROME` and `SHOT_CHROME` point to a binary of your choice.
- Optional: Pillow (`pip install pillow` in a venv). With Pillow the PDF carries the captures as JPEG and weighs much less, and the review sheets get built; without Pillow it uses PNG.
- Optional: `poppler-utils` (`pdfinfo`, `pdftoppm`) to count pages and build the review sheets.
- Optional: `lucide-static` for `{i:name}` icons: `npm i lucide-static` in the booklet folder (or the one above it), or `LUCIDE_DIR=.../lucide-static/icons`. Without it, the build warns and continues without icons.
- Network only the first time, to download fonts.

## Procedure
1. **Contract (5 min or less).** What stays fixed (routes, data, hard limits, client brand) and what varies. If there is a site or screenshots, analyze them first: real colors, typefaces and components.
2. **Product screens, not templates.** Pick 3 or 4 key screens with believable domain data (the same in every direction). Write them as HTML in `source/screens/` at their real size: 1440×900 dashboard, 390×844 mobile, 1920×1080 TV. Use the classes from `base.css` and your own `screens.css`. No rows of big numbers and no generic sidebar: the screen is the one the product needs.
3. **Directions.** In `source/proposal.json`: `project` (product name), a name from the client's world, tagline, idea in 2 lines, signature moment, 6 axes (temperature, density, typography, shape, imagery, motion; each direction differs from the others in at least 3), light and dark tokens, fonts, and honest pros and cons. Composition and signature go in `source/directions/<id>.css` (everything under `[data-dir="<id>"]`). Reference level: Linear, Vercel, Stripe, Raycast.
4. **Nothing from average AI design.** Banned: rows of big numbers, cards with a colored stripe, purple gradients, glass (background blur), gradient text, cards inside cards, drawn device frames, emojis as icons. One accent color only; states carry a dot or icon plus text.
5. **Images.** Free photos (Unsplash by ID on `images.unsplash.com`, Unsplash License) downloaded to `source/assets/photos/`, or your own SVG. No paid credits. Icons: inline Lucide with `{i:name}`; the build copies them to `source/assets/icons/` (see Requirements; never a global install).
6. **Render and measured checks.** `bash scripts/render.sh <folder>`. It leaves `limits.txt` (text 12 px or more, 28 px or more on TV, including `::before/::after`; no horizontal scroll; no clipped text) and `contrast.txt` (AA per direction and mode). To iterate: `python3 scripts/build.py <folder> --only screens,limits --dir <id>`. Steps: `themes,screens,catalog,limits,contrast,docs,pdf,gallery,review`.
7. **Visual review** of each PNG and of the sheets `source/.build/review-*.png` with the criteria in `references/review.md`. Fix and render again. A mediocre direction gets dropped and replaced.
8. **Closing in `proposal.json`:** comparison, 4 to 6 mixes ("take X from A and Y from B") and a recommendation with an alternative and steps.
9. **Delivery.** Paths to the PDF and `index.html`, 3 lines per direction and **one single question**: "Which one do you choose, or do we mix? (recommended: ...)". Once chosen, follow `references/handoff.md`.

## Language
The `lang` field in `proposal.json` controls all generated text (booklet, gallery, `design.md`, reports). `"en"` is the default; `"es"` is supported.

## Output (project folder, `docs/proposals/<date>-<topic>/`)
`index.html`, `proposals.pdf`, `screens/<dir>-<screen>.png`, `<dir>/design.md`, `<dir>/tokens.css`, `contrast.txt`, `limits.txt`, `README.md` and `source/` (everything needed to regenerate; `source/.build/` and `proposals.html` are intermediate and go in `.gitignore`).

Older booklets with Spanish keys and folders (`fuente/`, `propuesta.json`, `pantallas/`...) still render with their original names. See `references/legacy.md`.

## With many directions
With 5 or more directions, hand each direction to a subagent that only touches `source/directions/<id>.css`: you build the screens, `screens.css` and the first direction; each subagent renders its own with `--dir <id>` and reviews it visually. Show 2 screens of the first direction as soon as they are ready, before finishing the rest.

## Pitfalls
- Chrome with `--headless=new` takes ~87 px off the viewport height: the build uses `chrome-headless-shell` (Playwright) if present; otherwise it compensates the window size.
- Lucide no longer ships brand icons (Instagram, WhatsApp): use `at-sign`, `message-circle`.
- Drawn device frames: banned. Screens go full bleed or on a plain background.
- On surfaces that show the client's brand (TV, public pages) that brand rules: the direction changes composition, not the brand.
- `design.md` and `tokens.css` are generated from the JSON: do not edit them by hand.
- In the PDF the captures go as 2x JPEG (quality 85) if Pillow is present: lossless PNGs push it to 20 to 60 MB.
- Text hidden with `text-indent` or `overflow` counts as clipping: to show part of a value, use a `data-*` attribute and `::after`.

## Works well with
Optional, if you have them: a skill that analyzes an existing site (for step 1) and a project spec skill (to receive the "For the SPEC" block from `design.md`). The skill works on its own without either.
