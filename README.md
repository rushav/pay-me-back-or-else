# Pay Me Back or Else

An AI-powered debt collection letter generator that helps you finally 
confront that friend who "forgot" they owe you money without ruining 
the relationship (maybe).

Fill out a quick form, pick your rage level (1–4), and get a 
hilarious, copy-paste-ready letter tuned to your exact level of 
done-ness: from a polite nudge to full unhinged courtroom drama.


## Features

- Simple input form: debtor name, amount, time owed, relationship type
- Rage level slider (1–4) with live tone preview
- AI-generated letter via Claude API — personal, funny, and actually sendable
- Regenerate button for a fresh version
- One-click copy
- Letter history with save and delete


## Tech Stack

- Python + Streamlit
- Claude API (Anthropic)


## Developer

**Developer:** Rushav Dash  
**Agreed Fee:** 35 GIX Bucks  
**Target Completion:** June 1, 2026

---

## Timeline & Check-in Points

| Check-in | Date | Required Progress |
|----------|------|-------------------|
|Check-in 1 | April 18, 2026 | App skeleton running locally, input form UI complete, Claude API connected and returning letters |
|Check-in 2 | May 2, 2026 | Results page done (Copy, Regenerate, Save buttons working), rage level slider controls tone correctly |
|Check-in 3 | May 16, 2026 | History page working, illustrated UI style applied, all edge cases handled |
|Final | June 1, 2026 | App deployed on Streamlit Cloud, README updated with live link, all 8 issues closed |

---

## Live Demo

🔗 [Coming soon]

---

## Local Setup
```bash
git clone https://github.com/lisa2001115/TECHIN514_Final_Pay-Me-Back-or-Else.git
cd TECHIN514_Final_Pay-Me-Back-or-Else
pip install -r requirements.txt
streamlit run app.py
```

Add your Claude API key to `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your-key-here"
```
