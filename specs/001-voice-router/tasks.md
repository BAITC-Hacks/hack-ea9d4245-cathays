---

description: "Dependency-ordered implementation tasks for Voice Router"
---

# Tasks: Voice Router

**Input**: Design documents from `/specs/001-voice-router/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md), [HTTP API contract](contracts/http-api.md)

**Tests**: Tests are required by the specification and Constitution. Implement story tests before their production code and verify they fail for the intended reason first.

**Organization**: Tasks are arranged by user story in priority order. Story phases are independent testable increments once shared foundations are complete; the stated integration dependencies remain intentional.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Different files and no dependency on an incomplete task.
- **[US#]**: User story ownership; omitted for setup, foundational, and cross-cutting work.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the reproducible modular-monolith workspace and local developer workflow.

- [X] T001 Create the planned backend and web directory skeleton in `backend/app/`, `backend/tests/`, and `apps/web/src/`.
- [X] T002 Create the Python 3.12 FastAPI/Pydantic/pytest dependency and tool configuration in `backend/pyproject.toml`.
- [X] T003 [P] Create the React/TypeScript/Vite/Tailwind dependency and tool configuration in `apps/web/package.json`.
- [X] T004 [P] Add backend environment template and typed settings for provider, model, dataset path, and test date override in `backend/.env.example` and `backend/app/settings.py`.
- [X] T005 [P] Add root ignore rules for local environments, browser artifacts, provider credentials, and `artifacts/` in `.gitignore`.
- [X] T006 [P] Create reproducible API/web/evaluation commands and prerequisites in `README.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the shared dataset, schemas, configuration, trace timing, API error, and test infrastructure required by every story.

**⚠️ CRITICAL**: Complete this phase before beginning any user-story implementation.

- [ ] T007 Create immutable Pydantic dataset models for scenario, slot, action, queue, knowledge, mock-backend, and snapshot metadata in `backend/app/dataset/models.py`.
- [X] T008 Implement dataset path resolution and immutable JSON loading from `voice_router_dataset/case_2/voice_router_dataset/` in `backend/app/dataset/repository.py`.
- [X] T009 Implement startup cross-file validation for SC01–SC40, all slot/action/boundary IDs, action errors, and handoff queues in `backend/app/dataset/validator.py`.
- [ ] T010 [P] Create shared runtime schemas for `RoutingResult`, selected/alternative intents, clarification, fallback, handoff, execution state, and public turn response in `backend/app/api/schemas.py`.
- [X] T011 [P] Create monotonic stage timers with `measured|skipped|failed` statuses and interpretable totals in `backend/app/tracing/timers.py`.
- [X] T012 [P] Create redaction helpers for display-safe phone, IIN, policy, claim, and email values in `backend/app/tracing/redaction.py`.
- [ ] T013 Implement the in-memory conversation, trace, and evaluation-run stores with request/turn lookup support in `backend/app/tracing/store.py`.
- [ ] T014 Implement FastAPI application factory, versioned router registration, startup dataset validation, health check, and structured error envelope in `backend/app/main.py` and `backend/app/api/errors.py`.
- [X] T015 [P] Add dataset schema/cross-reference tests asserting 40 scenarios, 43 slots, 31 actions, six queues, valid `use_instead`, and no unresolved references in `backend/tests/contract/test_dataset_validator.py`.
- [ ] T016 [P] Add timer/redaction/store unit tests in `backend/tests/unit/test_timers.py`, `backend/tests/unit/test_redaction.py`, and `backend/tests/unit/test_trace_store.py`.
- [ ] T017 Add API application/startup/error-envelope contract tests in `backend/tests/contract/test_app_contract.py`.

**Checkpoint**: The application fails closed on invalid dataset contracts, starts reproducibly with the authoritative snapshot, and offers shared schemas/traces for story work.

---

## Phase 3: User Story 1 — Route a Natural-Language Request (Priority: P1) 🎯 MVP

**Goal**: Route an unseen RU/KK/mixed text request dynamically against all scenarios/system intents, return a validated structured decision, and record router latency/trace.

**Independent Test**: Send unseen single- and multi-intent text through `POST /v1/conversations/{id}/turns`; verify eligible IDs, alternatives/uncertainty/reasons, language/slots/status fields, no action for system results, and a trace with router latency.

