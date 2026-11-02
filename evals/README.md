# Extraction evaluation design

## Dataset

`cases.json` contains ten hand-labeled synthetic development cases. Labels were
written before running the model on these cases. They cover explicit commitments,
accepted, refused and unanswered requests, suggestions, unknown owners,
unspecified deadlines, dependencies, relative deadlines, and mixed discussion.
Each case includes an expected `ExtractionResult` and a labeling rationale.
These cases are a small development set, not an independent benchmark or evidence
of performance on real meetings. Do not tune on them and call them held-out data.

## Matching rubric

Review each system's proposed items against each case's labels. Pair items
one-to-one by task meaning, independent of owner and deadline. Equivalent wording
is acceptable only if it preserves the work, object, scope, and any dependency.
For example, "Send budget" can match "Send the budget"; "Review budget" cannot.
An omitted dependency prevents a task match. Ignore list order. If several
pairings are possible, choose the pairing with the most task matches; break ties
by the most correct owner/deadline fields, then label order and prediction order.
Record pairings and reasons for human decisions so the scores are auditable.
No model-based judge or substring-only task scoring is planned.

- A paired task is a task true positive (TP). Each unmatched prediction is a
  false positive (FP); each unmatched label is a false negative (FN). Duplicate
  predictions can match a label only once; remaining duplicates are FP.
- Owner and deadline are scored separately on paired tasks. Compare their exact
  label values, including null. Deadline wording must remain unchanged: a
  converted date or "Friday" instead of "tomorrow" is a deadline error.
- Evidence presence requires a nonblank exact substring of the transcript.
  Separately, human review checks whether it supports the task, owner, deadline,
  and acceptance. For accepted requests it must include both request and
  acceptance in one contiguous excerpt. A different supporting excerpt from the
  label is allowed. Quote presence alone does not establish correctness.
- Every returned item must have `needs_review`. A fully correct paired item
  needs correct owner, deadline, supporting evidence, and review status as well
  as a matching task. Report this count separately from task TP.
- Suggestions, refusals, ambiguous commitments, and unanswered requests have no
  labels. Extracting them is FP. A correct empty result on an empty-label case
  is recorded as a correct negative case, without adding a TP.

## Metrics and failures

Report micro task precision `TP / (TP + FP)` and recall `TP / (TP + FN)` by summing
counts across all cases. Report counts with every rate. A zero denominator is
`N/A`, not perfect performance. Report owner/deadline error counts over paired
tasks, fully correct paired items, and correct negative cases over all
empty-label cases. Report results by category as well as in aggregate.

Record every attempted case, including connection errors, timeouts, malformed
JSON, schema failures, and evidence rejection. Report successful calls/attempts
alongside task metrics. On a failed call, no items were delivered: all its labels
count as FN and the failure is not a correct negative. There are no delivered FP
on that call. Do not silently discard failures or interpret them as successful
empty results.

For model diagnostics, retain raw generated text locally using only these
synthetic inputs. Report parse/schema validity on responses actually received,
and fabricated (nonmatching) evidence items over schema-valid generated items,
including items rejected by the service. Keep these diagnostics separate from
delivered-result metrics; the service itself rejects unsupported evidence.

Measure wall-clock duration around the full extraction call for every attempt.
Report individual durations, successful-call median and maximum, and failed-call
durations separately. Record model name/digest, Ollama version, machine details,
generation settings, repository commit, and whether the model was warm or cold.
Do not hide loading time or retry silently. Current runs use the configured `num_predict` cap (default 1024) with other
Ollama defaults; repeated runs may vary. Historical runs retain their original
settings. The first measured run and provisional Codex semantic review are in [results/REPORT-8dc8253.md](results/REPORT-8dc8253.md); human adjudication is pending.

## Running collection

Run from the repository root. Output is JSON Lines: one metadata record followed
by one baseline and one model attempt per case. Each attempt has status and
wall-clock duration; success includes a result, while failure includes an error
type/message and no result. Model attempts also retain raw HTTP responses so
invalid generated text and rejected evidence remain inspectable. Only the fixed
synthetic dataset is loaded.

```bash
.venv/bin/python -m evals.run --baseline-only --output /tmp/actiongraph-baseline.jsonl
.venv/bin/python -m evals.run --output /tmp/actiongraph-comparison.jsonl
```

Output files must not already exist; choose a new name for each run. Writes are
flushed after each attempt so completed records survive a later interruption.
No automatic retries or warmup calls occur. Ctrl-C stops the run; incomplete runs
must be described as incomplete. Model inventory and Ollama version are collected
when available; metadata errors are recorded without discarding attempts. Initial
model warmth is explicitly unknown. Raw Ollama envelopes include load durations
when supplied by Ollama. No new dependencies are needed.

The baseline matches only entire `Name: I will ... .` lines (with a final period,
no space required before it) and splits the work on the first ` by ` to obtain a
deadline. It does not understand acceptance, negation, ambiguity, or semantics.
It leaves `tomorrow` in the action with a null deadline when no `by` occurs, and
misses ownerless commitments and requests accepted using other wording. These
limitations must be scored rather than repaired using expected labels.

