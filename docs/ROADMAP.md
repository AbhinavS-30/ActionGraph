# Delivery roadmap

Initial demo target: November 3, 2026.

1. **Validation foundation — implemented:** transcript validator, output contract, JSON parser, exact evidence checker, and component tests.
2. **Local inference — in progress:** standalone text client and simulated failure tests implemented; extraction policy and prompt builder implemented; optional schema-constrained requests and parser-boundary tests implemented, with one live structured-output smoke check. Connect Ollama llama3.2:3b; test valid responses, unavailable model, timeouts, malformed output, and schema failures.
3. **Extraction orchestration — implemented as a Python function:** connected stages, unsupported-evidence failure, and review-state enforcement. Ambiguity and relative-date semantics are instructed through the prompt and have observed failures in the first development comparison. Do not silently invent or repair values.
4. **API demo — implemented; demonstration verification in progress:** text submission and structured results, HTTP error responses, and documented curl and interactive API examples.
5. **Evaluation — in progress:** ten synthetic development transcripts labeled and matching rubric documented in `evals/README.md`; collector and deterministic baseline implemented; first model comparison and provisional Codex semantic review recorded; human adjudication pending. Compare a simple baseline with model extraction, and report measured precision, recall, fabricated evidence, schema validity, and latency. Distinguish explicit from ambiguous commitments.

Completion requires reproducible setup, a working local demonstration, measured evaluation results, and documented limitations. Audio, calendar integrations, polished dashboards, and cross-meeting memory are deferred.

Local-release and public-service requirements are separate in
`docs/RELEASE.md`. Public hosting and production readiness are not implemented.

Approved public presentation: a polished project page and recorded local demo,
with extraction staying local. Build the presentation after local reliability
and release checks; do not describe it as a hosted inference service.

November 1 strict-contract run: six of ten model calls failed string-null
validation. Next quality work targets generation-contract alignment before
untouched evaluation; see `evals/results/REPORT-b7bf4c4.md`.

November 2: production field-text provenance checks now reject non-null owners
and deadlines absent from item evidence. This is textual enforcement, not a
semantic correctness claim. Actual browser verification and untouched evaluation
remain pending.

November 2 demo smoke verified the running Uvicorn TCP path, Swagger markup,
OpenAPI, blank-input rejection, and one real-model extraction. The user then
verified Swagger Try it out via screenshots showing actual 200 and 422 responses.
Automated browser access remained unavailable. Reproducible
steps and presentation limits are in `docs/DEMO.md`; no recording is complete.

First fresh validation completed November 2: model task precision 50% (2/4),
recall 25% (2/8), and 5/10 call success. Baseline exceeded those results. Current
quality is a blocker for production-ready claims; see the preserved validation
report before deciding release messaging or further tuning.

Approved product pivot: the local API now defaults to a narrowly scoped rules
engine; experimental Ollama is explicitly opt-in, with no silent fallback.
Responses identify the engine and its limitations. See `docs/RULES.md` for grammar
and response-shape migration. Existing baseline/model evaluations remain
unchanged; the new rules engine requires its own recorded comparison.

November 3 rules-focused validation: 4 TP, 1 FP, 5 FN on nine labels in twelve
fresh synthetic cases; cross-line cancellation produced an extra task. Results
and scope must accompany the public project page/demo. No production-ready or
real-meeting accuracy claim is supported by this sample.

Rules v2 adds explicit same-speaker matching-task cancellation under a documented
policy; broader correction/reassignment remains unsupported. Per the user’s
instruction, public page creation and demo recording are deferred until product
readiness. Replay with original labels is recorded: cancellation false positive removed, five broader-set misses remain. Rules v3 now implements bounded adjacent matching-verb acceptance; 214 tests and Ruff pass. Observed-case replay completed with original labels: one additional correct request per set, other outputs unchanged. November 4: rules v4 implements bounded two-task direct promises with explicit deadline scope and independent single-task cancellation. 233 tests and Ruff pass. Replay with original labels now records 7/0/2 on the rules-focused set; the other sets remain 7/0/1 each. Next evaluate frozen v4 on new pre-labeled cases; public page and recording remain deferred.

November 4 first frozen-v4 validation recorded: 6 TP / 1 FP / 5 FN on eleven
labels across fourteen cases. No post-run source or label changes. Broader
withdrawal still produces a false positive. Next audit local release requirements
and scope against the report before selecting more implementation work.

November 4 release audit completed in RELEASE.md. 234 tests, Ruff, pip check and
current rules TCP smoke pass. Latest CI queried is queued. Next close blank
output-field validation, define local review/correction behavior, then finish
release verification and packaging before the page/video. No completion date
or general extraction reliability is established by this audit.

November 4 nonblank output-field validation implemented: blank strings fail the
shared schema before evidence/provenance validation; model API maps to 502 with
no partial result. 259 tests and Ruff pass. Next define bounded local review
behavior before implementing persistence/endpoints.

November 4 stateless POST /review implemented with preserved originals, explicit
confirm/correct/reject decisions and exact evidence. 284 tests and Ruff pass.
Persistence remains deferred pending retention/identity/version policy. Next
verify extract-to-review over TCP before expanding review scope.

November 4 extract-to-review TCP workflow verified for source 5acb10e, including
confirm/correct/reject and invalid-batch failures. STORAGE.md defines opt-in local
SQLite, immutable proposals, revisions, atomicity and explicit retention/deletion.
Next implement persistence under that policy; saved-session routes do not exist yet.

November 4 opt-in SQLite saved sessions implemented under STORAGE.md: immutable
rules proposals, stable IDs, latest review, revision conflicts and atomic deletion.
303 tests/Ruff pass; real TCP restart persistence and conflict/delete checks pass.
Next current browser interaction and remaining release checks. No production
readiness claim; broader semantic failures and independent review remain open.

November 4 clean install verification completed for source 252c776: fresh Python
3.12.13 environment and committed source pass 303 tests/Ruff/pip check. Exact CI
job is queued; browser automation unavailable. Manual Swagger checklist prepared;
current visual interaction remains pending. No public presentation started.
