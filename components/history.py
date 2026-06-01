"""The hall of grudges — draggable sticky note with horizontal grudge cards."""


def history_js() -> str:
    return r"""
const RAGE_FG = { 1: '#1c3b8f', 2: '#5a3a1a', 3: '#c8421a', 4: '#0a0a0a' };

// Bottom-left collapsible drawer (anchored bottom-left; grows up + right).
function HallDrawer({ currentRage, letters, onDelete, onPick, active, animate }) {
  const [open, setOpen] = useState(false);
  const [confirmId, setConfirmId] = useState(null);

  const count = letters?.length || 0;
  const W = open ? 460 : 130;
  const H = open ? 330 : 120;

  return React.createElement('div', {
    style: {
      position: 'absolute', left: 80, bottom: 40,
      width: W, height: H,
      zIndex: open ? 30 : 6,
      opacity: active ? 1 : 0,
      pointerEvents: active ? 'auto' : 'none',
      transition: (animate ? 'opacity 380ms ease 320ms, ' : '')
        + 'width .35s cubic-bezier(.2,.7,.2,1), height .35s cubic-bezier(.2,.7,.2,1)',
    },
  },
    React.createElement(KidPaper, {
      width: W, height: H, seed: open ? 23 : 17,
      tone: PAPER_BG_ALT, rotation: open ? -1.2 : -3,
    },
      !open && React.createElement(CollapsedHallView, {
        count, onOpen: () => setOpen(true),
      }),
      open && React.createElement(ExpandedHallView, {
        currentRage, letters, onClose: () => { setOpen(false); setConfirmId(null); },
        onDelete, onPick, confirmId, setConfirmId,
      })
    )
  );
}

function CollapsedHallView({ count, onOpen }) {
  return React.createElement('button', {
    'data-no-drag': true,
    onClick: onOpen,
    'aria-label': 'open hall of grudges',
    style: {
      position: 'absolute', inset: 0,
      padding: '12px 10px',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 6, boxSizing: 'border-box',
      background: 'transparent', border: 'none', cursor: 'pointer',
      width: '100%', height: '100%',
    },
  },
    React.createElement('div', {
      style: {
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 17, color: CRAYON_NAVY,
        lineHeight: 1.05, letterSpacing: '.4px', textAlign: 'center',
      },
    }, 'the hall of', React.createElement('br'), 'grudges'),
    React.createElement('div', {
      style: {
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 13, color: PENCIL_GRAY, opacity: .8,
      },
    }, `${count} on file`),
    React.createElement(RoughBox, {
      stroke: CRAYON_NAVY, strokeWidth: 2, seed: 29, padding: '4px 12px',
    },
      React.createElement('span', {
        style: { fontFamily: '"Gochi Hand", cursive', fontSize: 15, color: CRAYON_NAVY },
      }, 'open')
    )
  );
}

function ExpandedHallView({ currentRage, letters, onClose, onDelete, onPick, confirmId, setConfirmId }) {
  return React.createElement('div', {
    style: {
      position: 'absolute', inset: 0,
      padding: '16px 22px 18px',
      display: 'flex', flexDirection: 'column', gap: 10,
      boxSizing: 'border-box',
    },
  },
    React.createElement('div', {
      style: { display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 },
    },
      React.createElement('div', { style: { minWidth: 0 } },
        React.createElement('div', {
          style: {
            fontFamily: '"Gochi Hand", cursive',
            fontSize: 30, color: CRAYON_NAVY,
            lineHeight: 1, letterSpacing: '.5px',
          },
        }, 'the hall of grudges'),
        React.createElement('div', {
          style: {
            fontFamily: '"Gochi Hand", cursive',
            fontSize: 16, color: PENCIL_GRAY, opacity: .8, marginTop: 2,
          },
        }, `${letters.length} letter${letters.length === 1 ? '' : 's'} on file · scroll →`)
      ),
      React.createElement('button', {
        'data-no-drag': true, onClick: onClose, 'aria-label': 'close',
        style: {
          background: 'transparent', border: 'none', cursor: 'pointer',
          fontFamily: '"Gochi Hand", cursive', fontSize: 28, color: '#1a1410',
          lineHeight: 1, padding: '0 8px', transform: 'translateY(-2px)',
        },
      }, '×')
    ),
    React.createElement('div', {
      style: {
        height: 1, alignSelf: 'stretch',
        background: 'repeating-linear-gradient(to right, rgba(60,40,10,.4) 0 6px, transparent 6px 10px)',
      },
    }),
    React.createElement('div', {
      'data-no-drag': true,
      className: 'grudge-scroll',
      style: {
        display: 'flex', gap: 12, overflowX: 'auto',
        flex: 1, paddingBottom: 4,
        scrollSnapType: 'x mandatory',
      },
      onPointerDown: (e) => e.stopPropagation(),
    },
      letters.length === 0
        ? React.createElement('div', {
            style: {
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: '"Gochi Hand", cursive', fontSize: 18,
              color: PENCIL_GRAY, opacity: .7,
            },
          }, 'no grudges yet. start collecting →')
        : letters.map((g) =>
            React.createElement(GrudgeCard, {
              key: g.id, g,
              isCurrentRage: g.rage_level === currentRage,
              confirmDelete: confirmId === g.id,
              onPick: () => onPick(g),
              onAskDelete: () => setConfirmId(g.id),
              onConfirmDelete: () => { onDelete(g.id); setConfirmId(null); },
              onCancelDelete: () => setConfirmId(null),
            })
          )
    )
  );
}

function GrudgeCard({ g, isCurrentRage, confirmDelete, onPick, onAskDelete, onConfirmDelete, onCancelDelete }) {
  const dots = '●●●●'.slice(0, g.rage_level) + '○○○○'.slice(0, 4 - g.rage_level);
  const fg = RAGE_FG[g.rage_level];
  const snippet = (g.letter_text || '').slice(0, 80) + ((g.letter_text || '').length > 80 ? '…' : '');
  const tone = CRAYON[g.rage_level].label;
  const created = (g.created_at || '').split(' ')[0] || '';

  // The whole card is a reopen target (change #1): clicking it loads the
  // saved letter back into the worksheet. The delete controls below
  // stopPropagation so they don't double as a reopen.
  return React.createElement('div', {
    'data-no-drag': true,
    onClick: onPick,
    title: 'reopen this letter',
    onMouseEnter: (e) => { e.currentTarget.style.transform = 'translateY(-2px)'; },
    onMouseLeave: (e) => { e.currentTarget.style.transform = 'none'; },
    style: {
      flex: '0 0 240px',
      background: '#fbf5e3',
      border: '1.5px solid rgba(26,20,16,.16)',
      borderRadius: 10, padding: 12,
      boxShadow: isCurrentRage
        ? '0 0 0 2px #1a1410, 0 8px 18px rgba(40,20,0,.18)'
        : '0 4px 12px rgba(40,20,0,.12)',
      display: 'flex', flexDirection: 'column', gap: 7,
      scrollSnapAlign: 'start',
      fontFamily: 'Inter, system-ui, sans-serif',
      color: '#1a1410', position: 'relative',
      cursor: 'pointer',
      transition: 'transform .12s ease',
    },
  },
    React.createElement('div', {
      style: { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 },
    },
      React.createElement('div', {
        style: {
          fontFamily: '"Special Elite", monospace', fontSize: 14,
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          minWidth: 0, flex: '1 1 auto',
        },
      }, g.debtor_name),
      React.createElement('div', {
        style: { fontSize: 11, color: '#5a3a1a', letterSpacing: '.04em', whiteSpace: 'nowrap', flexShrink: 0 },
      }, created)
    ),
    React.createElement('div', {
      style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    },
      React.createElement('div', {
        style: { fontFamily: '"Special Elite", monospace', fontSize: 20 },
      }, `$${Number(g.amount).toFixed(0)}`),
      React.createElement('div', {
        style: { fontFamily: 'monospace', fontSize: 12, color: fg, letterSpacing: 2 },
      }, dots)
    ),
    React.createElement('div', {
      style: {
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 15, lineHeight: 1.2, color: '#3b3226',
        borderTop: '1px dashed rgba(26,20,16,.22)',
        paddingTop: 6, minHeight: 38,
      },
    }, '"', snippet, '"'),
    React.createElement('div', {
      style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 6 },
    },
      React.createElement('div', {
        style: {
          fontSize: 10, textTransform: 'uppercase', letterSpacing: '.14em',
          color: fg, fontWeight: 700,
        },
      }, tone),
      confirmDelete
        ? React.createElement('div', { style: { display: 'flex', gap: 4 } },
            React.createElement('button', {
              'data-no-drag': true,
              onClick: (e) => { e.stopPropagation(); onConfirmDelete(); },
              style: {
                background: '#b51212', color: 'white', border: 'none',
                padding: '3px 7px', borderRadius: 4, fontSize: 11,
                cursor: 'pointer', fontFamily: '"Gochi Hand", cursive',
              },
            }, 'yes, burn it'),
            React.createElement('button', {
              'data-no-drag': true,
              onClick: (e) => { e.stopPropagation(); onCancelDelete(); },
              style: {
                background: 'transparent', color: PENCIL_GRAY,
                border: '1px solid rgba(60,40,10,.3)',
                padding: '3px 7px', borderRadius: 4, fontSize: 11,
                cursor: 'pointer', fontFamily: '"Gochi Hand", cursive',
              },
            }, 'no')
          )
        : React.createElement('button', {
            'data-no-drag': true,
            onClick: (e) => { e.stopPropagation(); onAskDelete(); },
            style: {
              background: 'transparent', color: PENCIL_GRAY,
              border: 'none', cursor: 'pointer',
              fontFamily: '"Gochi Hand", cursive', fontSize: 14, opacity: .6,
              padding: 0,
            },
            onMouseEnter: (e) => e.currentTarget.style.opacity = 1,
            onMouseLeave: (e) => e.currentTarget.style.opacity = .6,
          }, 'delete')
    )
  );
}
"""
