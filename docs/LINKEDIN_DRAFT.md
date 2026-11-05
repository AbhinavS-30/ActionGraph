# LinkedIn draft

Status: prepared for review; not posted. Upload `media/actiongraph-demo.mp4`
as the video attachment, then paste the text below. The MP4 is silent and captioned.

---

I've built ActionGraph: a local tool that turns supported meeting commitments
into structured action items with source evidence and an explicit human review step.

The engineering question behind it: how do you make an extraction result easy
to inspect, correct, and save without losing the original proposal?

ActionGraph includes:
• A FastAPI API with strict Pydantic contracts and exact transcript evidence.
• Confirmation, correction, and rejection with separate original and reviewed copies.
• Optional SQLite sessions that survive restarts.
• Revision checks that reject stale updates and deletes.
• 346 passing tests, CI, and documented resource boundaries.

The attached video is a captioned replay of real local API calls using synthetic
data. It shows both the working review flow and a known missed action item.

Rules are the default engine. Local Ollama is experimental: the recorded
validation exposed quality failures, and those results are preserved in the repo.
This is a local engineering portfolio project, with limited language coverage
and provisional evaluation—not a production meeting service.

Code, architecture diagrams, setup, and evaluation evidence:
https://github.com/AbhinavS-30/ActionGraph

I'd welcome feedback on the evidence and review workflow, especially how to make
missed commitments visible to reviewers.

#Python #FastAPI #SoftwareEngineering
