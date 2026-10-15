import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

type SceneData = {
  kicker: string;
  headline: string;
  highlight: string;
  subtitle: string;
  accent: string;
  layout: "hero" | "steps" | "quote" | "stat";
};

type Props = {
  title: string;
  scenes: SceneData[];
  accentColor: string;
  backgroundColor: string;
};

const defaultScenes: SceneData[] = [
  {
    kicker: "THE AI PLAYBOOK",
    headline: "Better prompts.",
    highlight: "Better answers.",
    subtitle: "One small change can transform your next AI conversation.",
    accent: "#f06a43",
    layout: "hero",
  },
  {
    kicker: "01 — GIVE IT A ROLE",
    headline: "Set the context.",
    highlight: "Define the goal.",
    subtitle: "Tell the model who it should be and what success looks like.",
    accent: "#f0a35b",
    layout: "steps",
  },
  {
    kicker: "02 — SHOW THE STANDARD",
    headline: "Examples make",
    highlight: "expectations clear.",
    subtitle: "A small example can be more useful than a long explanation.",
    accent: "#e76f51",
    layout: "quote",
  },
  {
    kicker: "03 — REFINE THE OUTPUT",
    headline: "First draft?",
    highlight: "Keep improving.",
    subtitle: "Ask for gaps, assumptions, and a stronger second version.",
    accent: "#e9b45e",
    layout: "stat",
  },
  {
    kicker: "SAVE THIS",
    headline: "Clear input.",
    highlight: "Stronger output.",
    subtitle: "Follow for practical ideas you can use today.",
    accent: "#f06a43",
    layout: "hero",
  },
];

export const defaultShortProps: Props = {
  title: "A simple way to get better AI answers",
  scenes: defaultScenes,
  accentColor: "#f06a43",
  backgroundColor: "#f4efe5",
};

const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

const Grain = () => {
  const frame = useCurrentFrame();
  const specks = Array.from({ length: 100 }, (_, i) => ({
    x: (i * 47 + frame * (i % 3 + 1)) % 100,
    y: (i * 71 + frame * (i % 2 + 1)) % 100,
    size: i % 4 === 0 ? 2 : 1,
  }));

  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: 0.17 }}>
      {specks.map((s, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${s.x}%`,
            top: `${s.y}%`,
            width: s.size,
            height: s.size,
            background: i % 2 ? "#34271e" : "#fffaf0",
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

const Background = ({
  accent,
  background,
}: {
  accent: string;
  background: string;
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const driftX = interpolate(frame, [0, 240], [-15, 15], {
    easing: Easing.inOut(Easing.ease),
    ...clamp,
  });
  const driftY = Math.sin(frame / 42) * 18;

  return (
    <AbsoluteFill style={{ background }}>
      <div
        style={{
          position: "absolute",
          width: width * 0.9,
          height: width * 0.9,
          left: width * 0.2 + driftX,
          top: height * 0.07 + driftY,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${accent}22 0%, ${accent}08 34%, transparent 70%)`,
          filter: "blur(8px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          width: width * 0.7,
          height: width * 0.7,
          left: -width * 0.35 - driftX / 2,
          bottom: -width * 0.12,
          borderRadius: "50%",
          background: "radial-gradient(circle, #bfac8b25, transparent 70%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 30,
          border: "1px solid #332a201c",
          borderRadius: 5,
        }}
      />
      <Grain />
    </AbsoluteFill>
  );
};

const WordBlock: React.FC<{
  text: string;
  start: number;
  accent: string;
  highlight?: boolean;
}> = ({ text, start, accent, highlight = false }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const p = spring({
    frame: frame - start,
    fps,
    config: { damping: 18, stiffness: 105, mass: 0.75 },
  });
  const opacity = interpolate(frame - start, [0, 5], [0, 1], clamp);
  const y = interpolate(p, [0, 1], [52, 0]);

  return (
    <div
      style={{
        width: "100%",
        maxWidth: width * 0.88,
        textAlign: "center",
        opacity,
        transform: `translateY(${y}px) scale(${interpolate(p, [0, 1], [0.96, 1])})`,
        color: highlight ? accent : "#211e19",
        fontFamily: "'Arial Black', Arial, Helvetica, sans-serif",
        fontSize: highlight ? 88 : 78,
        fontWeight: 900,
        lineHeight: 1.02,
        letterSpacing: "-0.065em",
        overflowWrap: "break-word",
        textWrap: "balance",
      }}
    >
      {text}
    </div>
  );
};

