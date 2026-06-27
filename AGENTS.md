# Paper2Video Agent Instructions

This repo turns academic paper PDFs, mostly neuroscience and machine-learning papers, into faithful video explainers using paper figures, concise on-screen bullets, narration, and evidence references.

## Core Decisions

- Use Remotion for deterministic React-based video rendering.
- Use Mistral OCR as the default parser for paper text, captions, and section flow.
- Use PDF page rendering/cropping or publisher figure assets for video-ready figures.
- Use Sarvam TTS for voiceover.
- Use Sarvam Document Intelligence only as a secondary layout/parser comparison unless a task asks otherwise.
- Keep GROBID optional for metadata, references, and TEI-style structure.

## Files to Commit

Commit source, scripts, schemas, skills, README updates, package manifests, and small hand-written examples.

Do not commit:

- paper PDFs or source documents
- OCR/parser outputs
- generated figure crops, page renders, audio, subtitles, or videos
- `data/raw/`, `data/outputs/`, `artifacts/`, or `public/generated/`
- `.env`, `*.env`, `.venv/`, `node_modules/`, or credentials

Use external env files for keys, for example `/home/rka/code/paper2video_v3/.env`. Never copy secret values into this repo.

## Explainer Quality Bar

Do not make a high-level-only figure summary unless the user explicitly asks for a very short overview.

Every real paper explainer must include:

- the motivation: why the paper exists and what prior interpretation it challenges
- the task/setup: what the subject/model does, what is measured, and why the setup can answer the question
- figure-wise claims: what each main figure contributes to the argument
- figure mechanics: what was plotted, axes or variables, groups/colors/conditions, alignment event, and comparison being made
- figure observations: what pattern is visible and what changes
- interpretation: how the observed pattern supports, weakens, or limits the authors' claim
- caveats: what remains uncertain or what the figure does not prove
- evidence references: captions, Results paragraphs, page numbers, figure IDs, and panel IDs

For each figure scene, consult the figure caption and nearby Results text before writing narration. A scene fails review if it only says "they found X" without explaining what was plotted, what the viewer should notice, and how the plot makes the point.

## Workflow

1. Parse the paper with Mistral OCR.
2. Extract title, abstract, introduction, discussion, figure captions, and Results paragraphs around each figure.
3. Obtain figure assets from publisher/arXiv/source when possible; otherwise render PDF pages and crop figure regions.
4. Build a storyboard with motivation, task/setup, figure setup, panel explanation, figure claim, synthesis, and limitations.
5. Render with Remotion.
6. Generate Sarvam TTS and update scene durations.
7. Render the voiceover MP4.
8. Verify MP4 duration, audio stream, audio levels, and representative frames.

Use subagents when useful to preserve context, especially for separate reading/story-writing and Remotion implementation passes. Keep the final storyboard evidence-backed.

## Commands

Install dependencies:

```bash
npm install
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Install the repo skill into Codex:

```bash
npm run skill:install
```

Validate storyboards:

```bash
npm run validate:storyboard
```

Generate Sarvam voiceover and render the prototype:

```bash
npm run tts:prototype
npm run render:prototype:voiceover
```

Verify a rendered MP4:

```bash
ffprobe -v error -show_entries format=duration,size -show_streams -of json artifacts/path/to/video.mp4
ffmpeg -hide_banner -i artifacts/path/to/video.mp4 -af volumedetect -f null /dev/null
```

## Current Prototype Notes

The earlier 95.7 second voiceover video was only a smoke test. The longer 4:18 task/motivation prototype is the baseline for judging explanation quality, but future videos should add more zoomed panel scenes and stronger caption-grounded plot explanations.
