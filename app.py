"""Pay Me Back. Or Else. — single-page Streamlit entry point.

The entire interactive UI is rendered inside one streamlit.components.v1.html
iframe (a faithful port of the Claude Design React mock). Streamlit owns the
session state and the Claude API call; the iframe owns the visual scene and
talks back via the standard component setComponentValue protocol.
"""

import base64
import json
import mimetypes
import sys
from pathlib import Path

import streamlit as st

from components.background import background_js
from components.form import form_js
from components.history import history_js
from components.letter_paper import letter_paper_js
from components.mascot import mascot_js
from components.rage_meter import rage_meter_js
from components.shared import shared_js
from pmb_component import render as pmb_render
from services import claude_service, db_service
from utils.validators import validate_form


REPO_ROOT = Path(__file__).resolve().parent
DESIGN_DIR = REPO_ROOT / "design"
ASSETS_DIR = REPO_ROOT / "assets"
STATIC_DIR = REPO_ROOT / "static"


# ── Asset loading ─────────────────────────────────────────────
#
# Assets are embedded as base64 data: URLs inline in the iframe HTML.
#
# We previously used Streamlit static serving (./static at /app/static/),
# but the iframe is now srcdoc'd inside the pmb_component harness — and
# srcdoc iframes have a null origin, so relative paths and even absolute
# /app/static/ URLs can't resolve (window.top.location throws cross-origin
# on Streamlit Cloud's split-domain deploy). Inlining bytes sidesteps origin
# entirely: data: URLs work in any iframe regardless of origin policy.
#
# Total payload after main_table.jpg compression is ~1 MB raw → ~1.4 MB
# base64, which is acceptable. Cached so the encoding cost is paid once.


@st.cache_resource(show_spinner=False)
def _asset_data_urls() -> dict:
    def url(name: str) -> str:
        path = STATIC_DIR / name
        mime, _ = mimetypes.guess_type(path.name)
        if mime is None:
            mime = "application/octet-stream"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"
    return {
        "desk":     url("main_table.jpg"),
        "chicken":  [url(f"chicken{i}-removebg-preview.png") for i in (1, 2, 3, 4)],
        "therm":    [url(f"T{i}-removebg-preview.png") for i in (1, 2, 3, 4)],
        "drawing":  [url(f"drawing{i}-removebg-preview.png") for i in (1, 2, 3, 4)],
    }


@st.cache_resource(show_spinner=False)
def _styles_css() -> str:
    return (ASSETS_DIR / "styles.css").read_text()


# ── Session state ─────────────────────────────────────────────

def _init_state() -> None:
    ss = st.session_state
    # Every fresh session starts on the landing page. We deliberately do NOT
    # read from query params or any other persistence — a hard refresh
    # should bring the desk + "write a letter" CTA back, not drop the user
    # straight into the worksheet. In-session reruns (form keystrokes, rage
    # tile clicks) preserve view via session_state's natural lifetime, and
    # the zoom transition's animate-only-on-click guard lives in the iframe.
    ss.setdefault("view", "landing")
    ss.setdefault("rage_level", 1)
    ss.setdefault("form_data", {
        "debtor_name": "",
        "amount": "",
        "time_owed": "",
        "time_unit": "weeks",
        "relationship": "friend",
        "context": "",
        "payment_handle": "",
    })
    ss.setdefault("generated_letter", None)
    ss.setdefault("is_streaming", False)
    ss.setdefault("letters", db_service.get_all_letters())
    ss.setdefault("validation_errors", [])
    ss.setdefault("last_action_nonce", None)
    # user_age is the optional age-gate input from the landing worksheet;
    # validated as a positive int (or None) in the submit handler.
    ss.setdefault("user_age", None)
    ss.setdefault("api_error", None)


# ── Action dispatch ───────────────────────────────────────────

