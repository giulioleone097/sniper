stamp: 492dbe1 none 2026-09-05
# sniper - conventions

Nessuna pull request merged nella finestra: le convenzioni qui vengono dai commit, dalle regole in `AGENTS.md` e da `scripts/check.sh`, che le esegue.

## Commit
Un commit per comportamento, con il perché nel corpo quando non è ovvio; nessuna attribuzione all'agente (`Co-Authored-By`, "Generated with"). I soggetti recenti aprono con il componente toccato (`narrate:`, `scripts:`, `map:`) invece del tipo Conventional Commits; 7 su 19 seguono il formato `feat:`. Mediana del soggetto: 55 caratteri.

## Skill e riferimenti
Corpo sotto le 120 righe, un solo blocco di output, condizione di stop per ultima; un ramo davvero condizionale vive in `references/<nome>.md` sotto le 80 righe. La descrizione apre con "Use when", sta sotto le 70 parole e chiude con "Not for". Eseguito da `check.sh`.

## Percorsi e host
Nessuna variabile di host dentro skill e agenti; `<this skill>` e `<plugin root>` al loro posto. Gli hook usano solo eventi e forme che entrambi gli host supportano. Eseguito da `check.sh` per le variabili.

## Rilascio
Bump della versione in entrambi i manifesti, `sh scripts/check.sh` verde, commit, push, poi `claude plugin update sniper@sniper` e `codex plugin remove` + `codex plugin add sniper@sniper`, e `scripts/install-codex-agents.sh` quando un agente cambia.

## Prova
Directly inspectable changes get output inspection; behavioral changes use the nearest existing check; il rilevatore o lo script nuovo viene provato su repository reali di stack diversi prima del commit (dieci repository, sei stack, per i rilevatori).
