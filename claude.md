# CLAUDE.md — Pay Me Back or Else

## Project Overview
A Streamlit app that generates AI-powered, humorous debt collection letters. Users
fill out a form about who owes them money, pick a rage level (1–4, "Heaven to Hell"),
and get a copy-paste-ready letter generated via the Claude API. The tone escalates
from angelic kindness to full demonic fury. A big cartoon chicken mascot whose eyes
follow the mouse cursor accompanies the user throughout.

## Stack
- **Python 3.11+**
- **Streamlit** — UI framework
- **Anthropic Python SDK** — Claude API for letter generation
- **Resend** (or smtplib fallback) — direct email sending
- **SQLite** (future) — letter history persistence. For now, use `st.session_state`.

## Repo Structure
```
├── app.py                  # Entry point, page routing, CSS/font injection
├── pages/
│   ├── form.py             # Input form page
│   ├── results.py          # Letter review + actions page
│   └── history.py          # Saved letters page
├── core/
│   ├── generator.py        # Claude API call
│   ├── prompts.py          # Prompt templates (rage + relationship + family-friendly)
│   ├── history_store.py    # History interface (session state now, SQLite later)
│   └── email_sender.py     # Email sending (Resend / SMTP / mailto)
├── components/
│   ├── chicken.py          # Chicken mascot with mouse-tracking eyes
│   ├── loading.py          # Loading animation (chicken scribbling at desk)
│   └── letter_box.py       # Letter display (real letter styling)
├── assets/
│   ├── chicken_rage_*.svg  # Chicken SVG states (1–4)
│   └── doodles/            # Decorative SVG elements
├── styles/
│   └── theme.css           # All custom CSS, rage-level classes, overrides
├── DESIGN.md               # Design system — READ THIS before any UI work
├── SPEC.md                 # Product spec
├── ARCHITECTURE.md         # Technical architecture
├── requirements.txt
├── .env.example
└── README.md
```

## Key Files to Read Before Coding
1. **DESIGN.md** — Colors, fonts, components, animations, mascot specs
2. **SPEC.md** — User stories, functional requirements, rage level table
3. **ARCHITECTURE.md** — Data flow, session state schema, module responsibilities

## Art Style — CRITICAL
The entire app should look like a **kid's scratchy crayon drawing.** Not polished,
not clean — messy, childlike, hand-drawn energy. Wobbly borders, dashed lines, thick
offset shadows, slight rotations on elements. A 7-year-old made this.

## Design Rules (Summary)
- **No default Streamlit styling.** Override everything.
- **Four Google Fonts:** Rock Salt (titles), Gaegu (body/letter), Schoolbell (UI),
  Coming Soon (inputs). All scratchy/childlike.
- **Rage = Heaven to Hell:** Level 1 is angelic (sky blue bg, halo chicken). Level 4
  is hellfire (dark red bg, demon chicken, flames).
- **Chicken mascot** is large, on the right side, eyes follow mouse cursor via JS.
- **Letter looks like a real physical letter** — torn edges, paper texture, stamp,
  handwritten font, ruled lines.
- **Family-friendly toggle** controls whether Claude uses profanity.
- **Relationship type** affects letter tone (best friend = teasing, ex = ruthless).
- **User reviews and can edit** the letter before sending.

## Environment
- `ANTHROPIC_API_KEY` — required
- `RESEND_API_KEY` — optional (for direct email)
- `SMTP_EMAIL` / `SMTP_APP_PASSWORD` — optional fallback for email
- Model: `claude-sonnet-4-20250514`

## Code Conventions
- Type hints on all function signatures
- Docstrings on public functions
- `history_store.py` exposes a clean interface (`save_letter`, `get_letters`,
  `delete_letter`) swappable from session state to SQLite later
- All CSS in `styles/theme.css`, injected once in `app.py`
- No inline styles — use CSS classes
- Interactive components (chicken, loading) use `st.components.v1.html`

## Common Commands
```bash
streamlit run app.py
pip install -r requirements.txt
```

## Current Phase
**Check-in 1 (April 18, 2026):** App skeleton + input form + Claude API returning
rage-appropriate letters + chicken mascot visible. Results page functional.
Loading animation and email sending can be stubs.