def _coerce_age(raw) -> int | None:
    """Coerce a user-supplied age into a positive int, or None if invalid/blank.

    None is the "under-18 default" — safer when a user leaves it blank;
    the prompt-side age gate (claude_service.build_prompt) treats None
    and <18 identically (no profanity modifier).
    """
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def _generate_letter(form_data: dict, rage: int, user_age: int | None = None) -> None:
    """Call Claude (streaming) and accumulate into session state."""
    merged = {**form_data, "rage_level": rage, "user_age": user_age}
    errors = validate_form(merged)
    if errors:
        st.session_state["validation_errors"] = errors
        st.session_state["is_streaming"] = False
        return

    st.session_state["validation_errors"] = []
    st.session_state["is_streaming"] = True
    st.session_state["generated_letter"] = None
    st.session_state["api_error"] = None

    print(
        f"[app] _generate_letter: calling stream_letter "
        f"debtor={form_data.get('debtor_name')!r} rage={rage} age={user_age!r}",
        file=sys.stderr, flush=True,
    )
    chunks: list[str] = []
    try:
        first = True
        for chunk in claude_service.stream_letter(merged):
            if first:
                print(
                    f"[app] _generate_letter: first chunk received ({len(chunk)} chars)",
                    file=sys.stderr, flush=True,
                )
                first = False
            chunks.append(chunk)
        full = "".join(chunks).strip()
        print(
            f"[app] _generate_letter: stream complete, {len(full)} chars total",
            file=sys.stderr, flush=True,
        )
        st.session_state["generated_letter"] = full or "(the chicken is speechless.)"
    except claude_service.MissingAPIKeyError as exc:
        print(f"[app] _generate_letter: MissingAPIKeyError: {exc}", file=sys.stderr, flush=True)
        st.session_state["api_error"] = str(exc)
    except Exception as exc:  # noqa: BLE001 — user-facing error display
        print(
            f"[app] _generate_letter: failed: {type(exc).__name__}: {exc}",
            file=sys.stderr, flush=True,
        )
        st.session_state["api_error"] = f"the chicken couldn't reach claude: {exc}"
    finally:
        st.session_state["is_streaming"] = False


def _handle_action(payload: dict) -> str | None:
    """Dispatch an iframe action. Returns 'no_rerun' if the caller should
    deliberately NOT call st.rerun() afterwards (currently just `save`,
    which would otherwise re-srcdoc the iframe and re-stream the letter).
    """
    nonce = payload.get("_nonce")
    if nonce is not None and nonce == st.session_state.get("last_action_nonce"):
        return None
    st.session_state["last_action_nonce"] = nonce

    action = payload.get("action")
    if action == "set_view":
        view = payload.get("view")
        if view in ("landing", "app"):
            st.session_state["view"] = view
            # The landing CTA validates age client-side before allowing the
            # transition, so by the time set_view fires we know user_age is
            # present and well-formed. Store it now so the prompt-side gate
            # has it ready for the first submit.
            age = _coerce_age(payload.get("user_age"))
            if age is not None:
                st.session_state["user_age"] = age
            # Intentionally NOT mirroring to st.query_params anymore —
            # that's what caused refresh-after-CTA to skip the landing
            # page. session_state alone keeps view stable across the
            # in-session reruns; a true refresh resets it to "landing".

    # 'set_rage' is intentionally not handled here — rage is iframe-local
    # state and arrives with submit/regenerate when it actually matters.
    # Suppressing it removes the per-tile-click rerun + page flicker.

    elif action == "update_form":
        st.session_state["form_data"].update(payload.get("form_data") or {})

    elif action == "submit":
        form = {**st.session_state["form_data"], **(payload.get("form_data") or {})}
        st.session_state["form_data"] = form
        rage = int(payload.get("rage", st.session_state["rage_level"]))
        st.session_state["rage_level"] = rage
        age = _coerce_age(payload.get("user_age"))
        st.session_state["user_age"] = age
        _generate_letter(form, rage, age)

    elif action == "regenerate":
        rage = int(payload.get("rage", st.session_state["rage_level"]))
        age = _coerce_age(payload.get("user_age"))
        if age is not None:
            st.session_state["user_age"] = age
        _generate_letter(st.session_state["form_data"], rage, st.session_state.get("user_age"))

    elif action == "save":
        # Save is deliberately fire-and-forget: write to the DB but do
        # NOT trigger a rerun. The iframe optimistically prepended the
        # letter to its local hall list and flashed its own SAVED stamp,
        # so a rerun here would only cause a re-srcdoc and re-stream of
        # an already-displayed letter. ss["letters"] is not refreshed
        # here either — main() pulls a fresh copy on every script run,
        # so the next real rerun picks up this save naturally.
        letter = st.session_state.get("generated_letter")
        if letter:
            payload_form = payload.get("form_data") or {}
            saved_rage = int(payload.get("rage", st.session_state["rage_level"]))
            db_service.save_letter(
                {**st.session_state["form_data"], **payload_form, "rage_level": saved_rage},
                letter,
            )
        return "no_rerun"

    elif action == "delete":
        letter_id_raw = payload.get("id")
        # Optimistic-save entries have ids like 'local-<timestamp>' and
        # don't exist in the DB. Ignore them — the next refresh will
        # drop the optimistic row in favor of the real one.
        try:
            letter_id = int(letter_id_raw)
        except (TypeError, ValueError):
            return None
        db_service.delete_letter(letter_id)
        st.session_state["letters"] = db_service.get_all_letters()

    elif action == "start_over":
        st.session_state["form_data"] = {
            "debtor_name": "",
            "amount": "",
            "time_owed": "",
            "time_unit": "weeks",
            "relationship": "friend",
            "context": "",
            "payment_handle": "",
        }
        st.session_state["generated_letter"] = None
        st.session_state["is_streaming"] = False
        st.session_state["validation_errors"] = []
        st.session_state["api_error"] = None
    return None


