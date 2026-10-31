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
Do not hide loading time or retry silently. Default generation settings currently
apply; repeated runs may vary. No results have been measured on this dataset yet.

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
model inventory/digest, Ollama version, and default generation settings. Dirty
source runs are exploratory; use a clean committed source tree for a reportable
comparison. The runner does not calculate semantic scores. Review saved outputs
and record one-to-one task pairings under the rubric above before reporting
precision, recall, or fully correct items. A baseline-only CLI smoke run has been
verified; a full model comparison has not yet been collected.
