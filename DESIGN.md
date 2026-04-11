# DESIGN.md — Pay Me Back or Else

> **Purpose:** This file is the single source of truth for all visual and interaction
> design decisions. It is intended to be read by AI coding agents (Claude Code) to
> produce consistent, on-brand UI output. Every component, color, font, spacing rule,
> and animation behavior is specified here. When in doubt, reference this file.

---

## 1. Design Philosophy

**One-liner:** A hand-drawn, slightly unhinged letter-writing desk — like a friend
rage-journaling about money on a napkin.

### Principles
- **Handcrafted over polished.** Nothing should look like default Streamlit. Every
  visible element should feel sketched, stamped, or scribbled.
- **Escalating emotion.** The entire UI shifts mood as the rage level increases —
  colors warm, fonts get bolder, the mascot gets angrier, micro-animations intensify.
- **Funny, not mean.** The tone is comedic catharsis. Design should make the user
  laugh, not feel like they're actually threatening someone.
- **Copy-paste confidence.** The generated letter must look polished and intentional
  inside its container so users trust it enough to actually send it.

---

## 2. Color System

### Base Palette

| Token                | Hex       | Usage                                      |
|----------------------|-----------|---------------------------------------------|
| `--ink-black`        | `#1A1A1A` | Primary text, borders, mascot outlines      |
| `--paper-cream`      | `#FDF6E3` | Page background, letter background          |
| `--pencil-gray`      | `#6B6B6B` | Secondary text, placeholder text            |
| `--eraser-pink`      | `#F5E6E0` | Input field backgrounds, subtle highlights  |
| `--money-green`      | `#2D6A4F` | Success states, "paid" indicators, accents  |
| `--money-green-light`| `#D8F3DC` | Green tint backgrounds                      |
| `--angry-red`        | `#D32F2F` | Rage-4 accents, delete buttons, alerts      |
| `--angry-red-light`  | `#FFCDD2` | Red tint backgrounds                        |
| `--caution-amber`    | `#F9A825` | Rage-2/3 slider midpoint, warnings          |
| `--white`            | `#FFFFFF` | Card surfaces, modal backgrounds            |

### Rage-Level Color Classes

Each rage level applies a CSS class to the app root that shifts accent colors and
background tints. The transition between levels should be animated (`transition: all
0.4s ease`).

| Class      | Accent Color   | Background Tint  | Border Style          |
|------------|----------------|-------------------|-----------------------|
| `.rage-1`  | `--money-green` | `--paper-cream`  | 1px solid `#C8C8C8`   |
| `.rage-2`  | `--caution-amber` | `#FFF8E1`      | 1px dashed `#F9A825`  |
| `.rage-3`  | `#E65100`      | `#FFF3E0`        | 2px solid `#E65100`   |
| `.rage-4`  | `--angry-red`  | `#FFF0F0`        | 3px solid `--angry-red`, slight box-shadow `0 0 12px rgba(211,47,47,0.15)` |

---

## 3. Typography

All fonts are loaded from Google Fonts.

| Token              | Font Family       | Weight | Usage                            |
|--------------------|-------------------|--------|----------------------------------|
| `--font-display`   | Permanent Marker  | 400    | Page titles, rage-4 letter text  |
| `--font-body`      | Special Elite     | 400    | Letter output, form labels       |
| `--font-ui`        | Patrick Hand      | 400    | Buttons, nav, helper text        |
| `--font-input`     | Caveat            | 500    | User input fields                |

### Scale

| Element          | Size   | Line Height |
|------------------|--------|-------------|
| Page title (h1)  | 2.4rem | 1.2         |
| Section head (h2)| 1.6rem | 1.3         |
| Body / letter    | 1.1rem | 1.7         |
| Buttons          | 1.0rem | 1.4         |
| Captions / meta  | 0.85rem| 1.4         |

---

## 4. Layout & Spacing

### Page Structure
- Max content width: **680px**, centered.
- Horizontal padding: **1.5rem** on each side.
- Vertical rhythm base unit: **1rem**. Sections separated by **2.5rem**.
- Streamlit sidebar: **hidden** (not used in this app).
- Streamlit header/footer/hamburger menu: **hidden via CSS injection**.

### Card / Container
- Background: `--white`
- Border-radius: **6px**
- Padding: **1.5rem**
- Border: per rage-level class (see §2)
- Box-shadow (default): `0 2px 8px rgba(0,0,0,0.06)`

---

## 5. Components

### 5.1 Rage Slider

**Visual concept:** A horizontal slider styled as a thermometer or fuse. The filled
portion transitions from green → amber → orange → red as the value increases.

| Attribute        | Specification                                             |
|------------------|-----------------------------------------------------------|
| Type             | `st.slider` with custom CSS overlay                       |
| Range            | 1–4 (integer steps)                                       |
| Track color      | Gradient left-to-right matching rage palette               |
| Thumb            | Circle, 24px, `--ink-black` border, inner fill = current rage accent |
| Label display    | Below slider: level number + label text (e.g. "3 — Fed Up") in `--font-display` at current rage accent color |