const Kicker = ({ text, accent }: { text: string; accent: string }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12], [0, 1], clamp);
  const tracking = interpolate(frame, [0, 16], [7, 3.5], clamp);
  return (
    <div
      style={{
        opacity,
        color: accent,
        fontFamily: "Arial, Helvetica, sans-serif",
        fontSize: 19,
        fontWeight: 800,
        letterSpacing: tracking,
        textAlign: "center",
        marginBottom: 34,
      }}
    >
      {text.toUpperCase()}
    </div>
  );
};

const Rule = ({ start, accent }: { start: number; accent: string }) => {
  const frame = useCurrentFrame();
  const width = interpolate(frame - start, [0, 17], [0, 176], clamp);
  return (
    <div
      style={{
        margin: "30px auto 24px",
        height: 5,
        width,
        borderRadius: 99,
        background: accent,
      }}
    />
  );
};

const SceneGraphic = ({
  scene,
  start,
}: {
  scene: SceneData;
  start: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - start,
    fps,
    config: { damping: 16, stiffness: 100 },
  });
  const opacity = interpolate(frame - start, [0, 8], [0, 1], clamp);
  const y = interpolate(p, [0, 1], [24, 0]);

  if (scene.layout === "steps") {
    const items = ["ROLE", "CONTEXT", "GOAL"];
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 12,
          marginTop: 38,
          opacity,
          transform: `translateY(${y}px)`,
        }}
      >
        {items.map((item, i) => (
          <React.Fragment key={item}>
            <div
              style={{
                padding: "17px 16px",
                border: `2px solid ${i === 2 ? scene.accent : "#c9bdac"}`,
                borderRadius: 12,
                fontFamily: "Arial, sans-serif",
                fontWeight: 800,
                fontSize: 18,
                letterSpacing: 1,
                color: "#25211b",
                background: "#fffaf04d",
              }}
            >
              {item}
            </div>
            {i < items.length - 1 && (
              <span style={{ fontSize: 24, color: scene.accent }}>→</span>
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  if (scene.layout === "quote") {
    return (
      <div
        style={{
          opacity,
          transform: `translateY(${y}px)`,
          margin: "36px auto 0",
          maxWidth: 570,
          padding: "18px 26px",
          borderLeft: `5px solid ${scene.accent}`,
          background: "#fffaf04d",
          color: "#51483d",
          fontFamily: "Georgia, serif",
          fontStyle: "italic",
          fontSize: 29,
          lineHeight: 1.35,
        }}
      >
        “Show me the kind of answer you want.”
      </div>
    );
  }

  if (scene.layout === "stat") {
    const amount = Math.round(
      interpolate(frame - start, [0, 25], [0, 3], clamp),
    );
    return (
      <div
        style={{
          opacity,
          transform: `translateY(${y}px)`,
          marginTop: 36,
          display: "flex",
          justifyContent: "center",
          gap: 12,
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 70,
              height: 9,
              borderRadius: 9,
              background: i < amount ? scene.accent : "#d6cbbb",
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      style={{
        opacity,
        margin: "34px auto 0",
        display: "flex",
        gap: 12,
        justifyContent: "center",
        transform: `translateY(${Math.sin((frame - start) / 8) * 5}px)`,
      }}
    >
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            width: 11,
            height: 11,
            borderRadius: "50%",
            background: scene.accent,
            opacity: 1 - i * 0.2,
          }}
        />
      ))}
    </div>
  );
};

const Progress = ({
  duration,
  accent,
}: {
  duration: number;
  accent: string;
}) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const progress = interpolate(frame, [0, duration - 1], [0, 1], clamp);
  return (
    <div style={{ width: "100%" }}>
      <div
        style={{
          height: 4,
          background: "#30281d18",
          borderRadius: 20,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress * 100}%`,
            background: accent,
          }}
        />
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: 16,
          color: "#777064",
          fontSize: 15,
          letterSpacing: 1.4,
          fontWeight: 800,
          fontFamily: "Arial, sans-serif",
        }}
      >
        <span>THINK CLEARER.</span>
        <span>{Math.round(progress * 100).toString().padStart(2, "0")}%</span>
      </div>
    </div>
  );
};

export const MyComponent: React.FC<Props> = ({
  title,
  scenes,
  accentColor,
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const safeScenes = scenes?.length ? scenes : defaultScenes;
  const sceneDuration = durationInFrames / safeScenes.length;
  const sceneIndex = Math.min(
    safeScenes.length - 1,
    Math.floor(frame / sceneDuration),
  );
  const sceneStart = Math.floor(sceneIndex * sceneDuration);
  const localFrame = frame - sceneStart;
  const scene = safeScenes[sceneIndex];
  const enter = spring({
    frame: localFrame,
    fps,
    config: { damping: 21, stiffness: 90 },
  });
  const fadeOut = interpolate(
    frame,
    [sceneStart + sceneDuration - 8, sceneStart + sceneDuration],
    [1, 0],
    clamp,
  );
  const contentY = interpolate(enter, [0, 1], [18, 0]);
  const baseAccent = scene.accent || accentColor;
  const safeTitle = title || "Ideas worth keeping";

  return (
    <AbsoluteFill style={{ background: backgroundColor, overflow: "hidden" }}>
      <Background accent={baseAccent} background={backgroundColor} />

      <div
        style={{
          position: "absolute",
          top: height * 0.075,
          left: width * 0.09,
          right: width * 0.09,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          color: "#655d52",
          fontFamily: "Arial, sans-serif",
          fontSize: 16,
          fontWeight: 800,
          letterSpacing: 2,
        }}
      >
        <span>FIELD NOTES / AI</span>
        <span style={{ color: baseAccent }}>
          {String(sceneIndex + 1).padStart(2, "0")} /{" "}
          {String(safeScenes.length).padStart(2, "0")}
        </span>
      </div>

      <AbsoluteFill
        style={{
          top: "20%",
          height: "59%",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 6%",
          opacity: fadeOut,
          transform: `translateY(${contentY}px)`,
        }}
      >
        <Kicker text={scene.kicker || safeTitle} accent={baseAccent} />
        <WordBlock
          text={scene.headline}
          start={sceneStart}
          accent={baseAccent}
        />
        <WordBlock
          text={scene.highlight}
          start={sceneStart + 5}
          accent={baseAccent}
          highlight
        />
        <Rule start={sceneStart + 9} accent={baseAccent} />
        <div
          style={{
            opacity: interpolate(localFrame, [13, 25], [0, 1], clamp),
            maxWidth: width * 0.8,
            textAlign: "center",
            color: "#5c554b",
            fontFamily: "Arial, Helvetica, sans-serif",
            fontSize: 27,
            lineHeight: 1.38,
            fontWeight: 500,
          }}
        >
          {scene.subtitle}
        </div>
        <SceneGraphic scene={scene} start={sceneStart + 20} />
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          bottom: height * 0.075,
          left: width * 0.09,
          right: width * 0.09,
        }}
      >
        <Progress duration={durationInFrames} accent={accentColor} />
      </div>

      <div
        style={{
          position: "absolute",
          bottom: height * 0.14,
          left: width * 0.09,
          right: width * 0.09,
          textAlign: "center",
          fontFamily: "Arial, sans-serif",
          color: "#887e70",
          fontSize: 13,
          letterSpacing: 1.1,
          opacity: interpolate(
            frame,
            [durationInFrames - fps * 2, durationInFrames - fps],
            [0, 0.75],
            clamp,
          ),
        }}
      >
        {safeTitle.toUpperCase()}
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => (
  <Composition
    id="MyComp"
    component={MyComponent}
    durationInFrames={360}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={defaultShortProps}
  />
);
