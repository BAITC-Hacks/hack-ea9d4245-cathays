# Implementation Plan: Voice Router

**Branch**: `001-voice-router` | **Date**: 2026-09-23 | **Spec**: [spec.md](spec.md)

## Summary

Build a hackathon-scale modular monolith that routes Russian, Kazakh, and mixed-language Saqta Insurance requests through an LLM final decision against the complete version 1.0 dataset. Deterministic validation, decision policy, dialogue state, controlled mock execution, grounded responses, and traces surround that decision. Deliver text routing/evaluation first; add state, execution, UI, and voice only after measured routing quality.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript 5.x / React 18 frontend.

**Primary Dependencies**: FastAPI, Pydantic v2, httpx, pytest; Vite, React, TypeScript, Tailwind, browser MediaRecorder/Web Audio. LLM/STT/TTS are provider adapters, selected through configuration.

**Storage**: Checked-in JSON dataset; in-memory process-local conversation/trace stores; ignored local `artifacts/` evaluation reports. No production database initially.

**Testing**: pytest unit/contract/integration, Playwright UI/device mocks, supplied `evaluate.py` unchanged.

**Target Platform**: Single-process local/container backend and modern Chromium browser.

**Project Type**: React web application with Python API.

**Performance Goals**: Measure text router latency from Milestone 1; optimize later toward ~500 ms routing and 1.5 s speech-to-first-audio without sacrificing safety/correctness.

**Constraints**: Dataset v1.0 and date 2026-10-01 are authoritative; LLM selects every final semantic route; 40 scenarios + 3 system intents; no label lookup; max 10 exchanges; irreversible action idempotency; no chain-of-thought in traces.

## Constitution Check

**Pre-design gate: PASS.** This design loads/cross-validates the authoritative artifacts, makes an LLM the final semantic selector, explicitly models system intents and ordered multi-intent results, and isolates validation/execution from the model. It contains no encoder classifier, utterance mapping, separate evaluator router, production integration, vector database, or persistent database.

| Gate | Evidence |
|---|---|
| Dataset source of truth | Startup cross-reference validation; version/date fingerprint in each trace/evaluation |
| Boundary-aware LLM routing | Versioned prompt passes descriptions, exclusions, substitutions, priority, state and catalog |
| Context/language/multi-intent | Dialogue state, ordered selections, language-independent reuse and dialogue tests |
| Safe uncertainty/actions | Pydantic validator, deterministic policy, preview/confirmation/idempotency state machine |
| Grounding/traces | Dataset-only evidence, masked structured trace; no hidden reasoning |
| Evaluation/latency | Product router batch runner; unchanged scorer and stage timers |

The constitution’s uncertainty-policy TODO is resolved by a Milestone 3 calibration experiment and versioned policy. Real-data telemetry and cost governance are explicit pre-production gates; they do not block the synthetic hackathon artifact.

## Proposed Architecture and Data Flow

```text
text ──────────────────────────────────────────────────────────────┐
microphone → STT adapter → transcript                              │
                         ↓                                         ↓
                 TurnOrchestrator → triage → LLM router → validator
                         ↕ DialogueState       ↑ catalog/prompt
                         ↓                      │
                    DecisionPolicy → executor → grounded response → TTS → audio
                         ↓             ↓
                   TraceRecorder   DatasetRepository → supervisor API/UI
```

Text and voice join at `TurnOrchestrator`; there is one business pipeline. Triage may normalize values, detect language/urgency, and propose candidates, but only `LLMClient.route` makes a final semantic selection. Validator rejection triggers repair/fallback, while policy converts a validated decision into normal routing, clarification, fallback, or handoff without changing its semantics.

## Component Responsibilities

| Component | Does | Must not do |
|---|---|---|
| Dataset repository/validator | Load immutable dataset, validate schemas/cross-refs | Substitute or rewrite data meaning |
| Prompt builder | Build versioned catalog/state routing prompt | Include dev labels/hidden answers |
| LLM client | Return `RawRoutingDecision` via adapter | Execute actions/generate company facts |
| Routing validator | Validate JSON, IDs, ordering, slots/queues | Guess replacement scenarios |
| Decision policy | Deterministically accept/clarify/retry/fallback/handoff | Make LLM-free semantic routing |
| Dialogue service | Maintain relevant 10-turn state, suspend/resume | Depend on browser-owned canonical state |
| Scenario executor | Identity, slots, declared mock actions | Execute unsupported action/system intent |
| Grounded responder | Produce short response from data/action result | Invent insurer/client facts |
| Trace recorder | Masked decision/action/config/timing trace | Store hidden reasoning |
| Evaluation runner | Call production router and project predictions | Provide a second router |

## LLM Router and Structured Output

`PromptBuilder` emits a monotonic `routing_prompt_version` with task rules; system intents; relevant state; normalized slots; and compact cards for all 40 scenarios—purpose, `not_this_if`, `use_instead`, priority, identification/actions and multilingual examples. It requires boundary comparison, distinct selected vs alternative IDs, ordered multi-intent output (urgent first, otherwise utterance order), concise reasons, and JSON only.

Start with the full catalog. Retrieval is deferred until a benchmark proves every evaluation/boundary target remains eligible and product-router metrics are preserved. Provider adapters expose `route(request)`, `transcribe(audio)`, and `synthesize(text, language)`; trace provider/model/schema/temperature, prompt, catalog and policy versions.

Use provider-native JSON schema when available, normalized into Pydantic models; otherwise JSON-only prompting with identical validation. Malformed JSON, unknown/duplicate ID, selected/alternative overlap, invalid slot/action/queue, invalid ordering, or system intent with action causes one corrective re-prompt. A second failure creates explicit safe fallback with no action. Missing/invalid catalog fails closed before a model call.

