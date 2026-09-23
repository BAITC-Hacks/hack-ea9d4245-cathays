# HTTP API Contract (Initial)

Responses include `conversation_id`, applicable `turn_id`, and `trace_id`. Errors are `{ "code": string, "message": string, "trace_id": string }` without provider internals.

## `POST /v1/conversations`

Optional `{ "preferred_language": "ru|kk|mixed" }`; returns `{ "conversation_id": "...", "status": "open" }`.

## `POST /v1/conversations/{conversation_id}/turns`

Request: `{ "text": "...", "input_mode": "text", "client_turn_id": "uuid" }`. Response contains customer-safe `assistant_message`, public `routing` (selected, alternatives, language, clarification/fallback/handoff), execution state and latency summary. Repeated `client_turn_id` returns the original result.

## `GET /v1/conversations/{conversation_id}`

Customer-safe history/current public state; no supervisor trace, raw identifiers or hidden model content.

## `GET /v1/conversations/{conversation_id}/traces/{turn_id}`

Returns masked `SupervisorTrace`: decision, slots, state, actions, fallback/handoff, snapshot/prompt/policy/model IDs and stage `{duration_ms,status}` fields. It never returns chain-of-thought.

## `POST /v1/evaluations` and `GET /v1/evaluations/{evaluation_id}`

Start/query product-router batch evaluation. Results include reference metrics, artifacts/configuration and errors. Prediction projection is `{"U001":["SC01"],"U081":["SC27","SC04"]}`.

## Deferred voice API

Milestone 9 adds `POST /v1/conversations/{id}/audio-turns`, taking a completed recording plus client capture timestamps and returning the exact normal turn response with STT/TTS timings—never a separate business path.
