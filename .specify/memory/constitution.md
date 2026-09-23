<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles:
  - I. Context-Aware Routing -> VI. Context-Aware and Stateful Routing
  - II. Dynamic Scenario Switching -> VI. Context-Aware and Stateful Routing
  - III. Russian/Kazakh Language Parity -> VII. Russian, Kazakh, and Mixed-Language Support
  - IV. LLM Decisions, Controlled Scenario Execution -> II. LLM Makes the Final Routing
    Decision and IX. Controlled Scenario Execution
  - V. Observable and Explainable Routing -> VIII. Structured Decision Trace, Not Hidden
    Reasoning
  - VI. Safe Uncertainty and Explicit Fallback -> XII. Deterministic and Inspectable Fallback
  - VII. Voice-Grade Latency -> XV. Measurable Latency
  - VIII. Dialogue-Level Testability and Evaluation -> XIII. Evaluation-Driven Development
  - IX. Data Privacy and Production Safety -> Architectural and Data Constraints
- Added principles:
  - I. Dataset Is the Evaluation Source of Truth
  - III. Scenario Boundaries Are First-Class
  - IV. Multi-Intent Routing Is a First-Class Requirement
  - V. System Intents Are Part of the Routing Contract
  - X. Safe Handling of Irreversible Actions
  - XI. Data-Grounded Responses
  - XIV. Hidden-Test Independence
- Added sections: none; existing constraint and workflow sections were materially expanded.
- Removed sections: none.
- Follow-up TODOs:
  - TODO(UNCERTAINTY_POLICY): validate selection, clarification, and handoff policy.
  - TODO(TELEMETRY_POLICY): define real-data retention, access, redaction, and deletion rules.
  - TODO(COST_BUDGETS): define production operating-cost limits during planning.
-->

# Voice Router Constitution

## Core Principles

### I. Dataset Is the Evaluation Source of Truth

The checked-in Voice Router dataset and its reference evaluator MUST define the project's external
behavioral baseline. Implementations MUST consume the actual contracts rather than substitute
application-specific taxonomies, hardcoded demonstrations, or incompatible data shapes. The
baseline consists of:

- 40 business scenarios, `SC01` through `SC40`, and their metadata in `scenarios.json`;
- the separate system intents `SYS_OUT_OF_SCOPE`, `SYS_UNCLEAR`, and `SYS_GOODBYE`;
- slot definitions in `slots.json`;
- executable actions, error semantics, and handoff queues in `actions.json`;
- company facts in `knowledge_base.json`;
- synthetic clients, policies, claims, and payments in `mock_backend.json`;
- annotated stateful conversations in `dialogs_sample.json`;
- labeled routing cases in `dev_utterances.json`; and
- prediction format and metric semantics in `evaluate.py`.

Dataset version and snapshot metadata MUST remain identifiable in evaluation evidence and decision
traces. A contract change MUST be explicit, reviewed, and versioned; it MUST NOT be silently hidden
behind an adapter that changes observable meaning.

Rationale: these files are the evaluation contract, not optional examples, so behavior that ignores
them cannot be considered a valid Voice Router implementation.

### II. LLM Makes the Final Routing Decision

An LLM MUST make the final semantic selection of the business scenario or system intent. An
encoder-based intent classifier MUST NOT make that final decision. Keyword lookup, hardcoded
utterance-to-scenario mappings, memorized evaluation answers, or evaluation-specific rules MUST NOT
determine the result.

A deterministic preprocessing or triage layer MAY detect language, normalize spoken values, detect
urgency, identify possible multi-intent structure, or retrieve a candidate subset. Such a layer MUST
pass semantic authority to the LLM and MUST NOT remove the correct outcome from consideration
without a safe, observable recovery path.

Rationale: the product exists to replace brittle intent classification with contextual semantic
routing while retaining deterministic safeguards around the decision.

### III. Scenario Boundaries Are First-Class

The router MUST evaluate scenario boundaries as well as positive descriptions. For each decision it
MUST consider the applicable `description`, `not_this_if` exclusions and `use_instead` targets,
priority, conversation state, available and collected slots, identification requirements, allowed
actions, and handoff policy from the active catalog. Similar wording MUST NOT override a documented
boundary between neighboring scenarios.

Scenario definitions MUST remain data-driven so catalog descriptions, boundaries, or examples can
change without rewriting utterance-specific routing logic. Invalid boundary references MUST fail
validation before they can influence live routing.

Rationale: neighboring insurance scenarios often share vocabulary; their exclusions and operational
constraints carry the meaning needed to distinguish them.

