# Feature Specification: Voice Router

**Feature Branch**: Not created (no `before_specify` hook configured)

**Created**: 2026-09-23

**Status**: Draft

**Input**: User description: "Create a complete Voice Router product specification using the
checked-in Saqta Insurance dataset and reference evaluator as the authoritative contract."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Route a Natural-Language Request (Priority: P1)

As a customer, I can enter an unfamiliar Russian, Kazakh, or mixed-language message in natural
language and be routed to the matching insurance scenario without knowing scenario names or
memorizing sample phrases. After the turn, a supervisor can see the structured decision and its
routing latency.

**Why this priority**: Accurate LLM routing is the product's primary value and forms the first usable
milestone before voice and full scenario execution are added.

**Independent Test**: Enter unseen text requests representing scenarios from the supplied catalog
and verify that each result names an eligible scenario, exposes uncertainty and alternatives,
provides a short structured rationale, and appears in the trace.

**Acceptance Scenarios**:

1. **Given** the 40-scenario catalog is available, **When** a customer submits an unseen Russian
   request matching one scenario, **Then** an LLM selects an eligible scenario and the trace records
   the required decision fields and routing latency.
2. **Given** the same catalog, **When** a customer submits a Kazakh or mixed Russian/Kazakh request,
   **Then** the request follows the same routing process and language choice alone does not trigger
   fallback or a different scenario.
3. **Given** a request is similar to examples but crosses a documented scenario boundary, **When**
   routing completes, **Then** the selected scenario reflects purpose and boundary rules rather than
   keyword overlap alone.
4. **Given** a request contains more than one distinct supported goal, **When** routing completes,
   **Then** the result identifies a primary scenario for current handling and preserves other
   applicable scenarios for subsequent handling.
5. **Given** a request is outside Saqta's services, cannot be determined reliably, or ends the
   conversation, **When** routing completes, **Then** the router returns `SYS_OUT_OF_SCOPE`,
   `SYS_UNCLEAR`, or `SYS_GOODBYE` respectively instead of inventing a business scenario.

---

### User Story 2 - Continue and Switch Topics with Context (Priority: P2)

As a customer, I can clarify an existing request, switch to another task, and later return to an
interrupted task without repeating information that remains relevant.

**Why this priority**: Context awareness and dynamic switching are the defining improvements over a
one-turn intent classifier.

**Independent Test**: Run the supplied annotated dialogues and verify continuation, topic switch,
scenario history, retained parameters, and return-to-topic behaviour against their annotations.

**Acceptance Scenarios**:

1. **Given** an active scenario and information already supplied by the customer, **When** the next
   message is a clarification or continuation, **Then** the router uses relevant prior context and
   does not classify the message as an unrelated new request.
2. **Given** an active payment or policy scenario, **When** the customer asks in another language to
   update contact information, **Then** the router records a topic change and selects the contact
   information scenario for the new goal.
3. **Given** a previous scenario was suspended by a topic switch, **When** the intervening task ends
   or the customer refers back to the earlier goal, **Then** the system can resume it with relevant
   collected information intact.
4. **Given** a language switch without a semantic topic change, **When** the next turn is processed,
   **Then** the active scenario and relevant conversation state remain unchanged.

---

### User Story 3 - Resolve Ambiguity Safely (Priority: P3)

As a customer with an ambiguous or incomplete request, I receive one useful clarification question
instead of being silently sent into a possibly incorrect scenario. If the system still cannot
continue safely, I can be transferred to a human without repeating the conversation.

**Why this priority**: Explicit uncertainty prevents high-cost misrouting while keeping the
experience recoverable.

**Independent Test**: Submit ambiguous, incomplete, conflicting, out-of-scope, and invalid routing
cases and verify uncertainty, alternatives, clarification, fallback, and handoff behaviour.

**Acceptance Scenarios**:

1. **Given** two or more scenarios remain materially plausible, **When** the available evidence is
   insufficient to choose reliably, **Then** the result exposes alternatives and uncertainty and the
   assistant asks a concise clarification question.
2. **Given** the customer answers the clarification, **When** the answer resolves the boundary,
   **Then** the router chooses the supported scenario using both the answer and prior context.
3. **Given** the request remains unsafe to route or a routing failure persists, **When** fallback is
   invoked, **Then** the system offers an appropriate human handoff and carries forward a concise
   context summary.