## Decision / Uncertainty Policy

Model confidence and alternatives are evidence, not a permanent threshold. Milestone 3 chooses a versioned accept-versus-clarify policy from false-route, false-clarification, boundary, language and multi-intent measurements. Before calibration, accept only a single valid high-certainty result without material competition; otherwise return `SYS_UNCLEAR`, preserve two alternatives, and ask one concise contrast question. Two unresolved attempts, direct operator request, or dataset-declared handoff condition creates a validated queue handoff package.

## Dialogue State and Scenario Execution

`Conversation` contains turns and `DialogueState`: active scenario, LIFO suspended goals with relevant slots, language history, slot provenance, identity references, unresolved goals, clarification state, and action/idempotency records. A material goal change suspends instead of erasing state; language-only change never changes scenario. At ten exchanges, summarize/conclude or hand off safely.

Execution is deterministic: validate business scenario → identify if needed → reuse valid profile/slots → collect one missing required slot → normalize/validate by `slots.json` and snapshot date → preview → explicit affirmative tied to preview → execute declared mock action → map dataset error → grounded response. `READY → PREVIEW → WAITING_CONFIRMATION → EXECUTING → COMPLETED`, with `CANCELLED`, `FAILED`, `HANDOFF` exits. `(conversation_id, preview_id, action_name, normalized-input digest)` ensures a duplicate returns prior result rather than repeating a side effect.

## Frontend / Backend Boundary and Observability

React owns microphone permission/recording, text entry and presentational state. It never owns canonical dialogue state or business policy. Customer view shows transcript, listening/processing/audio/text/clarification/handoff states. Supervisor view displays only trace fields.

Every trace has conversation/turn IDs; masked transcript; language; selections/confidence/structured reasons; alternatives; slots/provenance; continuation/topic state; actions; fallback/handoff; snapshot/prompt/policy/model configuration; and timers. Timers are `{duration_ms, status: measured|skipped|failed}`; total remains interpretable. No raw provider reasoning is retained or displayed. See [HTTP contract](contracts/http-api.md).

## Testing and Evaluation

- Contract tests validate 40 scenarios, 43 slots, 31 actions, six queues, `use_instead`, action contracts and system-intent isolation before startup/evaluation.
- Router tests cover schema validation/retry, three system intents, alternative separation, multi-intent ordering, RU/KK/mixed inputs, malformed output and all specified boundary groups.
- Batch evaluation calls the production `RouterService` for all 104 cases, writes `{id:[ordered IDs]}`, invokes unchanged `evaluate.py`, and saves stdout plus diagnostic error/trace reports. It reports overall, language/type, primary/full match and multi-intent recall.
- Dialogue tests replay all 10 annotated dialogs. Execution tests cover identifiers, normalization, all eight errors, grounding, and all nine irreversible action paths including duplicates/cancellation.
- UI tests cover customer/supervisor views and microphone/STT/TTS recovery with browser APIs mocked.

## Project Structure

```text
backend/app/{api,dataset,routing,dialogue,execution,grounding,tracing,evaluation,voice}/
backend/tests/
apps/web/src/{features/customer,features/supervisor,api}/
voice_router_dataset/case_2/voice_router_dataset/ # authoritative, unchanged
specs/001-voice-router/                          # design artifacts
```

## Milestones and Exit Criteria

1. **Dataset and skeleton**: project structure, validator, configuration, start procedure. Exit: all cross-references validate and identity appears in traces.
2. **Stateless text router**: full catalog, adapter, schema/repair, system/multi-intent, API, trace/timers. Exit: unseen text completes dynamic pipeline.
3. **Evaluation baseline**: product batch router, prediction map, evaluator, errors, boundary suites. Exit: 104 valid output arrays and unmodified scorer works.
4. **Quality/policy**: benchmark prompt/provider/policy, improve general boundaries/languages. Exit: saved >=80% primary development accuracy before later major work.
5. **Dialogue state**: continuation/switch/suspend/resume and cap. Exit: 10 supplied dialogs replay with expected relevant state.
6. **Controlled execution**: identification/slots/grounding/errors/handoff. Exit: only declared actions and all eight errors tested.
7. **Irreversible safety**: preview/confirmation/idempotency. Exit: explicit consent required and duplicates/non-confirmations execute zero extra actions.
8. **UI**: customer and supervisor views. Exit: required states/trace fields visible without hidden reasoning.
9. **Voice**: browser recording, swappable STT/TTS, equivalent pipeline/recovery/timers. Exit: supported request works through voice and text.
10. **Hardening**: all evaluation/dialogue/boundary/safety/grounding/browser/latency suites. Exit: reproducible evidence for scoped success criteria.

## Risks, Mitigations, and Complexity

| Risk | Mitigation |
|---|---|
| Full prompt harms accuracy/latency | Benchmark first; only introduce observable retrieval when no expected/boundary candidate is lost |
| Output/provider variance | Adapter, native-schema preference, validator, one repair and safe fallback |
| Confidence miscalibration | Versioned policy calibrated by measured outcome |
| RU/KK speech quality | Provider benchmark; transcript/text fallback preserving state |
| Duplicate actions | Preview-bound idempotency key |
| Trace leakage | Masking and purpose-separated in-memory synthetic records |

This modular monolith is the minimum complexity needed for independent routing, safety and testing boundaries. Vector DB, complex RAG, auth, persistent history, streaming voice, scenario editor, microservices, queues, Kubernetes and CRM integrations are deferred.

## Post-Design Constitution Check

**PASS for the synthetic product.** Dataset authority, LLM final routing, boundaries, multi-intent/system intents, context/language, grounded deterministic execution, confirmation/fallback, hidden-input independence, evaluation and latency are all represented in the architecture and tests. Production telemetry/cost governance remains a named release gate.
