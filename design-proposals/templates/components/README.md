# "SaaS pro" library

Plain CSS, no framework. Components read **only variables**, so any theme can re-dress them.
`catalog.html` shows everything together on a 1440 px sheet (about 2590 px tall).

## Files

| File | Contents |
|---|---|
| `base.css` | Token contract (shadcn/ui names), reset, typography and small controls: `.btn` `.kbd` `.badge` `.avatar` `.crumbs` `.tabs` `.seg` `.field` `.input` `.select` `.switch` `.check` |
| `shell.css` | App frame: sidebar, rail, organization switcher, topbar |
| `table.css` | Data table with toolbar, filters, selection, bulk actions and pagination |
| `overlays.css` | ⌘K bar, modal, destructive confirmation, side sheet, toasts, scrim |
| `forms.css` | Form layout, prefix/suffix, counter, validation, option cards, file upload, `.bar` |
| `states.css` | Empty state with illustration, skeletons, spinner, error with retry |
| `pages.css` | Getting started, settings, plans and billing |
| `charts.css` | Bars, sparkline, 24 h availability strip, legend, tooltip |
| `themes-example.css` | Sample theme (id `example`), light and dark (warm neutral + green `#1f6b4f`) |
| `catalog.html` | Sample sheet with data from a made-up product (Nocturne, an independent cinema) |

Load order: `base.css` → components → themes. The catalog has the line `<!-- THEMES -->` right after the `<link>` tags: that is where the build injects the other themes' stylesheets.

## How a theme plugs in

```html
<html data-theme="marquee" data-mode="dark">
```

A theme is a `[data-theme="id"] { ... }` block plus `[data-theme="id"][data-mode="dark"] { ... }` that **overrides variables and nothing else**: `--background --foreground --card --popover --muted --muted-foreground --primary --primary-foreground --accent --accent-ink --border --input --ring --destructive --success --warning --info --sidebar* --chart-1..5 --font-sans/-display/-mono --radius --shadow-float`. Optional: `--scrim` (if missing, it comes from `--foreground` in light mode and from `--background` in dark mode).
Rules: text at least 4.5:1 on `--card` and `--background`; `--input` at least 3:1 on `--card`; in dark mode surfaces get lighter as they rise (`--background` < `--card` < `--popover`).

## Class API (one line per component)

**shell.css**
- `.shell > .sidebar + .main` · `.shell[data-collapsed]` turns the 240 px sidebar into a 60 px rail (icons only, `.tip` for the name).
- `.org-switch` (`.avatar.avatar--sq.org-mark` + `.org-switch__name/__plan` + chevron) · `[aria-expanded="true"]` open.
- `.popover` > `.popover__label` + `.menu-item` (`.menu-item__text/__sub`, `[data-highlighted]`) + `.menu-sep`.
- `.nav` > `.nav__section` + `a.nav__item` (`.nav__label`, `.nav__count`, `.nav__count--alert`) · `[aria-current="page"]` active · `[data-badge]` dot on the rail.
- `.sidebar__foot > .user-row` (`.avatar[data-presence]` + `.user-row__name/__mail`).
- `.topbar` > `.crumbs` + `.search-trigger` ("Search... ⌘K") + `.topbar__actions` (`.icon-dot` = something new).
- `.page` > `.page-head` (`.page-head__title/__desc` + buttons).

**table.css**
- `.dt` > `.dt-toolbar` | `.dt-bulk` | `table.table` | `.dt-foot`.
- `.search` (input with icon) · `.chip` (`.chip__key` + `.chip__val`, `[data-active]`, `.chip--add` dashed, `.chip__clear`).
- `.dt-bulk` (`.dt-bulk__count`, `.sep`, `.btn--ghost`, `.is-danger`).
- `th[aria-sort] > .sort` · `.num` right-aligned (cells in tabular mono) · `.col-check` · `.col-more > .row-more`.
- `tr[aria-selected="true"]` · `tr:hover` / `.is-hover` · `.cell-main` (`__title` + `__sub`) · `.cell-ico`.
- `.dt-foot` > `.dt-foot__range` + `.pager > .pager__btn[aria-current="page"]`.

**overlays.css**
- `.scrim` flat translucent backdrop (no blur) · `.float` generic floating surface.
- `.cmdk` > `.cmdk__input` + `.cmdk__list > .cmdk__group > .cmdk__label + .cmdk__item[aria-selected]` (`mark`, `.cmdk__meta`) + `.cmdk__foot`.
- `.dialog` > `.dialog__head` (`__titles`, `__title`, `__desc`, `__close`) + `.dialog__body` + `.dialog__foot` · `.dialog--danger` with `.dialog__icon`.
- `.sheet` > `.sheet__head` + `.sheet__body` + `.sheet__foot` · `.kv` key/value list (`dt`/`dd`).
- `.toast-stack > .toast.toast--ok|--err|--info` (`.toast__title/__desc`, `.toast__actions`, `.toast__close`).