### IV. Multi-Intent Routing Is a First-Class Requirement

The router MUST preserve every distinct supported intent found in one customer turn as a
deterministically ordered list of scenario IDs. The first item MUST be the primary scenario.
Additional items MUST represent distinct intentions, not alternative guesses; alternatives and
multi-intent selections MUST remain separate fields or concepts.

Urgent scenarios MUST precede normal scenarios when the active dataset priority rules require it.
Otherwise, selected scenarios MUST follow their semantic order of appearance in the customer
request. The implementation MUST NOT collapse a labeled multi-intent request into one arbitrary
scenario or silently discard later intentions.

Rationale: `dev_utterances.json` contains ordered multi-intent outcomes and the evaluator treats the
first prediction as primary while measuring recovery of the complete expected set.

### V. System Intents Are Part of the Routing Contract

`SYS_OUT_OF_SCOPE`, `SYS_UNCLEAR`, and `SYS_GOODBYE` MUST be valid, explicit routing outcomes and
MUST be distinguishable from `SC01` through `SC40` in decisions, traces, and evaluation output.
`SYS_OUT_OF_SCOPE` MUST represent requests outside Saqta Insurance's supported services.
`SYS_UNCLEAR` MUST represent an intent that cannot yet be determined reliably and MUST lead to one
concise clarifying question. `SYS_GOODBYE` MUST close a customer-ended conversation.

System intents MUST NOT authorize business actions or masquerade as business scenarios.

Rationale: fallback, scope, and conversation termination are evaluated behaviors with different
semantics from business routing.

### VI. Context-Aware and Stateful Routing

Every routing decision MUST use the current message and all relevant available conversation state.
Relevant state includes recent dialogue turns, active and suspended scenarios, extracted slots,
identified customer, information already supplied, language state, and unresolved goals. A
clarification, short answer, paraphrase, or continuation MUST NOT be treated as an isolated intent
when its meaning depends on prior turns.

The system MUST detect a material topic change, suspend the current scenario when appropriate,
handle the new scenario, and support returning to the suspended scenario with still-valid context.
It MUST NOT force the customer to repeat information that remains valid and safe to reuse. State
transfer between scenarios MUST exclude irrelevant or unsafe values.

Rationale: topic switching and return are explicit behaviors in `dialogs_sample.json` and cannot be
implemented by independent single-turn classification.

### VII. Russian, Kazakh, and Mixed-Language Support

Russian, Kazakh, and mixed Russian/Kazakh speech MUST be first-class routing inputs. The system MUST
support language switching between turns and within one utterance. Language detection MAY inform
normalization and response language but MUST NOT determine the business scenario by itself.

Changing language MUST NOT reset conversation state, discard slots, switch scenarios, trigger
fallback, or require human handoff without separate semantic justification. User-facing responses
SHOULD follow the customer's current language preference; any exception MUST be documented and
must preserve understandable service.

Rationale: the dataset explicitly labels `ru`, `kk`, and `mixed` cases and includes stateful language
switches.

### VIII. Structured Decision Trace, Not Hidden Reasoning

Every customer turn MUST create an inspectable trace linked to the dialogue and turn. The trace MUST
contain the transcript, detected language, ordered selected scenarios, confidence or equivalent
uncertainty, alternative candidates, concise structured rationale, topic-change status, extracted
slots, clarification status, selected or executed actions, fallback or handoff status, and applicable
latency measurements. It MUST also identify the catalog and decision-policy version or equivalent
configuration used for the decision.

User-facing responses and internal trace data MUST remain distinct. Observability MUST NOT depend on
capturing, exposing, or reconstructing hidden LLM chain-of-thought. Structured reasons MUST describe
decision-relevant evidence and boundaries without revealing private model reasoning.

Rationale: supervisors need reproducible diagnostic evidence, not opaque answers or unrestricted
model internals.

### IX. Controlled Scenario Execution

The LLM MAY choose a scenario but MUST NOT freely create business logic, company facts, actions, or
side effects. Execution MUST be constrained by the selected scenario in `scenarios.json`, its slot
definitions in `slots.json`, its declared actions and errors in `actions.json`, and the available
facts and records in `knowledge_base.json` and `mock_backend.json`.

The execution layer MUST validate the routing result, required identification, inputs, allowed
actions, action errors, and handoff queue before acting. An action not declared for the selected
scenario MUST NOT execute. Unknown scenarios, actions, slots, or queues MUST enter safe fallback.

Rationale: semantic flexibility belongs in routing; business operations require deterministic,
auditable boundaries.

