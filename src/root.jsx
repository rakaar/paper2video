import React from 'react';
import {Composition} from 'remotion';
import {PaperExplainer} from './video.jsx';
import storyboard from './storyboard.voiceover.json';

export const Root = () => {
  const durationInFrames = storyboard.scenes.reduce(
    (total, scene) => total + scene.durationFrames,
    0,
  );

  return (
    <Composition
      id="PaperExplainer"
      component={PaperExplainer}
      durationInFrames={durationInFrames}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{storyboard}}
    />
  );
};