# ── Iframe HTML assembly ──────────────────────────────────────

APP_JS_TEMPLATE = r"""
// Assets are passed in pre-encoded as data: URLs (see _asset_data_urls in
// app.py). They work in any iframe regardless of origin policy — important
// because we now live inside a srcdoc iframe whose effective origin is
// "null" and where /app/static/ URLs can't resolve.
const CHICKEN_IMGS = __CHICKEN_IMGS__;
const T_IMGS = __T_IMGS__;
const DRAWING_IMGS = __DRAWING_IMGS__;
const DESK_SRC = __DESK_SRC__;

// Fixed design-space stage. Everything is positioned in these 1440x900
// coordinates, then the stage is scaled to fit the viewport (letterbox).
const STAGE_W = 1440;
const STAGE_H = 900;

__SHARED__
__BACKGROUND__
__MASCOT__
__RAGE_METER__
__FORM__
__LETTER_PAPER__
__HISTORY__

function App() {
  const initial = __INITIAL_STATE__;

  const [rage, setRage] = useState(initial.rage_level);
  const [values, setValues] = useState(initial.form_data);
  const [letter, setLetter] = useState(initial.generated_letter || '');
  const [letterVersion, setLetterVersion] = useState(initial.letter_version || 0);
  const [busy, setBusy] = useState(!!initial.is_streaming);
  const [errors, setErrors] = useState(initial.validation_errors || []);
  // savedFlash is now triggered locally inside the iframe (no Python
  // round-trip on Save), so it always starts false on a fresh mount.
  const [savedFlash, setSavedFlash] = useState(false);
  const [apiError, setApiError] = useState(initial.api_error || null);
  const [view, setView] = useState(initial.view || 'landing');
  const [animateZoom, setAnimateZoom] = useState(false);
  // letters: stored in local state (not just initial.letters) so Save can
  // optimistically prepend a new entry without waiting for a Python rerun.
  // On any other action that re-srcdocs the iframe, this is re-seeded from
  // initial.letters which is the canonical DB state.
  const [letters, setLetters] = useState(initial.letters || []);
  // Age input (landing). Stored as a string while the user types; coerced
  // to int and passed to Python in the submit payload.
  const [userAge, setUserAge] = useState(
    initial.user_age != null ? String(initial.user_age) : ''
  );
  // Chicken-poke counter: each click pokes the mascot, bumping its
  // displayed rage state by 1 (capped at 4). Decays to 0 after 3s of
  // no clicks. Purely visual; does NOT change the rage the user picked.
  const [pokes, setPokes] = useState(0);
  // Age-input inline error (e.g. "please enter your age first"). Cleared
  // automatically on focus or any successful gate pass.
  const [ageError, setAgeError] = useState('');

  const stageRef = useRef(null);
  // Decay timer for the chicken-poke counter. Held in a ref so it
  // survives re-renders and we can clear it explicitly on each click.
  const pokeTimerRef = useRef(null);

  // Scale the fixed 1440x900 stage to fit the viewport (letterbox).
  // rescale() is cheap and safe to fire on every iframe resize; the height
  // report is intentionally NOT triggered from here — that path is owned
  // by setFrameHeight's own debounced/idempotent listener on window.top.
  // Calling setFrameHeight from rescale() created the resize feedback loop.
  useEffect(() => {
    const rescale = () => {
      const el = stageRef.current;
      if (!el) return;
      // Scale-to-FIT (Math.min) so the whole stage stays inside the
      // viewport in both dimensions — nothing is ever clipped at an
      // edge. The shorter axis may letterbox; the bars are filled by
      // the Streamlit page's cream (#efe4c6, desk-edge tone) showing
      // through the transparent iframe chain.
      const s = Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H);
      el.style.transform = `scale(${s})`;
    };
    rescale();
    setFrameHeight();  // one-shot on mount, dedup'd inside setFrameHeight
    window.addEventListener('resize', rescale);
    return () => window.removeEventListener('resize', rescale);
  }, []);

  // SAVED stamp animation is one-shot.
  useEffect(() => {
    if (!savedFlash) return;
    const t = setTimeout(() => setSavedFlash(false), 1300);
    return () => clearTimeout(t);
  }, [savedFlash]);

  // (Chicken-poke decay timer is now owned directly by pokeChicken below,
  // using a ref. The prior useEffect-based approach was fragile if the
  // iframe re-srcdoc'd mid-window — the new mount started fresh at
  // pokes=0 but the displayed-rage calculation in the previous mount
  // could leave the chicken visibly "stuck" for the user.)

  // One late re-measure after layout settles (fonts, async images). This
  // used to have no dep array — it fired on EVERY render and queued two
  // more setFrameHeights per render, which was the dominant resize-loop
  // amplifier. Now it runs exactly once on mount.
  useEffect(() => {
    const t = setTimeout(setFrameHeight, 400);
    return () => clearTimeout(t);
  }, []);

  const changeRage = (r) => {
    // Rage lives entirely in iframe state. Sending it back to Python
    // every click caused a full rerun → re-srcdoc → page flicker. The
    // current rage is included in submit/regenerate payloads when those
    // fire, so Python learns the rage at the moment it actually matters.
    setRage(r);
  };

  // Landing → app: validate age first, then play the zoom locally and
  // persist the view + age once the 700ms transform finishes. Empty or
  // invalid age blocks the transition and shows an inline crayon error.
  const enterApp = () => {
    if (view === 'app') return;
    const trimmed = (userAge || '').trim();
    const age = parseInt(trimmed, 10);
    if (!trimmed || isNaN(age) || age < 1 || age > 120) {
      setAgeError('please enter your age first');
      return;
    }
    setAgeError('');
    setAnimateZoom(true);
    setView('app');
  };

  const onCameraEnd = (e) => {
    if (e.propertyName === 'transform' && view === 'app') {
      // Persist both view AND the age the user typed — by the time we
      // dispatch set_view we've already validated, so user_age is non-
      // empty and Python's _coerce_age will accept it.
      sendToStreamlit({ action: 'set_view', view: 'app', user_age: userAge });
    }
  };

  const submitForm = () => {
    console.log('[pmb-inner] submitForm fired', { rage, valuesKeys: Object.keys(values), hasAge: !!userAge });
    const localErrors = quickValidate(values);
    if (localErrors.length) {
      console.log('[pmb-inner] submitForm: client-side validation failed', localErrors);
      setErrors(localErrors);
      return;
    }
    setErrors([]);
    setBusy(true);
    sendToStreamlit({ action: 'submit', form_data: values, rage, user_age: userAge });
    console.log('[pmb-inner] submitForm: postMessage to harness dispatched');
  };

  const regenerate = () => {
    setBusy(true);
    sendToStreamlit({ action: 'regenerate', rage, user_age: userAge });
  };

  // Save: optimistic local update + SAVED stamp, plus a fire-and-forget
  // dispatch to Python which writes to the DB but does NOT trigger a
  // rerun (see app.py:_handle_action). This keeps the letter from
  // re-streaming and the iframe from re-srcdoc'ing.
  const save = () => {
    if (!letter) return;
    setSavedFlash(true);
    const amt = parseFloat(String(values.amount || '').replace(/^\$/, ''));
    const local = {
      id: 'local-' + Date.now(),
      debtor_name: values.debtor_name || '',
      amount: isNaN(amt) ? 0 : amt,
      rage_level: rage,
      letter_text: letter,
      created_at: new Date().toISOString().replace('T', ' ').slice(0, 19),
    };
    setLetters(prev => [local, ...prev]);
    sendToStreamlit({ action: 'save', form_data: values, rage });
  };

  const startOver = () => {
    setValues(__DEFAULT_FORM__);
    setLetter('');
    setBusy(false);
    setErrors([]);
    setApiError(null);
    setPokes(0);
    sendToStreamlit({ action: 'start_over' });
  };

  // Chicken poke: bump local poke counter; reset decay timer to 3s.
  // Purely iframe-local — no Python round-trip — so the click is instant.
  // The timer is held in a ref so each click can explicitly clear the
  // previous one (debounced decay) — this is what was broken before.
  const pokeChicken = () => {
    setPokes(p => Math.min(p + 1, 4));
    if (pokeTimerRef.current) clearTimeout(pokeTimerRef.current);
    pokeTimerRef.current = setTimeout(() => {
      setPokes(0);
      pokeTimerRef.current = null;
    }, 3000);
  };
  const displayedChickenRage = Math.min(rage + pokes, 4);

  const copyLetter = async () => {
    try { await navigator.clipboard.writeText(letter); }
    catch (e) {
      const ta = document.createElement('textarea');
      ta.value = letter; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); ta.remove();
    }
  };

  const showLetter = letter || '';

  // Camera (desk) zoom + per-view fade helpers. Transitions are enabled only
  // after a real CTA click (animateZoom) so reruns/refresh render instantly.
  const camStyle = {
    position: 'absolute', inset: 0, zIndex: 0,
    transformOrigin: '680px 450px',
    transform: view === 'app' ? 'scale(2)' : 'scale(1)',
    transition: animateZoom ? 'transform 700ms cubic-bezier(.66,0,.34,1)' : 'none',
    willChange: 'transform',
  };
  const landing = (extra) => ({
    opacity: view === 'landing' ? 1 : 0,
    transition: animateZoom ? 'opacity 280ms ease' : 'none',
    pointerEvents: view === 'landing' ? 'auto' : 'none',
    ...extra,
  });
  const appUI = (extra) => ({
    opacity: view === 'app' ? 1 : 0,
    transition: animateZoom ? 'opacity 380ms ease 320ms' : 'none',
    pointerEvents: view === 'app' ? 'auto' : 'none',
    ...extra,
  });

  return React.createElement('div', {
    // Viewport: fills the iframe, centers + letterboxes the stage.
    style: {
      position: 'fixed', inset: 0, overflow: 'hidden',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'transparent',
    },
  },
   React.createElement('div', {
    // Stage: fixed 1440x900 design space, scaled to fit via stageRef effect.
    ref: stageRef,
    style: {
      position: 'relative',
      width: STAGE_W, height: STAGE_H,
      flex: '0 0 auto',
      overflow: 'hidden',
    },
  },
    // ── Camera / desk layer (the only thing that zooms) ──
    React.createElement('div', { style: camStyle, onTransitionEnd: onCameraEnd },
      React.createElement(Desk),

      // View 1: content sits DIRECTLY on the desk's painted paper — the
      // rendered KidPaper rectangle is gone. The chicken, copy, and age
      // input are layered onto the desk's existing sheet so we're not
      // stacking two pieces of paper on top of each other.
      React.createElement('div', {
        style: landing({
          position: 'absolute', left: 510, top: 180,
          width: 420, height: 520, zIndex: 1,
          transform: 'rotate(2deg)',
          padding: '32px 30px 28px',
          boxSizing: 'border-box',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', gap: 12,
        }),
      },
        // Angry chicken — visual centerpiece, sets the tone immediately.
        React.createElement('img', {
          src: CHICKEN_IMGS[3], alt: '', draggable: false,
          style: {
            width: 170, height: 'auto', display: 'block',
            filter: 'drop-shadow(0 6px 12px rgba(0,0,0,.18))',
            marginTop: -4,
          },
        }),
        // Body copy in crayon. Lines break manually so the rag stays tidy.
        React.createElement('div', {
          style: {
            fontFamily: '"Gochi Hand", cursive',
            fontSize: 19, lineHeight: 1.32,
            color: PENCIL_GRAY, textAlign: 'center',
            letterSpacing: '.2px',
          },
        },
          React.createElement('div', { style: { color: CRAYON_NAVY, marginBottom: 6 } },
            'a tone-controlled', React.createElement('br'),
            'debt-collection letter generator.'
          ),
          'someone owes you money.', React.createElement('br'),
          "you don't want to ask.", React.createElement('br'),
          React.createElement('span', { style: { display: 'inline-block', height: 6 } }),
          React.createElement('br'),
          'the chicken will ask.', React.createElement('br'),
          'you pick how nicely.'
        ),
        // Age input — empty by default, placeholder doubles as the
        // label so there's no confusion between placeholder text and a
        // pre-filled value. Required to proceed (enterApp validates).
        React.createElement('div', {
          style: { marginTop: 6, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 },
        },
          React.createElement('div', { style: { position: 'relative', width: 150 } },
            React.createElement('input', {
              type: 'text',
              inputMode: 'numeric',
              value: userAge,
              onChange: (e) => {
                const cleaned = (e.target.value || '').replace(/[^0-9]/g, '').slice(0, 3);
                setUserAge(cleaned);
                if (cleaned) setAgeError('');
              },
              onFocus: () => setAgeError(''),
              placeholder: 'your age',
              'data-no-drag': true,
              autoComplete: 'off',
              autoCorrect: 'off',
              spellCheck: false,
              maxLength: 3,
              style: {
                width: '100%', textAlign: 'center',
                background: 'transparent', border: 'none', outline: 'none',
                fontFamily: '"Gochi Hand", cursive',
                fontSize: 22, color: PENCIL_GRAY, letterSpacing: '.5px',
                padding: '2px 0',
                cursor: 'text',
              },
            }),
            React.createElement(PencilUnderline, { seed: 23 })
          ),
          ageError && React.createElement('div', {
            style: {
              marginTop: 2,
              fontFamily: '"Gochi Hand", cursive',
              fontSize: 15, color: '#b51212',
              textAlign: 'center', lineHeight: 1.1,
            },
          }, ageError)
        )
      ),

      // View 1: kid's drawing prop resting on the desk. Nudged left a touch
      // so it doesn't crowd the (now wider) worksheet.
      React.createElement('div', {
        style: landing({ position: 'absolute', left: 240, top: 580, zIndex: 1, transform: 'rotate(-6deg)' }),
      },
        React.createElement(Drawing, { rage, width: 240 })
      )
    ),

    // ── UI layer (fixed; does not zoom) ──

    // Landing: brand title.
    React.createElement('div', {
      style: landing({ position: 'absolute', top: 70, left: 0, right: 0, padding: '0 40px', zIndex: 5 }),
    },
      React.createElement(BrandHeader),
      React.createElement('div', {
        style: {
          marginTop: 10, height: 1,
          width: 'min(700px, 60%)', margin: '12px auto 0',
          background: 'linear-gradient(to right, transparent, rgba(20,12,4,.45), transparent)',
        },
      })
    ),

    // Landing: call-to-action → zoom into the app. (Standalone descriptive
    // copy that used to sit here has been moved onto the worksheet itself.)
    React.createElement('div', {
      style: landing({ position: 'absolute', left: 0, right: 0, top: 740, zIndex: 6, display: 'flex', justifyContent: 'center' }),
    },
      React.createElement(LandingCTA, { onClick: enterApp })
    ),

    // App: API error banner.
    apiError && React.createElement('div', {
      style: appUI({
        position: 'absolute', top: 10, left: '50%', transform: 'translateX(-50%)',
        background: '#fff3cd', color: '#664d03', border: '1px solid #ffe69c',
        borderRadius: 6, padding: '6px 14px', fontFamily: '"Gochi Hand", cursive',
        fontSize: 16, zIndex: 100,
      }),
    }, apiError),

    // App: rage meter left rail. Card grew to 256×760; nudged to left:18
    // to keep a small gap before the worksheet (its right edge sits at 274).
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 18, top: 90, zIndex: 4 }),
    },
      React.createElement(RageMeter, { rage, setRage: changeRage })
    ),

    // App: worksheet center (form + streamed letter on one paper).
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 288, top: 60, zIndex: 5 }),
    },
      React.createElement(Worksheet, {
        rage, values, onChange: setValues,
        onSubmit: submitForm, errors, busy,
        letter: showLetter, version: letterVersion,
        onCopy: copyLetter, onRegenerate: regenerate,
        onSave: save, onStartOver: startOver,
        savedFlash,
      })
    ),

    // App: chicken on the right, reacting to the rage. Clickable — each
    // click pokes the chicken to the next angrier image, decaying back
    // after 3s. displayedChickenRage = min(rage + pokes, 4).
    React.createElement('div', {
      style: appUI({
        position: 'absolute', left: 1060, top: 100,
        width: 360, height: 460, zIndex: 3,
        cursor: 'pointer',
      }),
      onClick: pokeChicken,
      title: 'poke me',
    },
      React.createElement(Chicken, {
        rage: displayedChickenRage, width: 360,
        style: { position: 'absolute', left: 0, top: 0, width: 360 },
      })
    ),

    // App: kid's drawing prop, bottom-right. Larger so it doesn't read
    // as a footnote next to the bigger chicken above it.
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 1080, top: 555, width: 330, zIndex: 3, transform: 'rotate(4deg)' }),
    },
      React.createElement(Drawing, { rage, width: 330 })
    ),

    // App: hall of grudges drawer (bottom-left, self-positioned).
    React.createElement(HallDrawer, {
      currentRage: rage, letters,
      onDelete: (id) => sendToStreamlit({ action: 'delete', id }),
      active: view === 'app', animate: animateZoom,
    })
   )
  );
}

function quickValidate(v) {
  const errs = [];
  if (!String(v.debtor_name || '').trim()) errs.push('debtor name is required');
  const amt = String(v.amount || '').trim().replace(/^\$/, '');
  if (!amt) errs.push('amount is required');
  else if (isNaN(parseFloat(amt)) || parseFloat(amt) <= 0) errs.push('amount must be a positive number');
  const t = String(v.time_owed || '').trim();
  if (!t) errs.push('time owed is required');
  else if (isNaN(parseFloat(t)) || parseFloat(t) <= 0) errs.push('time owed must be a positive number');
  if (!String(v.relationship || '').trim()) errs.push('relationship is required');
  return errs;
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
"""


