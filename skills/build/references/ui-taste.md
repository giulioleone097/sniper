# ui-taste

The diff touches components, styles, or templates.

1. The repository's own design system wins. Reuse its tokens, spacing scale, type scale, and components before inventing anything, per the core ladder, and match the neighbouring file's conventions exactly.
2. Only when no system exists, commit to one aesthetic direction and execute it precisely. Name the direction in one line before writing any CSS.
3. Fonts: pick faces with context-specific character. Inter, Roboto, Arial, and the default system stack read as machine output.
4. Color: a dominant color with sharp accents beats an evenly spread palette. Purple gradients on white are the single most recognizable AI-generated tell.
5. Layout: the centered card on a hero gradient is the default nobody chose. Earn attention with asymmetry, overlap, controlled density, or genuine negative space.
6. Motion: spend it on one high-impact moment — a staggered load, a hover that surprises — instead of scattering micro-interactions.
7. Specify every value concretely: `16px`, `#1a1a1a`, `1.35` line height. A value you cannot write as a number or a hex is a value you have not decided.
8. Keep accessibility intact, per core: contrast ratios, focus states, keyboard paths, reduced-motion handling, semantic elements over div soup.
9. Self-audit your own summary and comments before reporting:

```bash
grep -inE 'clean|modern|sleek|user-friendly|intuitive|seamless|polished|minimalist' <changed files>
```

Then reread your own summary for the same words. Every hit describing your own work marks a decision you did not make. Replace it with the px, the hex, or the trade-off you actually chose.