### X. Safe Handling of Irreversible Actions

Every action whose `irreversible` field is `true` in `actions.json` MUST use three distinguishable
states: preview, explicit customer confirmation, and execution. The system MUST read back or display
the consequential details before confirmation and MUST execute only after an unambiguous affirmative
response tied to that preview.

An LLM inference, prior generic consent, silence, ambiguous reply, retry, or duplicated turn MUST NOT
count as confirmation. Cancellation or non-confirmation MUST produce no irreversible side effect,
and retries MUST NOT execute the same confirmed action more than once.

Rationale: the dataset models policy changes, cancellations, claims, bookings, and contact updates as
consequential actions requiring explicit consent.

### XI. Data-Grounded Responses

Company-specific statements MUST be grounded in `knowledge_base.json`, `mock_backend.json`, or a
validated result from an allowed action. The assistant MUST NOT invent prices, policy or customer
details, office or clinic information, claim or payment status, coverage, insurance rules, or product
availability. Missing or conflicting data MUST result in an honest limitation, safe alternative, or
handoff rather than fabrication.

Date-sensitive simulation behavior SHOULD resolve relative dates against the dataset's
`meta.as_of_date`; the current contract uses `2026-10-01`. The machine wall-clock MUST NOT silently
replace that snapshot date. A deliberate date override MUST be explicit in test or trace metadata.

Rationale: Saqta Insurance and all supplied records are fictional, and consistency is measurable only
against their authoritative snapshot.

### XII. Deterministic and Inspectable Fallback

The router MUST keep uncertainty visible and MUST NOT disguise an unresolved choice as successful
routing. When ambiguity can be resolved, it SHOULD select `SYS_UNCLEAR`, preserve the leading
alternatives, and ask one concise question. When safe continuation is impossible, the system MUST
support human handoff with relevant conversation state so the customer need not repeat the case.

Handoff queue selection MUST follow the active scenario and action definitions. Invalid model
output, unavailable required data, unsupported actions, and technical failures MUST have explicit,
traceable fallback behavior. Selection, clarification, retry, and handoff rules MUST be deterministic
for the same validated routing result and policy version.

TODO(UNCERTAINTY_POLICY): specification and planning MUST validate the thresholds or equivalent
signals that select normal routing, clarification, retry, and handoff; this Constitution does not
fix model-specific confidence values.

Rationale: explicit and reproducible uncertainty handling is safer than silent guessing.

### XIII. Evaluation-Driven Development

Every routing implementation and material routing change MUST be evaluated with the checked-in
development contract. The current `dev_utterances.json` contains 104 cases: 84 single-intent,
13 multi-intent, 4 out-of-scope, and 3 unclear; language counts are 52 Russian, 45 Kazakh, and
7 mixed-language.

Predictions MUST remain compatible with `evaluate.py`: a JSON object maps each utterance ID to an
ordered array of predicted scenario IDs. Missing predictions MUST count as errors. The first
predicted ID MUST be evaluated against the first expected ID for primary accuracy. Full-match
accuracy MUST use equality of predicted and expected ID sets. Multi-intent recall MUST measure the
share of expected multi-intent IDs recovered. Reports MUST preserve the evaluator's overall,
language, and intent-type breakdowns and MUST expose individual errors for inspection.

Annotated dialogues MUST additionally test scenario switching, topic return, context carry,
clarification, handoff, multilingual behavior, and irreversible-action confirmation. Acceptance
targets MUST be defined in the applicable specification or plan and reported without changing the
reference metric definitions.

Rationale: quality claims are credible only when they reproduce the actual evaluator and exercise
the stateful behaviors not represented by isolated utterances alone.

### XIV. Hidden-Test Independence

The implementation MUST process unseen and hidden jury inputs dynamically through the same catalog,
context, LLM decision, validation, and trace path used for known inputs. Development utterances,
expected labels, or hidden-test guesses MUST NOT appear in runtime mappings, prompts as answer keys,
special-case branches, or lookup tables.

Evaluation data MAY be used to measure and diagnose general behavior, but a fix MUST address a
scenario boundary, context rule, multilingual behavior, or other general cause rather than memorize
the failing utterance.

Rationale: hidden evaluation measures generalization; memorization invalidates both the product goal
and the external contract.

### XV. Measurable Latency

Latency MUST be measured rather than inferred or hidden. For each applicable voice turn, the
architecture MUST support separate timing for speech-to-text, triage, routing, scenario or backend
execution, response generation, text-to-speech, and the end-of-customer-speech to first-audio total.
Skipped or unavailable stages MUST be marked explicitly so the total remains interpretable.