def _build_iframe_html(state: dict, assets: dict) -> str:
    initial_state = {
        "view":               state["view"],
        "rage_level":         state["rage_level"],
        "form_data":          state["form_data"],
        "generated_letter":   state["generated_letter"],
        "is_streaming":       state["is_streaming"],
        "letters":            state["letters"],
        "validation_errors":  state["validation_errors"],
        "api_error":          state["api_error"],
        "letter_version":     state["letter_version"],
        "user_age":           state.get("user_age"),
    }
    default_form = {
        "debtor_name": "",
        "amount": "",
        "time_owed": "",
        "time_unit": "weeks",
        "relationship": "friend",
        "context": "",
        "payment_handle": "",
    }

    app_js = (
        APP_JS_TEMPLATE
        .replace("__CHICKEN_IMGS__", json.dumps(assets["chicken"]))
        .replace("__T_IMGS__", json.dumps(assets["therm"]))
        .replace("__DRAWING_IMGS__", json.dumps(assets["drawing"]))
        .replace("__DESK_SRC__", json.dumps(assets["desk"]))
        .replace("__SHARED__", shared_js())
        .replace("__BACKGROUND__", background_js())
        .replace("__MASCOT__", mascot_js())
        .replace("__RAGE_METER__", rage_meter_js())
        .replace("__FORM__", form_js())
        .replace("__LETTER_PAPER__", letter_paper_js())
        .replace("__HISTORY__", history_js())
        .replace("__INITIAL_STATE__", json.dumps(initial_state))
        .replace("__DEFAULT_FORM__", json.dumps(default_form))
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Gochi+Hand&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    html, body {{ margin: 0; padding: 0; min-height: 100%; background: transparent; overflow: hidden; }}
    body {{ font-family: Inter, system-ui, sans-serif; color: #1a1410; }}
    @keyframes crayon-blink {{ 0%,49%{{opacity:1}} 50%,100%{{opacity:0}} }}
    @keyframes saved-stamp {{
      0%   {{ transform: translate(-50%, -50%) rotate(-12deg) scale(2.4); opacity: 0; }}
      35%  {{ transform: translate(-50%, -50%) rotate(-12deg) scale(0.92); opacity: 1; }}
      55%  {{ transform: translate(-50%, -50%) rotate(-12deg) scale(1.05); opacity: 1; }}
      80%  {{ transform: translate(-50%, -50%) rotate(-12deg) scale(1.0);  opacity: 1; }}
      100% {{ transform: translate(-50%, -50%) rotate(-12deg) scale(1.0);  opacity: 0; }}
    }}
    .grudge-scroll::-webkit-scrollbar {{ height: 10px; }}
    .grudge-scroll::-webkit-scrollbar-thumb {{ background: rgba(26,20,16,.25); border-radius: 999px; }}
    /* Letter-area scrollbar: muted so it blends with the cream paper
       instead of reading as a default-gray browser bar. */
    .pmb-letter-scroll {{ scrollbar-width: thin; scrollbar-color: rgba(60,40,10,0.28) transparent; }}
    .pmb-letter-scroll::-webkit-scrollbar {{ width: 10px; }}
    .pmb-letter-scroll::-webkit-scrollbar-track {{ background: transparent; }}
    .pmb-letter-scroll::-webkit-scrollbar-thumb {{
      background: rgba(60, 40, 10, 0.28); border-radius: 5px;
      border: 2px solid transparent; background-clip: padding-box;
    }}
    .pmb-letter-scroll::-webkit-scrollbar-thumb:hover {{
      background: rgba(60, 40, 10, 0.45); background-clip: padding-box;
    }}
    input::placeholder, textarea::placeholder {{ color: rgba(58,53,48,.42); }}
    select {{ -webkit-appearance: none; appearance: none; }}
  </style>
  <script src="https://unpkg.com/react@18.3.1/umd/react.production.min.js" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js" crossorigin="anonymous"></script>
</head>
<body>
  <div id="root"></div>
  <script>
{app_js}
  </script>
</body>
</html>"""


# ── Streamlit page ────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="Pay Me Back. Or Else.",
        page_icon="🐔",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    _init_state()
    ss = st.session_state

    # Always pull a fresh letters list from the DB at the top of each
    # script run. This keeps the hall in sync with `save` writes done
    # in previous non-rerunning script runs (see _handle_action save
    # branch) without forcing those writes to trigger a rerun + iframe
    # re-srcdoc (which would re-stream the displayed letter).
    ss["letters"] = db_service.get_all_letters()

    assets = _asset_data_urls()
    # Page-chrome reset + neutral fill behind the letterboxed stage. The desk
    # itself now lives inside the iframe (it's the zoomable camera layer).
    st.markdown(f"<style>{_styles_css()}</style>", unsafe_allow_html=True)

    # data-rage attribute on the page body for any external CSS hooks.
    st.markdown(
        f'<script>document.body.setAttribute("data-rage", "{ss["rage_level"]}");</script>',
        unsafe_allow_html=True,
    )

    # Letter version bumps on each new letter so the iframe knows to re-stream.
    ss.setdefault("letter_version", 0)
    if ss["generated_letter"] and ss.get("_last_letter") != ss["generated_letter"]:
        ss["letter_version"] += 1
        ss["_last_letter"] = ss["generated_letter"]

    html = _build_iframe_html(
        state={
            "view":              ss["view"],
            "rage_level":        ss["rage_level"],
            "form_data":         ss["form_data"],
            "generated_letter":  ss["generated_letter"],
            "is_streaming":      ss["is_streaming"],
            "letters":           ss["letters"],
            "validation_errors": ss["validation_errors"],
            "api_error":         ss["api_error"],
            "letter_version":    ss["letter_version"],
            "user_age":          ss.get("user_age"),
        },
        assets=assets,
    )

    # Use the registered custom component (pmb_component) instead of
    # streamlit.components.v1.html — the latter is render-only and silently
    # drops the inner iframe's setComponentValue messages, which is why
    # form submit appeared to hang forever on the deployed app.
    component_value = pmb_render(payload_html=html, key="pmb_chicken")

    if isinstance(component_value, dict) and component_value.get("action"):
        nonce = component_value.get("_nonce")
        last_nonce = ss.get("last_action_nonce")
        # Streamlit caches the component's last setComponentValue and returns
        # it on every subsequent rerun — we must only dispatch + rerun when
        # the nonce actually changes, otherwise the same action loops forever.
        if nonce is None or nonce != last_nonce:
            print(
                f"[app] iframe → python: action={component_value.get('action')!r} "
                f"nonce={nonce!r}",
                file=sys.stderr, flush=True,
            )
            result = _handle_action(component_value)
            # `save` deliberately suppresses the rerun so the iframe's
            # already-displayed letter doesn't re-srcdoc and re-stream.
            if result != "no_rerun":
                st.rerun()


main()
