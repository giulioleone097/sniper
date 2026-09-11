stamp: e6f1fc1 none 2026-09-08
# sniper - conventions

Nessuna pull request merged nella finestra: le convenzioni qui vengono dai commit, dalle regole in `AGENTS.md` e da `scripts/check.sh`, che le esegue.

## Commit
Un commit per comportamento, con il perché nel corpo quando non è ovvio; nessuna attribuzione all'agente (`Co-Authored-By`, "Generated with"). I soggetti recenti aprono con il componente toccato (`narrate:`, `scripts:`, `map:`) invece del tipo Conventional Commits; 7 su 19 seguono il formato `feat:`. Mediana del soggetto: 55 caratteri.

## Skill e riferimenti
Corpo sotto le 120 righe, un solo blocco di output, condizione di stop per ultima; un ramo davvero condizionale vive in `references/<nome>.md` sotto le 80 righe. La descrizione apre con "Use when", sta sotto le 70 parole e chiude con "Not for". Eseguito da `check.sh`. Un cambio piccolo e compreso segue il percorso diretto; il chaining tra `scope`, `build` e `review` resta per lavoro ampio o incerto.

## Implementazione e review
KISS, YAGNI, DRY e SOLID guidano soluzioni economiche; i confini Clean/Hexagonal restano quando proteggono una responsabilità o un confine dominio/I/O concreto. Un'unica implementazione non basta da sola a rimuovere un port utile. I test nuovi sono indispensabili solo per regressioni significative che i controlli esistenti non coprono; TDD è opzionale. La review corregge i difetti verificati dentro l'obiettivo per default, rispetta `--read-only`, e usa subagent senza team minimo quando l'analisi indipendente serve.

## Scorciatoie
Un limite deliberato in uno script porta `ceiling: <limite>, upgrade <trigger>`; `scripts/debt.sh` li elenca e marca chi non ha trigger. Eseguito da `check.sh` come risposta del registro.

## Percorsi e host
Nessuna variabile di host dentro skill e agenti; `<this skill>` e `<plugin root>` al loro posto. Un file hook per famiglia di host, ciascuno solo con gli eventi che quella famiglia lancia; gli script hook rispondono con l'unione delle forme dei quattro host. Eseguito da `check.sh` per variabili ed eventi.

## Rilascio
Bump della versione nei quattro manifesti, `sh scripts/check.sh` verde, commit, push, poi `claude plugin update sniper@sniper`, `codex plugin remove` + `codex plugin add sniper@sniper`, `devin plugins update sniper` o reinstall su Cursor, `scripts/install-*.sh` dove usati, e `scripts/install-codex-agents.sh` quando un agente cambia.

## Prova
Le modifiche direttamente ispezionabili usano l'ispezione dell'output; quelle comportamentali usano il controllo esistente più vicino o un esercizio reale del percorso. Il rilevatore o lo script nuovo viene provato su repository reali di stack diversi prima del commit. Gli eval confrontano baseline, plugin corrente e precedente opzionale su cinque sonde; costi, durata e turni riportano copertura `available/total`, senza trasformare metriche mancanti in zero.
