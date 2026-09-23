<!--
Sync Impact Report
- Version change: unversioned scaffold -> 1.0.0
- Modified principles:
  - Scaffold Principle 1 -> I. Context-Aware Routing
  - Scaffold Principle 2 -> II. Dynamic Scenario Switching
  - Scaffold Principle 3 -> III. Russian/Kazakh Language Parity
  - Scaffold Principle 4 -> IV. LLM Decisions, Controlled Scenario Execution
  - Scaffold Principle 5 -> V. Observable and Explainable Routing
- Added principles:
  - VI. Safe Uncertainty and Explicit Fallback
  - VII. Voice-Grade Latency
  - VIII. Dialogue-Level Testability and Evaluation
  - IX. Data Privacy and Production Safety
- Added sections:
  - Architectural Boundaries and Quality Constraints
  - Development Workflow and Compliance Gates
- Removed sections: none (placeholder sections were concretized)
- Follow-up TODOs:
  - TODO(ROUTING_THRESHOLDS): define confidence/uncertainty thresholds per scenario.
  - TODO(LATENCY_BUDGETS): define routing, response-generation, and end-to-end budgets.
  - TODO(EVALUATION_TARGETS): define acceptance targets for quality and fallback metrics.
  - TODO(TELEMETRY_POLICY): define retention, access, and redaction requirements.
  - TODO(COST_BUDGETS): define measurable operating-cost limits.
-->

# Voice Router Constitution

## Core Principles

### I. Context-Aware Routing

The router MUST base every scenario decision on the current user utterance and the relevant
dialogue context available at that step. It MUST be able to use prior utterances, prior scenario
decisions, clarifications, and unresolved user goals when they affect meaning. A paraphrase,
clarification, or continuation MUST NOT be treated as an independent intent solely because its
wording differs from an earlier utterance. Specifications and tests MUST state what context is
provided to the router and how relevance, truncation, and context loss are handled.

Rationale: routing isolated utterances repeats the failure mode this project exists to remove and
cannot reliably resolve follow-ups or ambiguous wording.

### II. Dynamic Scenario Switching

A scenario choice MUST remain revisable throughout a dialogue. The system MUST detect a material
change in the user's current goal and switch to an eligible scenario when that scenario better
serves the goal. A switch MUST preserve the context required by the new scenario while preventing
irrelevant or unsafe state from leaking into its execution. Correct handling of the current user
goal MUST take precedence over retaining a previous scenario. Every switch and its source and
destination scenarios MUST be recorded and evaluated.

Rationale: a contact-centre conversation is a sequence of evolving goals, not a one-time intent
classification.

### III. Russian/Kazakh Language Parity

Russian, Kazakh, and mixed Russian-Kazakh speech MUST be first-class routing inputs. Language
switching alone MUST NOT cause context loss, scenario switching, fallback, or escalation. Routing
quality and scenario-switching quality MUST be evaluated separately for Russian, Kazakh, and mixed
dialogues. The architecture MUST NOT model Kazakh as merely a translation layer around a Russian
intent router; both languages MUST participate directly in meaning and context resolution.

Rationale: language choice is independent of the user's business goal and must not determine the
quality or continuity of service.

### IV. LLM Decisions, Controlled Scenario Execution

The LLM layer MUST interpret the dialogue and choose only from an explicitly defined, versioned
set of eligible scenarios. It MUST return a machine-validated structured routing decision. Unknown,
malformed, or ineligible scenario selections MUST be rejected and handled through explicit
fallback. Business operations, authorization, critical rules, and side effects MUST remain under
deterministic scenario logic; LLM output MUST NOT bypass those controls.

The boundaries between voice input/output, dialogue context, routing, scenario execution, and
observability MUST be explicit. New scenarios MUST be addable through scenario contracts and
routing metadata without retraining a dedicated encoder-based intent classifier. Replacing or
upgrading the LLM MUST NOT require rewriting business scenarios when their contracts are unchanged.

Rationale: the LLM supplies semantic flexibility while controlled execution preserves predictable
and auditable business behaviour.

### V. Observable and Explainable Routing

Every routing decision MUST produce a trace linked to the dialogue and step. The trace MUST contain
at least the selected scenario, decision timestamp, decision duration, a confidence or equivalent
uncertainty signal, whether a scenario switch occurred, and whether fallback or escalation occurred.
It MUST also contain structured, user-comprehensible reasons or decision signals sufficient for a
supervisor to investigate the choice. User-facing responses and internal decision traces MUST be
kept distinct. Observability MUST NOT depend on storing or exposing hidden LLM chain-of-thought.

Supervisor-facing views MUST make the sequence of scenario choices, switches, uncertainty,
fallbacks, escalations, and routing errors understandable without access to raw model reasoning.

Rationale: structured evidence enables diagnosis and reproducible analysis without creating a
requirement to disclose private model reasoning.

### VI. Safe Uncertainty and Explicit Fallback

The router MUST NOT present an uncertain or conflicting choice as a normal successful decision.
Insufficient confidence, materially conflicting scenarios, absence of an eligible scenario,
invalid model output, and technical routing failure MUST enter a defined safe fallback path.
Fallback behaviour MUST be distinguishable from successful routing in control flow, telemetry, and
evaluation. A fallback MUST safely clarify, conclude, or hand off the dialogue according to an
approved policy; it MUST NOT conceal a routing error.

