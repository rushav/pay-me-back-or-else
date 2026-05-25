# Pay Me Back. Or Else.

An AI-powered debt collection letter generator that helps you finally
confront that friend who "forgot" they owe you money without ruining
the relationship (maybe).

Fill out a quick form, pick your rage level (1–4), and get a
hilarious, copy-paste-ready letter tuned to your exact level of
done-ness: from a polite nudge to full unhinged courtroom drama.

**Live URL:** _coming soon — see deployment steps below_


## Features

- "The demand" worksheet — debtor name, amount, time owed, relationship, optional context and Venmo/Zelle handle
- 4-tile rage meter (polite nudge / passive aggressive / fed up / unhinged) with dynamic submit button labels and crayon-color shifting
- AI-generated letter via Claude API — streams character-by-character in a crayon handwriting font with per-character jitter
- Regenerate, Copy, Save, Send Email, Start Over actions
- "The Hall of Grudges" — draggable sticky note in the top-right with horizontal-scroll grudge cards, save and delete (with confirmation)
- Chicken mascot, thermometer, and kid's drawing that cross-fade through their rage states as you change the tone
- Full-bleed storybook desk background


## Tech Stack

- Python 3.11+ and Streamlit
- Claude API (Anthropic) via `anthropic.messages.stream`
- SQLite for local letter history (see "Known limitations" below)


## Local development

```bash
git clone <this-repo-url>
cd <repo-dir>

# 1. Create and activate a virtualenv
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Configure your Anthropic API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Open .streamlit/secrets.toml and replace sk-... with your real key.
# (.env.example is included for tooling that wants the env var, but the
#  app reads from st.secrets — only secrets.toml is required.)

# 4. Run
streamlit run app.py
```

The app opens at <http://localhost:8501>. The first run creates `db/history.db` automatically.


## Deployment (Streamlit Community Cloud)

Streamlit Community Cloud auto-pulls from GitHub on every push to `main`.
The `.github/workflows/deploy.yml` workflow runs a smoke test first so a
broken push is visible on GitHub before the broken code goes live.

1. **Push the repo to GitHub.** The repo must be public, or the
   account deploying must be a member of the GitHub org that owns it.
   Streamlit Community Cloud cannot read fully-private repos for the
   free tier.
2. **Sign in to Streamlit Community Cloud** at
   <https://share.streamlit.io/>. Use "Continue with GitHub" and
   authorize Streamlit to read the target repo.
3. **Click "Create app" → "Deploy a public app from GitHub".**
4. **Repository / Branch / Main file path:**
   - Repository: `<your-github-user>/<your-repo>`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL (optional): pick a subdomain on `.streamlit.app`
5. **Set Python version** under "Advanced settings" → set to
   `3.11`. (`requirements.txt` is read automatically; no extra setup
   needed.)
6. **Paste the secret.** Under "Advanced settings" → "Secrets",
   paste exactly this TOML (substituting your real Anthropic key):

   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

7. **Click "Deploy".** The first build takes ~2 minutes (installing
   `streamlit` + `anthropic`). Subsequent pushes redeploy in ~30 seconds.

When the build finishes, paste the live URL back into the **Live URL**
line near the top of this README.


## Known limitations

- **SQLite is ephemeral on Streamlit Community Cloud.** `db/history.db`
  lives in the container's writable layer. The container is recreated
  on every redeploy (every push to `main`), every config change, and
  whenever the app sleeps after inactivity. Saved grudges disappear
  with the container. This is acceptable for v1 — the hall of grudges
  is a fun feature, not durable storage.

  If durable history matters later, candidate migration targets are
  **Supabase** (Postgres) or **Turso** (libSQL/SQLite-over-HTTP). Out
  of scope for v1.

- **Single-user app, no auth.** Anyone visiting the live URL sees the
  same hall of grudges. Per the spec, user accounts are out of scope.

- **Letter generation cost is on the deployer.** Every form submit
  hits the Claude API against the `ANTHROPIC_API_KEY` configured in
  the host's secrets. If you share the live URL widely, watch your
  Anthropic usage dashboard.

- **Missing-secret failure mode.** If `ANTHROPIC_API_KEY` is missing
  from `st.secrets`, the app still loads — but submitting the form
  surfaces a friendly banner reading "the chicken couldn't reach
  claude…" instead of crashing. Fix by configuring the secret in
  Community Cloud's UI (step 6 above).


## Project files

| Path | What it is |
|------|------------|
| `app.py` | Streamlit entry point. Owns session state and the Claude streaming call. Renders the entire interactive UI as a single `components.v1.html` iframe. |
| `components/` | Per-component HTML/JS chunks (rage meter, mascot, form, letter paper, hall of grudges, shared primitives). |
| `services/claude_service.py` | Prompt builder and `messages.stream` wrapper. |
| `services/db_service.py` | SQLite save/get/delete for the hall of grudges. |
| `utils/validators.py` | Form input validation. |
| `assets/styles.css` | Streamlit-level CSS — hides Streamlit chrome and renders the desk-background layer behind the iframe. |
| `design/` | Source assets from the design handoff — `main_table.png`, `chicken{1..4}-removebg-preview.png`, `T{1..4}-removebg-preview.png`, `drawing{1..4}-removebg-preview.png`. |
| `.streamlit/config.toml` | Production server / browser / theme config (committed). |
| `.streamlit/secrets.toml.example` | Placeholder for the Anthropic key (real `secrets.toml` is gitignored). |
| `.env.example` | Documentation-only stub; the app reads from `st.secrets`, not `.env`. |
| `.github/workflows/deploy.yml` | Pre-deploy smoke test: syntax check, dependency install, app import, AppTest cold-load. |
| `ARCHITECTURE.md` | Binding architecture spec — read this before changing module boundaries. |


## Developer

**Developer:** Rushav Dash  
**Agreed Fee:** 35 GIX Bucks  
**Target Completion:** June 1, 2026


## Timeline & Check-in Points

| Check-in | Date | Required Progress |
|----------|------|-------------------|
| Check-in 1 *(Completed)* | April 18, 2026 | App skeleton running locally, input form UI complete, Claude API connected and returning letters |
| Check-in 2 *(Completed)* | May 2, 2026 | Results page done (Copy, Regenerate, Save buttons working), rage level slider controls tone correctly |
| Check-in 3 | May 16, 2026 | History page working, illustrated UI style applied, all edge cases handled |
| Final | June 1, 2026 | App deployed on Streamlit Cloud, README updated with live link, all 8 issues closed |
