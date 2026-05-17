"""Chicken video mascot — preloaded base64 mp4, scrubs based on rage level."""


def mascot_js() -> str:
    return r"""
// Chicken video. Scrubs to match rage level instead of autoplaying.
// rage 1 → t=0%, 2 → 33%, 3 → 66%, 4 → 100% of video.duration.
const RAGE_TO_VIDEO_POS = [0, 0.33, 0.66, 1.0];
const SCRUB_DURATION_MS = 600;
const easeInOutCubic = (t) => t < 0.5
  ? 4 * t * t * t
  : 1 - Math.pow(-2 * t + 2, 3) / 2;

function ChickenVideo({ rage = 1, width = 260, style = {} }) {
  const videoRef = useRef(null);
  const animRef = useRef(null);
  const readyRef = useRef(false);
  const durationRef = useRef(0);

  const targetFor = (r) => {
    const d = durationRef.current;
    if (!d || !isFinite(d)) return null;
    return d * RAGE_TO_VIDEO_POS[Math.max(0, Math.min(3, r - 1))];
  };

  const setCurrentTime = (v, t) => {
    try { v.currentTime = t; return true; }
    catch (err) { return false; }
  };

  const scrubTo = (target) => {
    const v = videoRef.current;
    if (!v || target == null) return;
    cancelAnimationFrame(animRef.current);
    const startTime = v.currentTime;
    const delta = target - startTime;
    if (Math.abs(delta) < 0.001) { v.pause(); return; }
    const startTs = performance.now();
    const tick = (now) => {
      const t = Math.min((now - startTs) / SCRUB_DURATION_MS, 1);
      const eased = easeInOutCubic(t);
      setCurrentTime(v, startTime + delta * eased);
      if (t < 1) {
        animRef.current = requestAnimationFrame(tick);
      } else {
        v.pause();
        try { sessionStorage.setItem('chicken_t', String(v.currentTime)); } catch (e) {}
      }
    };
    v.pause();
    animRef.current = requestAnimationFrame(tick);
  };

  const onLoadedMetadata = () => {
    const v = videoRef.current;
    if (!v) return;
    durationRef.current = v.duration;
    readyRef.current = true;
    // restore previous position from sessionStorage if available, then scrub to target
    let restored = null;
    try {
      const saved = sessionStorage.getItem('chicken_t');
      if (saved != null) restored = parseFloat(saved);
    } catch (e) {}
    const target = targetFor(rage);
    if (restored != null && isFinite(restored)) {
      setCurrentTime(v, restored);
      v.pause();
      if (target != null && Math.abs(target - restored) > 0.001) scrubTo(target);
    } else if (target != null) {
      setCurrentTime(v, target);
      v.pause();
    }
  };

  useEffect(() => {
    if (!readyRef.current) return;
    const target = targetFor(rage);
    if (target != null) scrubTo(target);
    return () => cancelAnimationFrame(animRef.current);
  }, [rage]);

  return React.createElement('video', {
    ref: videoRef,
    src: window.CHICKEN_SRC,
    muted: true,
    playsInline: true,
    preload: 'auto',
    onLoadedMetadata: onLoadedMetadata,
    style: {
      width, height: 'auto', display: 'block',
      filter: 'url(#knockout-white)',
      pointerEvents: 'none',
      background: 'none',
      ...style,
    },
  });
}

// Thermometer: pure visual indicator. T1-T4 crossfade.
function Thermometer({ rage, width = 180 }) {
  return React.createElement('div', {
    style: {
      position: 'relative',
      width, height: width * 1.77,
      pointerEvents: 'none',
      background: 'none',
    },
  },
    T_IMGS.map((src, i) =>
      React.createElement('img', {
        key: src, src, alt: '', draggable: false,
        style: {
          position: 'absolute', inset: 0,
          width: '100%', height: '100%',
          objectFit: 'contain',
          filter: 'url(#knockout-white) drop-shadow(0 6px 14px rgba(0,0,0,.18))',
          opacity: rage === i + 1 ? 1 : 0,
          transition: 'opacity .45s ease',
          pointerEvents: 'none',
          background: 'none',
        },
      })
    )
  );
}
"""
