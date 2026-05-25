"""Shared JS primitives for the iframe.

The whole interactive UI is one React app rendered inside a single
``streamlit.components.v1.html`` iframe. This module returns the JS that
defines the shared atoms (colors, paper textures, header) — every other
component module pulls from globals defined here.
"""


def shared_js() -> str:
    return r"""
const { useState, useEffect, useRef, useMemo } = React;

// Crayon colors keyed to rage 1..4.
const CRAYON = {
  1: { main: '#1c3b8f', accent: null,       label: 'gentle reminder' },
  2: { main: '#5a3a1a', accent: null,       label: 'firm note'       },
  3: { main: '#c8421a', accent: null,       label: 'final warning'   },
  4: { main: '#0a0a0a', accent: '#b51212',  label: 'unleash hellfire'},
};
const PENCIL_GRAY = '#3a3530';
const CRAYON_NAVY = CRAYON[1].main;
const CRAYON_BROWN = CRAYON[2].main;

const PAPER_BG = 'rgba(246,236,209,0.80)';     // warm off-white cream (translucent)
const PAPER_BG_ALT = 'rgba(243,231,197,0.80)'; // form paper, very slightly different

// Deterministic pseudo-random from index (so jitter is stable across renders).
function rand(i, salt = 0) {
  let s = (i * 9301 + 49297 + salt * 7919) % 233280;
  return s / 233280;
}

// Generate a torn-edge clip-path polygon for paper.
function tornPath(seed = 1, segments = 28, jitter = 1.4) {
  let s = seed;
  const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const pts = [];
  for (let i = 0; i <= segments; i++) pts.push([(i/segments)*100, (r()-0.5)*jitter]);
  for (let i = 1; i <= segments; i++) pts.push([100 + (r()-0.5)*jitter, (i/segments)*100]);
  for (let i = segments - 1; i >= 0; i--) pts.push([(i/segments)*100, 100 + (r()-0.5)*jitter]);
  for (let i = segments - 1; i >= 1; i--) pts.push([(r()-0.5)*jitter, (i/segments)*100]);
  return `polygon(${pts.map(([x,y]) => `${x.toFixed(2)}% ${y.toFixed(2)}%`).join(', ')})`;
}

// Paper substrate — kid's drawing-paper feel. Torn edge + grain + crease.
function KidPaper({ width, height, seed = 1, tone = PAPER_BG, rotation = 0, children, style = {}, innerStyle = {} }) {
  const clip = useMemo(() => tornPath(seed), [seed]);
  return (
    React.createElement('div', {
      style: {
        width, height,
        filter: 'drop-shadow(0 14px 22px rgba(40,20,0,.22)) drop-shadow(0 2px 4px rgba(40,20,0,.18))',
        transform: `rotate(${rotation}deg)`,
        ...style,
      },
    },
      React.createElement('div', {
        style: {
          position: 'relative',
          width: '100%', height: '100%',
          background: tone,
          clipPath: clip,
          WebkitClipPath: clip,
          overflow: 'hidden',
          ...innerStyle,
        },
      },
        // paper grain
        React.createElement('svg', {
          'aria-hidden': true,
          style: {
            position: 'absolute', inset: 0, width: '100%', height: '100%',
            pointerEvents: 'none', mixBlendMode: 'multiply', opacity: .35,
          },
        },
          React.createElement('filter', { id: `paper-noise-${seed}` },
            React.createElement('feTurbulence', { type: 'fractalNoise', baseFrequency: '0.9', numOctaves: '2', stitchTiles: 'stitch', seed: seed }),
            React.createElement('feColorMatrix', { values: '0 0 0 0 0.78  0 0 0 0 0.68  0 0 0 0 0.5  0 0 0 0.55 0' })
          ),
          React.createElement('rect', { width: '100%', height: '100%', filter: `url(#paper-noise-${seed})` })
        ),
        // subtle crease
        React.createElement('div', {
          style: {
            position: 'absolute', left: '-2%', right: '-2%',
            top: `${30 + (seed * 7) % 30}%`, height: 1,
            background: 'linear-gradient(90deg, transparent, rgba(60,40,10,.18), transparent)',
            transform: `rotate(${(rand(seed) - 0.5) * 2}deg)`,
            pointerEvents: 'none',
          },
        }),
        // one tiny smudge
        React.createElement('div', {
          style: {
            position: 'absolute',
            left: `${10 + (seed * 13) % 70}%`,
            top:  `${65 + (seed * 5)  % 20}%`,
            width: 32, height: 18,
            background: 'radial-gradient(ellipse at center, rgba(80,55,15,.13), transparent 70%)',
            pointerEvents: 'none',
          },
        }),
        children
      )
    )
  );
}

// Hand-drawn wobbly rectangle outline.
function ActiveRing({ color, seed }) {
  const segs = 20;
  let s = seed;
  const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const j = 2.4;
  const W = 100, H = 100;
  const path = [];
  const corners = [[3,4], [W-3,4], [W-3,H-4], [3,H-4]];
  const side = (from, to) => {
    for (let i = 0; i <= segs; i++) {
      const t = i / segs;
      const x = from[0] + (to[0]-from[0]) * t + (r()-0.5)*j;
      const y = from[1] + (to[1]-from[1]) * t + (r()-0.5)*j;
      path.push(`${path.length === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`);
    }
  };
  side(corners[0], corners[1]);
  side(corners[1], corners[2]);
  side(corners[2], corners[3]);
  side(corners[3], corners[0]);
  return React.createElement('svg', {
    viewBox: '0 0 100 100', preserveAspectRatio: 'none',
    style: { position: 'absolute', inset: '4px 6px', width: 'calc(100% - 12px)', height: 'calc(100% - 8px)', pointerEvents: 'none' },
  },
    React.createElement('path', {
      d: path.join(' ') + 'Z', fill: 'none', stroke: color,
      strokeWidth: '2.4', strokeLinecap: 'round', strokeLinejoin: 'round', opacity: '.9',
    })
  );
}

// Hand-drawn rough rectangle as a child wrapper.
function RoughBox({ children, stroke = '#1a1410', strokeWidth = 2.5, seed = 7, padding = '14px 22px', style = {} }) {
  const segs = 14;
  let s = seed;
  const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const j = 1.2;
  const W = 100, H = 100;
  const path = [];
  const corners = [[2,2], [W-2,2], [W-2,H-2], [2,H-2]];
  let first = true;
  const side = (from, to, axis) => {
    for (let i = 0; i <= segs; i++) {
      const t = i / segs;
      const x = from[0] + (to[0]-from[0]) * t + (axis === 'x' ? 0 : (r()-0.5)*j);
      const y = from[1] + (to[1]-from[1]) * t + (axis === 'y' ? 0 : (r()-0.5)*j);
      path.push(`${first ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`);
      first = false;
    }
  };
  side(corners[0], corners[1], 'y');
  side(corners[1], corners[2], 'x');
  side(corners[2], corners[3], 'y');
  side(corners[3], corners[0], 'x');
  return React.createElement('span', {
    style: { position: 'relative', display: 'inline-block', padding, ...style },
  },
    React.createElement('svg', {
      viewBox: '0 0 100 100', preserveAspectRatio: 'none',
      style: { position: 'absolute', inset: 0, width: '100%', height: '100%' },
    },
      React.createElement('path', {
        d: path.join(' ') + 'Z', fill: 'none', stroke,
        strokeWidth, strokeLinecap: 'round', strokeLinejoin: 'round',
      })
    ),
    React.createElement('span', { style: { position: 'relative' } }, children)
  );
}

// Pencil underline with hand-drawn jiggle.
function PencilUnderline({ width = '100%', seed = 1 }) {
  const segs = 16;
  let s = seed;
  const r = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const pts = [];
  for (let i = 0; i <= segs; i++) {
    const x = (i / segs) * 100;
    const y = 50 + (r() - 0.5) * 14;
    pts.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`);
  }
  return React.createElement('svg', {
    viewBox: '0 0 100 8', preserveAspectRatio: 'none',
    style: { display: 'block', width, height: 8, marginTop: 2 },
  },
    React.createElement('path', {
      d: pts.join(' '), fill: 'none', stroke: PENCIL_GRAY,
      strokeWidth: '1.2', strokeLinecap: 'round', opacity: '.85',
    })
  );
}

// Brand wordmark, top of page.
function BrandHeader() {
  return React.createElement('div', { style: { textAlign: 'center', color: '#161208' } },
    React.createElement('div', {
      style: {
        fontFamily: '"Special Elite", "Courier New", monospace',
        fontSize: 58, lineHeight: 1.02, letterSpacing: '-0.01em',
        textShadow: '0 2px 0 rgba(255,255,255,.55)',
      },
    },
      'Pay Me Back. ',
      React.createElement('span', { style: { fontStyle: 'italic' } }, 'Or Else…')
    ),
    React.createElement('div', {
      style: {
        marginTop: 4,
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 22, color: '#2a221a',
      },
    },
      'a tone-controlled debt-collection generator for the morally flexible'
    )
  );
}

// ── Bridge to Streamlit (postMessage protocol used by st.components.v1.html) ──
function sendToStreamlit(value) {
  window.parent.postMessage({
    isStreamlitMessage: true,
    type: 'streamlit:setComponentValue',
    value: { ...value, _nonce: Math.random() }, // force change detection
    dataType: 'json',
  }, '*');
}

function setFrameHeight() {
  const h = Math.max(
    document.documentElement.scrollHeight,
    document.body.scrollHeight,
    window.innerHeight
  );
  window.parent.postMessage({
    isStreamlitMessage: true,
    type: 'streamlit:setFrameHeight',
    height: h,
  }, '*');
}

window.parent.postMessage({
  isStreamlitMessage: true,
  type: 'streamlit:componentReady',
  apiVersion: 1,
}, '*');
"""
