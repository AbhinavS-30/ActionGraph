# Rules mode v1

Rules mode is the default local demo engine. It requires no running Ollama and
does not call a model. The API explicitly labels `engine: rules` and returns a
scope notice in `limitations`. `engine: ollama` opts into the existing experimental
model path; no automatic fallback or mixing of engines occurs.

## Supported grammar

One task per speaker-labelled line starting exactly with `I will`, `I'll`, or
`I’ll`, followed by work beginning with a supported verb. Speaker text before
the colon is the owner; the recipient is never substituted for the speaker.
Original lines, including boundary spaces, are retained as exact evidence.
Supported initial verbs:

`send email review export update investigate notify publish upload check prepare
validate test archive refresh revise deploy migrate inspect document share write`

All items are `needs_review`. An optional final period is removed from the action
only; evidence is untouched. Lines containing internal sentence punctuation,
compound/alternative clauses, negation, tentative or conditional markers are
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

## Explicit limitations

- Requests accepted across lines, ownerless agreed work, indirect commitments,
  unsupported verbs, and compound tasks are not handled.
- Pronoun resolution, sarcasm, quotations, cross-line cancellation/reassignment,
  and meeting-wide semantic consistency are not understood. Later corrections
  can invalidate a previously matched line; human review remains required.
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
