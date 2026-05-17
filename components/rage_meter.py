"""Rage meter sticky note — thermometer + 4-tile segmented bar."""


def rage_meter_js() -> str:
    return r"""
const RAGE_TIERS = [
  { rage: 1, label: 'polite nudge'       },
  { rage: 2, label: 'passive aggressive' },
  { rage: 3, label: 'fed up'             },
  { rage: 4, label: 'unhinged'           },
];

function ActiveTileRing({ color, seed }) {
  const segs = 18;
  let s = seed;
  const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const j = 2.2;
  const corners = [[4, 8], [96, 8], [96, 92], [4, 92]];
  const path = [];
  const side = (from, to) => {
    for (let i = 0; i <= segs; i++) {
      const t = i / segs;
      const x = from[0] + (to[0] - from[0]) * t + (r() - 0.5) * j;
      const y = from[1] + (to[1] - from[1]) * t + (r() - 0.5) * j;
      path.push(`${path.length === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`);
    }
  };
  side(corners[0], corners[1]);
  side(corners[1], corners[2]);
  side(corners[2], corners[3]);
  side(corners[3], corners[0]);
  return React.createElement('svg', {
    viewBox: '0 0 100 100', preserveAspectRatio: 'none',
    style: { position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' },
  },
    React.createElement('path', {
      d: path.join(' ') + 'Z', fill: 'none', stroke: color,
      strokeWidth: '2.4', strokeLinecap: 'round', strokeLinejoin: 'round', opacity: '.9',
    })
  );
}

function NakedRageTiles({ rage, setRage }) {
  return React.createElement('div', {
    style: { display: 'flex', flexDirection: 'column', gap: 4, width: '100%' },
  },
    RAGE_TIERS.map((t) => {
      const active = rage === t.rage;
      const c = CRAYON[t.rage];
      return React.createElement('button', {
        key: t.rage,
        type: 'button',
        'data-no-drag': true,
        onClick: () => setRage(t.rage),
        style: {
          position: 'relative',
          background: 'transparent', border: 'none',
          padding: '7px 12px', cursor: 'pointer',
          textAlign: 'left',
          fontFamily: '"Gochi Hand", cursive',
          color: active ? c.main : '#3a3530',
          opacity: active ? 1 : 0.62,
          transition: 'opacity .15s, color .15s, transform .15s',
          display: 'flex', alignItems: 'baseline', gap: 8,
          transform: active ? 'translateX(2px)' : 'none',
        },
        onMouseEnter: (e) => { if (!active) e.currentTarget.style.opacity = 0.85; },
        onMouseLeave: (e) => { if (!active) e.currentTarget.style.opacity = 0.62; },
      },
        React.createElement('span', {
          style: { fontSize: 14, opacity: .55, minWidth: 14 },
        }, t.rage),
        React.createElement('span', {
          style: {
            fontSize: 19, fontWeight: active ? 700 : 400,
            letterSpacing: '.4px', lineHeight: 1.1, flex: 1,
          },
        }, t.label),
        active && React.createElement(ActiveTileRing, { color: c.main, seed: t.rage * 17 + 5 })
      );
    })
  );
}

function RageMeter({ rage, setRage }) {
  const W = 300, H = 480;
  return React.createElement(KidPaper, {
    width: W, height: H, seed: 47, tone: PAPER_BG_ALT, rotation: -1.6,
  },
    React.createElement('div', {
      style: {
        position: 'absolute', inset: 0,
        padding: '22px 20px 22px',
        boxSizing: 'border-box',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', gap: 10,
      },
    },
      React.createElement('div', {
        style: {
          fontFamily: '"Gochi Hand", cursive',
          fontSize: 28, color: CRAYON_NAVY,
          lineHeight: 1, letterSpacing: '.5px',
        },
      }, 'the rage meter'),
      React.createElement('div', {
        style: { display: 'flex', justifyContent: 'center', alignItems: 'center', flex: '0 0 auto' },
      },
        React.createElement(Thermometer, { rage, width: 120 })
      ),
      React.createElement('div', {
        style: {
          fontFamily: '"Gochi Hand", cursive',
          fontSize: 17, color: PENCIL_GRAY, opacity: .85, marginTop: -4,
        },
      }, 'pick a tone ↓'),
      React.createElement('div', {
        style: { width: '100%', display: 'flex', justifyContent: 'center', marginTop: 2 },
      },
        React.createElement(NakedRageTiles, { rage, setRage })
      )
    )
  );
}
"""