4. **Given** the customer explicitly requests a human operator, **When** the turn is processed,
   **Then** the handoff path is selected without requiring the customer to fail clarification first.

---

### User Story 4 - Execute a Controlled Scenario (Priority: P4)

As a customer, I can receive information and complete supported mock insurance tasks after routing,
while consequential actions remain constrained by the selected scenario and require my explicit
confirmation.

**Why this priority**: Routing delivers customer value only when the selected scenario can respond
or act without inventing company facts or uncontrolled business operations.

**Independent Test**: Select representative informational and action scenarios, exercise them using
the supplied knowledge and mock customer data, and verify allowed actions, required information,
confirmation, errors, and handoff.

**Acceptance Scenarios**:

1. **Given** a selected informational scenario, **When** the assistant responds, **Then** every
   company-specific fact is supported by the supplied knowledge data.
2. **Given** a selected scenario requires customer information, **When** information is missing,
   **Then** the assistant collects only the required information and reuses relevant values already
   supplied in the conversation.
3. **Given** a consequential or irreversible action is ready, **When** the customer has not yet
   confirmed it, **Then** the system previews the action and does not execute it.
4. **Given** a requested operation is unsupported or fails safely, **When** execution cannot
   continue, **Then** the system follows the scenario's fallback or escalation path.
5. **Given** a scenario requires identification, **When** the customer supplies a phone, IIN,
   policy number, or claim number accepted by the dataset contract, **Then** the matching synthetic
   profile is used and known valid information is not requested again without a validation or
   confirmation reason.
6. **Given** an action produces a dataset-defined error, **When** the result is handled, **Then** the
   assistant follows the corresponding retry, explanation, alternative, or handoff behavior from
   `actions.json`.

---

### User Story 5 - Hold a Voice Conversation (Priority: P5)

As a customer, I can speak through a browser microphone, see the transcript, and hear the
assistant's response while retaining text input as a fallback.

**Why this priority**: Voice interaction is required for the final product, but routing correctness
must be established before speech quality is optimized.

**Independent Test**: Complete the same supported request once through microphone input and once
through text input, and verify that both paths share routing, context, execution, trace, and response
behaviour.

**Acceptance Scenarios**:

1. **Given** microphone use is available and permitted, **When** the customer records a Russian,
   Kazakh, or mixed-language request, **Then** the interface shows listening and processing states,
   displays the transcript, routes it, and plays the assistant response.
2. **Given** microphone input is unavailable, denied, or unsuitable, **When** the customer uses text
   input, **Then** the request enters the same pipeline from routing onward.
3. **Given** a speech-processing failure, **When** the turn cannot be completed, **Then** the customer
   receives a recoverable error and can retry or use text without losing conversation state.

---

### User Story 6 - Investigate Every Routing Decision (Priority: P6)

As a supervisor, I can inspect each customer turn and understand what was selected, what alternatives
were considered, whether the topic changed, how uncertainty was handled, and where processing time
was spent without seeing hidden model reasoning.

**Why this priority**: Observable decisions are required to debug routing quality, evaluate errors,
and distinguish model uncertainty from pipeline failures.

**Independent Test**: Process turns covering success, topic switch, clarification, fallback, and
escalation, then verify all required fields are visible and linked to the correct dialogue step.

**Acceptance Scenarios**:

1. **Given** any completed customer turn, **When** the supervisor opens its trace, **Then** all
   required decision, state, outcome, and latency fields are present and understandable.
2. **Given** a routing error, **When** a supervisor reviews the trace, **Then** the expected and
   predicted scenarios and relevant structured decision signals can be compared without internal
   development tools.
3. **Given** internal model reasoning is unavailable or intentionally withheld, **When** a trace is
   displayed, **Then** it uses concise structured rationale and metadata rather than hidden
   chain-of-thought.

---

### User Story 7 - Evaluate Routing Reproducibly (Priority: P7)

As a developer, I can evaluate dynamic router predictions against the supplied labeled data and
inspect results by language, request type, and commonly confused scenarios before expanding the
product beyond its routing core.

**Why this priority**: Repeatable measurement protects the primary quality goal and prevents a
polished voice interface from hiding routing regressions.

**Independent Test**: Run all supplied development utterances through the same router used by the
product, compare expected and predicted scenario sequences, and review aggregate and sliced results
plus individual errors.

**Acceptance Scenarios**:

