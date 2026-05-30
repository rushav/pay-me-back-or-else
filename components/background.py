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
      // Brighter paper-stock card so the CTA pops off the desk wood and
      // reads as the primary action. The hover lift now has a transition
      // so it actually animates instead of snapping.
      background: 'rgba(255,250,235,1)', border: 'none', padding: 0,
      cursor: 'pointer', borderRadius: 12,
      boxShadow: '0 14px 30px rgba(20,12,4,.36), 0 2px 4px rgba(20,12,4,.22)',
      transform: 'translateY(0)',
      transition: 'transform 160ms ease, box-shadow 160ms ease',
    },
    onMouseEnter: (e) => {
      e.currentTarget.style.transform = 'translateY(-3px)';
      e.currentTarget.style.boxShadow = '0 18px 36px rgba(20,12,4,.42), 0 2px 4px rgba(20,12,4,.22)';
    },
    onMouseLeave: (e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 14px 30px rgba(20,12,4,.36), 0 2px 4px rgba(20,12,4,.22)';
    },
  },
    React.createElement(RoughBox, {
      stroke: CRAYON[3].main, strokeWidth: 3.4, seed: 91, padding: '18px 38px',
    },
      React.createElement('span', {
        style: {
          fontFamily: '"Gochi Hand", cursive', fontSize: 34,
          color: CRAYON[3].main, letterSpacing: '.5px', whiteSpace: 'nowrap',
        },
      }, '✎ write a letter')
    )
  );
}
"""