**forms.css**
- `.form` · `.form-row` (2 columns) · `.form-actions`.
- `.field` + `.field__top` (`.label` + `.counter[data-near|data-over]`) · `.req` (required) · `.opt` (optional) · `.field__msg` with icon.
- `.input-group` > `.addon` (prefix/suffix, `.addon--ghost`) + `input` · `.select > .select__val` · `.textarea`.
- `.radio-cards > .radio-card[aria-checked]` (`__title`, `__desc`, `__mark`, `__shape`).
- `.dropzone[data-dragover]` · `.file-row` (`__name`, `__meta`, `.bar`) · `.bar > span` with `--p: 0..1` (`[data-level="warn|full"]`).

**states.css**
- `.empty` > `svg.empty__art` (strokes `.ill-line .ill-faint .ill-dash .ill-soft .ill-card .ill-accent .ill-fill .ill-text`) + `.empty__title/__desc/__actions`.
- `.skel` + `--line|--title|--avatar|--block|--pill` (`--w`, `--h`) · `.skel-lines` · `.skel-table > .skel-table__row` · `.skel-card`.
- `svg.spinner` (`.track` + `.head`) · `.loading-inline` · `.btn[data-loading]`.
- `.error-state` > `__icon` + `__title` + `__desc` + `__actions` (`__code`).

**pages.css**
- `.onboarding` > `__head` (`__title`, `__count` "2 of 4") + `.bar` + `ol.steps > li.step[data-state="done|current|pending"]` (`__mark`, `__title`, `__desc`, action).
- `.settings` > `.subnav > .subnav__item[aria-current]` + `.settings__body > .set-section` (`__label/__title/__desc` + `__controls`, `.set-line`) · `.set-section--full` · `.danger-zone > .danger-zone__row` · `.btn--danger-outline`.
- `.plans > .plan[aria-current="true"]` (`__head`, `__name`, `__price > __amount + __per`, `__desc`, `__feats`, `__cta`).
- `.meter[data-level="full"]` (`__top`, `__label`, `__val`, `.bar`, `__note`) · `table.table.invoices`.

**charts.css**
- `svg.chart` with `.chart__grid` `.chart__base` `.chart__axis(--end|--mid)` `.chart__bar(--2..--5)` `.chart__line(--2)` `.chart__area` `.chart__dot` `.chart__hover` `.chart__cursor`.
- `.chart-tip` (`__title`, `__row > b`) · `.legend > .legend__item > .legend__sw(--2..--5|--ok|--warn|--err|--none)`.
- `.spark` (`__label`, `__num > __value + __delta(--down)`, `svg`) · `.uptime > .uptime__row` (`__name`, `__strip > i[data-s="warn|down|none"]`, `__pct`) + `.uptime__axis`.

## States per component

| Component | States |
|---|---|
| Nav / subnav | normal, hover, active (`aria-current`), with count, with alert, collapsed rail + tooltip |
| Organization switcher | closed, open (popover), current organization with check, highlighted item |
| Table | normal row, hover, selected, mixed header; ascending/descending sort; filters with a value and to add; bulk bar; pagination with previous/next disabled |
| ⌘K bar | empty, with query and highlighted matches, highlighted item, groups, shortcuts |
| Modal | standard, destructive (`--danger`, `role="alertdialog"`) |
| Side sheet | header with status, scrolling body, footer with destructive action |
| Toast | success, error, with action ("Undo"), stacked; animated entry |
| Field | normal, hover, focus (`:focus` or `.is-focus`), disabled, error (`data-invalid`), valid (`data-valid`), counter near/over the limit |
| Option card | selected, unselected, disabled |
| File upload | idle, dragging (`data-dragover`), uploading with progress |
| Empty / error / loading | empty with illustration and CTA; error with retry and code; skeleton with shimmer; spinner; loading button |
| Getting started | done, current, pending; progress |
| Plan / meter | current plan, available plan; normal meter and at the limit |
| Charts | hovered bar with tooltip; strip: up, intermittent, down, off |

## Motion and accessibility

Transitions of 120-280 ms with `--ease-out`, only `transform` and `opacity` (the width of `.bar` animates with `scaleX`). With `prefers-reduced-motion`, entries and the skeleton shimmer turn off; the spinner rotates slowly. Text 12 px or more, touch areas 24 px or more (`.check` and `.switch` enlarge theirs), visible focus with `--ring`. Icons: inline Lucide with `class="i"` and `stroke="currentColor"`.
