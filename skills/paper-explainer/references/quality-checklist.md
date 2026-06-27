# Quality Checklist

Use this before declaring a storyboard or video complete.

## Story

- The video starts with motivation, not just methods.
- The task/setup is explained before results.
- The viewer knows what the authors are trying to convince them of.
- The synthesis connects figures into the main claim.
- Limitations or remaining uncertainty are stated.

## Figures

- Each main figure scene used the caption and nearby Results text.
- Each important panel explanation says what was plotted.
- Axes, measured variables, groups/colors/conditions, and alignment events are explained when relevant.
- The narration states what pattern appears before interpreting it.
- The narration distinguishes data from author inference.
- Full-figure views are supplemented with crops or highlights when panel details matter.

## Video

- On-screen bullets are short and do not duplicate full narration.
- Captions are readable and do not overlap important figure content.
- Highlight boxes guide attention to the discussed panel.
- Voiceover duration matches scene duration with a short hold.
- The rendered MP4 has video and audio streams.
- Representative frames are checked visually.
- Audio levels are checked with `ffmpeg volumedetect`.

## Repository Hygiene

- Generated PDFs, OCR outputs, audio, video, figure crops, and page renders are not staged.
- API keys are not copied into the repo.
- `npm run validate:storyboard` passes before rendering from a changed storyboard.