### Tests for User Story 1

- [ ] T018 [P] [US1] Add prompt-builder tests proving every catalog card includes description, `not_this_if`, `use_instead`, priority, relevant state, and no dev expected labels in `backend/tests/unit/test_prompt_builder.py`.
- [ ] T019 [P] [US1] Add routing schema/validator tests for malformed JSON, unknown IDs, duplicate IDs, selected-versus-alternative overlap, invalid queue/slot/action, system-action rejection, and ordered multi-intent rules in `backend/tests/contract/test_routing_validator.py`.
- [ ] T020 [P] [US1] Add boundary tests for SC01/SC02, SC17/SC19, SC25/SC26, SC26/SC30, SC07/SC14, SC08/SC16, SC11/SC12/SC13, SC19/SC35, SC21/SC22, SC23/SC21, SC28/SC35, and SC36/SC37 in `backend/tests/routing/test_scenario_boundaries.py`.
- [ ] T021 [P] [US1] Add RU, KK, mixed-language, system-intent, and ordered multi-intent API integration tests in `backend/tests/integration/test_text_routing.py`.
- [ ] T022 [P] [US1] Add contract tests for `POST /v1/conversations`, `POST /v1/conversations/{id}/turns`, and turn trace response shape in `backend/tests/contract/test_conversation_api.py`.

### Implementation for User Story 1

- [ ] T023 [P] [US1] Implement deterministic text triage for language hinting, safe normalization candidates, urgency signals, and utterance segment metadata in `backend/app/routing/triage.py`.
- [ ] T024 [P] [US1] Implement versioned full-catalog prompt construction with structured relevant-state section in `backend/app/routing/prompt_builder.py`.
- [ ] T025 [P] [US1] Define provider-neutral routing request/raw-decision port and a scripted test adapter in `backend/app/routing/llm_client.py`.
- [ ] T026 [US1] Implement configured provider structured-output adapter with JSON-only fallback in `backend/app/routing/provider_client.py`.
- [ ] T027 [US1] Implement strict raw-decision parsing and catalog/policy validation, including one corrective repair request payload, in `backend/app/routing/validator.py`.
- [ ] T028 [US1] Implement deterministic multi-intent ordering, initial conservative accept/clarify/fallback policy, and no-business-action system intent handling in `backend/app/routing/decision_policy.py`.
- [ ] T029 [US1] Implement `RouterService` to compose triage, prompt, LLM call, validation, repair/fallback, structured result, and routing stage timings in `backend/app/routing/service.py`.
- [ ] T030 [US1] Implement `Conversation`, `Turn`, and initial `DialogueState` creation plus `client_turn_id` deduplication in `backend/app/dialogue/service.py`.
- [ ] T031 [US1] Implement basic supervisor trace construction with selected IDs, reasons, alternatives, slots, decision status, catalog/prompt/policy/model identity, and masked input in `backend/app/tracing/service.py`.
- [ ] T032 [US1] Implement conversation creation, text-turn processing, customer-safe state, and per-turn trace endpoints in `backend/app/api/conversations.py`.
- [ ] T033 [US1] Register conversation endpoints and map domain failures to the HTTP contract in `backend/app/main.py`.

**Checkpoint**: An unseen text request reaches an LLM final semantic decision against the full catalog, returns/records a safe structured result, and supports three distinct system outcomes.

---

## Phase 4: User Story 2 — Continue and Switch Topics with Context (Priority: P2)

**Goal**: Preserve relevant context across up to ten exchanges, distinguish continuation from material topic change, suspend/resume work, and retain state across language changes.

**Independent Test**: Replay supplied annotated dialogs and dedicated continuation/switch/return/language-only cases; verify state/flags/slots are retained and relevant without treating a short reply as isolated intent.

### Tests for User Story 2

- [ ] T034 [P] [US2] Add dialogue-state model tests for the 10-exchange cap, slot provenance/relevance, active/suspended goal transitions, and language history in `backend/tests/unit/test_dialogue_state.py`.
- [ ] T035 [P] [US2] Add continuation, clarification-answer, topic-switch, topic-return, and language-only-switch router integration tests in `backend/tests/integration/test_dialogue_routing.py`.
- [ ] T036 [P] [US2] Add parameterized replay tests for all 10 `dialogs_sample.json` conversations in `backend/tests/integration/test_dialog_samples.py`.

