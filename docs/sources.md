# sources

What sniper is built from. Star counts snapshotted 2026-09-03.

## Top 10 (what was taken)

| source | url | stars | taken |
|---|---|---|---|
| obra/superpowers | https://github.com/obra/superpowers | 281k | brainstorming (trimmed to `scope`), writing-plans → `plan`, systematic-debugging → `debug`, verification-before-completion → `prove`, requesting/receiving-code-review → `review`, finishing-a-development-branch → `ship` |
| affaan-m/everything-claude-code | https://github.com/affaan-m/everything-claude-code | 247k | block-no-verify hook, KISS/DRY/YAGNI rules distilled into `core`; rejected: 80% coverage mandate, planning-doc quintuplet, 100+ agents |
| mattpocock/skills | https://github.com/mattpocock/skills | 246k | grilling → `scope`, tdd seams → `build`, diagnosing-bugs feedback loop → `debug`, code-review Standards/Spec axes → `review`, codebase-design vocabulary → `simplify --repo`, writing-for-agents → how every SKILL.md here is written, git-guardrails → `guard.sh` |
| garrytan/gstack | https://github.com/garrytan/gstack | 131k | completion status protocol → `prove`, careful guardrails → `guard.sh`, ship checklist (trimmed from 76 KB to one page); rejected: skill size, telemetry, 23 personas |
| DietrichGebert/ponytail | https://github.com/DietrichGebert/ponytail | 123k | the ladder and the review format (`delete:` `stdlib:` `native:` `yagni:` `shrink:` plus sniper's `reuse:`, `net: -N lines`) → `core`, `simplify`, `review` slop lens; SessionStart/SubagentStart injection pattern |
| anthropics/claude-plugins-official | https://github.com/anthropics/claude-plugins-official | 36k | code-review parallel agents + confidence >= 80 filter → `review`; code-simplifier → `simplify`; feature-dev explorer agents → `sniper-scout`; pr-review-toolkit silent-failure-hunter → `review` safety lens; plugin-dev structure |
| EveryInc/compound-engineering-plugin | https://github.com/EveryInc/compound-engineering-plugin | 25k | ce-plan output contract (direct / brief / artifact) → `plan`; ce-compound one-learning-per-run → `learn`; lfg pipeline → `flow`; ce-simplify-code personas collapsed into a checklist |
| JuliusBrussee/caveman | https://github.com/JuliusBrussee/caveman | 72k | native-core reuse ladder → `core`; lean-build / surgical-patch / safe-refactor / migration → `build` modes; verify-and-stop → `prove`; cavecrew compressed subagent output → all three agents |
| taste (design taste skill) + frontend-design | local — Claude skills, no public repo | local | anti-slop for UI: concrete px/hex, no vague vibes → `references/ui-taste.md` |
| agent-workflow-orchestrator (own) | https://github.com/giulioleone097/agent-workflow-orchestrator | local | goal contract, owner contract + handoff, review-diff one-pass rule, elision rule, prove-work ladder, "## Code Review Rules" in AGENTS.md → `scope`, agents, `review`, `core`, `prove`, `learn` |

| humanlayer/skills | https://github.com/humanlayer/skills | 2026-09 | show-me: explain a change by its shape (pseudocode, call tree, file tree, one Mermaid sequence, diff-shaped before/after) → `narrate` shape views |

## Also read / rejected

- hamelsmu/claude-review-loop (https://github.com/hamelsmu/claude-review-loop) — stop-hook review loop; rejected as too intrusive.
- OneRedOak/claude-code-workflows (https://github.com/OneRedOak/claude-code-workflows) — design/security review lenses.
- github/spec-kit (https://github.com/github/spec-kit) and BMAD — rejected: ceremony.
