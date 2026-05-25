# Pay Me Back — V2 Layout: Landing + Zoom + App (Layout A)

**Status:** approved, in progress (uncommitted reference doc).
**Date:** 2026-05-25.
**Source spec:** `design/Pay Me Back Wireframes _standalone_.html` (embedded grayscale wireframe, 1440×900 design space). Wireframe is **layout & asset sizing only — no styling decisions**; existing crayon-paper styling, fonts, and rage-based copy are retained.

## Locked decisions
1. **Worksheet:** merge form + generated-letter onto ONE centered worksheet.
2. **Hall of Grudges:** bottom-left collapsible drawer (not the old top-right draggable sticky).
3. **Assets:** adapt to the committed flat PNGs (`chicken1-4`, `T1-4`, `drawing1-4`, `main_table.png`). No layered chicken (body/eyes/fire), no worksheet/CTA/sprite-sheet PNGs from the spec's asset table.
4. **Zoom depth:** tuned ~2× (not the spec's 3.4×).

## Views
- **View 1 — Landing / Desk (zoomed out):** whole desk fills the viewport; small worksheet paper prop (center) + kid's-drawing prop sit on it; "✎ write a letter" CTA overlaid. Clicking the CTA zooms in.
- **View 2 — App / Layout A (zoomed in):** desk zoomed ~2× (photoreal edges still visible); single worksheet center (form + streamed letter), thermometer left rail (rage selector), chicken right, drawing bottom-right, grudges drawer bottom-left.

## Coordinate model (1440×900 stage)
A fixed `1440×900` `#stage` is scaled-to-fit the viewport (letterbox) inside the iframe, so wireframe pixel coords are used directly.

| Element | View | Stage coords (x,y,w,h) | Notes |
|---|---|---|---|
| Desk image | both | fills stage (camera layer) | `main_table.png`, object-fit cover |
| Worksheet prop | V1 | 560,250, 320×400, rot 2° | center (720,450) = stage center; zoom target |
| Drawing prop | V1 | 280,540, 280×240, rot −6° | rides camera |
| CTA "✎ write a letter" | V1 | 600,680, 240×64 | fixed UI layer; fades out on click |
| Thermometer / rage selector | V2 | 80,180, 130×540 | left rail |
| Worksheet (form + letter) | V2 | 260,60, 760×780 | center; fields top, streamed letter + actions below |
| Chicken | V2 | 1060,140, 300×380 | right |
| Kid's drawing | V2 | 1060,540, 300×220, rot 4° | bottom-right |
| Hall of Grudges | V2 | 80,740, 130×120 (closed) | bottom-left collapsible drawer |

## Zoom mechanism (real transform, not crossfade)
- **Camera/desk layer** (recreated `components/background.py`): holds the desk `<img>` + the V1 paper props. One animated `transform`:
  - Landing: `scale(1)`.
  - App: `scale(2)`, `transform-origin: 680px 450px` (≈ worksheet center).
  - `transition: transform 700ms` — **only when `animateZoom` is true**.
- **UI layer** (fixed in stage coords, above camera): CTA in landing; Layout A components in app. Contents crossfade, timed to the zoom (CTA out ~0–250ms; V1 props zoom+fade ~300–600ms; Layout A in ~400–700ms).
- **Sharpness:** at `scale(2)` the visible region is the central ~1456 source px of the 2912px desk → native on a 1440 standard-DPI display, but upscaled/soft on retina/>1440. **Action item:** regenerate `main_table.png` ≥ ~5800px wide (ideally ~7680) for crisp 2× on retina. Code is resolution-agnostic; same filename hot-swaps.

## View state + persistence
- `view ∈ {landing, app}` lives in React **and** persists via **`st.query_params`** (URL), seeded into `st.session_state` on init.
- New `set_view` action: writes `session_state["view"]` + `st.query_params["view"]`, then reruns.
- CTA click: locally `animateZoom=true` → `view=app` (plays 700ms zoom) → on `transitionend`, notify Streamlit (`set_view`). The rerun rebuilds the iframe with `initial.view=app`, rendered **pre-zoomed, transition disabled** (no replay on reruns/keystrokes).
- **Hard refresh in app** → URL `?view=app` → restores app pre-zoomed. **First load** → no param → landing.

## File changes (frontend only; backend untouched)
| File | Change |
|---|---|
| `components/background.py` | **Recreate** = Desk/Stage + camera-zoom component (carries V1 props). |
| `app.py` | Stage/letterbox scaffold; `view`/`set_view` + `query_params`; move desk into iframe; remove Streamlit `.pmb-desk`; Layout A wiring. |
| `components/form.py` + `letter_paper.py` | **Combine** into one centered worksheet (fields → streamed letter + Copy/Regen/Save/Email/StartOver), validation/streaming preserved. |
| `components/rage_meter.py` | Reposition to left rail (130×540). |
| `components/mascot.py` | No logic change; repositioned/resized via props. |
| `components/history.py` | Bottom-left collapsible drawer; save/delete preserved. |
| `assets/styles.css` | Stage/letterbox + neutral page fill; drop desk-bg rule. |
| Backend (`claude_service`, `db_service`, `validators`) | **Untouched.** Form fields map 1:1. |

## Build sequence (pause + report after each)
1. Stage + letterbox scaffold (coordinate system, scale-to-fit). App stays runnable (current layout, letterboxed).
2. Desk camera + landing view + CTA. *(user eyeballs)*
3. Zoom state machine + `query_params` persistence. *(user eyeballs)*
4. Layout A repositioning.
5. Merge worksheet (form + letter).
6. Grudges drawer.

## Verification
After each step: `py_compile` + `AppTest` (runs clean across view×rage, asset URIs present) + headless `streamlit run` (HTTP 200, no traceback). Visual confirmation (zoom feel, no 404s) is the user's to eyeball.