### Implementation for User Story 2

- [ ] T037 [US2] Expand state models with active goal, LIFO suspended goals, language history, unresolved goals, relevant slots, identity refs, and clarification state in `backend/app/dialogue/models.py`.
- [ ] T038 [US2] Implement relevance-filtered router context, continuation/topic-change detection, safe slot merging, suspension, resumption, and 10-exchange summary/handoff behavior in `backend/app/dialogue/service.py`.
- [ ] T039 [US2] Integrate updated dialogue state into turn orchestration and trace continuation/topic-change/active/suspended fields in `backend/app/api/conversations.py` and `backend/app/tracing/service.py`.

**Checkpoint**: Context-dependent short replies route using prior turns; switches are visible, resumable, and unaffected by language-only changes.

---

## Phase 5: User Story 3 — Resolve Ambiguity Safely (Priority: P3)

**Goal**: Make ambiguity, invalid model output, fallback, direct operator requests, and handoffs safely visible and recoverable.

**Independent Test**: Exercise materially plausible alternatives, unanswered/answered clarification, two failed attempts, malformed model output, unavailable catalog, and direct operator request; assert question/alternatives/handoff package and zero unsupported actions.

### Tests for User Story 3

- [ ] T040 [P] [US3] Add decision-policy calibration fixture and accept/clarify/retry/fallback/handoff unit tests in `backend/tests/unit/test_decision_policy.py`.
- [ ] T041 [P] [US3] Add malformed-output repair-then-safe-fallback and unavailable-catalog fail-closed tests in `backend/tests/integration/test_routing_failures.py`.
- [ ] T042 [P] [US3] Add ambiguous clarification, direct-human request, repeat-unresolved, and handoff-package API tests in `backend/tests/integration/test_clarification_handoff.py`.

### Implementation for User Story 3

- [ ] T043 [US3] Implement versioned uncertainty-policy configuration, outcome counters, leading-alternative selection, and experimental calibration report inputs in `backend/app/routing/policy_config.py`.
- [ ] T044 [US3] Extend decision policy with one concise two-option clarification, repeat-attempt handling, direct-operator detection after LLM routing, safe fallback, and validated queue selection in `backend/app/routing/decision_policy.py`.
- [ ] T045 [US3] Implement minimal handoff package generation from masked relevant transcript, scenario history, slots, failure reason, and summary in `backend/app/dialogue/handoff.py`.
- [ ] T046 [US3] Add clarification/fallback/handoff state and policy evidence to traces and public turn responses in `backend/app/tracing/service.py` and `backend/app/api/schemas.py`.

**Checkpoint**: Uncertainty does not become a silent route; all technical/model failures and operator requests follow explicit traceable safe paths.

---

## Phase 6: User Story 4 — Execute a Controlled Scenario (Priority: P4)

**Goal**: Execute only data-declared mock operations with identification, slot collection/normalization, grounded responses, error mapping, and safe irreversible confirmation.

**Independent Test**: Run representative information/action scenarios against mock data; verify identity reuse, missing-slot prompts, all action errors, grounding, preview/confirmation, action eligibility, and idempotency.

### Tests for User Story 4

- [ ] T047 [P] [US4] Add slot normalization/validation tests for phone, IIN, policy/claim IDs, enums, numbers, spoken values, and snapshot-relative dates in `backend/tests/unit/test_slots.py`.
- [ ] T048 [P] [US4] Add identification tests for phone, IIN, policy and claim lookup plus reuse/conflicting identifiers in `backend/tests/integration/test_identification.py`.
- [ ] T049 [P] [US4] Add action contract tests for declared inputs/outputs, all eight dataset errors, queue behavior, unknown action rejection, and generated-ID collision protection in `backend/tests/contract/test_actions.py`.
- [ ] T050 [P] [US4] Add action-state-machine tests for preview, explicit affirmation, ambiguity/silence/cancel, duplicate retry, and all nine irreversible actions in `backend/tests/integration/test_irreversible_actions.py`.
- [ ] T051 [P] [US4] Add grounding audit tests rejecting company/customer facts absent from knowledge, backend, or validated action result in `backend/tests/unit/test_grounded_responder.py`.

