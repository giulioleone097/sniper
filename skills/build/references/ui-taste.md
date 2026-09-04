# ui-taste

The diff touches components, styles, or templates. Read the repository before reading your own taste.

1. Measure the system that already exists, before inventing one. Run `sh <plugin root>/scripts/tokens.sh <ui path>` (the `scripts/` folder at the plugin root): it prints the design tokens the repository actually defines - custom properties, theme keys, spacing and type scales, the fonts it loads - with counts, so the dominant values are visible. Those values win, per the core ladder; a neighbouring component's conventions win next.
2. Only when no system exists, commit to one aesthetic direction and execute it precisely. Name the direction in one line before writing any CSS, with the three decisions that carry it: the type pairing, the dominant colour and its accent, the spacing unit.
3. Every value is a number or a hex: `16px`, `#1a1a1a`, `1.35` line height, `240ms`. A value you cannot write that way is a decision you have not made.
4. Fonts: pick faces with context-specific character. Inter, Roboto, Arial, and the default system stack read as machine output unless the repository already chose them.
5. Colour: one dominant colour with sharp accents beats an evenly spread palette. The purple gradient on white is the single most recognisable machine tell.
6. Layout: the centred card on a hero gradient is the default nobody chose. Earn attention with asymmetry, overlap, controlled density, or real negative space, and say which one you chose and what it costs.
7. Motion: one high-impact moment, staggered load or a hover that surprises, instead of scattered micro-interactions.
8. Restraint is a decision too. At least one thing you deliberately did not add, named with its reason: the second accent colour you refused, the shadow you kept at zero, the animation you left out.
9. Accessibility stays intact, per core: contrast ratios, focus states, keyboard paths, reduced-motion handling, semantic elements over div soup.
10. Self-audit before reporting. Grep the changed files and your own summary:

```bash
grep -inE 'clean|modern|sleek|user-friendly|intuitive|seamless|polished|minimalist|elegant|beautiful' <changed files>
```

Every hit describing your own work marks a decision you did not make: replace it with the px, the hex, or the trade-off. Then the harder test, per decision: could this sentence have been written without ever seeing this repository? If yes, it is not a decision, delete it.

Distilled from the `taste` skill (design map plus taste DNA: trigger, decision, reason, evidence, one restraint per design) and Anthropic's frontend-design guidance.
