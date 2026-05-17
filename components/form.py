"""The demand worksheet — crayon labels, pencil underlines, custom dropdown."""


def form_js() -> str:
    return r"""
const RELATIONSHIPS = ['friend', 'family', 'coworker', 'ex', 'roommate', 'total stranger'];
const TIME_UNITS = ['days', 'weeks', 'months', 'years'];

const BUTTON_LABEL = {
  1: 'ask nicely →',
  2: 'drop a hint →',
  3: 'demand justice →',
  4: 'UNLEASH HELLFIRE →',
};

function CrayonLabel({ children, style = {} }) {
  return React.createElement('span', {
    style: {
      fontFamily: '"Gochi Hand", cursive',
      fontSize: 19, color: CRAYON_NAVY,
      lineHeight: 1, letterSpacing: '.5px',
      ...style,
    },
  }, children);
}

function WorksheetInput({ value, onChange, placeholder, type = 'text', width, prefix, errorTone = false }) {
  return React.createElement('div', { style: { position: 'relative', width: width || '100%' } },
    prefix && React.createElement('span', {
      style: {
        position: 'absolute', left: 2, top: 4,
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 22, color: PENCIL_GRAY,
      },
    }, prefix),
    React.createElement('input', {
      type,
      value: value || '',
      onChange: (e) => onChange(e.target.value),
      placeholder,
      'data-no-drag': true,
      style: {
        width: '100%',
        background: 'transparent',
        border: 'none', outline: 'none',
        padding: `4px 0 4px ${prefix ? 22 : 2}px`,
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 22, color: PENCIL_GRAY,
        letterSpacing: '.5px',
        boxSizing: 'border-box',
        textDecoration: errorTone ? 'underline wavy #b51212' : 'none',
      },
    }),
    React.createElement(PencilUnderline, { seed: (placeholder?.length || 0) * 13 + 3 })
  );
}

function WorksheetTextarea({ value, onChange, placeholder, rows = 2 }) {
  return React.createElement('div', { style: { position: 'relative' } },
    React.createElement('textarea', {
      rows,
      value: value || '',
      onChange: (e) => onChange(e.target.value),
      placeholder,
      'data-no-drag': true,
      style: {
        width: '100%',
        background: 'repeating-linear-gradient(transparent 0 30px, rgba(60,55,48,.35) 30px 31px)',
        backgroundPosition: '0 8px',
        border: 'none', outline: 'none',
        padding: '4px 0 0 2px',
        fontFamily: '"Gochi Hand", cursive',
        fontSize: 22, lineHeight: '31px',
        color: PENCIL_GRAY, letterSpacing: '.5px',
        boxSizing: 'border-box', resize: 'none',
      },
    })
  );
}

function WorksheetDropdown({ value, onChange, options, seed = 71 }) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [open]);

  return React.createElement('div', { ref: wrapRef, style: { position: 'relative' }, 'data-no-drag': true },
    React.createElement('button', {
      type: 'button',
      'data-no-drag': true,
      onClick: () => setOpen(o => !o),
      style: {
        display: 'flex', alignItems: 'center', gap: 10,
        background: 'transparent', border: 'none',
        padding: '4px 0', cursor: 'pointer',
        fontFamily: '"Gochi Hand", cursive', fontSize: 22,
        color: PENCIL_GRAY, letterSpacing: '.5px',
      },
    },
      React.createElement('span', null, value),
      React.createElement('svg', {
        width: '22', height: '14', viewBox: '0 0 22 14',
        style: { transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .2s' },
      },
        React.createElement('path', {
          d: 'M2,3 L11,11 L20,3',
          fill: 'none', stroke: PENCIL_GRAY,
          strokeWidth: '1.6', strokeLinecap: 'round', strokeLinejoin: 'round',
        })
      )
    ),
    React.createElement(PencilUnderline, { seed }),
    open && React.createElement('div', {
      style: {
        position: 'absolute', top: '100%', left: 0, marginTop: 6,
        background: '#fbf3df',
        border: '1px solid rgba(60,40,10,.18)',
        borderRadius: 6, padding: 6,
        boxShadow: '0 12px 28px rgba(40,20,0,.22)',
        minWidth: 180, zIndex: 80,
      },
    },
      options.map(opt =>
        React.createElement('button', {
          key: opt, type: 'button', 'data-no-drag': true,
          onClick: () => { onChange(opt); setOpen(false); },
          style: {
            display: 'block', width: '100%', textAlign: 'left',
            background: opt === value ? 'rgba(28,59,143,.10)' : 'transparent',
            border: 'none', padding: '6px 10px', borderRadius: 4,
            fontFamily: '"Gochi Hand", cursive', fontSize: 20,
            color: opt === value ? CRAYON_NAVY : PENCIL_GRAY,
            cursor: 'pointer',
          },
          onMouseEnter: (e) => e.currentTarget.style.background = 'rgba(28,59,143,.08)',
          onMouseLeave: (e) => e.currentTarget.style.background = opt === value ? 'rgba(28,59,143,.10)' : 'transparent',
        }, opt)
      )
    )
  );
}

function WorksheetForm({ rage, values, onChange, onSubmit, errors, busy }) {
  const set = (k) => (v) => onChange({ ...values, [k]: v });
  const c = CRAYON[rage];
  const W = 400, H = 720;

  const errSet = new Set(errors || []);
  const hasErr = (field) => Array.from(errSet).some(e => e.includes(field.replace('_', ' ')));

  return React.createElement(KidPaper, {
    width: W, height: H, seed: 11, tone: PAPER_BG_ALT, rotation: 1.4,
  },
    React.createElement('div', {
      style: {
        position: 'absolute', inset: 0,
        padding: '32px 32px 26px',
        boxSizing: 'border-box',
        display: 'flex', flexDirection: 'column', gap: 10,
        overflow: 'hidden',
      },
    },
      React.createElement('div', {
        style: { display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' },
      },
        React.createElement('div', {
          style: {
            fontFamily: '"Gochi Hand", cursive',
            fontSize: 30, color: CRAYON_NAVY, lineHeight: 1,
          },
        }, 'the demand'),
        React.createElement('div', {
          style: {
            fontFamily: '"Gochi Hand", cursive',
            fontSize: 18, color: CRAYON_BROWN,
            transform: 'rotate(-3deg)', transformOrigin: 'right',
          },
        }, 'file no. 0427')
      ),

      React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        React.createElement(CrayonLabel, null, 'who owes you?'),
        React.createElement(WorksheetInput, {
          value: values.debtor_name,
          onChange: set('debtor_name'),
          placeholder: 'marcus',
          errorTone: hasErr('debtor name'),
        })
      ),

      React.createElement('div', {
        style: { display: 'grid', gridTemplateColumns: '1.1fr 1fr 1fr', gap: 14 },
      },
        React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
          React.createElement(CrayonLabel, null, 'how much?'),
          React.createElement(WorksheetInput, {
            value: values.amount, onChange: set('amount'),
            placeholder: '240', prefix: '$',
            errorTone: hasErr('amount'),
          })
        ),
        React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
          React.createElement(CrayonLabel, null, 'how long?'),
          React.createElement(WorksheetInput, {
            value: values.time_owed, onChange: set('time_owed'),
            placeholder: '3',
            errorTone: hasErr('time owed'),
          })
        ),
        React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
          React.createElement(CrayonLabel, null, 'unit'),
          React.createElement(WorksheetDropdown, {
            value: values.time_unit || 'weeks',
            onChange: set('time_unit'),
            options: TIME_UNITS,
            seed: 13,
          })
        )
      ),

      React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        React.createElement(CrayonLabel, null, 'they are your…'),
        React.createElement(WorksheetDropdown, {
          value: values.relationship || 'friend',
          onChange: set('relationship'),
          options: RELATIONSHIPS, seed: 71,
        })
      ),

      React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        React.createElement(CrayonLabel, null,
          'what happened? ',
          React.createElement('span', { style: { color: PENCIL_GRAY, opacity: .6 } }, '(optional)')
        ),
        React.createElement(WorksheetTextarea, {
          value: values.context, onChange: set('context'),
          placeholder: 'brunch, again', rows: 2,
        })
      ),

      React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        React.createElement(CrayonLabel, null,
          'venmo / zelle? ',
          React.createElement('span', { style: { color: PENCIL_GRAY, opacity: .6 } }, '(optional)')
        ),
        React.createElement(WorksheetInput, {
          value: values.payment_handle, onChange: set('payment_handle'),
          placeholder: '@you-know-it',
        })
      ),

      errors && errors.length > 0 && React.createElement('ul', {
        style: {
          margin: 0, padding: '4px 0 0 18px',
          fontFamily: '"Gochi Hand", cursive', fontSize: 16,
          color: '#b51212', lineHeight: 1.2,
        },
      },
        errors.map((e, i) => React.createElement('li', { key: i }, e))
      ),

      React.createElement('div', {
        style: { marginTop: 'auto', display: 'flex', justifyContent: 'center' },
        'data-no-drag': true,
      },
        React.createElement('button', {
          type: 'button', 'data-no-drag': true,
          onClick: busy ? null : onSubmit,
          disabled: busy,
          style: {
            background: 'transparent', border: 'none',
            padding: 0, cursor: busy ? 'wait' : 'pointer',
            color: c.main, opacity: busy ? 0.6 : 1,
          },
        },
          React.createElement(RoughBox, {
            stroke: c.main, strokeWidth: 3,
            seed: rage * 17 + 3, padding: '14px 26px',
          },
            React.createElement('span', {
              style: {
                fontFamily: '"Gochi Hand", cursive',
                fontSize: rage === 4 ? 30 : 26,
                color: c.main, letterSpacing: '.5px',
                textTransform: rage === 4 ? 'uppercase' : 'none',
              },
            }, busy ? 'the chicken is thinking…' : BUTTON_LABEL[rage])
          )
        )
      )
    )
  );
}
"""