### Implementation for User Story 4

- [ ] T052 [P] [US4] Implement typed slot extraction candidates, normalization, `slots.json` validation, and snapshot-date resolver in `backend/app/execution/slots.py`.
- [ ] T053 [P] [US4] Implement synthetic customer identification and safe profile/identifier conflict resolution over the mock backend in `backend/app/execution/identity.py`.
- [ ] T054 [P] [US4] Implement dataset-constrained knowledge/backend access and mock action handlers in `backend/app/execution/actions.py`.
- [ ] T055 [US4] Implement action eligibility, required-identification/slot collection, declared error mapping, and generated-ID uniqueness checks in `backend/app/execution/service.py`.
- [ ] T056 [US4] Implement `READY → PREVIEW → WAITING_CONFIRMATION → EXECUTING → COMPLETED` plus cancellation/failure/handoff action state machine and preview-bound idempotency in `backend/app/execution/state_machine.py`.
- [ ] T057 [US4] Implement evidence-bounded response composition that can use only catalog responses, knowledge, mock records, and validated action outputs in `backend/app/grounding/responder.py`.
- [ ] T058 [US4] Integrate deterministic execution and grounded response after accepted business routing, while blocking all system/fallback actions, in `backend/app/dialogue/orchestrator.py`.
- [ ] T059 [US4] Extend trace/public schemas with identity-safe slots, action mode/result/error, evidence IDs, and handoff state in `backend/app/tracing/service.py` and `backend/app/api/schemas.py`.

**Checkpoint**: Scenario actions are deterministic, dataset-bounded and grounded; irreversible actions have preview, affirmative confirmation and idempotency evidence.

---

## Phase 7: User Story 5 — Hold a Voice Conversation (Priority: P5)

**Goal**: Add browser microphone, transcript, STT/TTS adapters and recoverable voice failure handling while retaining the exact text turn pipeline.

**Independent Test**: Complete one supported request by text and audio; assert equivalent routing/state/execution/trace behavior, displayed transcript/audio state, and recoverable denied/empty/STT/TTS failures.

### Tests for User Story 5

- [ ] T060 [P] [US5] Add provider-port tests for STT/TTS success, empty audio, unavailable provider, and failed synthesis in `backend/tests/unit/test_voice_adapters.py`.
- [ ] T061 [P] [US5] Add audio-turn API integration tests proving delegation to normal orchestrator and stage timing status in `backend/tests/integration/test_audio_turns.py`.
- [ ] T062 [P] [US5] Add browser customer-flow tests for microphone permission, listening/processing/transcript/playback state, text fallback, and voice failures in `apps/web/src/features/customer/CustomerConversation.spec.tsx`.

### Implementation for User Story 5

- [ ] T063 [P] [US5] Define swappable STT/TTS ports, provider settings, and deterministic test adapters in `backend/app/voice/providers.py`.
- [ ] T064 [US5] Implement completed-recording transcription/synthesis adapters, recoverable error mapping, and STT/TTS stage measurements in `backend/app/voice/service.py`.
- [ ] T065 [US5] Implement deferred audio-turn endpoint that invokes the existing turn orchestrator and records client capture timestamps in `backend/app/api/audio_turns.py`.
- [ ] T066 [US5] Register audio route and enforce same conversation/turn deduplication/state behavior in `backend/app/main.py`.
- [ ] T067 [P] [US5] Implement typed browser API client including completed audio upload and audio response handling in `apps/web/src/api/client.ts`.
- [ ] T068 [US5] Implement microphone recording, permission/error states, visible transcript, processing indicator, TTS playback, and text fallback in `apps/web/src/features/customer/CustomerConversation.tsx`.

**Checkpoint**: Voice is a thin adapter around the existing text pipeline; all failures preserve valid conversation state and offer retry/text fallback.

---

## Phase 8: User Story 6 — Investigate Every Routing Decision (Priority: P6)

**Goal**: Give supervisors an understandable, masked per-turn trace with decision, state, outcome, configuration, and latency details without hidden reasoning.

