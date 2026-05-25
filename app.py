"""Pay Me Back. Or Else. — single-page Streamlit entry point.

The entire interactive UI is rendered inside one streamlit.components.v1.html
iframe (a faithful port of the Claude Design React mock). Streamlit owns the
session state and the Claude API call; the iframe owns the visual scene and
talks back via the standard component setComponentValue protocol.
"""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from components.background import background_js
from components.form import form_js
from components.history import history_js
from components.letter_paper import letter_paper_js
from components.mascot import mascot_js
from components.rage_meter import rage_meter_js
from components.shared import shared_js
from services import claude_service, db_service
from utils.validators import validate_form


REPO_ROOT = Path(__file__).resolve().parent
DESIGN_DIR = REPO_ROOT / "design"
ASSETS_DIR = REPO_ROOT / "assets"


# ── Asset loading ─────────────────────────────────────────────
#
# Assets are served via Streamlit static file serving (./static, exposed at
# <app>/app/static/<file>) rather than base64-embedded into the iframe. This
# keeps the component HTML tiny — a large base64 srcdoc fails to render on
# Streamlit Community Cloud (blank page), while rendering fine locally.


def _asset_files() -> dict:
    return {
        "desk":     "main_table.png",
        "chicken":  [f"chicken{i}-removebg-preview.png" for i in (1, 2, 3, 4)],
        "therm":    [f"T{i}-removebg-preview.png" for i in (1, 2, 3, 4)],
        "drawing":  [f"drawing{i}-removebg-preview.png" for i in (1, 2, 3, 4)],
    }


@st.cache_resource(show_spinner=False)
def _styles_css() -> str:
    return (ASSETS_DIR / "styles.css").read_text()


# ── Session state ─────────────────────────────────────────────

def _init_state() -> None:
    ss = st.session_state
    # View persists in the URL so a hard refresh restores the same view.
    qp_view = st.query_params.get("view")
    ss.setdefault("view", qp_view if qp_view in ("landing", "app") else "landing")
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
    ss.setdefault("flash_saved", False)
    ss.setdefault("flash_plane", False)
    ss.setdefault("api_error", None)


# ── Action dispatch ───────────────────────────────────────────

def _generate_letter(form_data: dict, rage: int) -> None:
    """Call Claude (streaming) and accumulate into session state."""
    merged = {**form_data, "rage_level": rage}
    errors = validate_form(merged)
    if errors:
        st.session_state["validation_errors"] = errors
        st.session_state["is_streaming"] = False
        return

    st.session_state["validation_errors"] = []
    st.session_state["is_streaming"] = True
    st.session_state["generated_letter"] = None
    st.session_state["api_error"] = None

    chunks: list[str] = []
    try:
        for chunk in claude_service.stream_letter(merged):
            chunks.append(chunk)
        full = "".join(chunks).strip()
        st.session_state["generated_letter"] = full or "(the chicken is speechless.)"
    except claude_service.MissingAPIKeyError as exc:
        st.session_state["api_error"] = str(exc)
    except Exception as exc:  # noqa: BLE001 — user-facing error display
        st.session_state["api_error"] = f"the chicken couldn't reach claude: {exc}"
    finally:
        st.session_state["is_streaming"] = False


def _handle_action(payload: dict) -> None:
    nonce = payload.get("_nonce")
    if nonce is not None and nonce == st.session_state.get("last_action_nonce"):
        return
    st.session_state["last_action_nonce"] = nonce

    action = payload.get("action")
    if action == "set_view":
        view = payload.get("view")
        if view in ("landing", "app"):
            st.session_state["view"] = view
            st.query_params["view"] = view

    elif action == "set_rage":
        st.session_state["rage_level"] = int(payload.get("rage", 1))
        st.session_state["form_data"]["rage_level"] = st.session_state["rage_level"]

    elif action == "update_form":
        st.session_state["form_data"].update(payload.get("form_data") or {})

    elif action == "submit":
        form = {**st.session_state["form_data"], **(payload.get("form_data") or {})}
        st.session_state["form_data"] = form
        rage = int(payload.get("rage", st.session_state["rage_level"]))
        st.session_state["rage_level"] = rage
        _generate_letter(form, rage)

    elif action == "regenerate":
        rage = int(payload.get("rage", st.session_state["rage_level"]))
        _generate_letter(st.session_state["form_data"], rage)

    elif action == "save":
        letter = st.session_state.get("generated_letter")
        if letter:
            db_service.save_letter(
                {**st.session_state["form_data"], "rage_level": st.session_state["rage_level"]},
                letter,
            )
            st.session_state["letters"] = db_service.get_all_letters()
            st.session_state["flash_saved"] = True

    elif action == "delete":
        letter_id = int(payload.get("id"))
        db_service.delete_letter(letter_id)
        st.session_state["letters"] = db_service.get_all_letters()

    elif action == "email":
        st.session_state["flash_plane"] = True

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


