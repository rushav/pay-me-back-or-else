"""Pay Me Back. Or Else. — single-page Streamlit entry point.

The entire interactive UI is rendered inside one streamlit.components.v1.html
iframe (a faithful port of the Claude Design React mock). Streamlit owns the
session state and the Claude API call; the iframe owns the visual scene and
talks back via the standard component setComponentValue protocol.
"""

import base64
import json
import time
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

@st.cache_resource(show_spinner=False)
def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


@st.cache_resource(show_spinner=False)
def _asset_uris() -> dict:
    return {
        "chicken":  f"data:video/mp4;base64,{_b64(DESIGN_DIR / 'chicken.mp4')}",
        "sky":      [f"data:image/png;base64,{_b64(DESIGN_DIR / f'sky_rage_{i}.png')}" for i in (1, 2, 3, 4)],
        "therm":    [f"data:image/png;base64,{_b64(DESIGN_DIR / f'T{i}.png')}" for i in (1, 2, 3, 4)],
    }


@st.cache_resource(show_spinner=False)
def _styles_css() -> str:
    return (ASSETS_DIR / "styles.css").read_text()


# ── Session state ─────────────────────────────────────────────

def _init_state() -> None:
    ss = st.session_state
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
    if action == "set_rage":
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


# ── Sky background (rendered outside the iframe) ──────────────

def _render_sky(rage: int, sky_uris: list[str]) -> None:
    layers = "".join(
        f'<div class="pmb-sky-layer{" active" if i + 1 == rage else ""}" '
        f'style="background-image:url({uri});"></div>'
        for i, uri in enumerate(sky_uris)
    )
    st.markdown(
        f'<style>{_styles_css()}</style>'
        f'<div class="pmb-sky">{layers}</div>',
        unsafe_allow_html=True,
    )


# ── Iframe HTML assembly ──────────────────────────────────────

APP_JS_TEMPLATE = r"""
window.SKY_IMGS = __SKY_IMGS__;
window.T_IMGS = __T_IMGS__;
window.CHICKEN_SRC = __CHICKEN_SRC__;

// Use shared list names used by components.
const SKY_IMGS = window.SKY_IMGS;
const T_IMGS = window.T_IMGS;

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
  const showBusy = busy && !showLetter;
  const letters = initial.letters || [];

  return React.createElement('div', {
    style: {
      position: 'relative',
      width: '100vw', minHeight: '100vh',
      overflow: 'hidden',
    },
  },
    // Header
    React.createElement('div', {
      style: {
        position: 'absolute', top: 18, left: 0, right: 0,
        padding: '0 40px', zIndex: 2, pointerEvents: 'none',
      },
    },
      React.createElement(BrandHeader),
      React.createElement('div', {
        style: {
          marginTop: 10, height: 1,
          width: 'min(700px, 60%)', margin: '12px auto 0',
          background: 'linear-gradient(to right, transparent, rgba(20,12,4,.35), transparent)',
        },
      })
    ),

    apiError && React.createElement('div', {
      style: {
        position: 'absolute', top: 8, left: '50%',
        transform: 'translateX(-50%)',
        background: '#fff3cd', color: '#664d03',
        border: '1px solid #ffe69c', borderRadius: 6,
        padding: '6px 14px', fontFamily: '"Gochi Hand", cursive',
        fontSize: 16, zIndex: 100,
      },
    }, apiError),

    // Top-left: rage meter sticky note
    React.createElement('div', {
      style: { position: 'absolute', left: 24, top: 130, zIndex: 3 },
    },
      React.createElement(RageMeter, { rage, setRage: changeRage })
    ),

    // Bottom-left: chicken peeking up. z-index above letter so chicken overlaps.
    React.createElement('div', {
      style: {
        position: 'absolute',
        left: -140, bottom: 0,
        width: 1120, height: 580,
        overflow: 'hidden', pointerEvents: 'none',
        zIndex: 10,
      },
    },
      React.createElement(ChickenVideo, {
        rage, width: 1120,
        style: {
          position: 'absolute', left: 0, top: 0, width: 1120,
          transform: 'scaleX(1.3) translateY(10%)',
          transformOrigin: 'center top',
        },
      })
    ),

    // Center: letter paper
    React.createElement('div', {
      style: {
        position: 'absolute',
        left: '50%', top: 152,
        transform: 'translateX(-50%)', zIndex: 4,
      },
    },
      React.createElement(LetterPaper, {
        rage, letter: showLetter, version: letterVersion,
        busy: showBusy,
        onCopy: copyLetter, onRegenerate: regenerate,
        onSave: save, onEmail: sendEmail, onStartOver: startOver,
        savedFlash, planeFlash,
      })
    ),

    // Right rail: worksheet form
    React.createElement('div', {
      style: {
        position: 'absolute', right: 32, top: 130, zIndex: 4,
      },
    },
      React.createElement(WorksheetForm, {
        rage, values, onChange: setValues,
        onSubmit: submitForm, errors, busy,
      })
    ),

    // Top-right: hall of grudges (draggable)
    React.createElement(HallStickyNote, {
      currentRage: rage, letters,
      onDelete: (id) => sendToStreamlit({ action: 'delete', id }),
    })
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
        .replace("__SKY_IMGS__", json.dumps(assets["sky"]))
        .replace("__T_IMGS__", json.dumps(assets["therm"]))
        .replace("__CHICKEN_SRC__", json.dumps(assets["chicken"]))
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
  <svg width="0" height="0" style="position:absolute; pointer-events:none;" aria-hidden="true">
    <defs>
      <filter id="knockout-white" x="0" y="0" width="100%" height="100%">
        <feColorMatrix type="matrix" values="
          1 0 0 0 0
          0 1 0 0 0
          0 0 1 0 0
          -3 -3 -3 1 7
        "/>
      </filter>
    </defs>
  </svg>
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

    # Sky background (outside the iframe).
    assets = _asset_uris()
    _render_sky(ss["rage_level"], assets["sky"])

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
