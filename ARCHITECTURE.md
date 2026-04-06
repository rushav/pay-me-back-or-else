# ARCHITECTURE.md — Pay Me Back or Else

**Project:** Pay Me Back or Else  
**Developer:** Rushav Dash  
**Client:** Lisa Li  
**Target Completion:** June 1, 2026

---

## Overview

Pay Me Back or Else is a single-user, client-side web application built with Python and Streamlit. It integrates with the Anthropic Claude API to generate tone-controlled debt collection letters based on structured user input. The application is deployed on Streamlit Cloud and requires no backend server or database beyond Streamlit's native session state and a local SQLite store for letter history.

---

## System Architecture

```
+-------------------+        +----------------------+        +------------------+
|   Browser (UI)    | <----> |  Streamlit App       | <----> |  Claude API      |
|   (Desktop)       |        |  (Python, app.py)    |        |  (Anthropic)     |
+-------------------+        +----------+-----------+        +------------------+
                                         |
                                         v
                               +---------+----------+
                               |  SQLite Database   |
                               |  (history.db)      |
                               +--------------------+
```

The application runs as a single-process Streamlit server. All user interactions flow through Streamlit's reactive component model. Letter history is persisted to a local SQLite file. The Claude API is called on-demand when the user submits the form or clicks Regenerate.

---

## Directory Structure

```
pay-me-back-or-else/
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API key (not committed to git)
├── db/
│   └── history.db          # SQLite database (auto-created on first run)
├── components/
│   ├── form.py             # Input form component
│   ├── results.py          # Letter display and action buttons
│   └── history.py          # History list and delete controls
├── services/
│   ├── claude_service.py   # Claude API call logic and prompt construction
│   └── db_service.py       # SQLite read/write operations
├── utils/
│   └── validators.py       # Input validation helpers
├── assets/
│   └── styles.css          # Custom CSS (handwritten fonts, rage-level theming)
├── SPEC.md
├── README.md
└── ARCHITECTURE.md
```

---

## Module Descriptions

### `app.py`
The root entry point. Manages Streamlit page routing between three views: Form, Results, and History. Holds top-level session state (current form inputs, active letter, view state). Applies global CSS from `assets/styles.css`.

### `components/form.py`
Renders the input form. Fields: debtor name, amount owed, time duration (number plus unit selector), relationship type (dropdown), and rage level (slider 1-4). Calls `validators.py` before allowing submission. Displays the live rage level label and illustrated mascot state based on slider position.

### `components/results.py`
Renders the generated letter in a styled output box. Provides the following action buttons: Copy to Clipboard, Regenerate (same inputs, new API call), Save to History, Start Over (clears session and returns to form), and Send Email Now (opens mailto link).

### `components/history.py`
Fetches all saved letters from SQLite via `db_service.py` and renders them as a list. Each entry shows debtor name, amount, rage level, and generation date. Entries are expandable to reveal the full letter. Each entry has a Delete button.

### `services/claude_service.py`
Responsible for all Claude API interactions. Constructs the prompt from form inputs and rage level, calls `anthropic.messages.create`, and returns the generated letter text. The prompt template instructs the model to adopt the tone corresponding to the selected rage level and to address the debtor by name with specifics about the amount and relationship.

**Prompt construction:**
```python
def build_prompt(name, amount, duration, unit, relationship, rage_level):
    tone_instructions = {
        1: "polite and friendly, like a gentle reminder between close friends",
        2: "passive aggressive, full of subtle shade and 'just checking in' energy",
        3: "fed up and direct, with mild implicit threats and clear frustration",
        4: "completely unhinged, emotionally chaotic, maximum drama, bordering on courtroom monologue"
    }
    ...
```

