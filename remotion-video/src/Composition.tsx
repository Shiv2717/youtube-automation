import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";

type Props = {
  title?: string;
};

const calculateMetadata: CalculateMetadataFunction<Props> = () => {
  return {};
};

export const MyComposition = () => {
  return (
    <Composition
      id="MyComp"
      component={MyComponent}
      durationInFrames={360}
      fps={12}
      width={720}
      height={1280}
      calculateMetadata={calculateMetadata}
      defaultProps={{ title: "Even the quiet days matter." }}
    />
  );
};

const scenes = [
  { sky: "#162326", ground: "#283a35", accent: "#c77c46", kind: "bakery" },
  { sky: "#193a45", ground: "#1d3436", accent: "#e0a15d", kind: "rooftop" },
  { sky: "#1d2925", ground: "#18231e", accent: "#a85a40", kind: "forest" },
  { sky: "#342b28", ground: "#1d1a19", accent: "#db9d55", kind: "desk" },
];

const particles = Array.from({ length: 18 }, (_, index) => ({
  left: `${8 + ((index * 37) % 84)}%`,
  top: `${12 + ((index * 53) % 74)}%`,
  size: 2 + (index % 4),
  delay: index * 7,
}));

const grainSpecks = Array.from({ length: 28 }, (_, index) => ({
  left: `${(index * 43) % 100}%`,
  top: `${(index * 67) % 100}%`,
}));

const Scene = ({ sceneIndex, opacity }: { sceneIndex: number; opacity: number }) => {
  const frame = useCurrentFrame();
  const scene = scenes[sceneIndex % scenes.length];
  const drift = interpolate(frame % 144, [0, 144], [-2.5, 2.5], {
    easing: Easing.inOut(Easing.ease),
  });
  const push = interpolate(frame % 144, [0, 144], [1.03, 1.1], {
    easing: Easing.inOut(Easing.ease),
  });
  const lightPulse = 0.58 + Math.sin(frame / 12) * 0.1;

  return (
    <AbsoluteFill style={{ opacity, overflow: "hidden", background: scene.sky }}>
      <div
        style={{
          position: "absolute",
          inset: "-5%",
          transform: `translateX(${drift}%) scale(${push})`,
          background: `radial-gradient(circle at 70% 22%, ${scene.accent}55, transparent 22%), linear-gradient(180deg, ${scene.sky} 0%, ${scene.ground} 72%, #101614 100%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "-14%",
          left: "58%",
          width: "38%",
          height: "90%",
          background: `linear-gradient(110deg, transparent, ${scene.accent}22, transparent)`,
          transform: `rotate(${12 + drift / 2}deg)`,
          filter: "blur(18px)",
          opacity: lightPulse,
        }}
      />
      <div style={{ position: "absolute", left: "-10%", right: "-10%", bottom: "18%", height: "2%", background: "#0c1414", opacity: 0.9 }} />
      <div style={{ position: "absolute", left: "-5%", right: "-5%", bottom: "0%", height: "20%", background: "linear-gradient(180deg, #192522, #0c1110)" }} />
      {scene.kind === "bakery" && (
        <>
          {[0, 1, 2].map((row) => (
            <div key={row} style={{ position: "absolute", left: "10%", right: "10%", top: `${25 + row * 13}%`, height: 7, background: "#6f4934", boxShadow: "0 5px 0 #241d19" }} />
          ))}
          <div style={{ position: "absolute", left: "17%", top: "12%", width: 110, height: 55, borderRadius: "50%", background: "#d19b58", filter: "blur(3px)", opacity: 0.8 }} />
        </>
      )}
      {scene.kind === "rooftop" && (
        <>
          <div style={{ position: "absolute", right: "11%", top: "15%", width: 8, height: "44%", background: "#87918a" }} />
          <div style={{ position: "absolute", right: "5%", top: "14%", width: 70, height: 28, borderRadius: "50%", background: scene.accent, boxShadow: `0 0 35px ${scene.accent}` }} />
          <div style={{ position: "absolute", left: "4%", bottom: "18%", width: "92%", height: 12, background: "#516d67" }} />
        </>
      )}
      {scene.kind === "forest" && (
        <>
          {[0, 1, 2, 3].map((tree) => (
            <div key={tree} style={{ position: "absolute", left: `${tree * 31 - 8}%`, top: "8%", width: 90, height: "75%", background: "linear-gradient(90deg, #141b17, #4a4935, #101613)", transform: `rotate(${tree % 2 ? 5 : -4}deg)` }} />
          ))}
        </>
      )}
      {scene.kind === "desk" && (
        <>
          <div style={{ position: "absolute", left: "8%", right: "8%", bottom: "23%", height: 16, background: "#755137" }} />
          <div style={{ position: "absolute", left: "20%", bottom: "25%", width: 180, height: 115, background: "#b8773e", transform: "rotate(-5deg)", boxShadow: "0 12px 0 #482e28" }} />
          <div style={{ position: "absolute", right: "19%", bottom: "25%", width: 85, height: 12, background: "#c9b795", transform: "rotate(8deg)" }} />
        </>
      )}
      {particles.map((particle) => (
        <div
          key={particle.left}
          style={{
            position: "absolute",
            left: particle.left,
            top: particle.top,
            width: particle.size,
            height: particle.size,
            borderRadius: "50%",
            background: scene.accent,
            opacity: 0.25 + 0.2 * Math.sin((frame + particle.delay) / 14),
            transform: `translateY(${Math.sin((frame + particle.delay) / 20) * 12}px)`,
          }}
        />
      ))}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 50% 40%, transparent 35%, ${scene.sky}99 100%)`,
          mixBlendMode: "multiply",
          opacity: 0.35,
        }}
      />
    </AbsoluteFill>
  );
};