1. **Given** the supplied labeled development utterances, **When** automated evaluation runs,
   **Then** it reports overall primary accuracy, full match, multi-intent recall, and results split by
   available language and request-type labels.
2. **Given** incorrect predictions, **When** evaluation completes, **Then** each error exposes the
   input identifier, expected scenario sequence, predicted sequence, and confusion grouping.
3. **Given** hidden or previously unseen input, **When** it is submitted, **Then** it is processed
   dynamically through the catalog and no test-specific mapping determines the result.

### Edge Cases

- A short reply such as "да", "иә", a date, a number, or "там же" is meaningful only in the
  preceding scenario and must not be routed as an isolated intent.
- One utterance contains several supported goals, including an urgent goal and a normal goal.
- The customer switches language mid-sentence without changing topic, or changes topic without
  switching language.
- The customer returns to a suspended scenario after one or more intervening turns.
- The transcript is empty, truncated, low-confidence, malformed, or contains only noise.
- The LLM returns malformed structure, an unknown scenario ID, an ineligible action, or no decision.
- The scenario catalog, knowledge data, or mock backend is missing, invalid, or temporarily
  unavailable.
- A catalog update changes a boundary or adds a scenario while historic traces refer to an older
  catalog version.
- The customer requests a product outside the fictional insurer's scope, says goodbye, or directly
  requests an operator.
- A consequential action is requested and the customer's response is not an explicit confirmation.
- A backend lookup returns no customer, policy, claim, or payment record.
- A conversation reaches the supported limit of 10 customer/assistant exchanges while a task is
  still active.
- A latency stage is skipped, fails, or has no timing value; total latency must remain interpretable.
- Multiple turns arrive unexpectedly or duplicate a prior turn; state must not be corrupted or an
  irreversible action repeated.
- A relative date would differ between the machine clock and the dataset snapshot date; simulation
  behaviour must use `2026-10-01` unless an explicit test override is recorded.
- A customer identifier is valid in form but absent from the mock backend, or several identifiers
  conflict with one another.

## Requirements *(mandatory)*

### Authoritative Dataset Contract

The checked-in dataset version `1.0`, with snapshot date `2026-10-01`, is the source of truth for
observable product and evaluation behaviour. The product must preserve these contracts:

| Artifact | Verified contract |
|---|---|
| `scenarios.json` | 40 business scenarios (`SC01`–`SC40`), three separate system intents, scenario boundaries, priority, identification, slots, actions, confirmation, handoff, examples, and responses |
| `slots.json` | 43 slot definitions with typed values, validation patterns or allowed values, and Russian/Kazakh prompts |
| `actions.json` | 31 actions, eight error codes, nine irreversible actions, and six valid handoff queues |
| `knowledge_base.json` | Authoritative fictional company, office, product, clinic, claim, payment, cancellation, bonus-malus, application-help, fraud, document, and complaint facts |
| `mock_backend.json` | 11 synthetic clients, 11 policies, four claims, and two payments used for identification and action results |
| `dialogs_sample.json` | 10 annotated conversations covering context carry/return, scenario and topic switching, multi-intent, language switching, mixed speech, clarification, handoff, and confirmation |
| `dev_utterances.json` | 104 labeled cases: 84 single, 13 multi-intent, four out-of-scope, and three unclear; 52 Russian, 45 Kazakh, and seven mixed-language |
| `evaluate.py` | Prediction-map input, primary accuracy, set-based full match, multi-intent recall, language/type breakdowns, missing-prediction errors, and inspectable mismatch output |

The development set's 13 verified multi-intent sequences are:

| Primary | Secondary |
|---|---|
| `SC27` | `SC04` |
| `SC25` | `SC29` |
| `SC13` | `SC20` |
| `SC03` | `SC01` |
| `SC26` | `SC29` |
| `SC06` | `SC31` |
| `SC19` | `SC35` |
| `SC21` | `SC22` |
| `SC26` | `SC25` |
| `SC14` | `SC18` |
| `SC07` | `SC08` |
| `SC28` | `SC29` |
| `SC06` | `SC33` |

Boundary acceptance tests must include at least the following neighboring scenario distinctions:

