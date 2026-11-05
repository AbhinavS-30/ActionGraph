# Local demo recording storyboard

Prepared November 5, 2026. A [captioned recorded API replay](media/actiongraph-demo.mp4) is now available.
It is silent and rendered from real API responses; it is not a browser screen
recording. The following storyboard remains available for a future Swagger capture.
Position the project as a local release candidate with explicit review, measured
limitations and reproducible engineering. Do not call it production-ready or
claim broad extraction accuracy. The public repository can accompany the video.

## Preparation

Use the disposable saved-session setup in README.md and open /docs. Keep the
recording focused on Swagger and this project's diagram, with synthetic text.
Use a readable zoom and prepare request bodies before recording. Record actual
executed responses; if using saved footage, label it recorded. Model mode is
experimental and is not needed for this demonstration.

## Suggested 2–3 minute sequence

| Time | Screen/action | Explanation |
| --- | --- | --- |
| 0:00–0:20 | README architecture diagram | ActionGraph proposes tasks with exact evidence, then lets a person review them. Everything runs locally. |
| 0:20–0:50 | POST /sessions, transcript below | Show 201, owner Maya, tomorrow preserved, exact evidence, needs_review, session ID and revision 1. |
| 0:50–1:20 | PUT /sessions/{id}/review | Confirm the proposal. Show revision 2, original needs_review and separate reviewed confirmed copy. |
| 1:20–1:40 | Repeat review with expected_revision 1 | Show 409. Explain that stale requests cannot overwrite newer decisions. |
| 1:40–2:10 | GET saved session; optionally pre-rehearsed restart | Show persisted state. If showing restart, actually restart with the same database. |
| 2:10–2:35 | Evaluation table or known missed input | Explain that a valid quote does not prove completeness. The known-set replay still missed five labels; human review cannot add missing work yet. |
| 2:35–2:50 | Tests/CI and repository | State 346 tests, pinned setup, stored evaluations and local release-candidate scope. Invite readers to inspect the code. |

Suggested create body:

```json
{"transcript":"Maya: I will review the report tomorrow."}
```

Suggested saved review body (use returned ID in the path):

```json
{"expected_revision":1,"decisions":[{"proposal_index":0,"decision":"confirm"}]}
```

Known missed input for POST /extract:

```json
{"transcript":"Decision: The access roster will be updated. No owner or date was assigned."}
```

Expected current behavior is an empty rules result despite agreed work. Explain
that this is an omission, not a correct no-task decision. This example is already
observed and is illustrative, not new validation. A more complete mixed example
and its actual rehearsal observations are in WALKTHROUGH.md.

## Sharing sequence

1. Review the recording against what actually happened and the stated scope.
2. Add a real video link to README only when an accessible artifact exists.
3. Prepare the LinkedIn text around the problem, architecture, evaluation-driven
   rules/model decision, review/persistence, and one honest limitation.
4. Share the repository and video. An additional public project page is approved
   presentation scope but has not been built; it can follow as a separate artifact.
5. Publish only on the user's explicit instruction. No post is sent by this guide.

A suitable description is: "A local transcript-to-action review API with exact
source evidence, persisted review and revision-safe updates, evaluated against a
simple baseline." Avoid claiming users, deployment reliability, independent
accuracy or time savings that were not measured. Test count is implementation
verification, not the number of correctly interpreted meetings.