**Independent Test**: Process success, switch, clarification, fallback, handoff, action and voice turns; verify every applicable trace field/status, trace-to-turn linkage, config versions, expected/predicted comparison fields, and no chain-of-thought.

### Tests for User Story 6

- [ ] T069 [P] [US6] Add complete trace contract tests covering required routing, dialogue, action, config, and skipped/failed latency fields in `backend/tests/contract/test_supervisor_trace.py`.
- [ ] T070 [P] [US6] Add tests ensuring trace masking and absence of provider reasoning/raw sensitive values in `backend/tests/unit/test_trace_privacy.py`.
- [ ] T071 [P] [US6] Add supervisor trace-view rendering and forbidden-field tests in `apps/web/src/features/supervisor/SupervisorTrace.spec.tsx`.

### Implementation for User Story 6

- [ ] T072 [US6] Complete `SupervisorTrace` projection, configuration identity, per-stage outcome status, and expected/predicted diagnostic fields in `backend/app/tracing/service.py`.
- [ ] T073 [US6] Implement trace retrieval filtering and trace-not-found/error handling in `backend/app/api/conversations.py`.
- [ ] T074 [P] [US6] Implement supervisor API trace/query types in `apps/web/src/api/supervisor.ts`.
- [ ] T075 [US6] Implement trace panel for selected scenarios, alternatives, uncertainty, slots, state, action/handoff/fallback, metadata and latency in `apps/web/src/features/supervisor/SupervisorTrace.tsx`.
- [ ] T076 [US6] Compose customer and supervisor application routes without exposing supervisor-only fields in `apps/web/src/App.tsx`.

**Checkpoint**: A supervisor can investigate any turn using concise structured evidence, but never sees model chain-of-thought.

---

## Phase 9: User Story 7 — Evaluate Routing Reproducibly (Priority: P7)

**Goal**: Evaluate the same dynamic product router against all 104 development cases and inspect aggregate/sliced results and individual errors.

**Independent Test**: Run evaluation once with a controlled adapter/profile; inspect valid prediction JSON, unchanged evaluator output, overall/language/type metrics, multi-intent recall, individual errors, and confusion grouping.

### Tests for User Story 7

- [ ] T077 [P] [US7] Add prediction-projection tests for ordered IDs, all system intents, missing results, and separation from richer routing metadata in `backend/tests/unit/test_prediction_projection.py`.
- [ ] T078 [P] [US7] Add evaluation runner integration test that invokes unchanged `evaluate.py` against the checked-in development data in `backend/tests/integration/test_evaluation_runner.py`.
- [ ] T079 [P] [US7] Add evaluation API contract tests for start/status/result/error/artifact response shapes in `backend/tests/contract/test_evaluation_api.py`.
- [ ] T080 [P] [US7] Add evaluation result/error inspector UI tests in `apps/web/src/features/supervisor/EvaluationResults.spec.tsx`.

### Implementation for User Story 7

- [ ] T081 [US7] Implement evaluator prediction projection from product `RoutingResult` to ordered `{utterance_id: [scenario_id]}` in `backend/app/evaluation/projection.py`.
- [ ] T082 [US7] Implement batch execution through `RouterService`, artifact isolation, unchanged `evaluate.py` invocation, and configuration/snapshot recording in `backend/app/evaluation/runner.py`.
- [ ] T083 [US7] Implement enriched error report with input ID, expected/predicted IDs, language/type, alternatives, trace ID, and confusion group in `backend/app/evaluation/reporting.py`.
- [ ] T084 [US7] Implement evaluation start/status endpoints backed by the evaluation-run store in `backend/app/api/evaluations.py`.
- [ ] T085 [US7] Register evaluation API and artifact-safe response mapping in `backend/app/main.py`.
- [ ] T086 [P] [US7] Implement typed evaluation API client in `apps/web/src/api/evaluations.ts`.
- [ ] T087 [US7] Implement supervisor evaluation metrics, language/type slices, individual error list, and confusion display in `apps/web/src/features/supervisor/EvaluationResults.tsx`.

**Checkpoint**: The reference evaluator scores the product router's complete prediction map without adaptation, and every regression is inspectable without runtime label memorization.

---

## Phase 10: Polish and Cross-Cutting Concerns

