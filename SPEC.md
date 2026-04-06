# SPEC.md — Pay Me Back or Else

**Client:** Lisa Li
**Developer:** [Rushav Dash]
**Agreed Fee:** [35] GIX Bucks
**Target Completion:** June 1, 2026


## Project Overview
Pay Me Back or Else is a fun, AI-powered debt collection letter generator. Users input basic info about who owes them money — the debtor's name, the amount, how long it's been, and their relationship — then pick a "rage level" from 1 to 5. The app generates a hilarious, copy-paste-ready letter that escalates in tone from polite nudge to full unhinged courtroom drama. The goal is to give people a low-stakes, entertaining way to break the awkward "hey you still owe me money" conversation.


## User Stories
### Core Feature
- As a user, I want to fill out a simple form with my debtor's info so that 
  the AI has enough context to write a relevant letter.
- As a user, I want to select a rage level (1–4) so that I can control how 
  aggressive or funny the letter sounds.
- As a user, I want to instantly see the AI-generated letter so that I can 
  copy and send it right away.
- As a user, I want a "Regenerate" button so that I can get a different 
  version of the letter if I don't like the first one.
- As a user, I want a one-click copy button so that I don't have to 
  manually select the text.

### History
- As a user, I want to see my past generated letters so that I can 
  revisit or reuse them later.
- As a user, I want to delete old letters I no longer need so that my 
  history stays clean.

### Experience
- As a user, I want the app to feel fun and a little unhinged so that 
  using it is entertaining, not just functional.
- As a user, I want the rage level slider to show a preview of the tone 
  so that I know what to expect before generating.


## Functional Specifications
### 1. Input Form
- Fields:
  - Debtor's name (text)
  - Amount owed (number, in $)
  - Days/weeks/months owed (number + unit selector)
  - Relationship type (dropdown: Roommate / Friend / Ex / Coworker / Family / Other)
  - Rage level (slider: 1–4)
- All fields required before generation
- Rage level preview label:

| Level | Label | Tone |
|-------|-------|------|
| 1 | Gentle Nudge | Polite, friendly reminder |
| 2 | Passive Aggressive | Subtle shade, lots of "just checking in" |
| 3 | Fed Up | Direct, slightly threatening |
| 4 | Full Drama | Emotional, desperate, chaotic |

### 2. AI Letter Generation
- Calls Claude API with a prompt seeded by all form inputs + rage level
- Prompt instructs Claude to stay in character for the selected tone
- Letter should feel personal (uses debtor's name, specific amount, 
  relationship context)
- Generation should complete within 5 seconds

### 3. Results Page
- Displays the full generated letter in a styled text box
- Buttons: Copy / Regenerate / Save to History / Start Over / Send Email Now
- Regenerate keeps the same inputs but produces a different letter

### 4. History Page
- Lists all saved letters with: debtor name, amount, rage level, date generated
- Click to expand and view full letter
- Delete button per entry
## UI / Visual Requirements

### Overall Aesthetic
- **Style:** Hand-drawn illustration style — feels like a doodle come to life,
  not a corporate SaaS app
- Slightly imperfect lines, sketch-like borders, and textured backgrounds
  to reinforce the handmade feel
- Think: a angry sticky note your roommate left on the fridge, but make it an app

### Color Palette
- Ink-black for text and illustrated borders
- Accent colors: angry red and money green — used sparingly for buttons 
  and rage level indicators
- Rage level 4 should feel visually different — more chaotic, red-tinted,
  slightly "broken" UI elements (tilted text box, shaky borders)

### Typography
- Primary font: a handwritten / marker-style font (e.g. Caveat, Patrick Hand, 
  or Permanent Marker via Google Fonts)
- Body/letter text: clean readable font (e.g. Special Elite — typewriter feel)
- No generic sans-serif fonts — everything should feel personal and handmade

### Illustrated Elements
- Illustrated mascot: a small angry cartoon character (coin? fist? 
  angry piggy bank?) that reacts to the rage level
  - Level 1: calm, polite smile
  - Level 3: arms crossed, frowning
  - Level 4: steam coming out of ears, shaking
- Doodle decorations around the page: dollar signs, exclamation marks, 
  small lightning bolts — subtle, not cluttered
- Letter output box styled like a real physical letter — torn edge effect, 
  slight drop shadow, stamp or seal graphic in the corner

### Rage Level Slider
- Styled as a hand-drawn thermometer or fuse
- Color transitions from cool green (1) → yellow (2)→ orange (3) → angry red (4)
- Emoji or illustrated face above the slider that updates live as user drags

### Responsive
- Desktop first, but layout should not break on tablet
- Mobile is out of scope for MVP

## Non-Functional Specifications
- **Performance:** Letter should generate within 5 seconds
- **Reliability:** Form should validate inputs before calling the API 
  (no empty/broken requests)
- **Accessibility:** All buttons keyboard accessible, slider keyboard 
  controllable
- **Browser Support:** Latest Chrome and Firefox

## Out of Scope (MVP)
- User login or accounts
- Directly sending letters via email/SMS from the app
- Multilingual support
- Sharing letters via link
- Mobile native app

## Must-Have Feature
A rage level slider (1–4) that dynamically controls the AI-generated  letter's tone, from a polite gentle reminder to Full Drama.
