# Shapes for a dossier

One map for the whole change, one shape per domain. Smallest view that carries the point; a shape needing a paragraph of explanation is the wrong shape. Keep the neighbours that did **not** change - a picture of only the changed nodes says nothing about blast radius - and use real names and real numbers, or the shape is decoration.

## The map, once, after the plain-words list

Lanes are the reader's mental model - a runtime, a tier, a trust boundary - never the folder tree. Twelve nodes at the outside. Mark the one edge the change is really about. Mermaid renders natively on GitHub, GitLab and Azure DevOps.

```mermaid
flowchart LR
  subgraph browser[Browser]
    chat[Chat shell]:::changed
    dash[Dashboard]:::same
  end
  subgraph backend[Supervisor]
    turn[Turn pipeline]:::changed
    graph[Phase graph]:::new
  end
  subgraph tools[Retrieval tools]
    inv[Single investigation]:::new
    kg[Knowledge graph]:::same
  end
  chat ==>|one call, widgets streamed| turn
  turn --> graph --> inv --> kg
  dash --> inv
  classDef new stroke-width:2px
  classDef changed stroke-width:2px
  classDef same opacity:0.55
```

Faded nodes are untouched and prove the reach; a deleted node a reader would still look for stays, labelled removed.

## Per-domain shapes, in order of preference

**Control flow**, when the change is a decision:

```diff
 on(turn)
-  pick specialist by heuristic score
+  bind operator scope from the page catalogue
+  route to a typed phase (analytics | execution | troubleshooting)
   run tools
+  if the phase needs the operator: pause, persist, resume on answer
```

**Call tree**, when the change is who calls what:

```diff
 handle_turn
   bind_operator_request_scope_hook
-  TeamRuntime.route
+  XMateOrchestrator.run
+    xmate_investigate            # one call, was four
     stream_consumer
```

**File tree**, when the change is where responsibility now lives - shallow, comments say what each owns:

```diff
 analytics/
-├── _analytics_tools.py   # 2,239 lines: routing, queries, cards
+├── engine/               # query planning
+├── domains/              # one file per data domain
+└── insights/             # cards and KPI tiles
```

**Component tree**, for a UI change - state and boundaries that matter, real path on the root: `<AiChat> (…/ai-chat.ts)` / `useChatRuntime()` / `+ <AnswerProvenance/>` / `<ChatTimeline>` / `+ <KpiTiles/>`, in a `diff` fence.

**Sequence**, only when ordering across boundaries is the point and no tree shows it. One flow beats three thin ones: `Chat->>Supervisor: question` / `Supervisor->>Tools: one investigation call` / `Tools-->>Supervisor: metrics, chart, insights` / `Supervisor-->>Chat: widgets, then tokens`.

## Rules

- Unchanged neighbours stay in: faded on the map, a leading space in a `diff` fence.
- Two shapes must not carry substantially the same nodes; drop the weaker one.
- No findings in a shape - no severity, no bug, no security note. This is the comprehension layer; `review` owns defects.
- No folder tree presented as architecture, and no level added because the previous one existed: system context, then containers, then a component view only when an affected container's internals matter.

Distilled from humanlayer/skills `show-me` (view catalogue, diff-shaped views) and coldtea `pr-lens` (lanes, hero edge, unchanged neighbours, no findings lens, C4-inspired view choice).
