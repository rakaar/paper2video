import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
} from 'remotion';

const colors = {
  ink: '#172026',
  muted: '#5b646b',
  paper: '#f7f5ef',
  panel: '#ffffff',
  red: '#d84a36',
  blue: '#2667c9',
  green: '#1b9c5a',
  magenta: '#c22585',
  line: '#d9d3c7',
};

const SceneShell = ({children, caption, audio}) => (
  <AbsoluteFill
    style={{
      background: colors.paper,
      color: colors.ink,
      fontFamily:
        'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    }}
  >
    {audio ? <Audio src={staticFile(audio)} /> : null}
    {children}
    <div
      style={{
        position: 'absolute',
        left: 64,
        right: 64,
        bottom: 36,
        padding: '18px 24px',
        background: 'rgba(23, 32, 38, 0.92)',
        color: 'white',
        fontSize: 29,
        lineHeight: 1.26,
        borderRadius: 8,
      }}
    >
      {caption}
    </div>
  </AbsoluteFill>
);

const Evidence = ({items}) => (
  <div
    style={{
      position: 'absolute',
      top: 42,
      right: 56,
      color: colors.muted,
      fontSize: 18,
      textAlign: 'right',
      lineHeight: 1.35,
      maxWidth: 520,
    }}
  >
    {items.map((item) => (
      <div key={item}>{item}</div>
    ))}
  </div>
);

const IntroScene = ({scene, paper}) => {
  const frame = useCurrentFrame();
  const slide = interpolate(frame, [0, 45], [24, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <SceneShell caption={scene.narration} audio={scene.audio}>
      <Evidence items={scene.evidence} />
      <div style={{position: 'absolute', left: 92, top: 86, right: 92}}>
        <div style={{fontSize: 24, color: colors.blue, fontWeight: 700}}>
          {scene.eyebrow}
        </div>
        <h1
          style={{
            margin: '56px 0 0',
            maxWidth: 1180,
            fontSize: 72,
            lineHeight: 1.03,
            letterSpacing: 0,
          }}
        >
          {scene.title}
        </h1>
        <div
          style={{
            marginTop: 42,
            maxWidth: 1040,
            color: colors.muted,
            fontSize: 30,
            lineHeight: 1.34,
          }}
        >
          {paper.title}
        </div>
        <div
          style={{
            marginTop: 64,
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 24,
            transform: `translateY(${slide}px)`,
          }}
        >
          {scene.bullets.map((bullet, index) => (
            <div
              key={bullet}
              style={{
                background: colors.panel,
                border: `1px solid ${colors.line}`,
                borderTop: `7px solid ${
                  [colors.red, colors.blue, colors.green][index]
                }`,
                borderRadius: 8,
                padding: 28,
                minHeight: 150,
                fontSize: 29,
                lineHeight: 1.2,
                fontWeight: 680,
              }}
            >
              {bullet}
            </div>
          ))}
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: 96,
          bottom: 182,
          color: colors.muted,
          fontSize: 23,
        }}
      >
        {paper.citation} · doi:{paper.doi}
      </div>
    </SceneShell>
  );
};

const Highlight = ({focus}) => {
  if (!focus) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: `${focus.x}%`,
        top: `${focus.y}%`,
        width: `${focus.w}%`,
        height: `${focus.h}%`,
        border: `7px solid ${colors.red}`,
        boxShadow: '0 0 0 9999px rgba(247, 245, 239, 0.28)',
        borderRadius: 4,
      }}
    />
  );
};

const FigureScene = ({scene}) => (
  <SceneShell caption={scene.narration} audio={scene.audio}>
    <Evidence items={scene.evidence} />
    <div
      style={{
        position: 'absolute',
        left: 54,
        top: 42,
        bottom: 270,
        width: 1120,
        background: colors.panel,
        border: `1px solid ${colors.line}`,
        borderRadius: 8,
        overflow: 'hidden',
      }}
    >
      <Img
        src={staticFile(scene.asset)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          display: 'block',
        }}
      />
      <Highlight focus={scene.focus} />
    </div>
    <div
      style={{
        position: 'absolute',
        left: 1230,
        top: 146,
        right: 64,
      }}
    >
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          padding: '8px 14px',
          color: 'white',
          background: colors.ink,
          borderRadius: 6,
          fontSize: 24,
          fontWeight: 760,
        }}
      >
        {scene.figure}
      </div>
      <h2
        style={{
          margin: '28px 0 34px',
          fontSize: 47,
          lineHeight: 1.06,
          letterSpacing: 0,
        }}
      >
        {scene.title}
      </h2>
      <div style={{display: 'grid', gap: 20}}>
        {scene.bullets.map((bullet, index) => (
          <div
            key={bullet}
            style={{
              display: 'grid',
              gridTemplateColumns: '18px 1fr',
              gap: 16,
              alignItems: 'start',
              fontSize: 31,
              lineHeight: 1.18,
              fontWeight: 650,
            }}
          >
            <div
              style={{
                marginTop: 9,
                width: 14,
                height: 14,
                borderRadius: '50%',
                background: [colors.red, colors.blue, colors.green][index],
              }}
            />
            <div>{bullet}</div>
          </div>
        ))}
      </div>
    </div>
  </SceneShell>
);

export const PaperExplainer = ({storyboard}) => {
  let start = 0;

  return (
    <AbsoluteFill>
      {storyboard.scenes.map((scene, index) => {
        const from = start;
        start += scene.durationFrames;
        return (
          <Sequence
            key={`${scene.title}-${index}`}
            from={from}
            durationInFrames={scene.durationFrames}
          >
            {scene.kind === 'intro' ? (
              <IntroScene scene={scene} paper={storyboard.paper} />
            ) : (
              <FigureScene scene={scene} />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
