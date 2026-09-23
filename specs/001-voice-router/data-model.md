# Data Model: Voice Router

## Dataset models

`DatasetSnapshot` holds dataset name/version/as-of date/content fingerprint and immutable maps for `Scenario`, `SlotDefinition`, `ActionDefinition`, knowledge and mock-backend records. Startup validation requires SC01–SC40, validates scenario slot/action/boundary IDs and queues, and keeps `SYS_OUT_OF_SCOPE`, `SYS_UNCLEAR`, `SYS_GOODBYE` separate.

`Scenario` stores ID, domain/category, description, boundary rules, priority, identification, required/optional slots, actions, confirmation, handoff and multilingual examples/responses. `SlotValue` stores name, raw evidence, normalized typed value, source (`current_turn|prior_turn|identity|action`) and validation status.

## Runtime models

| Entity | Core fields / validation |
|---|---|
| `Conversation` | ID, ordered turns, `DialogueState`, status; maximum 10 exchanges |
| `DialogueState` | active/suspended goals, valid slots, identity refs, language history, unresolved goals, clarification/action records |
| `Turn` | ID, input mode, transcript, normalized input, response, timestamp; exactly one trace |
| `RoutingResult` | selected/alternatives, language, slots, continuation/topic change, clarification/fallback/handoff; first selection primary, unique IDs |
| `SelectedIntent` | ID, confidence/category, concise reason, segment/order; never conflated with alternative |
| `ExecutionState` | scenario, missing slots, preview/confirmation/result/error; declared action only |
| `ActionRecord` | action, normalized input digest, preview/idempotency key, mode and terminal result; duplicate returns original |
| `SupervisorTrace` | masked input, decision/state/action/config/timer fields; no hidden reasoning |
| `EvaluationRun` | config/snapshot IDs, predictions, evaluator output, per-case diagnostics |

```text
conversation: OPEN → GOODBYE | HANDOFF | TURN_LIMIT → CLOSED
goal: ACTIVE → SUSPENDED → RESUMED | COMPLETED | HANDOFF
action: READY → PREVIEW → WAITING_CONFIRMATION → EXECUTING → COMPLETED
                                  └→ CANCELLED | FAILED | HANDOFF
```

System intents/fallback/handoff never execute business actions. Relative dates use 2026-10-01 unless an explicit traceable test override is supplied.