# ── Iframe HTML assembly ──────────────────────────────────────

APP_JS_TEMPLATE = r"""
window.CHICKEN_FILES = __CHICKEN_IMGS__;
window.T_FILES = __T_IMGS__;
window.DRAWING_FILES = __DRAWING_IMGS__;
window.DESK_FILE = __DESK_SRC__;

// Assets are fetched from Streamlit static serving, not base64-embedded.
// Files live in ./static and are served at <app>/app/static/<file>. The
// srcdoc iframe is same-origin, so build absolute URLs from the parent
// location (with a relative fallback if that read is ever blocked).
let STATIC_BASE;
try {
  const L = window.parent.location;
  STATIC_BASE = L.origin + L.pathname.replace(/\/+$/, '') + '/app/static/';
} catch (e) {
  STATIC_BASE = 'app/static/';
}
const CHICKEN_IMGS = window.CHICKEN_FILES.map(function (f) { return STATIC_BASE + f; });
const T_IMGS = window.T_FILES.map(function (f) { return STATIC_BASE + f; });
const DRAWING_IMGS = window.DRAWING_FILES.map(function (f) { return STATIC_BASE + f; });
const DESK_SRC = STATIC_BASE + window.DESK_FILE;

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
  const [savedFlash, setSavedFlash] = useState(!!initial.flash_saved);
  const [planeFlash, setPlaneFlash] = useState(!!initial.flash_plane);
  const [apiError, setApiError] = useState(initial.api_error || null);
  const [view, setView] = useState(initial.view || 'landing');
  const [animateZoom, setAnimateZoom] = useState(false);

  const stageRef = useRef(null);

  // Scale the fixed 1440x900 stage to fit the viewport (letterbox).
  useEffect(() => {
    const fit = () => {
      const el = stageRef.current;
      if (!el) return;
      const s = Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H);
      el.style.transform = `scale(${s})`;
      setFrameHeight();
    };
    fit();
    window.addEventListener('resize', fit);
    return () => window.removeEventListener('resize', fit);
  }, []);

  // Saved/plane animations are one-shot.
  useEffect(() => {
    if (!savedFlash) return;
    const t = setTimeout(() => setSavedFlash(false), 1300);
    return () => clearTimeout(t);
  }, [savedFlash]);

  useEffect(() => {
    if (!planeFlash) return;
    const t = setTimeout(() => setPlaneFlash(false), 1500);
    return () => clearTimeout(t);
  }, [planeFlash]);

  // Re-tell Streamlit about our height after layout settles.
  useEffect(() => {
    const t = setTimeout(setFrameHeight, 60);
    const t2 = setTimeout(setFrameHeight, 400);
    return () => { clearTimeout(t); clearTimeout(t2); };
  });

  const changeRage = (r) => {
    setRage(r);
    sendToStreamlit({ action: 'set_rage', rage: r });
  };

  // Landing → app: play the zoom locally, then persist the view once the
  // 700ms transform finishes (so a refresh restores 'app' pre-zoomed).
  const enterApp = () => {
    if (view === 'app') return;
    setAnimateZoom(true);
    setView('app');
  };

  const onCameraEnd = (e) => {
    if (e.propertyName === 'transform' && view === 'app') {
      sendToStreamlit({ action: 'set_view', view: 'app' });
    }
  };

  const submitForm = () => {
    const localErrors = quickValidate(values);
    if (localErrors.length) { setErrors(localErrors); return; }
    setErrors([]);
    setBusy(true);
    sendToStreamlit({ action: 'submit', form_data: values, rage });
  };

  const regenerate = () => {
    setBusy(true);
    sendToStreamlit({ action: 'regenerate', rage });
  };

  const save = () => {
    setSavedFlash(true);
    sendToStreamlit({ action: 'save' });
  };

  const sendEmail = () => {
    const subject = encodeURIComponent('A letter from the chicken');
    const body = encodeURIComponent(letter);
    setPlaneFlash(true);
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
    sendToStreamlit({ action: 'email' });
  };

  const startOver = () => {
    setValues(__DEFAULT_FORM__);
    setLetter('');
    setBusy(false);
    setErrors([]);
    setApiError(null);
    sendToStreamlit({ action: 'start_over' });
  };

  const copyLetter = async () => {
    try { await navigator.clipboard.writeText(letter); }
    catch (e) {
      const ta = document.createElement('textarea');
      ta.value = letter; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); ta.remove();
    }
  };

  const showLetter = letter || '';
  const letters = initial.letters || [];

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

      // View 1: worksheet prop — the zoom target, centered on the stage.
      React.createElement('div', {
        style: landing({ position: 'absolute', left: 560, top: 250, width: 320, height: 400, zIndex: 1, transform: 'rotate(2deg)' }),
      },
        React.createElement(KidPaper, { width: 320, height: 400, seed: 11, tone: PAPER_BG_ALT, rotation: 0 },
          React.createElement('div', {
            style: { position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 },
          },
            React.createElement('div', { style: { fontFamily: '"Gochi Hand", cursive', fontSize: 32, color: CRAYON_NAVY } }, 'the demand'),
            React.createElement('div', { style: { fontFamily: '"Gochi Hand", cursive', fontSize: 17, color: PENCIL_GRAY, opacity: .7 } }, '(blank worksheet)')
          )
        )
      ),

      // View 1: kid's drawing prop resting on the desk.
      React.createElement('div', {
        style: landing({ position: 'absolute', left: 300, top: 560, zIndex: 1, transform: 'rotate(-6deg)' }),
      },
        React.createElement(Drawing, { rage, width: 220 })
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

    // Landing: call-to-action → zoom into the app.
    React.createElement('div', {
      style: landing({ position: 'absolute', left: 600, top: 690, width: 240, zIndex: 6, display: 'flex', justifyContent: 'center' }),
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

    // App: rage meter left rail.
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 78, top: 175, zIndex: 4 }),
    },
      React.createElement(RageMeter, { rage, setRage: changeRage })
    ),

    // App: worksheet center (form + streamed letter on one paper).
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 262, top: 60, zIndex: 5 }),
    },
      React.createElement(Worksheet, {
        rage, values, onChange: setValues,
        onSubmit: submitForm, errors, busy,
        letter: showLetter, version: letterVersion,
        onCopy: copyLetter, onRegenerate: regenerate,
        onSave: save, onEmail: sendEmail, onStartOver: startOver,
        savedFlash, planeFlash,
      })
    ),

    // App: chicken on the right, reacting to the rage.
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 1060, top: 150, width: 300, height: 380, zIndex: 3 }),
    },
      React.createElement(Chicken, {
        rage, width: 300,
        style: { position: 'absolute', left: 0, top: 0, width: 300 },
      })
    ),

    // App: kid's drawing prop, bottom-right.
    React.createElement('div', {
      style: appUI({ position: 'absolute', left: 1085, top: 545, width: 260, zIndex: 3, transform: 'rotate(4deg)' }),
    },
      React.createElement(Drawing, { rage, width: 260 })
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
        "flash_saved":        state["flash_saved"],
        "flash_plane":        state["flash_plane"],
        "api_error":          state["api_error"],
        "letter_version":     state["letter_version"],
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
    @keyframes paper-plane {{
      0%   {{ transform: translateX(0) translateY(0) rotate(-12deg); opacity: 1; }}
      100% {{ transform: translateX(120vw) translateY(-22vh) rotate(-18deg); opacity: 0; }}
    }}
    .grudge-scroll::-webkit-scrollbar {{ height: 10px; }}
    .grudge-scroll::-webkit-scrollbar-thumb {{ background: rgba(26,20,16,.25); border-radius: 999px; }}
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

    assets = _asset_files()
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
            "flash_saved":       ss["flash_saved"],
            "flash_plane":       ss["flash_plane"],
            "api_error":         ss["api_error"],
            "letter_version":    ss["letter_version"],
        },
        assets=assets,
    )

    # Clear one-shot flashes so they don't re-fire on next rerun.
    if ss["flash_saved"]:
        ss["flash_saved"] = False
    if ss["flash_plane"]:
        ss["flash_plane"] = False

    component_value = components.html(html, height=1000, scrolling=False)

    if isinstance(component_value, dict) and component_value.get("action"):
        _handle_action(component_value)
        st.rerun()


main()
