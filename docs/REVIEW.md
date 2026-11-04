# Local review contract

The first review step is stateless `POST /review`. Submit the original transcript,
caller-supplied `proposals`, and exactly one decision per zero-based proposal index.
This service does not authenticate reviewers or verify that submitted proposals
came from an earlier extraction. Original means the submitted snapshot, not a
server-verified immutable extraction record. No data is saved and no model runs.

Each proposal must have `review_status: needs_review` and an exact nonblank quote
from the transcript. Up to 100 proposals/decisions are allowed. Transcript limits
remain 12,000 characters. Empty proposals with empty decisions are valid; that
means only that this submitted batch was empty, not that the meeting had no work.

- `confirm`: keep the proposal unchanged, or supply a complete `replacement`
  action item. Replacement must retain the exact original evidence and be marked
  needs_review. Correct action, owner or deadline; use null for unknown values.
  Relative deadlines remain original wording; no date normalization. Non-null
  owner/deadline must occur verbatim at word boundaries in the preserved evidence.
  The server sets the returned reviewed item to confirmed.
- `reject`: replacement must be absent/null. Preserve the original proposal in
  the response and return reviewed=null. Rejection does not delete its snapshot.

Every output record includes proposal_index, decision, original and reviewed.
Records follow original proposal order, regardless of decision input order.
Original snapshot stays needs_review; reviewed is a separate copy. No item is
silently omitted. Missing, duplicate, out-of-range indices, edited evidence,
unconfirmed input violations, unsupported corrected fields or invalid schemas
fail the entire request with 422 and no partial review response. Rejected proposals need valid source quotes but may have wrong field attribution:
that is a reason to reject. Confirmations must pass field-text checks.

Confirmation records a caller's explicit decision, not automated semantic proof,
independent adjudication, completion of work or authenticated approval. Action
wording can be edited without exact substring matching; human judgment remains
responsible for meaning. This endpoint cannot add missed tasks, split/merge items,
change evidence or resume saved reviews. Persistence, identities, stable IDs,
version conflicts, deletion/retention and a custom review UI are separate work.

## Example

```json
{
  "transcript": "Maya: I will send Leo the report by Friday.",
  "proposals": [{
    "action": "Send Leo the report", "owner": "Leo", "deadline": "Friday",
    "evidence": "Maya: I will send Leo the report by Friday.",
    "review_status": "needs_review"
  }],
  "decisions": [{
    "proposal_index": 0, "decision": "confirm",
    "replacement": {
      "action": "Send Leo the report", "owner": "Maya", "deadline": "Friday",
      "evidence": "Maya: I will send Leo the report by Friday.",
      "review_status": "needs_review"
    }
  }]
}
```

Submit through POST /review in Swagger. The response keeps original.owner=Leo
and original.review_status=needs_review, while reviewed.owner=Maya and
reviewed.review_status=confirmed. persisted=false. To confirm unchanged, omit
replacement. To reject, set decision=reject and omit replacement.

The current HTTP workflow has been [verified over TCP](DEMO.md). Optional saved
sessions now follow [the storage policy](STORAGE.md) through separate routes.
They do not change this stateless endpoint's guarantees.
