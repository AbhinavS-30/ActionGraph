# Delivery roadmap

Initial demo target: November 3, 2026.

1. **Validation foundation — implemented:** transcript validator, output contract, JSON parser, exact evidence checker, and component tests.
2. **Local inference — in progress:** standalone text client and simulated failure tests implemented; extraction policy and prompt builder implemented; optional schema-constrained requests and parser-boundary tests implemented, with one live structured-output smoke check. Connect Ollama llama3.2:3b; test valid responses, unavailable model, timeouts, malformed output, and schema failures.
3. **Extraction orchestration — implemented as a Python function:** connected stages, unsupported-evidence failure, and review-state enforcement. Ambiguity and relative-date semantics are instructed through the prompt and remain unevaluated. Do not silently invent or repair values.
4. **API demo — implemented; demonstration verification in progress:** text submission and structured results, HTTP error responses, and documented curl and interactive API examples.
5. **Evaluation — in progress:** ten synthetic development transcripts labeled and matching rubric documented in `evals/README.md`; runner and measurements pending. Compare a simple baseline with model extraction, and report measured precision, recall, fabricated evidence, schema validity, and latency. Distinguish explicit from ambiguous commitments.

Completion requires reproducible setup, a working local demonstration, measured evaluation results, and documented limitations. Audio, calendar integrations, polished dashboards, and cross-meeting memory are deferred.
