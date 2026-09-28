# Handoff: from the chosen direction to the product repo

What the booklet generates per direction and where it goes:

| File | Destination | How |
|---|---|---|
| `<dir>/tokens.css` | `src/app/globals.css` (or the global stylesheet) in the repo | Replaces the shadcn/ui `:root` and `.dark` blocks. Includes `@theme inline` for Tailwind v4 (`bg-primary`, `font-display`, `rounded-lg`...). Variables use shadcn names: there is no mapping to do, just paste. Without shadcn, they work the same as CSS variables. |
| `<dir>/design.md` | `docs/design.md` in the repo | Frontmatter with tokens (colors, typography, radii, components) and a body with identity, system, components with states, layout and rules. Any agent building the interface reads it. |
| "For the SPEC" block in `design.md` | The project's spec or technical README, design section | Paste as is: idea, signature, tokens, typography, shape, density, motion and measured contrast. |
| Component table in `design.md` | Spec or brief for whoever implements | List of components with their required states; the library in `templates/components/` is the visual reference. |
| `screens/<dir>-*.png` | Brief for whoever implements | Visual reference for the key screens: rebuild them with the project's components and the signature CSS. |

Steps:
1. The user chooses (or mixes). For a mix, edit `source/proposal.json` with the mix as a new direction and run `render.sh` again: that way `tokens.css` comes from a single source.
2. A short decision note ("Visual direction") with the link to the PDF, wherever the project keeps its decisions.
3. Paste the "For the SPEC" block into the spec, with the measured hard limits (AA contrast, text 12 px or more, no clipping, no horizontal scroll) as verifiable criteria.
4. In the implementer's brief: "tokens from `docs/proposals/<folder>/<dir>/tokens.css`; signature per `design.md` §3.2; reference screens in `screens/`".
