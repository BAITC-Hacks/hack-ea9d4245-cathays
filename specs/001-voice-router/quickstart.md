# Voice Router Validation Guide

## Prerequisites

- Python 3.12 and Node.js 20+.
- Configured routing-provider credential/model. A fake adapter is allowed only for schema/UI tests, never as an evaluation baseline.
- Unmodified checked-in dataset at `voice_router_dataset/case_2/voice_router_dataset`.

## Start and validate

1. Install locked backend and web dependencies; configure provider/model outside source control.
2. Start FastAPI then `apps/web`; open customer and supervisor views.
3. Submit unseen Russian, Kazakh and mixed-language text. Each creates a validated decision/system outcome and trace containing snapshot/prompt/policy/config IDs and router timings.
4. Run dataset contract, router/boundary/multilingual/multi-intent/system/malformed-output tests.
5. Run batch evaluation: it writes evaluator-format predictions under `artifacts/evaluation/<run-id>/`, invokes unchanged `evaluate.py`, and saves evaluator output plus enriched errors.
6. Replay ten supplied dialogs; then test action errors, confirmation/idempotency and grounding. After voice, test denied microphone, empty audio, STT/TTS failures and text fallback without state loss.

Before major feature expansion: all 104 cases produce valid outputs, the reference evaluator runs without schema changes, errors are inspectable and recorded primary accuracy is at least 80%. Never use utterance IDs/expected labels at runtime. See [HTTP contract](contracts/http-api.md) and [data model](data-model.md).
