"""Letter paper — centered, char-by-char crayon streaming, action buttons."""


def letter_paper_js() -> str:
    return r"""
function StreamedCrayon({ text, rage, version = 0, fontSize = 22, speed }) {
  const [n, setN] = useState(0);

  // Reveal speed: rage 1-3 throttle ~26ms; rage 4 no throttle.
  const realSpeed = speed != null ? speed : (rage === 4 ? 6 : 26);

  useEffect(() => {
    setN(0);
    if (!text) return;
    const id = setInterval(() => {
      setN(prev => {
        if (prev >= text.length) { clearInterval(id); return prev; }
        return prev + 1;
      });
    }, realSpeed);
    return () => clearInterval(id);
  }, [text, version, realSpeed]);

  const c = CRAYON[rage];
  const visible = text.slice(0, n);

  // Word-level random uppercasing for rage 4.
  const words = visible.split(/(\s+)/);
  let wordIndex = 0;
  const transformed = words.map(w => {
    if (/^\s+$/.test(w) || !w) return w;
    const upcase = rage === 4 && rand(wordIndex, 8) < 0.18;
    wordIndex++;
    return upcase ? w.toUpperCase() : w;
  }).join('');

  const out = [];
  for (let i = 0; i < transformed.length; i++) {
    const ch = transformed[i];
    if (ch === '\n') { out.push(React.createElement('br', { key: `br-${i}` })); continue; }
    const j = rand(i, 1);
    const ry = (j - 0.5) * 3.5;             // y-offset px (~±1.75px)
    const rx = (rand(i, 4) - 0.5) * 1;      // x-offset px
    const rr = (rand(i, 2) - 0.5) * 6;      // rotation deg
    const rs = 1 + (rand(i, 3) - 0.5) * 0.16;
    const op = 0.85 + rand(i, 5) * 0.15;
    const isStreak = c.accent && (rand(i, 9) < 0.12) && ch !== ' ';
    // rage 3+: occasionally strike a char with overdraw (extra-bold-ish + slight darker)
    const isStruck = rage >= 3 && (rand(i, 11) < 0.04) && ch.trim();
    out.push(React.createElement('span', {
      key: i,
      style: {
        display: 'inline-block', whiteSpace: 'pre',
        transform: `translate(${rx}px, ${ry}px) rotate(${rr}deg) scale(${rs})`,
        color: isStreak ? c.accent : c.main,
        fontSize,
        lineHeight: 1.15,
        opacity: op,
        fontWeight: isStruck ? 800 : 'normal',
        textShadow: isStruck ? `0 0 1px ${c.main}` : 'none',
      },
    }, ch === ' ' ? ' ' : ch));
  }

  const streaming = n < text.length;
  return React.createElement('div', {
    style: {
      fontFamily: '"Gochi Hand", cursive',
      lineHeight: 1.55, letterSpacing: '.5px',
      textShadow: rage >= 3 ? '0 0 1px rgba(0,0,0,.18)' : 'none',
      filter: rage === 4 ? 'contrast(1.05)' : 'none',
    },
  },
    out,
    streaming && React.createElement('span', {
      style: {
        display: 'inline-block', width: 10, height: fontSize * 0.9,
        background: c.main, marginLeft: 2, verticalAlign: 'middle',
        animation: 'crayon-blink 0.7s steps(1) infinite',
      },
    })
  );
}

// "SAVED" stamp animation overlay.
function SavedStamp({ show, rage }) {
  if (!show) return null;
  const c = CRAYON[rage];
  return React.createElement('div', {
    style: {
      position: 'absolute', top: '30%', left: '50%',
      transform: 'translate(-50%, -50%) rotate(-12deg)',
      fontFamily: '"Gochi Hand", cursive',
      fontSize: 84, color: c.main,
      letterSpacing: '8px',
      pointerEvents: 'none',
      animation: 'saved-stamp 1.2s cubic-bezier(.34,1.56,.64,1) forwards',
      textShadow: `2px 2px 0 rgba(0,0,0,.15)`,
      zIndex: 20,
    },
  }, 'SAVED');
}

function PaperPlane({ show }) {
  if (!show) return null;
  return React.createElement('div', {
    style: {
      position: 'fixed', top: '50%', left: '20%',
      fontSize: 60,
      pointerEvents: 'none', zIndex: 80,
      animation: 'paper-plane 1.4s ease-in forwards',
    },
  }, '✈');
}

function LetterActions({ rage, letter, onCopy, onRegenerate, onSave, onEmail, onStartOver, busy }) {
  const c = CRAYON[rage];
  const btn = (label, fn, seed) => React.createElement('button', {
    type: 'button',
    'data-no-drag': true,
    onClick: busy ? null : fn,
    disabled: busy,
    style: {
      background: 'transparent', border: 'none',
      padding: 0, cursor: busy ? 'not-allowed' : 'pointer',
      color: c.main, opacity: busy ? 0.5 : 1,
    },
  },
    React.createElement(RoughBox, {
      stroke: c.main, strokeWidth: 2, seed, padding: '6px 12px',
    },
      React.createElement('span', {
        style: {
          fontFamily: '"Gochi Hand", cursive', fontSize: 15,
          color: c.main, letterSpacing: '.3px',
        },
      }, label)
    )
  );

  return React.createElement('div', {
    style: {
      display: 'flex', flexWrap: 'wrap', gap: 8,
      justifyContent: 'center', marginTop: 14,
      paddingTop: 8,
      borderTop: '1px dashed rgba(60,40,10,.2)',
    },
  },
    btn('copy', onCopy, 31),
    btn('regenerate', onRegenerate, 37),
    btn('save', onSave, 41),
    btn('send email', onEmail, 43),
    btn('start over', onStartOver, 47)
  );
}

// Normal-flow letter area (shares the centered worksheet with the form).
function LetterBody({ rage, letter, version, busy, onCopy, onRegenerate, onSave, onEmail, onStartOver }) {
  const empty = !letter;
  return React.createElement('div', {
    style: { flex: '1 1 auto', minHeight: 0, display: 'flex', flexDirection: 'column' },
  },
    React.createElement('div', {
      style: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        fontFamily: '"Gochi Hand", cursive',
        color: PENCIL_GRAY, fontSize: 16,
        marginBottom: 8, opacity: empty ? .5 : .85, flex: '0 0 auto',
      },
    },
      React.createElement('span', null, 'from: the chicken'),
      React.createElement('span', null, `tone: ${CRAYON[rage].label}`)
    ),

    empty && !busy && React.createElement('div', {
      style: {
        flex: 1,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        textAlign: 'center', gap: 8, color: PENCIL_GRAY,
      },
    },
      React.createElement('div', {
        style: {
          fontFamily: '"Gochi Hand", cursive',
          fontSize: 26, lineHeight: 1.15, color: CRAYON_NAVY,
        },
      }, 'the chicken is waiting.'),
      React.createElement('div', {
        style: {
          fontFamily: '"Gochi Hand", cursive',
          fontSize: 18, color: PENCIL_GRAY, opacity: .8,
        },
      },
        'fill out the worksheet above.', React.createElement('br'),
        'pick a tone on the left.', React.createElement('br'),
        'the chicken will write the letter.'
      )
    ),

    empty && busy && React.createElement('div', {
      style: {
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        textAlign: 'center', color: CRAYON[rage].main,
      },
    },
      React.createElement('div', {
        style: { fontFamily: '"Gochi Hand", cursive', fontSize: 28 },
      }, 'the chicken is writing…'),
      React.createElement('div', {
        style: {
          marginTop: 10, fontFamily: '"Gochi Hand", cursive',
          fontSize: 18, color: PENCIL_GRAY, opacity: .7,
        },
      }, '(give it a moment)')
    ),

    !empty && React.createElement(React.Fragment, null,
      React.createElement('div', { style: { flex: '1 1 auto', minHeight: 0, overflow: 'auto' } },
        React.createElement(StreamedCrayon, { text: letter, rage, version, fontSize: 21 })
      ),
      React.createElement(LetterActions, {
        rage, letter, busy,
        onCopy, onRegenerate, onSave, onEmail, onStartOver,
      })
    )
  );
}

// The merged worksheet: shows EITHER the form fields OR the streamed letter
// on the same sheet of paper — never both. Pre-submit shows the form; once
// the user submits (busy) or a letter exists, the form is replaced by the
// letter view. "start over" clears the letter and brings the form back.
// The two states cross-fade via opacity so the dimensions stay stable.
function Worksheet({ rage, values, onChange, onSubmit, errors, busy,
                     letter, version, onCopy, onRegenerate, onSave, onEmail, onStartOver,
                     savedFlash, planeFlash }) {
  const W = 760, H = 780;
  const showLetter = busy || !!letter;
  const layer = (visible) => ({
    position: 'absolute', inset: 0,
    padding: '30px 40px 26px',
    boxSizing: 'border-box',
    display: 'flex', flexDirection: 'column', gap: 10,
    overflow: 'hidden',
    opacity: visible ? 1 : 0,
    pointerEvents: visible ? 'auto' : 'none',
    transition: 'opacity 250ms ease',
  });
  return React.createElement('div', { style: { position: 'relative' } },
    React.createElement(SavedStamp, { show: savedFlash, rage }),
    React.createElement(KidPaper, { width: W, height: H, seed: 11, tone: PAPER_BG_ALT, rotation: 0.6 },
      React.createElement('div', { style: layer(!showLetter) },
        React.createElement(WorksheetFormBody, { rage, values, onChange, onSubmit, errors, busy })
      ),
      React.createElement('div', { style: layer(showLetter) },
        React.createElement(LetterBody, {
          rage, letter, version, busy,
          onCopy, onRegenerate, onSave, onEmail, onStartOver,
        })
      )
    ),
    React.createElement(PaperPlane, { show: planeFlash })
  );
}
"""
