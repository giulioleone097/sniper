stamp: e6f1fc1 none 2026-09-08
# sniper - map

## Cosa fa, in una frase
Un plugin per Claude Code e Codex che porta un lavoro dall'arrivo (issue, PR, idea) alla consegna (commit, PR, dossier) attraverso cinque fasi che si chiamano da sole (setup, scope, build, review, ship) più quattro ingressi digitati per nome (grill, simplify, handoff, optimize), quattro agenti, sette rilevatori e un banco di prova agentico, con una dottrina anti-slop iniettata a ogni sessione. Per i cambi piccoli e compresi il percorso è implementazione, review, fix e prova; il ciclo completo resta per lavori ampi o incerti.

## Domini
- Dottrina: `core/SNIPER.md`, iniettata da `scripts/core-context.sh` via `hooks/hooks.json` (SessionStart, SubagentStart); il blocco in `AGENTS.md` deve restare identico, `scripts/check.sh` lo verifica. Raggiunta da ogni sessione dei due host.
- Fasi: `skills/<stage>/SKILL.md` (<= 120 righe, router; descrizione che apre con "Use when", <= 70 parole) con `agents/openai.yaml` per Codex e `references/` (<= 80 righe) per ogni ramo: intake, grill e asking in scope; plan, debug, prove e i modi in build; shrink, slop, platform-native, audit e pr in review; narrate, shapes, evidence, posting, learn, environment in ship; map in setup; handoff e optimize senza rami, il corpo è la procedura. Raggiunte dai due host per nome e l'una dall'altra; Codex accorcia la descrizione a ~45 caratteri.
- Agenti: `agents/sniper-{scout,worker,reviewer,integrator}.md`; su Codex generati in `~/.codex/agents/*.toml` da `scripts/install-codex-agents.sh`.
- Guardie: `scripts/guard.sh` (PreToolUse Bash, nega `--no-verify`, force push, `reset --hard`, scarti dell'intero albero, `rm -rf` della radice); fixture in `scripts/test-guard.sh`.
- Rilevatori: `scripts/checks.sh` (comandi di verifica del progetto), `tracker.sh` (forge e CLI, con gh e glab sondati per un host enterprise o self-hosted), `consumers.sh` (repository dipendenti), `tokens.sh` (token di design), `repo-facts.sh` (fatti per la mappa), `debt.sh` (registro dei `ceiling:`), `pr-partition.py` (partizione del diff); `skills/ship/scripts/` tiene `pr-contracts.py`, `pr-walkthrough.py`, `test-summary.py`.
- Evals: `evals/run.py` e `evals/tasks.py`, cinque sonde in sessioni headless `--bare` con baseline, plugin corrente e plugin precedente opzionale, con riferimenti buono/cattivo; il selftest gira in `check.sh`, la corsa live richiede `ANTHROPIC_API_KEY` e le metriche mancanti restano non disponibili.
- Manifesti: `.claude-plugin/plugin.json` e `.codex-plugin/plugin.json` (versioni pari), marketplace in `.claude-plugin/marketplace.json` e `.agents/plugins/marketplace.json`.

## Flusso principale
```
setup? -> scope (intake | grill | card) -> build (plan? | debug? | modo | prove) -> review (shrink, review locale o subagent utili, integrazione se serve) -> ship (commit, dossier, lesson)
```
Fuori ciclo, per nome: `handoff` scrive dove sta il lavoro in `docs/handoff-*.md`, `scope <file>` lo riprende e `ship` lo cancella a lavoro committato; `optimize` spinge una metrica verso un target con round di ipotesi parallele in worktree, misurate contro una baseline presa in un worktree di `HEAD`, poi passa il diff tenuto a `review`.
Il ciclo sceglie il percorso: i cambi piccoli e compresi usano implementazione, review, fix e prova; i lavori ampi o incerti passano da `scope`, `build` e `review`. La review usa subagent economici solo quando aggiungono valore, senza un team minimo, e attribuisce le regressioni alla baseline dopo aver verificato i report.

## Confini
- `hooks/hooks.json` è condiviso dai due host: solo eventi e forme che entrambi supportano (SessionStart, SubagentStart con additionalContext; PreToolUse con permissionDecision).
- Nessuna variabile di host dentro una skill o un agente: i percorsi sono relativi al file che li nomina (`<this skill>`, `<plugin root>`).
- Le skill sono host-neutrali; Codex non ha agenti nel plugin, quindi li riceve come agenti custom generati.

## Repository collegati
Nessuno: `scripts/consumers.sh` non trova manifesti che nominino questo repository.

## Controlli
- `sh scripts/check.sh`: quattro `claude plugin validate --strict`, 45 fixture del guard, JSON dei manifesti, sincronia della dottrina, parità di versione, regole del repository (limiti di righe, nessuna variabile di host, script che parsano, rilevatori che rispondono, descrizioni con il trigger in testa).
- `scripts/checks.sh` non trova un manifesto di progetto: il controllo canonico è `check.sh`.

## Stato della mappa
Lo stamp riflette `HEAD` (`e6f1fc1`, 2026-09-08). Le modifiche di policy 1.2.0 e del runner eval presenti nel working tree sono state considerate per questa documentazione, ma non sono presentate come già committate.

## Scorciatoie dichiarate
`sh scripts/debt.sh .`: quattro `ceiling:` nei rilevatori (tokens.sh 400 fogli di stile, consumers.sh profondità 4, repo-facts.sh tre chiamate gh per PR, tracker.sh host non loggato letto come forge=none), tutti con trigger di upgrade.

## Punti caldi
`.claude-plugin/plugin.json` e `.codex-plugin/plugin.json` (ogni rilascio bumpa entrambi), `README.md` e `docs/DESIGN.md` (ogni rilascio li aggiorna), `skills/ship/references/narrate.md` (il documento più riscritto: dossier v1 -> v6).

## Persone
Un solo autore nella finestra: Giulio Leone. Nessuna PR merged: il lavoro arriva su `main` per push diretto.

## Fonti
`scripts/repo-facts.sh . 12 0`, `scripts/consumers.sh .`, `scripts/checks.sh .`, lettura diretta dei file; nessun server di grafo o simboli usato per questa mappa.
