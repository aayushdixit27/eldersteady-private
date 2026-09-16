# DESIGN.md — watch

Written 15 Sep 2026 by the setup lane during the anti-design-slop pass on `interface/index.html`. Mode: restyle (the screen worked; structure untouched).

## Readability floor — computed (WCAG, `scripts/contrast.mjs`)

Floor: **7:1 for every text pair** (labels, captions, badges included). Only text ≥ 24px bold may drop to 4.5:1.

| Pair | Ratio | Status |
|---|---|---|
| ink `#17221d` on paper `#fffdf8` | 16.10 | ok |
| muted `#414c46` on paper | 8.80 | ok (was `#647069` = 5.08 **rejected**) |
| muted `#414c46` on canvas `#f2eee5` | 7.73 | ok (was 4.46 **rejected**) |
| urgent-text `#8b2e20` on paper | 8.23 | ok (was `#c84931` = 4.64 **rejected** as text) |
| white on safe-deep `#0d5136` (button) | 9.34 | ok (was `#166747` = 6.85 **rejected**) |
| white on urgent-text `#8b2e20` (button) | 8.37 | ok (was `#c84931` = 4.72 **rejected**) |
| safe-deep `#0d5136` on paper (status) | 9.19 | ok (was 6.74 **rejected**) |
| white on night `#13251e` (ledger number) | 16.02 | ok |
| `#c8d8d0` / `#b9d2c6` / `#9fb9ac` on night | 10.8 / 10.0 / 7.6 | ok |
| `#0d5136` on safe-soft `#e8f5ed` | 8.33 | ok |

`#c84931` (terracotta) and `#166747` (green) remain as **fills for badges/dots only**, never as text or button background.

## Tokens
- Colours: exactly the table above. `--line #dcd6ca` is a rule colour, never text.
- Radius: 13px cards/buttons; pills only on status badges.
- Touch targets ≥ 56px (buttons are 58px).
- Sizes: headline clamp(28–42px); body 15–16px; secondary 14px; labels **13px/600**; nothing under 13px.
- `font-variant-numeric: tabular-nums` on all counts.

## Principles → consequences
- Privacy is an absence; make it countable → the ledger panel is the largest element and carries provenance on every number.
- One accent per state → green is the accent (safe action); red is semantic status only.
- No manufactured certainty → no confidence percentage on the family screen (ruling R8).

## Screen contract — family alert (tool)
- Goal: a family member at 4am knows what happened and answers in one tap.
- States: open (dominant action: "We're good"), answered (no dominant action).
- Signifiers: two filled buttons; nothing else clickable.
- Place: "Private at home" status + product name in header. Identity: name + purpose line once.
- Regions: header · incident · actions · ledger · footer (5).
- Anchor: buttons directly under the facts they answer.

## Not allowed
Gradients, glow, emoji icons, `transform: scale` on press, grey text under 7:1, a second accent, dark theme on the family screen.

## Not settled here
The backup deck (`pitch/backup/index.html`) is dark-with-yellow and was not restyled; it is a fallback artifact only.