- `SC01` quote versus `SC02` purchase;
- `SC17` claim status versus `SC19` claim dispute;
- `SC25` policy validity versus `SC26` document resend;
- `SC26` document resend versus `SC30` charged but policy not issued;
- `SC07` home insurance consultation versus `SC14` property damage claim;
- `SC08` accident insurance consultation versus `SC16` accident injury claim;
- `SC11` current road accident versus `SC12` or `SC13` post-accident claim;
- `SC19` claim dispute versus `SC35` service complaint;
- `SC21` doctor appointment versus `SC22` coverage check;
- `SC23` clinic list versus `SC21` doctor appointment;
- `SC28` policy cancellation versus `SC35` service complaint; and
- `SC36` callback versus `SC37` immediate human operator.

### Observable Routing Contract

Each routing result must provide an ordered list of selected scenario or system-intent records. The
first record is primary. Each selected record includes its ID, uncertainty signal, and concise
structured reason. The result also includes alternatives, detected language, extracted normalized
slots, continuation status, topic-change status, and clarification status. Fallback and handoff
status must be present when applicable.

For evaluator compatibility, development predictions must be exportable as a JSON object that maps
each utterance ID to an ordered array of predicted IDs. The first ID determines primary accuracy;
full match compares predicted and expected sets; multi-intent recall measures the proportion of
expected IDs recovered for multi-intent records. The richer interactive routing result must remain
separate from this evaluator projection so diagnostic metadata does not alter scoring.

### Functional Requirements

#### Routing and Catalog

- **FR-001**: The final scenario-routing decision MUST be made by an LLM using the customer message,
  relevant conversation context, and the available scenario catalog.
- **FR-002**: A traditional encoder-based intent classifier MUST NOT make the final routing decision.
- **FR-003**: Keywords, hardcoded mappings, prerecorded conversations, evaluation answers, and
  lookup tables derived from labeled or hidden utterances MUST NOT determine the final decision.
- **FR-004**: Candidate retrieval MAY reduce the set presented to the LLM, but the LLM MUST make the
  final selection from eligible catalog entries. `fast_path_eligible` MAY guide optimization after
  an LLM routing decision but MUST NOT authorize a non-LLM final semantic selection.
- **FR-005**: The system MUST load and route against all 40 business scenarios supplied by the
  starter-kit catalog rather than a demo-only subset.
- **FR-006**: `SYS_OUT_OF_SCOPE`, `SYS_UNCLEAR`, and `SYS_GOODBYE` MUST remain distinguishable from
  the 40 business scenarios. Out-of-scope requests MUST receive a scope explanation; unclear
  requests MUST receive one concise question offering the two leading options; goodbye MUST close
  the conversation. None of these outcomes may authorize a business action.
- **FR-007**: Routing MUST consider each scenario's purpose, `not_this_if` conditions and
  `use_instead` targets, priority, parameters, allowed actions, identification needs, handoff rules,
  and multilingual examples when present.
- **FR-008**: The scenario catalog MUST be replaceable or extensible without rewriting the routing
  behaviour around individual demo utterances; evaluation MUST continue to report against the
  original 40-scenario set.
- **FR-009**: For each customer turn, the router MUST produce a validated structured result containing
  an ordered list of selected IDs with uncertainty and concise reasons, alternative candidates,
  detected language, normalized slots, continuation status, topic-change status, clarification
  status, and fallback/escalation status.
- **FR-010**: When one message contains multiple supported goals, the system MUST identify the
  applicable scenario sequence, place a required urgent scenario first, otherwise preserve semantic
  order of appearance, designate the first item as primary, and retain every later goal.
- **FR-011**: Unknown IDs, malformed routing results, or scenarios unavailable in the active catalog
  MUST enter an explicit safe fallback and MUST NOT invoke business actions.

#### Conversation and Language

- **FR-012**: The system MUST retain and use relevant context for up to 10 customer/assistant
  exchanges, including recent messages, active scenario, suspended scenarios, normalized slots,
  identified client, relevant policy or claim identifiers, previously supplied information, and
  language state.
- **FR-013**: The system MUST distinguish continuations and clarifications from new topics based on
  both semantic meaning and conversation context.
- **FR-014**: When the customer's goal materially changes, the system MUST select the new eligible
  scenario, record the switch, and preserve context required to resume a suspended goal when
  appropriate.
- **FR-015**: The same utterance MUST be allowed to route differently when relevant prior context
  differs.
- **FR-016**: Russian, Kazakh, and mixed Russian/Kazakh messages MUST be accepted within and across
  turns as first-class routing inputs.