**Purpose**: Complete reproducibility, quality evidence, performance visibility, and final requirement coverage.

- [ ] T088 [P] Add benchmark harness/profile matrix for full-catalog versus candidate retrieval, provider/model, prompt version, valid-output rate, accuracy, and p50/p95 latency in `backend/app/evaluation/benchmark.py`.
- [ ] T089 [P] Add documented manual hidden-input sanity cases that are not copied from labeled utterances in `backend/tests/routing/test_unseen_sanity.py`.
- [ ] T090 Add end-to-end quickstart validation script that runs dataset, API, web, router, evaluation, dialogue, action, and voice checks in `scripts/validate-quickstart.ps1`.
- [ ] T091 Update the reproducible run, provider benchmark, policy-calibration, privacy-mask, and artifact-inspection procedures in `README.md` and `specs/001-voice-router/quickstart.md`.
- [ ] T092 Run the full required suite and record dataset/config identities, evaluator output, dialogue/action/voice evidence, latency summary, and outstanding production governance gates in `artifacts/validation/README.md`.

---

## Dependencies and Execution Order

### Phase dependencies

```text
Setup → Foundational → US1 (MVP) → US7 baseline → US3 quality/policy
                                      │
                    US2 state ───────┼→ US4 execution → US5 voice
                                      └→ US6 supervisor UI
All desired story phases → Polish
```

- Setup (T001–T006) has no dependencies.
- Foundational work (T007–T017) depends on setup and blocks every story.
- US1 depends on foundation and is the minimum shippable text-routing MVP.
- US2 depends on US1's turn orchestration; US3 depends on US1 validation/policy; US7 depends on US1 router and should establish the baseline before policy quality tuning.
- US4 depends on US1 acceptance plus US2 state and US3 fallback/handoff behavior.
- US5 depends on the normal orchestrator and US4 for final equivalent action behavior.
- US6 consumes tracing from US1–US5; its UI can begin after US1 trace API but is completed after all trace-producing behavior exists.
- Polish depends on all intended story phases.

### Parallel opportunities

- In setup: T003–T006 can proceed while T001–T002 establish project roots.
- In foundation: T010–T012 and T015–T016 are separate files once T007 model names are stable.
- In US1: T018–T022 and T023–T025 are parallel; T026–T033 then follow pipeline dependencies.
- Each later story’s `[P]` test tasks and isolated modules can run concurrently after its prerequisite models/contracts are agreed.
- US2, US3, and US7 can be staffed in parallel after US1, but merge US7 baseline before accepting calibrated US3 policy changes.

## Parallel Example: User Story 4

```text
After the foundational execution interfaces are agreed, run in parallel:
- T047 slot tests, T048 identification tests, T049 action contract tests,
  T050 irreversible-action tests, and T051 grounding tests.
- T052 slots, T053 identity, and T054 mock actions.

Then sequence T055 → T056 → T057 → T058 → T059.
```

## Implementation Strategy

### MVP first

1. Complete T001–T017.
2. Complete US1 through T033 and validate dynamic text routing/trace/system intent behavior.
3. Complete US7 T077–T087 early enough to record the required 104-case baseline.
4. Stop to inspect errors and validate the >=80% primary-accuracy readiness target before adding major product layers.

### Incremental delivery

1. Add US2 and US3 to make routing stateful and safely uncertain.
2. Add US4 for dataset-bounded execution and irreversible safety.
3. Add US6 customer/supervisor investigation surfaces, then US5 voice on the already proven turn pipeline.
4. Finish benchmark, quickstart, regression and governance evidence in T088–T092.

## Task Validation

- **Total tasks**: 92.
- **Per-story tasks**: US1 16; US2 6; US3 7; US4 13; US5 9; US6 8; US7 11.
- Every task uses the required checkbox, sequential ID, optional `[P]`, required story label in story phases, and an exact file path.
- Independent test criteria are stated for every user-story phase; test tasks are explicitly included because the specification and Constitution require them.

---

## Phase 11: Convergence

**Purpose**: Close implementation gaps found by convergence review after the initial partial implementation pass.

