# Rules mode v4

Rules mode is the default local demo engine. It requires no running Ollama and
does not call a model. The API explicitly labels `engine: rules` and returns a
scope notice in `limitations`. `engine: ollama` opts into the existing experimental
model path; no automatic fallback or mixing of engines occurs.

## Supported grammar

One task, or two tasks under the v4 policy below, per speaker-labelled line starting exactly with `I will`, `I'll`, or
`I’ll`, followed by work beginning with a supported verb. Speaker text before
the colon is the owner; the recipient is never substituted for the speaker.
Original lines, including boundary spaces, are retained as exact evidence.
Supported initial verbs:

`send email review export update investigate notify publish upload check prepare
validate test archive refresh revise deploy migrate inspect document share write`

All items are `needs_review`. An optional final period is removed from the action
only; evidence is untouched. Lines containing internal sentence punctuation,
unsupported compound/alternative clauses, negation, tentative or conditional markers are
conservatively skipped. Tasks with unresolved demonstratives/pronouns in the
main clause are skipped. This is a fixed grammar, not general language reasoning.

Recognized trailing deadlines: `today`, `tomorrow`, weekdays, `next` + weekday,
and valid `YYYY-MM-DD` dates, optionally introduced by `by` or `on`. Original
deadline wording/case is preserved; no relative-date normalization occurs.
Unsupported timing introduced by `by`, `on`, `at`, `within`, `before`, or `until`
causes the line to be skipped rather than guessed. Other unsupported phrasing
may remain in action text or be missed; this is not a full temporal parser.

An optional `after ...` dependency is retained in the action. Its timing is not
borrowed as the task deadline. A supported deadline before that dependency may
be extracted independently. Owner/deadline text is checked against evidence.

## Explicit cancellation policy

Process lines in transcript order. Recognize `Name: I will not ...`,
`Name: I won't ...`, or `Name: I won’t ...`, optionally with `Correction, `
before the first-person phrase. The same bounded task grammar is used for
promises and cancellation targets, so conditional or pronoun-only targets are
not guessed.

A cancellation removes earlier items only when the speaker label matches exactly
after trimming its edges, and task wording matches after case folding and internal
whitespace collapsing. Supported task deadlines are removed for task comparison;
dependencies remain part of the comparison. Output evidence and fields are never
normalized by this comparison.

- Without a deadline, cancel all earlier same-speaker items with that task wording.
- With a deadline, cancel only earlier matching tasks with the same stated deadline
  (case/whitespace comparison only, no calendar normalization).
- Do not cancel another speaker's work, different task wording, or a different
  dependency. Do not infer aliases or paraphrases.
- A cancellation affects earlier commitments only. A later explicit recommitment
  is kept with its own original evidence.
- Vague withdrawals, pronoun references, reassignment, unsupported timing, and
  other correction phrasing remain outside this policy.

For example, an earlier `Ben: I will publish the guide tomorrow.` is removed by
a later `Ben: Correction, I will not publish the guide.` A later cancellation
limited to Friday does not remove a task stated for Monday.

## Explicit limitations

- Requests outside the adjacent acceptance policy, ownerless agreed work, indirect commitments,
  unsupported verbs, and compounds outside the two-task policy are not handled.
- Pronoun resolution, sarcasm, quotations, cancellations outside the explicit
  policy, reassignment, and meeting-wide semantic consistency are not understood.
  Unsupported later corrections may still invalidate matched work; human review
  remains required.
- Matching a grammar does not guarantee the speaker means a real commitment.
- Empty output means no supported lines matched; it does not prove no work exists.
- Performance on known synthetic datasets is development evidence, not broad
  real-meeting accuracy. The old baseline and model reports remain unchanged.

## API migration

Requests may now include `engine` (`rules` by default, or `ollama`). Successful
responses retain `items` and add required `engine` and `limitations` fields. A
client expecting the previous exact response object should update accordingly.
Old model clients must explicitly send `engine: ollama` to preserve model use.
The model's failure handling and per-process concurrency guard remain; rules
requests can proceed while a model extraction is busy. Runtime configuration is
still validated at application startup.

```json
{"transcript": "Asha: I'll email Ben the agenda by Thursday.", "engine": "rules"}
```

This is a deliberately limited product mode selected after the local model
underperformed the simple baseline. It is not a claim that the model extraction
problem was solved.

## Accepted-request policy (v3)

Support only an immediately adjacent pair: `Requester: Assignee, can you ...?`
(or `could you`) followed by `Assignee: Yes, I will VERB it.` (or `them`,
`I'll`, `I’ll`). Speaker labels must match exactly after edge trimming; requester
and assignee must differ. The repeated verb must match the request verb ignoring
case. The request task must pass the existing bounded parser, including dates
and dependencies. Bare yes, different verbs/speakers, intervening or blank lines,
conditional replies and additional clauses are skipped. This is a fixed local
reference rule, not general pronoun resolution. Both original lines and their
original line separator form one contiguous evidence excerpt. Request deadlines
are preserved verbatim, without conversion; replies cannot override them.
Later explicit cancellations use the same task matching policy as other items.

## Two-task promise policy (v4)

A direct first-person promise may contain exactly two complete task clauses
joined by `and`. Each clause must independently pass the existing single-task
parser and begin with a supported verb. Both items retain the full original
line as evidence and the same speaker as owner, in clause order. Reject the
whole promise if either clause is unsupported; do not return a partial pair.
Object lists, more than two clauses, pronoun-only second objects, alternatives,
conditions, dependencies (`after`) and repeated `I will` remain unsupported.

No deadline is shared by inference. A deadline inside the first clause belongs
only to the first task. If both clauses state deadlines, preserve each locally.
If only the final clause has a deadline, skip the whole promise because its
scope may include both tasks. Undated pairs are supported. Compound requests
and compound negations remain unsupported. A later single-task cancellation
can remove one matching split item without removing the other.
