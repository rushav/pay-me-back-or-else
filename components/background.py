"""Desk background + landing CTA.

The photoreal desk (``main_table.png``) is the base of the camera/zoom layer:
View 1 shows the whole desk; clicking the CTA zooms the camera into the
worksheet region for View 2. There is no sky — the desk is the background.
"""


def background_js() -> str:
    return r"""
// The desk: single photoreal image, base of the camera/zoom layer.
function Desk() {
  return React.createElement('img', {
    src: DESK_SRC, alt: '', draggable: false,
    style: {
      position: 'absolute', inset: 0,
      width: '100%', height: '100%',
      objectFit: 'cover', objectPosition: 'center',
      pointerEvents: 'none', userSelect: 'none', display: 'block',
    },
  });
}

// Landing call-to-action — crayon-stroked "write a letter" button.
function LandingCTA({ onClick }) {
  return React.createElement('button', {
    type: 'button', 'data-no-drag': true, onClick,
    style: {
      background: 'rgba(255,252,244,.93)', border: 'none', padding: 0,
      cursor: 'pointer', borderRadius: 10,
      boxShadow: '0 12px 26px rgba(20,12,4,.32)',
    },
    onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)',
    onMouseLeave: (e) => e.currentTarget.style.transform = 'none',
  },
    React.createElement(RoughBox, {
      stroke: CRAYON[3].main, strokeWidth: 3, seed: 91, padding: '16px 30px',
    },
      React.createElement('span', {
        style: {
          fontFamily: '"Gochi Hand", cursive', fontSize: 30,
          color: CRAYON[3].main, letterSpacing: '.5px', whiteSpace: 'nowrap',
        },
      }, '✎ write a letter')
    )
  );
}
"""
