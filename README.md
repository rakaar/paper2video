# Paper2Video

Goal: give the system a neuroscience or machine-learning paper PDF and get back a faithful video explainer with the paper's own figures, short on-screen bullets, narration, subtitles, and traceable evidence.

## Current Decisions

- Use **Remotion** for the video renderer. It gives us a deterministic React-based video pipeline, reusable layouts, captions, figure overlays, and JSON-driven rendering.
- Use **Mistral OCR as the default parser for now**. It handled the test Nature paper well for text flow and figure captions.
- Use **Sarvam TTS for voiceover** for now. We already have the API key in the existing local env files, and the first prototype generated usable English narration.
- Treat the video as a structured presentation, not as pure text-to-video generation.
- Keep the pipeline modular:

```text
PDF or arXiv source
-> paper parsing
-> figure/caption extraction
-> explanation notes
-> storyboard JSON
-> Remotion render
-> TTS narration
-> subtitles
-> MP4
```

- Do not rely on one parser. Academic PDFs are messy enough that we should run a parser bake-off and keep provenance for each claim.
- For figures, prefer publisher/arXiv/source figure files when available. Otherwise render PDF pages and crop figure regions. OCR-extracted image fragments are not reliable enough as final video assets.

## Parser Decision So Far

### GROBID

GROBID is still worth knowing about, but it should not be the only parser for this project.

Where it is probably useful:

- paper metadata
- title/authors/abstract
- section structure
- references and citations
- TEI XML with coordinates when the PDF is well-behaved

Where I do not trust it enough for our main video path:

- clean extraction from complex Nature-style two-column PDFs
- figure assets for presentation use
- figure panel understanding
- OCR-like recovery when PDF text/layout is broken

So the current stance is: **use GROBID as an optional metadata/reference parser, not as the primary paper-to-video parser**. This matches your prior experience that it did not do well.

Local note: I did not run a fresh GROBID test here because this laptop has no Docker, and `tlavos` is reachable but its default shell has no Docker or Java either.

### Mistral OCR

Mistral OCR is a good first parser for full-paper OCR and paper text.

Tested on:

- Paper: `https://www.nature.com/articles/s41467-025-64132-4`
- PDF: `data/raw/nature_s41467-025-64132-4.pdf`
- Size: 19 pages, 3.5 MB

Observed result:

- Completed the full 19-page PDF successfully.
- Produced 19 per-page Markdown files.
- Found the main paper text in readable order.
- Captured all 10 main figure captions as text.
- Extracted 122 image files, but these are mostly fragments/panels, not clean final figures.

Conclusion: **Mistral is currently the best default text/caption parser**. It is not enough by itself for final figure assets.

### Sarvam Document Intelligence

Sarvam is worth keeping as a second parser, especially because it returns block metadata and layout tags.

Tested on the same Nature paper.

Observed result:

- Full 19-page PDF failed because Sarvam has a 10-page maximum per PDF job.
- Splitting into pages 1-10 and 11-19 worked.
- Both jobs completed with all pages succeeded.
- Output included Markdown plus per-page JSON metadata.
- Metadata has useful block coordinates and layout tags such as `paragraph`, `chart`, `image-caption`, `section-title`, `reference`, and `formula`.

Problems:

- Main Markdown embeds huge base64 images.
- Some chart/image descriptions are too verbose and can hallucinate details.
- Requires automatic splitting and recombining for papers over 10 pages.

Conclusion: **Sarvam is useful for layout/block comparison, but not the primary narrative parser yet**. We should keep it in the bake-off and use its coordinates cautiously.

## Current Parser Ranking

For the video explainer pipeline today:

1. **Mistral OCR** for text, captions, and overall paper flow. This is the default for now.
2. **PDF page rendering/cropping** for video-ready figure assets.
3. **Sarvam Document Intelligence** as a comparison parser for block layout and coordinates.
4. **GROBID** only if we need structured metadata, references, or TEI output.

## Voiceover Decision

Use **Sarvam TTS** as the first voiceover provider.

Current implementation:

- Script: `scripts/generate_sarvam_tts.py`
- Input: `src/storyboard.json`
- Output storyboard: `src/storyboard.voiceover.json`
- Audio files: `public/generated/nature_s41467-025-64132-4/audio/scene_*.wav`
- Default voice settings:
  - language: `en-IN`
  - speaker: `anushka`
  - model: `bulbul:v2`
  - pace: `0.9`
  - sample rate: `22050`

The script generates one WAV per scene, measures each clip, then updates the Remotion scene duration so the visuals stay on screen for the spoken narration plus a short hold.