const Skeleton = ({ sceneIndex }: { sceneIndex: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 18, stiffness: 70 } });
  const sway = Math.sin(frame / 16) * 2;
  const pose = sceneIndex % 4;
  const lift = pose === 1 ? Math.sin(frame / 10) * 8 : 0;
  const lean = pose === 2 ? -8 : pose === 3 ? 8 : 0;
  return (
    <div style={{ position: "absolute", left: "50%", top: "43%", width: 250, height: 420, translate: "-50% -50%", transformOrigin: "50% 80%", transform: `translateY(${(1 - enter) * 90 + lift}px) rotate(${sway + lean}deg)`, filter: "drop-shadow(0 14px 8px #0008)" }}>
      <svg viewBox="0 0 250 420" width="250" height="420">
        <g fill="none" stroke="#171715" strokeWidth="12" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="125" cy="54" r="38" fill="#ede6d0" />
          <path d="M106 77 Q125 91 144 77" strokeWidth="5" />
          <path d="M125 94 L125 222 M84 130 Q125 112 166 130 M88 158 Q125 140 162 158 M88 187 Q125 168 162 187" />
          <path d={`M125 100 L${pose === 1 ? 54 : 76} ${pose === 1 ? 160 : 196} L${pose === 1 ? 86 : 53} ${pose === 1 ? 286 : 292} M125 100 L${pose === 3 ? 205 : 174} ${pose === 3 ? 160 : 196} L${pose === 3 ? 228 : 199} ${pose === 3 ? 286 : 292}`} />
          <path d="M125 222 L74 326 L54 405 M125 222 L176 326 L198 405" />
        </g>
        <g fill="none" stroke="#ede6d0" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="125" cy="54" r="38" />
          <path d="M125 94 L125 222 M84 130 Q125 112 166 130 M88 158 Q125 140 162 158 M88 187 Q125 168 162 187" />
          <path d="M125 100 L76 196 L53 292 M125 100 L174 196 L199 292" />
          <path d="M125 222 L74 326 L54 405 M125 222 L176 326 L198 405" />
        </g>
      </svg>
    </div>
  );
};

const FilmAtmosphere = () => {
  const frame = useCurrentFrame();
  const sceneCut = frame % 90;
  const flare = interpolate(sceneCut, [0, 5, 14, 28], [0, 0.9, 0.12, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const grain = 0.035 + ((frame * 17) % 10) / 500;
  return (
    <>
      <AbsoluteFill style={{ opacity: grain, mixBlendMode: "screen" }}>
        {grainSpecks.map((speck, index) => (
          <div key={index} style={{ position: "absolute", left: speck.left, top: speck.top, width: 3, height: 3, borderRadius: "50%", backgroundColor: index % 2 ? "#fff" : "#0b0f0d" }} />
        ))}
      </AbsoluteFill>
      <AbsoluteFill style={{ opacity: flare, background: "linear-gradient(105deg, transparent 18%, #ffd39b88 48%, transparent 70%)", mixBlendMode: "screen" }} />
      <div style={{ position: "absolute", left: "-12%", top: `${45 + Math.sin(frame / 30) * 3}%`, width: "124%", height: 2, background: "#f4d8ae44", filter: "blur(7px)", transform: `rotate(${-3 + Math.sin(frame / 25)}deg)` }} />
    </>
  );
};

export const MyComponent: React.FC<Props> = ({ title = "Even the quiet days matter." }) => {
  const frame = useCurrentFrame();
  const sceneDuration = 90;
  const sceneIndex = Math.floor(frame / sceneDuration);
  const localFrame = frame % sceneDuration;
  const opacity = interpolate(localFrame, [0, 10, 80, 90], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const textIn = interpolate(frame, [8, 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#111714", fontFamily: "Georgia, serif", color: "#ede6d0" }}>
      <Audio src={staticFile("narration.wav")} volume={0.7} />
      <Scene sceneIndex={sceneIndex} opacity={opacity} />
      <Skeleton sceneIndex={sceneIndex} />
      <div style={{ position: "absolute", top: 90, left: 52, right: 52, opacity: textIn, fontSize: 34, lineHeight: 1.15, letterSpacing: 1, textShadow: "0 3px 12px #000" }}>{title}</div>
      <div style={{ position: "absolute", bottom: 80, left: 52, right: 52, fontSize: 20, letterSpacing: 4, opacity: interpolate(frame, [310, 345], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), textTransform: "uppercase" }}>Keep going • follow for more</div>
      <FilmAtmosphere />
      <div style={{ position: "absolute", inset: 0, boxShadow: "inset 0 0 120px #050807cc", pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};