- **FR-017**: Language switching alone MUST NOT reset state, change scenario, force escalation, or
  cause fallback.
- **FR-018**: Customer-facing responses and clarification questions MUST use a language appropriate
  to the customer's current speech while retaining cross-language context; language detection MUST
  NOT determine the business scenario by itself.

#### Uncertainty, Fallback, and Safety

- **FR-019**: The system MUST represent uncertainty explicitly and expose plausible alternative
  scenarios whenever multiple candidates remain relevant.
- **FR-020**: The system MUST select `SYS_UNCLEAR` and ask one concise clarification question that
  offers the two leading options when available evidence cannot reliably distinguish them; the
  specification assumes no fixed numeric confidence threshold.
- **FR-021**: Confidence thresholds and the choice between selection, clarification, and escalation
  MUST be established and validated experimentally against representative data before release.
- **FR-022**: If the system cannot continue safely after clarification or routing attempts, it MUST
  support human handoff with relevant transcript, scenario history, collected information, and a
  concise context summary through a queue defined by the active dataset.
- **FR-023**: A direct customer request for a human operator MUST be supported as a valid handoff
  path.
- **FR-024**: Fallback, clarification, and escalation MUST be visibly distinguishable from ordinary
  successful routing in both customer behaviour and supervisor trace.
- **FR-025**: Scenario execution MUST be limited to the selected scenario's declared information,
  slots, actions, identification rule, confirmation rule, and handoff configuration and MUST NOT
  invent a scenario or unsupported business operation.
- **FR-026**: Company-specific responses MUST be grounded in the supplied knowledge and mock backend
  data; inability to ground a required fact or action MUST trigger a safe fallback or escalation.
- **FR-027**: Every action marked `irreversible: true` MUST have visibly distinct preview,
  confirmation, and execution states and MUST require explicit affirmative customer confirmation
  after the preview and before execution.
- **FR-028**: Failed or repeated requests MUST NOT accidentally execute a consequential action more
  than once.

#### Voice and Customer Experience

- **FR-029**: The final product MUST allow customers to provide speech through a browser microphone
  and MUST show listening and processing states.
- **FR-030**: The final product MUST convert customer speech to a visible transcript and play the
  assistant's spoken response.
- **FR-031**: Text input MUST remain available as a fallback and MUST use the same routing, context,
  execution, response, and trace behaviour from the routing step onward.
- **FR-032**: Speech failures MUST provide a recoverable retry or text fallback without discarding
  valid conversation state.
- **FR-033**: The customer conversation area MUST show the transcript, microphone state, processing
  state, assistant responses, text input, and audio playback controls or status.

#### Trace and Evaluation

- **FR-034**: After every customer turn, the supervisor trace MUST show turn number, transcript,
  detected language, ordered scenarios, confidence or uncertainty, structured rationale,
  alternatives, extracted slots, active and suspended scenarios, topic-change and continuation
  status, clarification status, actions and action mode, handoff queue, and dialogue identifier.
- **FR-035**: The trace MUST show speech-to-text, triage, routing, scenario/backend processing,
  response generation, text-to-speech first-audio, and total end-of-utterance-to-first-audio latency,
  marking non-applicable stages explicitly.
- **FR-036**: User-facing content and internal trace data MUST be separated, and the trace MUST NOT
  expose hidden chain-of-thought.
- **FR-037**: Routing records MUST identify the applicable scenario-catalog and decision-policy
  version or equivalent configuration so historic decisions can be reproduced and compared.
- **FR-038**: Automated evaluation MUST accept the prediction map required by `evaluate.py`, compare
  the first predicted ID with the first expected ID for primary accuracy, compare predicted and
  expected sets for full match, and calculate recovered expected IDs for multi-intent recall.
- **FR-039**: Evaluation MUST allow results and errors to be inspected overall and by Russian,
  Kazakh, mixed-language, request type, topic switching where labeled, fallback/clarification, and
  confused scenario pairs or groups.
- **FR-040**: The jury's separate hidden set of 10 utterances and any other unseen inputs MUST be
  processed dynamically through the same product routing path; no hidden-test-specific mapping,
  guessed utterance, or expected result may be hardcoded.
- **FR-041**: The system MUST measure routing and end-to-end latency rather than infer or conceal it.
  Approximately 500 ms routing and 1.5 seconds from end of speech to first audio are optimization
  targets, not functional pass/fail requirements. Current jury scoring awards latency bonus by
  median total: two points at or below 1.5 seconds, one point at or below 3 seconds, and no points
  above 3 seconds.

