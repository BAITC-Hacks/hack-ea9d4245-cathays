# Research: Voice Router

## Decisions

| Area | Decision | Rationale | Alternatives rejected/deferred |
|---|---|---|---|
| Backend | Python 3.12 + FastAPI + Pydantic v2 | Fits the supplied Python scorer and JSON contract validation | Node-only backend duplicates evaluator integration |
| Web | React + TypeScript + Vite + Tailwind | Small browser/microphone UI boundary | Server-rendered Python UI is less suitable for audio state; Next.js is optional later |
| Catalog | Full 40-scenario prompt initially | Boundary safety outweighs premature optimization | Vector/embedding retrieval deferred; keyword final routing prohibited |
| Structured output | Native JSON schema where available; JSON-only fallback; Pydantic validation | Provider portability with strict safety | Free-form prose and unlimited retries are unsafe |
| Uncertainty | Calibrated, versioned policy; conservative clarification until measured | Constitution rejects arbitrary permanent threshold | README sample numbers are not adopted blindly |
| Prompt | Versioned catalog cards + separate structured state | Preserves exclusions/substitutions and avoids example-only ambiguity | Chain-of-thought prompting/tracing is disallowed |
| Voice | Adapter ports; choose vendor via RU/KK/mixed benchmark | No authoritative provider evidence exists | Single vendor/browser Web Speech-only lock-in |
| Timing | Backend monotonic timers + browser `performance.now()` timestamps | Avoids cross-clock assumptions; explicit skipped/failed states | Total-only/server wall-clock timing |
| Trace/action safety | In-memory masked synthetic trace + preview-bound idempotency | Meets demo evidence without premature production data platform | Indefinite persistence/no trace |

## Experiment Register

| Question | Evidence / decision rule | Milestone |
|---|---|---|
| Router provider/model | Valid schema rate, primary/full/multi-intent metrics, boundary errors, p50/p95 | 2–4 |
| Full catalog vs retrieval | Expected and boundary targets always retained; no product-router metric regression | 4 |
| Uncertainty policy | False-route/clarify/handoff rates across language/type/manual ambiguity cases | 4 |
| Prompt variants | General boundary error clusters improve without utterance-specific rules | 4 |
| STT/TTS | RU/KK/mixed transcription/intelligibility/failure/first-audio samples | 9 |
| Trace minimality | Review required diagnostic evidence after masking/purpose separation | 8–10 |