**CSS gradient for track fill:**
```css
background: linear-gradient(to right,
  #2D6A4F 0%,    /* green  */
  #F9A825 33%,   /* amber  */
  #E65100 66%,   /* orange */
  #D32F2F 100%   /* red    */
);
```

### 5.2 Input Form

- All fields inside a single card container.
- Field backgrounds: `--eraser-pink`
- Field font: `--font-input` (Caveat)
- Field border: 1px solid `#D0D0D0`, border-radius 4px
- On focus: border color transitions to current rage accent
- Labels: `--font-body` (Special Elite), `--ink-black`
- Required indicator: small red asterisk after label text

**Fields (in order):**
1. Debtor Name — text input
2. Amount Owed ($) — number input
3. How Long They've Owed You — text input (e.g. "3 months", "since last summer")
4. Relationship — dropdown: Friend, Roommate, Family, Co-worker, Ex, Acquaintance
5. Context / What Happened — text area (optional, 2–3 sentence max)
6. Your Venmo/Zelle Handle — text input (optional, placeholder: "@yourhandle")
7. Rage Level — slider (see §5.1)

**Submit button:**
- Full width of card
- Background: current rage accent color
- Text: `--white`, `--font-display`
- Label text changes by rage level:
  - 1: "Write My Letter ✉️"
  - 2: "Draft the Message 😤"
  - 3: "Let Them Have It 🔥"
  - 4: "UNLEASH THE LETTER 💀"
- Hover: slight scale bump (`transform: scale(1.02)`)
- Disabled state (incomplete form): 50% opacity, no hover effect

### 5.3 Letter Output Box

**Visual concept:** Looks like a physical letter on slightly off-white paper with a
torn or rough top edge.

| Attribute         | Specification                                            |
|-------------------|----------------------------------------------------------|
| Background        | `--paper-cream`                                          |
| Border            | Per rage-level class                                     |
| Top edge          | CSS `clip-path` or SVG mask simulating torn paper         |
| Font              | `--font-body` (Special Elite); at rage-4, switch to `--font-display` (Permanent Marker) |
| Font color        | `--ink-black`; at rage-4, dark red `#8B0000`             |
| Padding           | 2rem                                                     |
| Max-height        | 500px with `overflow-y: auto` (styled scrollbar)         |
| Line decoration   | Faint horizontal ruled lines behind text (like notebook paper): `repeating-linear-gradient(transparent, transparent 1.6rem, #E8E0D0 1.6rem, #E8E0D0 1.65rem)` |

### 5.4 Action Buttons (Results Page)

Arranged in a row below the letter box. Styled as hand-drawn buttons.

| Button         | Icon  | Style                                      |
|----------------|-------|--------------------------------------------|
| Copy           | 📋    | Outlined, `--ink-black` border              |
| Regenerate     | 🔄    | Outlined, `--pencil-gray` border            |
| Save to History| 💾    | Filled, `--money-green` bg                  |
| Start Over     | ↩️    | Text-only, underlined                       |
| Send Email     | ✉️    | Filled, current rage accent bg              |

**Copy feedback:** Button text changes to "Copied! ✓" for 2 seconds, border flashes
`--money-green`.

**Regenerate:** Spinner replaces button text while loading. New letter should differ
from previous (prompt includes "write a different version").

### 5.5 History Page

- List layout: vertical stack of cards, newest first.
- Each card shows: debtor name, amount, rage level badge, date, first 80 chars of
  letter as preview.
- Rage level badge: small pill with rage accent bg + white text, e.g. "LV 3 🔥"
- Click/expand: reveals full letter text inside the card.
- Delete button: small trash icon, top-right of card, `--angry-red` on hover.
  Confirm via inline "Are you sure?" text swap (no modal).
- Empty state: centered illustration of the capybara mascot looking bored/peaceful,
  with text: "No letters yet. Go collect some debts!" in `--font-ui`.

### 5.6 Navigation

Three-tab navigation at the top of every page. Styled as hand-drawn tabs.

| Tab             | Label           | Icon |
|-----------------|-----------------|------|
| Form page       | "Write a Letter"| ✏️   |
| Results page    | "Your Letter"   | 📨   |
| History page    | "Past Letters"  | 📚   |

- Active tab: `--ink-black` text, bottom border 3px solid current rage accent
- Inactive tab: `--pencil-gray` text, no bottom border
- Font: `--font-ui` (Patrick Hand), 1.1rem

---

## 6. Mascot — Capy the Capybara

### Character Description
A cartoon capybara with simple black outlines, minimal shading, and exaggerated
facial expressions. Think: doodle-in-a-notebook energy. Capy holds a quill pen or
pencil in most states.

