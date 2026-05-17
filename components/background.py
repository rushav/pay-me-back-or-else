"""Sky background — full-bleed crossfading sky_rage_N images."""


def background_js() -> str:
    return r"""
function SkyBackdrop({ rage }) {
  return React.createElement(React.Fragment, null,
    SKY_IMGS.map((src, i) =>
      React.createElement('img', {
        key: src, src, alt: '',
        style: {
          position: 'absolute', inset: 0,
          width: '100%', height: '100%', objectFit: 'cover',
          opacity: rage === i + 1 ? 1 : 0,
          transition: 'opacity .9s ease',
          pointerEvents: 'none',
          zIndex: 0,
        },
      })
    )
  );
}
"""
