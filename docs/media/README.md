# Recorded API replay

[Watch/download the MP4](actiongraph-demo.mp4). Duration 2:03; 1280×720 H.264;
silent, with captions. No voiceover or browser screen capture is included.

The slides replay selected responses from actual local HTTP requests against
ActionGraph at source commit `91c2590`. Synthetic inputs only. A disposable
SQLite database and temporary servers were removed after capture. Ollama was
not called; the demo uses rules v5. Presentation cards summarize selected fields
and do not purport to show every response field.

- [Full execution trace](demo-execution.json): actual requests/results and restart comparison.
- [Scene content](demo-scenes.json): captions and selected response excerpts.
- [Video verification](demo-video-qa.json): duration, tracks, dimensions, size and decoded timestamps.
- [Poster](demo-poster.png): decoded from the finished video at 3 seconds.

Native Swift CoreGraphics/CoreText and AVFoundation rendered the replay without
adding application dependencies. Five frames decoded successfully at 3, 32, 56,
96 and 119 seconds; representative render and encoded frames were visually
inspected. These checks verify the artifact, not extraction accuracy. The video
includes a known missed task and distinguishes first-run evaluation from replay.

This artifact accompanies main's documentation; the existing rc.1 tag is unchanged.
