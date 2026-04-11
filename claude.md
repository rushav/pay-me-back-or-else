# CLAUDE.md — Pay Me Back or Else

## Project Overview
A Streamlit app that generates AI-powered, humorous debt collection letters. Users
fill out a form about who owes them money, pick a rage level (1–4), and get a
copy-paste-ready letter generated via the Claude API. The tone escalates from polite
nudge to full unhinged courtroom drama.

## Stack
- **Python 3.11+**
- **Streamlit** — UI framework
- **Anthropic Python SDK** — Claude API for letter generation
- **SQLite** (future) — letter history persistence. For now, use `st.session_state`.

## Repo Structure
```
├── app.py                  # Entry point, page routing, CSS injection
├── pages/
│   ├── form.py             # Input form page
│   ├── results.py          # Letter display + actions page
│   └── history.py          # Saved letters page
├── core/
│   ├── generator.py        # Claude API call, prompt construction
│   ├── history_store.py    # History interface (session state now, SQLite later)
│   └── prompts.py          # Prompt templates per rage level
├── assets/
│   ├── capy_rage_1.svg     # Mascot SVG — calm
│   ├── capy_rage_2.svg     # Mascot SVG — side-eye
│   ├── capy_rage_3.svg     # Mascot SVG — steaming
│   ├── capy_rage_4.svg     # Mascot SVG — flaming eyes
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
1. **DESIGN.md** — All colors, fonts, components, animations, mascot specs, do's/don'ts
2. **SPEC.md** — User stories, functional requirements, rage level table
3. **ARCHITECTURE.md** — Data flow, session state schema, module responsibilities

## Design Rules (Summary — full details in DESIGN.md)
- **No default Streamlit styling.** Override all blue, default fonts, header/footer.
- **Four handwritten Google Fonts:** Permanent Marker (titles), Special Elite (body),
  Patrick Hand (UI), Caveat (inputs).
- **Rage-level theming:** A single CSS class on the app root (`.rage-1` to `.rage-4`)
  controls accent colors, background tint, border style, and mascot SVG.
- **Letter box** is the visual hero — torn paper edge, notebook ruled lines, cream bg.
- **Capy mascot** (capybara) has 4 SVG states, max 120×120px.
- Keep decorative doodles sparse (max 2 per screen area).

## Environment
- `ANTHROPIC_API_KEY` — required, loaded from `.env` or Streamlit secrets
- Model: `claude-sonnet-4-20250514`

## Code Conventions
- Type hints on all function signatures
- Docstrings on public functions
- `history_store.py` must expose a clean interface (`save_letter`, `get_letters`,
  `delete_letter`) so it can be swapped from session state to SQLite later without
  changing callers.
- All CSS lives in `styles/theme.css`, injected once in `app.py` via
  `st.markdown(unsafe_allow_html=True)`.
- No inline styles in Python code — use CSS classes.

## Common Commands
```bash
# Run locally
streamlit run app.py

# Install deps
pip install -r requirements.txt
```

## Current Phase
**Check-in 1 (April 18, 2026):** App skeleton + input form + Claude API returning
letters. Results page and history page can be stubs. Focus on: routing works, form
validates, API call returns a rage-appropriate letter.
