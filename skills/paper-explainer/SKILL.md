---
name: paper-explainer
description: Turn academic paper PDFs, arXiv papers, Nature-style articles, neuroscience papers, machine-learning papers, extracted paper text, figure captions, or paper figures into faithful video explainers, Remotion storyboards, figure-by-figure narration, or evidence-grounded explanations. Use when Codex is asked to explain a paper, read a paper for video, create a paper explainer, write a storyboard, convert a paper to video, interpret figures or panels, improve paper-video narration, or check whether an explainer overclaims beyond the paper.
---

# Paper Explainer

## Core Rule

Explain the paper as a chain of evidence, not as a generic summary. For every major claim, show what the authors measured, what they plotted, what pattern appears, and how that pattern supports or limits the claim.

## Workflow

1. Build the paper story.
   - Read title, abstract, introduction, discussion/conclusion, and all main figure captions.
   - State the central claim in one sentence.
   - Identify the old model, gap, or competing explanation the paper addresses.

2. Build the figure story.
   - For each figure, read the caption and nearby Results text before writing narration.
   - Identify the question the figure answers.
   - For each important panel, capture what is plotted, axes or measured variables, groups/colors/conditions, alignment event, and comparison.
   - State the visible pattern before stating the interpretation.

3. Build the video story.
   - Start with motivation and task/setup before results.
   - Use one visual idea per scene.
   - Add figure setup scenes, panel explanation scenes, claim scenes, synthesis, and limitations.
   - Keep on-screen bullets short; let narration carry the explanation.

4. Verify the story.
   - Separate what the data directly show from what the authors infer.
   - Attach evidence references to each scene.
   - Reject high-level-only figure narration unless the user explicitly requested a brief overview.

## Required References

Read these only when needed for the current task:

- `references/explanation-workflow.md`: use when planning the narrative or deciding how to read the paper.
- `references/figure-explanation-rubric.md`: use before writing or reviewing figure/panel scenes.
- `references/storyboard-contract.md`: use when producing or editing storyboard JSON for the Remotion renderer.
- `references/quality-checklist.md`: use before declaring an explainer video or storyboard complete.

## Output Expectations

- A storyboard must be evidence-grounded and include motivation, task/setup, figure mechanics, interpretation, and caveats.
- A figure scene must not merely say "the authors saw X." It must explain what was plotted, what the viewer should notice, and how that makes the point.
- A Remotion implementation should prefer actual paper figures, highlight boxes, zoomed panel scenes, synced narration, and readable captions.
- Generated PDFs, OCR outputs, audio, video, and figure crops are artifacts and should stay out of git unless the user explicitly asks otherwise.