TODO(ROUTING_THRESHOLDS): specifications and plans MUST define justified uncertainty thresholds
and fallback actions before the affected scenario is released.

Rationale: explicit uncertainty is safer and more measurable than confident misrouting.

### VII. Voice-Grade Latency

Latency is a product requirement for every critical voice interaction. The architecture MUST set
and measure budgets for routing time, response-generation time, and total time from the completed
user utterance to the robot response. Designs MUST avoid LLM calls that do not provide measurable
quality or safety value. A latency optimization MUST NOT be accepted when it causes an uncontrolled
decrease in routing correctness, switching correctness, or fallback safety; the trade-off MUST be
demonstrated with measurements.

TODO(LATENCY_BUDGETS): the applicable specification or plan MUST define numerical budgets and
measurement conditions before production release.

Rationale: a semantically correct voice robot that responds too slowly still provides a failed user
experience.

### VIII. Dialogue-Level Testability and Evaluation

Routing correctness MUST be evaluated on complete real and synthetic dialogues, not only isolated
classification examples. The maintained evaluation set MUST include normal and paraphrased
requests, ambiguous and cross-scenario requests, mid-dialogue topic changes, clarifications,
Russian, Kazakh, mixed-language dialogue, malformed or incomplete utterances, and required fallback
cases. Evaluation MUST separately report routing quality, scenario-switching correctness, fallback
rate, and latency. Regressions MUST be assessed by category and language so aggregate scores cannot
hide a critical failure mode.

TODO(EVALUATION_TARGETS): feature specifications MUST define acceptance targets and representative
dataset criteria before implementation can be declared production-ready.

Rationale: the system's defining behaviours emerge across turns, languages, and uncertainty cases.

### IX. Data Privacy and Production Safety

Voice data, transcripts, dialogue context, and decision traces MUST be handled as contact-centre
data with least-necessary collection and access. Logs MUST contain only information required for
the declared diagnostic, operational, or audit purpose. Sensitive data MUST NOT appear in telemetry
in clear text unless an approved requirement makes it necessary and establishes protection and
access controls. Production logs, operational traces, and development/debug data MUST be separated
by purpose and access level. Test and evaluation data MUST follow the same privacy classification
and redaction rules as their source data.

TODO(TELEMETRY_POLICY): the production plan MUST define retention, access, redaction, deletion, and
audit requirements before real customer data is processed.

Rationale: observability is valuable only when it does not create a second, less-controlled copy of
sensitive conversations.

## Architectural Boundaries and Quality Constraints

- Voice input/output, dialogue context, routing, scenario execution, and observability MUST expose
  clear responsibilities and testable contracts. A component MUST NOT assume another component's
  responsibilities merely to simplify one implementation.
- Routing outputs and scenario contracts MUST be versioned or otherwise identifiable so a recorded
  decision can be reproduced and analysed against the configuration that produced it.
- The deterministic execution layer MUST validate every routing output before selecting or
  switching a scenario. Critical side effects MUST remain subject to explicit business validation
  and authorization.
- Model, prompt, context strategy, or scenario-catalogue changes MUST be evaluated against routing
  quality, switching correctness, fallback behaviour, latency, reliability, privacy, and cost.
- Technology choices MUST remain an outcome of planning. This Constitution does not mandate a
  specific model, API, framework, database, transport, or UI implementation.
- TODO(COST_BUDGETS): plans for production-facing changes MUST establish measurable cost criteria
  and the expected workload before those changes are approved.

## Development Workflow and Compliance Gates

- Every feature specification MUST identify affected principles, relevant dialogue behaviours,
  failure and fallback paths, privacy impact, and measurable acceptance criteria.
- Every implementation plan MUST document component boundaries, routing and scenario contracts,
  observability fields, evaluation strategy, latency measurement, privacy controls, and justified
  quality/cost trade-offs relevant to its scope.
- Implementation tasks MUST include the tests and telemetry necessary to prove the applicable
  MUST requirements. A requirement MUST NOT be considered complete solely because its happy path
  works.
- Reviews MUST verify Constitution compliance and cite the evidence for each applicable gate.
  Unresolved MUST violations block completion; justified SHOULD exceptions MUST be documented in
  the plan with their scope and consequences.
- Production readiness MUST be supported by dialogue-level evaluation results, latency results,
  safe fallback evidence, and privacy/security review appropriate to the data being processed.

## Governance

This Constitution is the authoritative set of long-term project constraints for subsequent
specification, planning, task generation, implementation, and review. If a specification, plan, or
implementation violates a MUST principle, that artifact MUST be changed or the Constitution MUST
be formally amended; the principle MUST NOT be ignored or waived informally.

Amendments MUST state the reason, affected principles or sections, migration impact, and evidence
needed to retain safety and quality. They MUST be reviewed and approved before dependent work is
treated as compliant. Amendments use semantic versioning:

- MAJOR for removal or backward-incompatible redefinition of a principle or governance obligation;
- MINOR for a new principle or materially expanded obligation;
- PATCH for non-semantic clarification, correction, or wording improvement.

Compliance MUST be reviewed at specification approval, plan approval, and implementation review.
Open TODO decisions in this document MUST be resolved in the relevant specification or plan before
the affected production capability is released. Where SHOULD is used, deviation requires a written,
reviewable rationale; MUST requirements permit no exception without a Constitution amendment.

**Version**: 1.0.0 | **Ratified**: 2026-09-23 | **Last Amended**: 2026-09-23
