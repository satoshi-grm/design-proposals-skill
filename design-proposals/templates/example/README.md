# Example: Nocturne

Copy this folder to `docs/proposals/<date>-<topic>/` in the project and run `bash <skill>/scripts/render.sh <folder>`.

Nocturne is a made-up independent cinema. The example has three directions (Marquee, Ticket Stub, Projector) and three screens (programming dashboard 1440×900, mobile ticket + seat picker 390×844, lobby TV 1920×1080), enough to see the full pipeline: tokens → 2x capture → design.md → tokens.css → PDF → gallery.

- Add directions in `source/proposal.json` (each with `tokens.light` and `tokens.dark`) and the composition of each one in `source/directions/<id>.css`.
- Add screens in `source/screens/` and list them under `screens` in `source/proposal.json`. Shared screen styles live in `source/screens.css`.

Placeholders in the screen templates:
- `{{ATTRS}}` and `{{HEAD}}` are filled in by the build (theme, mode, direction and screen attributes; fonts and stylesheets).
- `{{NAME}}` is the direction's name.
- `{i:name}` is an inline Lucide icon (`{i:name|class}` adds a class).
- `{{A}}` is the relative path to `source/assets/`.

Photos: Unsplash (Unsplash License), IDs listed in source/proposal.json → photos.
