# Security Policy

## How API keys are handled

This app calls the Anthropic API and needs an `ANTHROPIC_API_KEY`. The key is
**never** committed to the repository.

- **Local development:** the key lives in `.streamlit/secrets.toml`, read by the
  app via `st.secrets["ANTHROPIC_API_KEY"]`. This file is **gitignored**.
  A `.env` file is also gitignored if you use one for editor/tooling, but the
  app itself reads from `secrets.toml`, not `.env`.
- **Production (Streamlit Community Cloud):** the key is stored in the
  Community Cloud **Secrets manager** (App → Settings → Secrets), pasted as TOML.
  It is injected at runtime and is never part of the repo or the build.

### Templates (committed, placeholders only)

- `.streamlit/secrets.toml.example` — copy to `.streamlit/secrets.toml` and add
  your real key.
- `.env.example` — reference for the expected variable name.

Both contain placeholder values only (e.g. `sk-...`), never a real key.

## Reporting a security concern

Please **do not** open a public issue for security problems. Instead:

1. Open a private report via the repository's **GitHub Security tab →
   "Report a vulnerability"** (private security advisory), or
2. Contact the repository owner directly.

Please include steps to reproduce and any relevant logs (with secrets redacted).

## If a key is ever exposed

If an API key is committed (even briefly) or otherwise leaked, **rotate it**:
revoke the exposed key in the [Anthropic Console](https://console.anthropic.com/)
and issue a new one. Removing the key from git history is **not sufficient** on
its own — once pushed, it must be treated as compromised and rotated.

## Known limitations

- **Ephemeral database:** the "Hall of Grudges" is stored in a local SQLite file
  (`db/history.db`). On Streamlit Community Cloud the filesystem is **ephemeral** —
  it is wiped on every app reboot, redeploy, or when the app sleeps. Saved letters
  are therefore **not durable** in production and may disappear without notice.
  No personal data is intended to be stored there; treat it as transient demo state.
