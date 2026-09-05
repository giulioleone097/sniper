stamp: 452f32d none 2026-09-05
# sniper - map

## Cosa fa, in una frase
Un plugin per Claude Code e Codex che porta un lavoro dall'arrivo (issue, PR, idea) alla consegna (commit, PR, dossier) attraverso sedici skill piccole, quattro agenti, sette rilevatori e un banco di prova agentico, con una dottrina anti-slop iniettata a ogni sessione.

## Domini
- Dottrina: `core/SNIPER.md`, iniettata da `scripts/core-context.sh` via `hooks/hooks.json` (SessionStart, SubagentStart); il blocco in `AGENTS.md` deve restare identico, `scripts/check.sh` lo verifica. Raggiunta da ogni sessione dei due host.
- Skill: `skills/<name>/SKILL.md` (<= 120 righe, descrizione che apre con "Use when", <= 70 parole) con `agents/openai.yaml` per Codex e `references/` (<= 80 righe) per i rami condizionali. Raggiunte dai due host per nome; Codex accorcia la descrizione a ~45 caratteri.
- Agenti: `agents/sniper-{scout,worker,reviewer,integrator}.md`; su Codex generati in `~/.codex/agents/*.toml` da `scripts/install-codex-agents.sh`.
- Guardie: `scripts/guard.sh` (PreToolUse Bash, nega `--no-verify`, force push, `reset --hard`, scarti dell'intero albero, `rm -rf` della radice); fixture in `scripts/test-guard.sh`.
- Rilevatori: `scripts/checks.sh` (comandi di verifica del progetto), `tracker.sh` (forge e CLI), `consumers.sh` (repository dipendenti), `tokens.sh` (token di design), `repo-facts.sh` (fatti per la mappa), `debt.sh` (registro dei `ceiling:`), `pr-partition.py` (partizione del diff); `skills/narrate/scripts/` tiene `pr-contracts.py`, `pr-walkthrough.py`, `test-summary.py`.
- Evals: `evals/run.py` e `evals/tasks.py`, sessioni headless `--bare` con e senza plugin su tre sonde con riferimenti buono/cattivo; il selftest gira in `check.sh`, la corsa live richiede `ANTHROPIC_API_KEY`.
- Manifesti: `.claude-plugin/plugin.json` e `.codex-plugin/plugin.json` (versioni pari), marketplace in `.claude-plugin/marketplace.json` e `.agents/plugins/marketplace.json`.

## Flusso principale
```
map? -> intake? -> grill? -> scope -> plan? -> build -> simplify -> review -> prove -> narrate -> ship -> learn?
                                                                                   handoff (quando la sessione si interrompe)
flow = la stessa catena senza check-in, mai grill
```
Ogni skill legge `docs/sniper/map.md` prima di esplorare; `review` e `simplify` dispacciano un revisore per area e un integratore che verifica e attribuisce le regressioni alla baseline.

## Confini
- `hooks/hooks.json` è condiviso dai due host: solo eventi e forme che entrambi supportano (SessionStart, SubagentStart con additionalContext; PreToolUse con permissionDecision).
- Nessuna variabile di host dentro una skill o un agente: i percorsi sono relativi al file che li nomina (`<this skill>`, `<plugin root>`).
- Le skill sono host-neutrali; Codex non ha agenti nel plugin, quindi li riceve come agenti custom generati.

## Repository collegati
Nessuno: `scripts/consumers.sh` non trova manifesti che nominino questo repository.

## Controlli
- `sh scripts/check.sh`: quattro `claude plugin validate --strict`, 45 fixture del guard, JSON dei manifesti, sincronia della dottrina, parità di versione, regole del repository (limiti di righe, nessuna variabile di host, script che parsano, rilevatori che rispondono, descrizioni con il trigger in testa).
- `scripts/checks.sh` non trova un manifesto di progetto: il controllo canonico è `check.sh`.

## Scorciatoie dichiarate
`sh scripts/debt.sh .`: tre `ceiling:` nei rilevatori (tokens.sh 400 fogli di stile, consumers.sh profondità 4, repo-facts.sh tre chiamate gh per PR), tutti con trigger di upgrade.

## Punti caldi
`.claude-plugin/plugin.json` e `.codex-plugin/plugin.json` (ogni rilascio bumpa entrambi), `README.md` e `docs/DESIGN.md` (ogni rilascio li aggiorna), `skills/narrate/SKILL.md` (la skill più riscritta: dossier v1 -> v6).

## Persone
Un solo autore nella finestra: Giulio Leone. Nessuna PR merged: il lavoro arriva su `main` per push diretto.

## Fonti
`scripts/repo-facts.sh . 12 0`, `scripts/consumers.sh .`, `scripts/checks.sh .`, lettura diretta dei file; nessun server di grafo o simboli usato per questa mappa.