- [ ] T093 CRITICAL Replace the provider's ad hoc JSON response path with strict provider-native schema support, one validation-error repair attempt, explicit unavailable-provider fallback classification, and tests in `backend/app/routing/provider_client.py`, `backend/app/routing/service.py`, and `backend/tests/integration/test_routing_failures.py` per Constitution II and FR-001/FR-011 (partial).
- [ ] T094 CRITICAL Implement typed slot normalization, supported identifier lookup, declared mock action handlers, all eight `actions.json` error behaviors, and generated-ID collision checks in `backend/app/execution/slots.py`, `backend/app/execution/identity.py`, `backend/app/execution/actions.py`, and `backend/tests/contract/test_actions.py` per Constitution IX and FR-025/FR-048–FR-054 (missing).
- [ ] T095 CRITICAL Implement the irreversible-action terminal state machine: preview-bound explicit affirmative confirmation, cancellation/ambiguous-answer rejection, action-result persistence, and idempotent duplicate handling in `backend/app/execution/state_machine.py` and `backend/tests/integration/test_irreversible_actions.py` per Constitution X and FR-027/FR-028 (missing).
- [ ] T096 Add evidence-bounded response selection/composition and prevent route-ID placeholder replies from reaching customer output in `backend/app/grounding/responder.py`, `backend/app/dialogue/orchestrator.py`, and `backend/tests/unit/test_grounded_responder.py` per Constitution XI and FR-026/SC-020 (missing).
- [ ] T097 Complete typed runtime/API schemas, application-factory/router separation, trace/evaluation stores, and the documented structured error envelope in `backend/app/api/schemas.py`, `backend/app/api/errors.py`, `backend/app/api/conversations.py`, `backend/app/tracing/store.py`, and `backend/tests/contract/test_app_contract.py` per plan technical context and FR-045 (partial).
- [ ] T098 Expand dialogue state to retain turns, slot provenance, identity references, unresolved/suspended goal metadata, clarification attempts, resumption, and 10-exchange safe conclusion; trace these fields in `backend/app/dialogue/models.py`, `backend/app/dialogue/service.py`, and `backend/tests/integration/test_dialog_samples.py` per Constitution VI and FR-012–FR-018 (partial).
- [ ] T099 Complete supervisor trace masking for phone/IIN/policy/claim/email, add active/suspended/action/configuration fields and every applicable measured/skipped/failed latency stage in `backend/app/tracing/redaction.py`, `backend/app/tracing/service.py`, and `backend/tests/contract/test_supervisor_trace.py` per Constitution VIII/XV and FR-034–FR-037/FR-043 (partial).
- [ ] T100 Implement evaluator projection, product-router batch runs, artifact isolation, unmodified `evaluate.py` execution, configuration/snapshot evidence, language/type/confusion reports, and evaluation HTTP endpoints in `backend/app/evaluation/`, `backend/app/api/evaluations.py`, and `backend/tests/integration/test_evaluation_runner.py` per Constitution XIII and FR-038–FR-040/SC-001–SC-003 (missing).
- [ ] T101 Add all documented scenario-boundary, RU/KK/mixed-language, system-intent, multi-intent, malformed-output, and conversation API tests in `backend/tests/routing/`, `backend/tests/integration/`, and `backend/tests/contract/` per FR-006–FR-024 and Constitution III–VII (missing).
- [ ] T102 Implement STT/TTS provider ports, completed-recording audio turn endpoint, recoverable voice error behavior, stage timings, browser microphone/transcript/playback controls, and voice tests in `backend/app/voice/`, `backend/app/api/audio_turns.py`, `apps/web/src/features/customer/CustomerConversation.tsx`, and associated tests per FR-029–FR-035/SC-010–SC-011 (missing).
- [ ] T103 Add the supervisor evaluation result client/view with language/type metrics, errors, alternatives and confusion groups in `apps/web/src/api/evaluations.ts`, `apps/web/src/features/supervisor/EvaluationResults.tsx`, and `apps/web/src/features/supervisor/EvaluationResults.spec.tsx` per FR-039 and User Story 7 (missing).
- [ ] T104 Run the full backend and web suite, quickstart flow, evaluator, dialogue/action/voice evidence collection, and record outstanding production telemetry/cost governance gates in `scripts/validate-quickstart.ps1` and `artifacts/validation/README.md` per SC-004–SC-020 and plan: milestones (missing).