#### Data, Privacy, and Operability

- **FR-042**: The product MUST operate on the supplied `scenarios.json`, `slots.json`, `actions.json`,
  `knowledge_base.json`, `mock_backend.json`, `dialogs_sample.json`, `dev_utterances.json`, and
  `evaluate.py` contracts rather than substitute demo-only data.
- **FR-043**: Supplied company and customer data MUST be treated as fictional, anonymized test data;
  traces MUST contain only data necessary for the declared evaluation or diagnostic purpose and
  SHOULD mask sensitive-looking values displayed back to users or supervisors.
- **FR-044**: Production, operational trace, and development/debug data MUST be separable by purpose
  and access level before any real customer data can be used.
- **FR-045**: The application MUST have a documented, reproducible start procedure that does not
  require manual source changes or developer intervention after its declared prerequisites are
  available.
- **FR-046**: The initial milestone MUST support text input through dataset-driven LLM routing to a
  structured result, supervisor trace, and evaluator-compatible prediction, including all 40
  scenarios, all three system intents, ordered multi-intent output, Russian, Kazakh, mixed language,
  uncertainty, boundaries, and routing latency.
- **FR-047**: The routing baseline MUST be evaluated on all supplied development utterances and its
  results recorded before the milestone expands to conversation memory, execution, voice, or
  advanced supervisor capabilities.

#### Identification, Slots, and Action Execution

- **FR-048**: Before an action in a scenario marked as requiring identification, the system MUST
  identify the synthetic customer through an identifier supported by the relevant slot and action
  contracts, including phone, IIN, policy number, or claim number where applicable.
- **FR-049**: A successfully identified profile and valid conversation state MUST supply already
  known information; the assistant MUST NOT ask for it again unless confirmation, conflict
  resolution, expiry, or dataset validation requires it.
- **FR-050**: Slot values MUST be validated and normalized according to `slots.json`, including
  spoken phone numbers, dates, relative dates, vehicle information, enum values, and numeric values.
- **FR-051**: Relative dates in the simulation MUST resolve against dataset snapshot `2026-10-01`
  unless an explicit test override is recorded; the machine wall clock MUST NOT silently replace it.
- **FR-052**: Scenario action handling MUST follow the observable sequence: route, identify when
  required, collect missing required slots, preview when applicable, confirm irreversible action,
  execute, and respond.
- **FR-053**: The system MUST handle `not_found`, `invalid_input`, `policy_inactive`, `not_eligible`,
  `not_covered`, `no_availability`, `already_done`, and `service_unavailable` according to the retry,
  explanation, alternatives, and handoff behavior defined in `actions.json`.
- **FR-054**: Action inputs, outputs, errors, new identifiers, and handoff queues MUST remain
  compatible with `actions.json`, `mock_backend.json`, and `knowledge_base.json`; generated mock IDs
  MUST NOT collide with existing records.

### Scope Boundaries

**Initial milestone includes**:

- customer text input;
- LLM selection against all `SC01`–`SC40` scenarios and all three system intents;
- ordered multi-intent results and boundary-aware routing;
- Russian, Kazakh, and mixed-language inputs;
- structured decision validation and trace display;
- uncertainty, alternatives, topic-change and clarification indicators;
- routing latency measurement;
- evaluator-compatible prediction export and automated evaluation of all 104 development utterances.

**Final product scope adds**:

- conversation memory and topic resumption;
- controlled scenario and mock-backend execution;
- browser voice input and spoken output;
- customer conversation and supervisor trace areas;
- full stage-by-stage latency measurement and safe handoff.

**Out of scope for the initial milestone**:

- advanced supervisor analytics;
- emotion detection;
- a scenario editor;
- streaming speech processing;
- vector databases;
- complex persistent storage;
- authentication;
- production contact-centre integrations.

These items may be considered later only when they support routing correctness and do not displace
the required final voice experience. The specification does not select a model provider, speech
provider, application framework, storage technology, cloud provider, or orchestration framework.

### Logical Processing Contract

The final observable flow is microphone input, speech-to-text, triage, LLM routing, decision policy,
controlled scenario execution, response generation, text-to-speech, and first audio. Dialogue state
and supervisor trace span every stage. Text input joins the same flow at routing after any required
text normalization.