### `services/db_service.py`
Wraps all SQLite operations. On startup, creates `history.db` and the `letters` table if they do not exist. Exposes three functions: `save_letter()`, `get_all_letters()`, and `delete_letter()`.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS letters (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    debtor_name TEXT NOT NULL,
    amount      REAL NOT NULL,
    duration    TEXT NOT NULL,
    relationship TEXT NOT NULL,
    rage_level  INTEGER NOT NULL,
    letter_text TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `utils/validators.py`
Validates form inputs before any API call is made. Ensures no fields are empty, amount is a positive number, and rage level is within 1-4. Returns a list of validation errors to display inline on the form.

---

## Data Flow

### Letter Generation Flow
```
User fills form
    --> validators.py checks inputs
        --> claude_service.py builds prompt
            --> Claude API returns letter text
                --> Results view renders letter
                    --> User optionally saves to history
                        --> db_service.py writes to SQLite
```

### History Retrieval Flow
```
User navigates to History page
    --> db_service.get_all_letters()
        --> SQLite query returns rows ordered by created_at DESC
            --> history.py renders expandable entries
```

---

## Session State Design

Streamlit re-runs the entire script on each user interaction. The following keys are maintained in `st.session_state` to preserve state across reruns:

| Key | Type | Description |
|-----|------|-------------|
| `view` | `str` | Current page: `"form"`, `"results"`, or `"history"` |
| `form_data` | `dict` | Last submitted form values |
| `generated_letter` | `str` | Most recently generated letter text |
| `is_loading` | `bool` | True while awaiting API response |

---

## API Integration

**Model:** `claude-opus-4-5` (or latest stable Sonnet if latency becomes an issue)  
**Auth:** API key stored in `.streamlit/secrets.toml` as `ANTHROPIC_API_KEY`, accessed via `st.secrets`  
**Max tokens:** 800 (sufficient for a letter-length response)  
**Expected latency:** Under 5 seconds for typical prompts  

The API is called synchronously within a Streamlit spinner context to indicate loading state to the user.

---

## UI and Theming

Custom CSS is injected via `st.markdown(..., unsafe_allow_html=True)` or loaded from `assets/styles.css`. The following visual requirements from the spec are addressed through CSS:

- **Fonts:** Permanent Marker (headings), Special Elite (letter body), both loaded from Google Fonts
- **Rage level theming:** A CSS class is applied to the results container based on rage level (`.rage-1` through `.rage-4`). Level 4 applies tilt transforms and shaky border animations.
- **Letter output box:** Styled with a torn-edge SVG clip-path, drop shadow, and a stamp graphic positioned in the upper-right corner
- **Mascot:** An SVG inline illustration with four states swapped in via conditional rendering based on `rage_level`
- **Rage slider track:** Styled via CSS custom properties to produce a green-to-red gradient that updates as the slider value changes

---

## Deployment

The application is deployed to Streamlit Cloud connected to the GitHub repository. The `ANTHROPIC_API_KEY` is set as a Streamlit Cloud secret (not stored in the repository). SQLite history persists within the Streamlit Cloud container but is reset on redeployment; this is acceptable for MVP scope since user accounts are out of scope.

**Repository:** `https://github.com/lisa2001115/TECHIN514_Final_Pay-Me-Back-or-Else`  
**Branch:** `main`  
**Entry point:** `app.py`

---

## Dependencies

```
streamlit
anthropic
```

No additional dependencies are required. SQLite is included in the Python standard library.

---

## Security Considerations

- The Claude API key is never exposed in the frontend or committed to version control. It is accessed only through `st.secrets` at runtime.
- Form inputs are validated before being interpolated into the prompt to prevent malformed API requests.
- No user authentication is implemented (out of scope for MVP). All history is stored locally and is not user-partitioned.

---

## Known Constraints and MVP Tradeoffs

| Constraint | Decision |
|------------|----------|
| No user accounts | History is stored locally per deployment; acceptable for MVP |
| SQLite resets on redeployment | Acceptable; history is a convenience feature, not critical data |
| Mobile layout not required | Desktop-first CSS; tablet layout maintained, mobile out of scope |
| Email sending not implemented | "Send Email Now" opens a `mailto:` link with the letter pre-filled |
| No link sharing | Out of scope per spec |

---

## Check-in Milestones Mapped to Architecture

| Check-in | Date | Architecture Components Targeted |
|----------|------|----------------------------------|
| Check-in 1 | April 18, 2026 | `app.py`, `components/form.py`, `services/claude_service.py` |
| Check-in 2 | May 2, 2026 | `components/results.py`, rage level prompt control, session state |
| Check-in 3 | May 16, 2026 | `components/history.py`, `db_service.py`, `assets/styles.css` full theming |
| Final | June 1, 2026 | Deployment, README live link, all issues closed |
