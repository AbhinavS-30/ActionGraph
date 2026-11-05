# Optional demo narration

The checked-in MP4 is silent. This script is optional and has not been recorded.
Scene timings match the 2:03 captioned API replay. Speak naturally; captions
already carry the technical details.

| Time | Suggested narration |
| --- | --- |
| 0:00–0:07 | ActionGraph turns supported meeting commitments into action items you can inspect, review, and save locally. |
| 0:07–0:17 | A transcript enters the FastAPI API. Rules propose items, source checks preserve exact evidence, and a person reviews the result. SQLite persistence is optional. |
| 0:17–0:27 | Here is a real local request using synthetic text. Maya promises to review a report tomorrow. Creating a session returns a saved proposal at revision one. |
| 0:27–0:39 | Each proposal includes the action, owner, deadline, and exact supporting sentence. Tomorrow remains relative text. Exact evidence makes inspection possible; it does not establish that the interpretation is correct. |
| 0:39–0:50 | Supported adjacent requests can also become proposals when the named person explicitly accepts the matching task. This example preserves both lines as evidence. |
| 0:50–1:02 | Confirming creates a separate reviewed copy and advances the revision. The original proposal remains unchanged. Confirmation records a review decision; it does not mean the task has been completed. |
| 1:02–1:12 | Repeating an update with the old revision returns a conflict. This prevents an outdated client from overwriting newer review work. |
| 1:12–1:22 | After restarting the temporary server against the same database, the saved response is identical. The review survives the process restart. |
| 1:22–1:31 | Blank input returns a validation error. The API rejects it instead of creating an empty session. |
| 1:31–1:43 | This ownerless statement is a known omission: rules return no items. Empty output does not prove there are no commitments, and the current review API cannot add a missed proposal. |
| 1:43–1:55 | Evaluation is small and synthetic. First-run results and an observed-case replay are reported separately. Passing tests verify software contracts, not general extraction accuracy. |
| 1:55–2:03 | The public repository includes architecture diagrams, setup instructions, tests, and limitations. ActionGraph is a local portfolio project with experimental model support. |