Triage may detect language, normalize values, detect urgency, and identify possible multi-intent
segments. It may supply or reduce candidates but may not independently make the final semantic
business-scenario decision. Exact service boundaries and technology choices are planning concerns.

### Key Entities *(include if feature involves data)*

- **Conversation**: A customer interaction containing a stable identifier, language history, up to
  10 customer/assistant exchanges, active and suspended goals, and ordered turns.
- **Conversation Turn**: One customer message and its resulting assistant handling, with transcript,
  language, relevant state changes, response, and stage timings.
- **Scenario**: One of the 40 catalogued business capabilities, identified by scenario ID and
  described by purpose, boundaries, priority, parameters, allowed actions, examples, confirmation
  needs, and handoff policy.
- **System Intent**: One of the separate non-business routing outcomes for out-of-scope, unclear, or
  goodbye behaviour; it cannot authorize a business action.
- **Routing Result**: The validated decision for a turn, including selected scenario, uncertainty,
  ordered additional scenarios, structured rationale, alternatives, normalized slots,
  continuation/topic-change, clarification, and fallback/escalation status.
- **Dialogue State**: Relevant recent messages, active scenario, suspended scenario where needed,
  identified customer and policy/claim references, previously supplied information, language, and
  scenario parameters collected so far.
- **Slot Value**: A typed and validated scenario parameter with its raw utterance evidence,
  normalized value, and source from the current turn, prior context, or identified profile.
- **Customer Identity**: A match to a synthetic customer record established through a supported
  identifier and reused only within relevant dialogue context.
- **Dataset Snapshot**: The versioned collection of catalog, slots, actions, knowledge, backend,
  dialogues, utterances, and evaluator contracts with reference date `2026-10-01`.
- **Scenario Execution**: Controlled progress within a selected scenario, including required
  identification, missing slots, preview, confirmation, allowed action, output/error, and completion.
- **Supervisor Trace Entry**: A turn-linked diagnostic record containing transcript, decision
  metadata, active/suspended state, actions and modes, handoff queue, outcomes, configuration
  identity, and latency by stage without hidden chain-of-thought.
- **Evaluation Case**: A labeled utterance or dialogue with language/type metadata and expected
  ordered scenario outcome used to measure routing behaviour.
- **Handoff Package**: The minimum relevant transcript, scenario history, collected information,
  uncertainty/failure reason, and summary transferred to a human operator.

### Requirement Traceability

| Requirement group | Acceptance coverage | Measurable outcome coverage |
|---|---|---|
| FR-001–FR-011: routing and catalog | User Stories 1, 3, and 7 | SC-001–SC-003, SC-006, SC-009, SC-014 |
| FR-012–FR-018: context and language | User Story 2 | SC-004–SC-005 |
| FR-019–FR-028: uncertainty and safety | User Stories 3 and 4 | SC-006–SC-007 |
| FR-029–FR-033: voice experience | User Story 5 | SC-010–SC-011 |
| FR-034–FR-041: trace and evaluation | User Stories 6 and 7 | SC-002, SC-008–SC-009, SC-011, SC-014 |
| FR-042–FR-047: data and operability | All user stories | SC-001–SC-004, SC-013–SC-016 |
| FR-048–FR-054: identification, slots, actions | User Story 4 | SC-007, SC-017–SC-019 |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The initial milestone dynamically processes 100% of the 104 supplied development
  utterances and produces a valid prediction or explicit system outcome for every item.
- **SC-002**: The recorded baseline reports primary routing accuracy, full-match accuracy,
  multi-intent recall, and all available language and request-type splits; no metric is omitted when
  the supplied labels support it, and the unmodified reference evaluator can score the exported
  predictions without schema adaptation.
- **SC-003**: Before voice expansion begins, routing reaches at least 80% primary accuracy on the
  supplied development set, with every incorrect prediction available for inspection. This is a
  milestone target, not a claim about hidden-set performance.
- **SC-004**: All 10 supplied annotated conversations can be replayed without losing turn order,
  language history, scenario-switch events, or relevant previously supplied information.
- **SC-005**: In acceptance tests covering continuation, topic change, language-only change, and
  topic return, 100% of turns produce the expected continuation/switch status and retain the
  annotated relevant context.
- **SC-006**: Every ambiguous acceptance case yields explicit uncertainty and alternatives; no case
  marked unclear silently executes a business scenario.
