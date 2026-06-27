# Storyboard Contract

The current Remotion renderer reads JSON with:

```json
{
  "paper": {
    "title": "",
    "shortTitle": "",
    "citation": "",
    "doi": ""
  },
  "scenes": []
}
```

## Scene Fields

All scenes require:

- `kind`: `intro` or `figure`
- `durationFrames`: integer at 30 fps
- `title`: concise scene title
- `bullets`: short on-screen bullets
- `narration`: voiceover text
- `evidence`: paper evidence references

Figure scenes also require:

- `figure`: visible figure label such as `Fig. 2`
- `asset`: path under Remotion `public/`
- `focus`: optional percent-based highlight rectangle with `x`, `y`, `w`, and `h`

Voiceover generation adds:

- `audio`: public asset path to WAV
- `audioDurationSeconds`: measured audio duration

## Storyboard Quality

Use scene titles and bullets for orientation, not full explanation. Narration should explain the actual plot mechanics and reasoning.

Prefer several focused panel scenes over one crowded full-figure scene. The viewer should always know where to look and why.

Evidence references should be concrete enough to audit, for example:

- `Fig. 2e-h caption`
- `Results: Force direction and DA neuron activity during Pavlovian conditioning`
- `Abstract, page 1`
