# Visual review

Look at **each PNG** in `screens/` at full size and at **each page** of the PDF in the sheets `source/.build/review-*.png`. Whatever fails gets fixed and rendered again; the verification notes what was looked at and what was fixed.

## Per screen
| Criterion | Passes if |
|---|---|
| Hierarchy | There is one focal point and it is found within 2 seconds (the preview in an editor, the status line on a monitor, the main button on mobile, the product on TV). |
| Air | Groups are separated by space before boxes; nothing is stuck to the edges; there is rhythm between dense and open areas. |
| One accent | One action color; states carry a dot or icon plus text. |
| Nothing from average AI | None of the habits of average AI design (rows of big numbers, cards with a colored stripe, purple gradients, glass, gradient text, cards inside cards, device frames, emojis). |
| Signature | The direction's signature moment is visible without searching for it, and only where it was defined. |
| Hard limits | Text 12 px or more (TV 28 px or more at 1080p, 5 % safe margin), single-row controls share the same height, nothing cut, overlapping or wrongly broken onto two lines. |
| Data | The same data in every direction; long names truncated with judgment. |

## Per PDF page
| Criterion | Passes if |
|---|---|
| Scale | The screen fills the page (1440 px out of 1600) and the interface text is readable at 100 % zoom. |
| Booklet text | No booklet text below 13 px; captions of 3 lines or fewer. |
| Cropping | Nothing overflows the 16:9 page; images are not distorted. |
| Rhythm | Opening, screens, mobile + components and TV alternate density; the recommendation reads on its own. |

## Before and after
If there is a previous booklet, build `before-after.png` with the equivalent page from the old and the new one, side by side and at the same height.