Latency targets are optimization objectives, not functional acceptance gates, unless governance is
formally amended. Latency optimization MUST NOT create an uncontrolled regression in routing
correctness, multi-intent completeness, multilingual behavior, or fallback safety. Unnecessary LLM
calls SHOULD be removed only when measurements demonstrate that decision quality is preserved.

Rationale: responsive voice interaction matters, but the dataset and jury rules make routing quality
the primary objective and latency a separately measured optimization.

## Architectural and Data Constraints

- Voice input/output, normalization and triage, dialogue state, LLM routing, decision policy,
  scenario execution, data access, and observability MUST have explicit, testable boundaries.
- The router MUST accept scenario catalog changes without retraining or restoring a dedicated
  encoder-based final intent classifier. Replacing the LLM MUST NOT require rewriting unchanged
  scenario execution contracts.
- The active dataset version, catalog, decision policy, and model configuration MUST be identifiable
  for reproducible evaluation and trace analysis.
- All supplied records are synthetic, but they resemble sensitive contact-center data. Logs and
  traces MUST collect only what is necessary, SHOULD mask sensitive-looking values when displayed,
  and MUST separate production, operational, and development/debug purposes and access.
- TODO(TELEMETRY_POLICY): retention, access, redaction, deletion, and audit rules MUST be approved
  before real customer data is processed.
- Technology and provider choices belong to planning. This Constitution does not prescribe a model,
  API, speech provider, framework, database, vector store, cloud, or orchestration product.
- TODO(COST_BUDGETS): production-facing plans MUST define measurable operating-cost criteria for the
  expected workload before approval.

## Development Workflow and Compliance Gates

- Specifications MUST identify affected dataset contracts, scenario boundaries, state transitions,
  multilingual behavior, multi-intent behavior, fallback paths, safety rules, privacy impact, and
  measurable acceptance criteria.
- Plans MUST document component boundaries, validated structured routing results, catalog and action
  validation, dialogue state, evaluation procedure, latency measurement, privacy controls, and
  justified quality, latency, reliability, and cost trade-offs.
- Tasks and implementation MUST include tests for applicable normal, boundary, multi-intent, system
  intent, context-switch, topic-return, Russian, Kazakh, mixed-language, malformed-output, fallback,
  action-error, and irreversible-confirmation cases.
- Every material routing change MUST run the unmodified reference evaluator or a demonstrably
  equivalent invocation against all 104 development utterances. Reports MUST retain individual
  errors and group metrics; aggregate accuracy MUST NOT hide regressions by language or type.
- Dataset schema and cross-file references MUST be validated before evaluation or scenario execution.
  Unknown scenario, slot, action, boundary, or queue references block release.
- Reviews MUST verify every applicable MUST with evidence. An unresolved MUST violation blocks
  completion. A SHOULD exception requires a written rationale, scope, and consequence analysis.
- Production readiness additionally requires stateful dialogue evidence, safe-action evidence,
  latency results, and privacy/security review appropriate to the processed data.

## Governance

This Constitution is the project's long-term engineering contract and supersedes conflicting local
conventions. Specifications, plans, tasks, implementation, and reviews MUST remain consistent with
it. The checked-in dataset and `evaluate.py` define the external evaluation contract; this document
defines the architectural and behavioral invariants governing how that contract is satisfied.

If an artifact or implementation conflicts with a MUST, the artifact or implementation MUST change,
or this Constitution MUST be formally amended. A principle MUST NOT be silently ignored, weakened by
an implementation detail, or waived informally. Concrete providers, frameworks, models, APIs, and
infrastructure remain planning decisions unless formally promoted to project invariants.

An amendment MUST state its rationale, affected principles and dataset contracts, migration impact,
compatibility impact, and evidence required to retain routing quality and safety. Amendments MUST be
reviewed and approved before dependent work is declared compliant. Semantic versioning applies:

- MAJOR for removing or incompatibly redefining a principle or governance obligation;
- MINOR for adding a principle or materially expanding mandatory guidance; and
- PATCH for non-semantic clarification, correction, or wording improvement.

Compliance MUST be reviewed at specification approval, plan approval, implementation review, and
before release. Dataset contract changes MUST receive the same review as code changes. Open TODOs in
this document MUST be resolved in the relevant specification or plan before the affected production
capability is released.

**Version**: 1.1.0 | **Ratified**: 2026-09-23 | **Last Amended**: 2026-09-23
