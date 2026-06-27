# Explanation Workflow

Use this workflow to turn a paper into a video story.

## Pass 1: Paper Story

Read:

- title, abstract, and graphical/summary text if present
- introduction, especially the problem framing
- discussion or conclusion
- all main figure captions

Extract:

- the paper's central claim in one sentence
- the prior model or assumption being challenged
- the task, dataset, experiment, or model setup
- what the authors need to prove for the claim to hold
- the minimum background the viewer needs before Figure 1

## Pass 2: Figure Story

For each main figure:

- identify the question the figure answers
- list the important panels and what each panel contributes
- record caption facts and nearby Results statements
- explain the plotted variables before interpreting the result
- mark any figure that needs zoomed panel scenes

Use this sequence in narration:

```text
why this figure exists
-> what the panel plots
-> what comparison is being made
-> what pattern appears
-> what this pattern supports
-> what it does not prove
```

## Pass 3: Video Story

Default shape for a normal paper:

```text
0:00-0:30   Hook and motivation
0:30-1:15   Old model, gap, or competing explanation
1:15-2:00   Task/setup and measurements
2:00-5:30   Main figures, one claim at a time
5:30-6:30   Synthesis
6:30-7:00   Limitations and why it matters
```

Use shorter timing only for explicit brief-overview requests or smoke tests.

## Subagents

Use subagents when the paper or video is large enough to threaten context quality:

- reading/story subagent: paper claim, figure captions, Results evidence, caveats
- implementation subagent: Remotion layout, assets, rendering, audio sync
- review subagent: overclaiming, missing figure mechanics, visual readability

Do not let subagents replace evidence checking. The final storyboard still needs cited paper evidence per scene.