- **SC-007**: 100% of tested consequential or irreversible actions require explicit confirmation
  before execution, and cancellation or non-confirmation results in zero such actions executed.
- **SC-008**: 100% of completed customer turns create a trace entry containing all applicable
  decision fields and all applicable latency stages; skipped stages are explicitly marked rather
  than silently absent.
- **SC-009**: For every evaluation error, a reviewer can identify the input, expected scenario,
  predicted scenario, language/type grouping, and top alternatives from the evaluation output and
  trace.
- **SC-010**: A customer can complete at least one supported request through voice and the same
  request through text while receiving equivalent routing and controlled scenario behaviour.
- **SC-011**: Routing latency and end-of-speech-to-start-of-response latency are measured on every
  applicable turn and summarized against the approximately 500 ms and 1.5 second optimization
  targets and current median bonus bands without treating them as functional acceptance gates.
- **SC-012**: In a usability check with 10 representative participants, at least 8 can submit a
  natural-language request, understand the next assistant action, and find the selected scenario and
  uncertainty status in the supervisor view without developer assistance.
- **SC-013**: The application starts from its documented prerequisites using one reproducible
  procedure and processes an unseen text request without any source-code or data edits.
- **SC-014**: Review of the delivered product finds zero hardcoded mappings from supplied or hidden
  evaluation utterances to expected scenario IDs and zero final routing decisions made solely by an
  encoder classifier, keywords, or candidate retrieval.
- **SC-015**: Dataset validation loads all 40 business scenarios, all three system intents, all 43
  slots, all 31 actions, and all six handoff queues with zero unresolved cross-file references.
- **SC-016**: All 13 development records labeled `multi_intent` produce ordered prediction arrays
  with a primary item and without silently dropping a detected secondary request; correctness is
  reported by primary accuracy, full match, and intent recall.
- **SC-017**: Acceptance tests cover all eight dataset action error codes and verify their declared
  retry, explanation, alternative, or handoff outcome with zero unsupported actions executed.
- **SC-018**: Acceptance tests demonstrate successful identification through every applicable
  supported identifier type and reuse known profile/context values without unnecessary re-entry.
- **SC-019**: Every tested irreversible action type records preview before confirmation and execution
  after confirmation; ambiguous or absent confirmation results in zero execution events.
- **SC-020**: A grounding audit of tested company responses finds zero unsupported prices, policy or
  customer details, office or clinic facts, claim/payment status, coverage claims, or insurance rules.

## Assumptions

- A "10-turn conversation" means up to 10 customer/assistant exchanges; behaviour beyond that
  limit may summarize, conclude, or hand off safely but must not silently corrupt state.
- The starter kit is authoritative for the fictional insurer: 40 business scenarios are evaluated,
  while out-of-scope, unclear, and goodbye are separate system outcomes.
- The supplied 104 development utterances and 10 annotated dialogues are development evidence, not
  the hidden jury set and not permission to encode answer mappings.
- The jury's 10 hidden utterances follow the same general contract but are unavailable during
  development; no minimum hidden-set accuracy is asserted before those results exist.
- The 80% development primary-accuracy threshold is a project milestone target selected for routing
  readiness, not a threshold defined by `evaluate.py` or a prediction of hidden-set performance.
- Routing confidence may be numeric or categorical as long as it is comparable, traceable, and
  useful to the experimentally validated decision policy.
- No fixed confidence threshold is part of this specification; thresholds may differ by risk or
  scenario if evaluation justifies the difference and the active policy is identifiable in traces.
- Approximately 500 ms routing and 1.5 seconds to the beginning of a spoken response are optimization
  targets. The current README's median latency bonus bands are scoring context, not functional
  gates. Routing correctness and safe uncertainty take priority when a measured trade-off exists.
- Dataset-relative dates use snapshot `2026-10-01`; an explicit test override may use another date
  only when that override is visible in evaluation or trace metadata.
- Speech recognition and synthesis quality are secondary to routing quality, but both must support
  an end-to-end voice demonstration in the final product.
- All supplied customer and company records are fictional and anonymized. Real customer data and
  production retention/access policies are outside this feature until separately approved.
- The catalog and starter-kit files are available to the running product in their documented shape.
  If temporarily absent during development, substitutes may mirror the interfaces but must not be
  presented as the final hackathon dataset.
- Authentication, production integrations, and durable multi-session history are not required for
  the initial milestone.