The script stores a fingerprint for each scene's narration and voice settings. If the storyboard text changes, that scene's audio is regenerated instead of silently reusing an older WAV file.

This is good enough for the prototype. Later we should compare voice quality, pronunciation of technical terms, latency, and cost against other TTS providers.

## Explanation Strategy

The hard part is not summarizing the paper. The hard part is explaining the paper in the same causal order a good human presenter would use:

```text
why this question matters
-> what the authors believed was missing or wrong
-> what they measured or built
-> what each main figure proves
-> how the figures combine into the main claim
-> what remains uncertain
```

The system should read papers in passes, not linearly from page 1 to the end. Keshav's three-pass method is a good model: first get the big picture, then understand the content, then go deep where needed. For video, the equivalent is:

1. **Pass 1: paper story**
   - Read title, abstract, introduction, conclusion/discussion, and figure captions.
   - Extract the paper's central claim in one sentence.
   - Identify the intended audience and prerequisite concepts.

2. **Pass 2: figure story**
   - Walk through the main figures in order.
   - For each figure, identify the question it answers.
   - For each important panel, explain what is measured, what comparison is being made, and what changes.
   - Convert the figure caption into viewer-facing language.

3. **Pass 3: verification**
   - Check whether the narration overclaims beyond the figure or text.
   - Check limitations, alternative explanations, and whether the authors' conclusion follows from the data.
   - Attach evidence references to every scene.

### Figure Explanation Template

Each figure should produce this intermediate object:

```json
{
  "figure_id": "Fig. 2",
  "author_claim": "What the authors use this figure to argue.",
  "viewer_takeaway": "One sentence the viewer should remember.",
  "why_it_matters": "How this figure advances the paper's story.",
  "panels": [
    {
      "panel": "a",
      "what_it_shows": "",
      "how_to_read_it": "",
      "result": "",
      "narration": "",
      "highlight_region": ""
    }
  ],
  "caveat": "",
  "evidence": ["page 6", "caption Fig. 2", "Results paragraph mentioning Fig. 2"]
}
```

### Video Explanation Rules

- Start with the problem, not the method.
- Explain only the minimum background needed to understand the next figure.
- Prefer one visual idea per scene.
- Use the actual paper figures whenever possible.
- Use highlight boxes, arrows, and zooms to guide attention.
- Do not read the figure caption aloud. Translate it.
- Keep on-screen text short; narration carries the detail.
- Say what the authors are trying to convince us of.
- Separate "what the data show" from "what the authors infer."
- End with the strongest claim, the practical meaning, and the main limitation.

This matches multimedia learning guidance: reduce irrelevant material, guide attention with visual cues, keep words near the relevant visual region, and synchronize narration with the figure being discussed.

### Target Output Shape

For a normal paper, the default video should be:

```text
0:00-0:30   Hook: what problem is this paper solving?
0:30-1:15   Background: the old model or open question
1:15-2:00   Setup: task, dataset, experiment, or model
2:00-5:30   Main figures, one claim at a time
5:30-6:30   Synthesis: what changed after seeing the figures?
6:30-7:00   Limitations and why the paper matters
```

For short videos, skip methods detail unless it is necessary to trust the result.

## Explanation Sources

Useful references for this content strategy:

