"""Rage meter — left-rail thermometer + compact 4-tile tone selector."""


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
      vectorEffect: 'non-scaling-stroke',
    })
  );
}

function NakedRageTiles({ rage, setRage, streaming }) {
  // While a letter is streaming (#3) the meter collapses to just the selected
  // tile: the other three fade out and shrink to zero height (so the layout
  // eases shut rather than snapping), and go non-interactive.
  return React.createElement('div', {
    style: { display: 'flex', flexDirection: 'column', width: '100%' },
  },
    RAGE_TIERS.map((t) => {
      const active = rage === t.rage;
      const hidden = streaming && !active;
      const c = CRAYON[t.rage];
      return React.createElement('button', {
        key: t.rage,
        type: 'button',
        'data-no-drag': true,
        disabled: hidden,
        onClick: () => setRage(t.rage),
        style: {
          position: 'relative',
          background: 'transparent', border: 'none',
          paddingLeft: 12, paddingRight: 12,
          paddingTop: hidden ? 0 : 9, paddingBottom: hidden ? 0 : 9,
          marginBottom: hidden ? 0 : 4,
          maxHeight: hidden ? 0 : 80,
          overflow: 'hidden',
          cursor: hidden ? 'default' : 'pointer',
          textAlign: 'left',
          fontFamily: '"Gochi Hand", cursive',
          color: active ? c.main : '#3a3530',
          // Inactive tiles get a soft dashed outline so they read as
          // interactive at a glance, not just labels. Suppressed once
          // collapsed.
          outline: (active || hidden) ? 'none' : '1px dashed rgba(60,40,10,.28)',
          outlineOffset: '-3px', borderRadius: 6,
          opacity: hidden ? 0 : (active ? 1 : 0.78),
          pointerEvents: hidden ? 'none' : 'auto',
          transition: 'opacity .3s ease, max-height .3s ease, padding .3s ease, '
            + 'margin .3s ease, color .15s, transform .15s, outline-color .15s',
          display: 'flex', alignItems: 'baseline', gap: 8,
          transform: active ? 'translateX(3px)' : 'none',
        },
        onMouseEnter: (e) => {
          if (!active && !hidden) {
            e.currentTarget.style.opacity = 0.95;
            e.currentTarget.style.outline = '1px dashed rgba(60,40,10,.55)';
          }
        },
        onMouseLeave: (e) => {
          if (!active && !hidden) {
            e.currentTarget.style.opacity = 0.78;
            e.currentTarget.style.outline = '1px dashed rgba(60,40,10,.28)';
          }
        },
      },
        React.createElement('span', {
          style: { fontSize: 17, opacity: .6, minWidth: 16 },
        }, t.rage),
        React.createElement('span', {
          style: {
            fontSize: 22, fontWeight: active ? 700 : 400,
            letterSpacing: '.3px', lineHeight: 1.1, flex: 1,
          },
        }, t.label),
        active && React.createElement(ActiveTileRing, { color: c.main, seed: t.rage * 17 + 5 })
      );
    })
  );
}

// Left rail: thermometer (the rage gauge) over a compact tone selector.
function RageMeter({ rage, setRage, streaming }) {
  // Bigger card + larger thermometer + larger tile labels so the meter
  // reads as a primary interactive surface, not a side accessory.
  const W = 256, H = 760;
  return React.createElement(KidPaper, {
    width: W, height: H, seed: 47, tone: PAPER_BG_ALT, rotation: -1.6,
  },
    React.createElement('div', {
      style: {
        position: 'absolute', inset: 0,
        padding: '24px 18px 26px',
        boxSizing: 'border-box',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', gap: 10,
      },
    },
      React.createElement('div', {
        style: {
          fontFamily: '"Gochi Hand", cursive',
          fontSize: 38, color: CRAYON_NAVY,
          lineHeight: 1, letterSpacing: '.5px',
        },
      }, 'the rage'),
      React.createElement('div', {
        style: { display: 'flex', justifyContent: 'center', alignItems: 'center', flex: '0 0 auto' },
      },
        React.createElement(Thermometer, { rage, width: 170 })
      ),
      React.createElement('div', {
        style: {
          fontFamily: '"Gochi Hand", cursive',
          fontSize: 20, color: PENCIL_GRAY, marginTop: -2,
          // The "pick a tone" prompt eases out while streaming — there's
          // nothing to pick once the meter has collapsed to one tile.
          opacity: streaming ? 0 : .9,
          maxHeight: streaming ? 0 : 40, overflow: 'hidden',
          transition: 'opacity .3s ease, max-height .3s ease',
        },
      }, '↓ pick a tone ↓'),
      React.createElement('div', {
        style: { width: '100%', display: 'flex', justifyContent: 'center', marginTop: 4 },
      },
        React.createElement(NakedRageTiles, { rage, setRage, streaming })
      )
    )
  );
}
"""
