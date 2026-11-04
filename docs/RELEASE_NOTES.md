# Draft v0.1.0 local release notes

Status: candidate source package only. No v0.1.0 tag, GitHub Release, public
project page or recorded video has been published. Implementation checkpoint:
351b3a0. The package's Git commit identifies documentation revisions as well.

ActionGraph turns supported text commitments into proposed action items with
exact evidence, explicit unknowns and human review. The default local rules v5
engine supports a bounded grammar; local Ollama llama3.2:3b is experimental and
explicitly selected. No model service is needed for the default workflow.

## Included

- FastAPI extraction, health, stateless review and optional SQLite saved sessions.
- Confirm/correct/reject decisions with preserved original proposal/evidence.
- Stable saved proposal IDs, revision conflicts, atomic review/deletion and
  persistence across restart. Latest review only.
- Input/output validation, documented API failures, 2 MiB request-body and
  1 MiB generation-envelope caps, token/network/model-slot/write-lock limits.
- Pinned dependencies, CI, 346 tests, synthetic labels, raw evaluation results
  and disclosed failed model/prompt experiments.

## Before using

Use Python 3.12 and follow README setup from the repository root. Run one worker
on loopback with synthetic/public text. Enable saved sessions only by explicitly
setting ACTIONGRAPH_DB_PATH; see STORAGE.md for retention/deletion. Use Swagger
at /docs. No authentication, automatic backup, full review history, listing,
audio, calendar integration or public inference deployment is included.

## Known quality and operational limits

The first fourteen-case rules validation returned 6 correct tasks, 1 extra and
5 misses across eleven labels. Targeted v5 replay on those observed cases removes
the extra task; five misses remain. Results are provisional Codex review, not
independent human validation or general meeting accuracy. Every item needs review;
an empty result is not proof of completeness. Confirmed records a caller decision,
not automated correctness or completion of work.

Hard total-duration, API output-byte, disk quota and distributed limits remain
unimplemented. Existing model timeouts are per network operation. Saved data is
retained until explicit deletion; deletion is not secure erasure from backups.
See RELEASE_CANDIDATE.md for evidence, exact gate status and remaining work.

## Validation

Implementation 351b3a0: 346 tests/Ruff and GitHub CI pass. A separate pinned
Python environment also passes against its committed-source export. Latest-code
TCP checks cover saved-session restart/conflict/deletion and oversized fixed/
chunked uploads. User screenshots verified the earlier saved-session browser
workflow. Response-limit tests use simulated envelopes; no new real-model quality
run is claimed. Later documentation-only package revisions require their own CI
observation before a release tag is finalized.