- S. Keshav, ["How to Read a Paper"](https://ccr.sigcomm.org/online/files/p83-keshavA.pdf): three-pass reading method.
- PLOS Computational Biology, ["Ten simple rules for reading a scientific paper"](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008032): pick a reading goal, understand the author's goal, ask structured questions, and unpack figures/tables.
- Caltech, ["Composing Effective Figure Captions"](https://writing.caltech.edu/documents/27629/HWC-FigureCaptionHandout.1-2024.pdf): figures need an orienting statement, panel identification, legends, and defined acronyms.
- Taylor & Francis, ["How to write and publish a Plain Language Summary"](https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/how-to-write-a-plain-language-summary/): explain the study, conclusions, and impact so non-specialists can understand it.
- Mayer multimedia learning principles: coherence, signaling, redundancy, spatial contiguity, and temporal contiguity.
- Existing AI paper tools such as [Explainpaper](https://www.explainpaper.com/) and [SciSpace Copilot](https://scispace.com/resources/introducing-copilot-ai-assistant-explains-research-papers/) show that users like highlight-level explanation, follow-up questions, and figure/table/equation explanations.

## Credential Locations

I found both key names here:

- `/home/rka/code/paper2video_v3/.env`
- `/home/rka/code/videomaker/.env`

Keys were not copied into this repo. Use `--env-file /home/rka/code/paper2video_v3/.env` when running local tests.

## Reproduce Parser Tests

Create the venv:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Download the Nature paper:

```bash
mkdir -p data/raw
curl -L -o data/raw/nature_s41467-025-64132-4.pdf \
  https://www.nature.com/articles/s41467-025-64132-4.pdf
```

Run Mistral:

```bash
.venv/bin/python scripts/mistral_ocr.py \
  data/raw/nature_s41467-025-64132-4.pdf \
  --out data/outputs/mistral \
  --env-file /home/rka/code/paper2video_v3/.env
```

Run Sarvam:

```bash
.venv/bin/python scripts/sarvam_document_intelligence.py \
  data/raw/nature_s41467-025-64132-4.pdf \
  --out data/outputs/sarvam \
  --env-file /home/rka/code/paper2video_v3/.env
```

The Sarvam script automatically splits PDFs into chunks of 10 pages or fewer.

## Next Software Step

Build the first real pipeline around this contract:

```json
{
  "paper": {
    "title": "",
    "abstract": "",
    "sections": []
  },
  "figures": [
    {
      "figure_id": "Fig. 1",
      "caption": "",
      "source_page": 4,
      "asset_path": "",
      "panels": []
    }
  ],
  "storyboard": [
    {
      "scene": 1,
      "duration_seconds": 30,
      "visuals": [],
      "bullets": [],
      "narration": "",
      "evidence": []
    }
  ]
}
```

The next decision to test is figure extraction:

- try publisher/Nature figure downloads
- try PDF page rendering plus manual or model-assisted crop detection
- compare against Mistral/Sarvam image fragments

## Prototype Run: Intro + Figures 1-2

Created a first Remotion prototype for the Nature paper:

```text
artifacts/nature_s41467-025-64132-4/video_intro_fig1_fig2.mp4
```

What this prototype includes:

- 59 second MP4
- 1920 x 1080
- intro scene explaining the RPE-versus-performance question
- Figure 1 setup scene
- Figure 1 main-claim scene
- Figure 2 experimental-test scene
- Figure 2 interpretation scene
- bottom narration captions
- evidence notes per scene
- red highlight boxes over the relevant figure regions

What worked:

- Mistral text plus figure captions were enough to write a coherent first explanation.
- PDF page rendering with manual crops produced better figure assets than Mistral image fragments.
- Remotion worked well for deterministic layout and rendering from storyboard JSON.

Current limitations:

- Full-page figures are too small for detailed panel reading.
- Next version should generate zoomed panel scenes, not only full-figure scenes.
- Figure crop and highlight coordinates are currently manual.
- Voiceover exists, but there is no word-level subtitle timing yet.

## Prototype Run With Sarvam Voiceover: Smoke Test

Generated a first Sarvam voiceover version:

```text
artifacts/nature_s41467-025-64132-4/video_intro_fig1_fig2_voiceover.mp4
```

What changed from the silent prototype:

- 5 Sarvam TTS clips, one per scene
- 95.7 second MP4
- 1920 x 1080, 30 fps
- H.264 video plus AAC stereo audio
- audio levels verified with `ffmpeg volumedetect`

Assessment: this was useful as a technical smoke test, but it was too short as an explainer. It skipped too much of the task, motivation, and experimental setup, so the viewer could see decent slides without understanding why the experiment mattered.

## Prototype Run With Task + Motivation

Generated a longer voiceover version:

```text
artifacts/nature_s41467-025-64132-4/video_intro_task_fig1_fig2_voiceover.mp4
```

What changed from the smoke test:

- 12 Sarvam TTS clips, one per scene
- 4:18 MP4
- 1920 x 1080, 30 fps
- H.264 video plus AAC stereo audio
- audio levels verified with `ffmpeg volumedetect`
- intro now explains the old dopamine reward-prediction-error story
- motivation now explains why coarse behavior can make neural activity look reward-like
- task setup now defines tone, sucrose, CS, US, conditioned response, and unconditioned response
- Figure 1 now explains movement-based dopamine neuron classification before jumping to results
- Figure 2 now explains the causal manipulation and why stimulus-aligned plots can hide movement signals

This is now the main prototype for judging explanation quality. The next quality step is not making it shorter; it is adding zoomed panel scenes and better word-level subtitles while keeping the task/motivation setup intact.

Reproduce:

```bash
npm run tts:prototype
npm run render:prototype:voiceover
```

Recommended next build step:

```text
Mistral OCR
-> extract figure captions and result paragraphs
-> render PDF pages
-> crop full figures
-> generate intro + figure-wise storyboard
-> create full-figure scene
-> create zoomed panel scenes
-> render in Remotion
```
