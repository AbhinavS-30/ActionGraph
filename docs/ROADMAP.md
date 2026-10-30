# Delivery roadmap

Initial demo target: November 3, 2026.

1. **Validation foundation — implemented:** transcript validator, output contract, JSON parser, exact evidence checker, and component tests.
2. **Local inference — in progress:** standalone text client and simulated failure tests implemented; extraction instructions and structured output remain planned. Connect Ollama llama3.2:3b; test valid responses, unavailable model, timeouts, malformed output, and schema failures.
3. **Extraction orchestration — planned:** connect the processing stages; define unsupported-evidence behavior, ambiguity handling, and relative-date policy. Do not silently invent or repair values.
4. **API demo — planned:** expose text submission and structured results with useful error responses and documented examples.
5. **Evaluation — planned:** label at least ten short synthetic transcripts, define a matching rubric, compare a simple baseline with model extraction, and report measured precision, recall, fabricated evidence, schema validity, and latency. Distinguish explicit from ambiguous commitments.

Completion requires reproducible setup, a working local demonstration, measured evaluation results, and documented limitations. Audio, calendar integrations, polished dashboards, and cross-meeting memory are deferred.
