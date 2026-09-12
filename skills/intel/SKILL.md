---
name: intel
description: Use when the user brings a question to research, docs or API facts to gather, or reading legwork to delegate while the session keeps working. Spins up a background subagent that reads primary sources, traces every claim to its owner, and writes findings to one cited Markdown file. Not for locating code inside this repo.
argument-hint: "[the question to research] [--out <file>]"
---

1. Take the argument as the question. Empty: ask what to research in one line and stop there.

2. Spin up a background subagent to do the reading, so the session keeps working while it investigates. This is not `sniper-scout`, which is code-read-only for this repo; give the question to the host's general-purpose or web-capable subagent instead. Hand it the question and steps 3-4 as its job.

3. Its job: investigate the question against primary sources only — official docs, source code, specs, first-party APIs — never a secondary write-up of them. Follow every claim back to the source that owns it; a blog post or forum answer citing a spec is a pointer to go read, not the source itself.

4. Write the findings to one Markdown file, citing each claim's source inline. Destination: `--out <file>` when given; else wherever the repo already keeps this kind of note (check `docs/sniper/map.md` and any existing `docs/intel-*` or similar files for the convention); when there is none, `docs/intel-<slug>.md`, `<slug>` derived from the question.

5. Report the path and a one-line summary of what the subagent found:

```
<path> — <one-line summary of the findings>
```

Stop when the file is written, cites its sources, and the path is printed.
