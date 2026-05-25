"""Rage-driven image mascots — chicken, thermometer, and kid's drawing.

Each is a simple stack of four base64 PNGs (one per rage level) that
cross-fade on opacity when ``rage`` changes — no video, no scrubbing.
"""


def mascot_js() -> str:
    return r"""
// Chicken: four PNGs (one per rage level) that cross-fade on rage change.
function Chicken({ rage = 1, width = 260, style = {} }) {
  return React.createElement('div', {
    style: {
      position: 'absolute',
      width, height: 'auto',
      pointerEvents: 'none', background: 'none',
      ...style,
    },
  },
    CHICKEN_IMGS.map((src, i) =>
      React.createElement('img', {
        key: src, src, alt: '', draggable: false,
        style: {
          // First image sizes the box; the rest overlay it absolutely.
          position: i === 0 ? 'relative' : 'absolute',
          top: i === 0 ? undefined : 0,
          left: i === 0 ? undefined : 0,
          width: '100%', height: 'auto', display: 'block',
          objectFit: 'contain',
          opacity: rage === i + 1 ? 1 : 0,
          transition: 'opacity .3s ease',
          pointerEvents: 'none', background: 'none',
        },
      })
    )
  );
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
          filter: 'drop-shadow(0 6px 14px rgba(0,0,0,.18))',
          opacity: rage === i + 1 ? 1 : 0,
          transition: 'opacity .45s ease',
          pointerEvents: 'none',
          background: 'none',
        },
      })
    )
  );
}

// Kid's drawing prop: drawing1-4 crossfade. The PNGs already include their
// paper, so no separate paper shape is drawn — just the image.
function Drawing({ rage = 1, width = 300 }) {
  return React.createElement('div', {
    style: {
      position: 'relative',
      width, height: 'auto',
      pointerEvents: 'none',
      background: 'none',
    },
  },
    DRAWING_IMGS.map((src, i) =>
      React.createElement('img', {
        key: src, src, alt: '', draggable: false,
        style: {
          position: i === 0 ? 'relative' : 'absolute',
          top: i === 0 ? undefined : 0,
          left: i === 0 ? undefined : 0,
          width: '100%', height: 'auto', display: 'block',
          objectFit: 'contain',
          filter: 'drop-shadow(0 8px 16px rgba(0,0,0,.20))',
          opacity: rage === i + 1 ? 1 : 0,
          transition: 'opacity .3s ease',
          pointerEvents: 'none', background: 'none',
        },
      })
    )
  );
}
"""