### Rage States (SVG Swap)

Four SVG illustrations, one per rage level. Each is displayed near the letter output
or in the sidebar/header area. Recommended size: 120×120px.

| State   | Expression & Pose                                               |
|---------|-----------------------------------------------------------------|
| Rage 1  | Calm, slightly smiling, holding a quill gently. Small heart above head. |
| Rage 2  | Side-eye expression, one eyebrow raised, tapping quill impatiently on desk. |
| Rage 3  | Teeth gritted, steam lines coming from ears, gripping quill tightly. |
| Rage 4  | Standing on desk, quill raised like a sword, flames in eyes, dramatic wind-blown fur. Papers flying around. |

### Placement
- **Form page:** Rage 1 Capy in top-right corner, switches SVG as slider moves.
- **Results page:** Current rage Capy next to the letter box header.
- **History page (empty):** Peaceful Capy (rage 1 variant, lying down) centered.

### Style Rules
- Stroke width: 2–3px, `--ink-black`
- Fill: flat colors only — tan/brown body (`#C4A882`), pink inner ears (`#F5C6C6`),
  white belly (`#FAF3E8`)
- No gradients, no drop shadows on the character itself
- Eyes: simple dot eyes at rage 1–2, angular/intense at rage 3–4

---

## 7. Animations & Micro-Interactions

All animations use CSS. Keep them subtle — the humor comes from the content, not
from the UI bouncing around.

| Trigger                    | Animation                                           | Duration |
|----------------------------|-----------------------------------------------------|----------|
| Rage slider value change   | Background tint cross-fade, accent color transition  | 0.4s ease |
| Rage slider value change   | Mascot SVG swap (no transition — instant cut works)  | instant  |
| Submit button hover        | `transform: scale(1.02)`                             | 0.15s    |
| Letter appearing           | Fade in + slight slide up                            | 0.5s ease-out |
| Copy button → "Copied!"   | Border flash green, text swap                        | 2s total |
| Delete confirmation        | Text swap inline (no modal)                          | instant  |
| Page transition            | Simple fade (`opacity 0→1`)                          | 0.3s     |
| Rage 4 letter box          | Very subtle `animation: shake 0.3s` on initial appear| 0.3s, once |
| Rage 4 background          | Faint pulsing red glow on letter container border     | 2s infinite, subtle |

### Shake Keyframes (Rage 4 only)
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-3px); }
  40% { transform: translateX(3px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
}
```

---

## 8. Doodle Decorations

Small hand-drawn SVG elements scattered as visual seasoning. These are static, not
interactive.

| Element           | Where                                  | Notes                    |
|-------------------|----------------------------------------|--------------------------|
| Dollar signs ($)  | Floating near page title               | 2–3, slightly rotated    |
| Squiggly underline| Under section headings                 | SVG path, not CSS border |
| Envelope doodle   | Near "Send Email" button               | Tiny, 20×16px            |
| Starburst / pow   | Behind rage level badge on history cards| Only at rage 3–4        |
| Coffee ring stain | Bottom-right corner of letter box      | Very faint, ~40% opacity |
| Crumpled paper    | Background texture tile (optional)     | Extremely subtle, 5% opacity max |

---

## 9. Streamlit CSS Overrides

Inject via `st.markdown(unsafe_allow_html=True)` at the top of the app.

### Must Override
- Hide Streamlit header, footer, hamburger menu, and "Made with Streamlit" badge
- Replace default font stack with project fonts
- Override `st.slider` track and thumb colors
- Override `st.button` to remove default blue styling
- Override `st.text_input`, `st.text_area`, `st.selectbox` backgrounds and borders
- Override `st.spinner` color to match rage accent
- Set page background to `--paper-cream`

### Do Not Override
- `st.error` / `st.warning` / `st.success` — keep functional, just re-font
- Scrollbar behavior — only style if inside the letter box

---

## 10. Do's and Don'ts

### Do
- ✅ Use handwritten fonts everywhere — consistency sells the aesthetic
- ✅ Let the rage level visually transform the entire page mood
- ✅ Keep the letter output area the visual hero — largest, most styled component
- ✅ Make Capy expressive and fun — the mascot carries personality
- ✅ Test with real letter output to make sure Special Elite is readable at body size
- ✅ Use CSS variables for all colors — makes rage-level theming a single class swap

### Don't
- ❌ Use any default Streamlit blue (`#FF4B4B`, `#0068C9`, etc.)
- ❌ Add heavy animations that distract from reading the letter
- ❌ Use more than 2 decorative doodles per visible screen area
- ❌ Make the mascot larger than 120×120px — it's seasoning, not the main dish
- ❌ Use rounded-pill buttons — keep corners slightly rounded (4–6px) for the
  hand-drawn feel
- ❌ Forget to style the empty/loading/error states — they should feel on-brand too