The runner calls the existing extraction function directly, not the API. It
records source commit, dirty-tree flag, dataset/instruction hashes, platform,
model inventory/digest, Ollama version, and effective runtime/generation settings. Dirty
source runs are exploratory; use a clean committed source tree for a reportable
comparison. The runner does not calculate semantic scores. Review saved outputs
and record one-to-one task pairings under the rubric above before reporting
precision, recall, or fully correct items. A baseline-only CLI smoke run has been
verified; the first full model comparison is retained under `results/`, with provisional Codex semantic decisions pending human adjudication.

The [November 1 strict-contract run](results/REPORT-b7bf4c4.md) includes six
validation failures. It demonstrates why successful-call rates and delivered
precision must be reported together. Rejected raw outputs remain available.

The [JSON-null candidate](results/REPORT-fcc91ec.md) was evaluated and rejected;
its raw outputs and semantic review are preserved while the previous prompt is
restored in application code. More completed calls did not mean better task
extraction.

## Experimental list contract

`--contract lists` selects an evaluation-only adapter. Owner and deadline are
required lists of at most one string: `[]` explicitly means unknown; `["Maya"]`
means a known value. The adapter maps those representations to the unchanged
public string-or-null contract, validates it, and checks evidence. `["null"]`,
multiple values, scalar strings, and JSON null at this model boundary are errors,
not silently repaired. Review status is assigned by the application.

```bash
.venv/bin/python -m evals.run --contract lists --output /tmp/actiongraph-lists.jsonl
```

The experiment changes model schema, matching prompt representation, and removes
model control of review status; this is a contract experiment, not a claim that
only prompt wording changed. It is not enabled in `POST /extract`. Metadata
records the variant and its actual instruction hash. Results require separate
semantic review under the same rubric. The [first measured list experiment](results/REPORT-2ccb473.md) completed 9/10 calls but still delivered four false-positive tasks. It is not adopted in the API.

## Experimental commitment decisions

`--contract decisions` uses a first model call to return action/evidence candidates
and a decision enum: committed, declined, suggested, unanswered, or ambiguous.
Every candidate quote must match the transcript exactly. Only committed candidates
enter a second call, which generates fields using the list contract. If there are
no committed candidates, the adapter returns an empty list without a second call.
Final quotes must equal selected candidate quotes, with one output per selected
candidate; missing or extra references fail the attempt. The public parser and
evidence rules remain enforced. This is not a semantic proof: classification,
coverage, field attribution, and unsupported interpretations can still be wrong.

The collector retains both raw envelopes in call order and measures combined
wall-clock duration; failures at either stage remain failures. Metadata records
the decisions variant and the hash of both instruction strings concatenated.
The API is unchanged. Command: `.venv/bin/python -m evals.run --contract decisions
--output /tmp/actiongraph-decisions.jsonl` (enter as one shell line). The [first measured run](results/REPORT-82df13e.md) excluded the three negative
cases but produced zero fully correct items because of field errors. This adapter
is not adopted in the public API. No new dependency, model, service, or paid API is used.

## Fresh validation set

`validation-cases.json` contains ten synthetic cases and eight expected items,
written after development but before running this set through the model. They
cover contractions, recipients versus owners, accepted/refused/unanswered requests,
suggestions, unknown values, dependencies, relative deadlines, and multiple items.
This is a fresh set under the existing rubric, authored with knowledge of prior
failures; it is not an independent external benchmark. Labels and the current
production extractor must be committed before the first run. Preserve the first
run, including failures. Do not tune on these outputs and continue calling the
set untouched; later changes require a separately identified evaluation.

```bash
.venv/bin/python -m evals.run --dataset validation --output /tmp/actiongraph-validation.jsonl
```

The default remains `--dataset development`. Only these two synthetic dataset
choices are supported; the collector records the selected filename and SHA-256.
Fixture checks validate both sets against the schema, quote presence, and current
field-provenance policy; these checks do not measure model extraction quality.

The [first validation results](results/REPORT-validation-d21e6b6.md) are now
recorded without post-run label/prompt changes. These cases are no longer
untouched; preserve the first run and identify later tuning explicitly. The
model underperformed the simple baseline on this sample.

## Example-free prompt experiment

`--contract concise` uses the public schema, single model call, exact evidence
check, field-provenance check, and needs_review enforcement. Only the extraction
instructions change: no illustrative names/tasks/dates and exclusion rules first.
This variant is evaluation-only. Before inspecting outputs, the planned comparison
is two development repetitions in public/concise/public/concise order, with no
retries, setting changes, or validation-set rerun. Sampling remains at defaults;
this tiny paired comparison cannot prove causality or generalization.

Candidate selection criteria (not release accuracy guarantees): zero delivered
false positives in both candidate runs; at least as many fully correct items and
no more failed calls than its paired public run; a strict fully-correct-item
improvement in at least one pair. If these are not met, do not adopt. Passing them
would still require independent review and separately frozen validation.

The [paired prompt results](results/REPORT-1cd4164.md) failed the selection
criteria. The concise candidate remains evaluation-only, with all four runs
preserved. Neither completion rate nor quote presence established correct task
meaning, and the public prompt also showed substantial run-to-run variation.

## Product rules engine

`--contract rules` evaluates the new deterministic demo engine, separately from
the unchanged historical baseline. No model inventory or generation requests occur;
metadata records model_used=false. The default public contract option in this
collector still measures experimental Ollama, whereas the API now defaults to
rules. Do not confuse these paths. Both datasets have already been inspected and
are development data for this rule implementation; future validation needs a new
frozen set.
