# DESIGN.md v2 — Pay Me Back or Else

> **Purpose:** Single source of truth for all visual and interaction design. Read by
> AI coding agents (Claude Code) to produce consistent, on-brand UI. Follow this
> file exactly. When in doubt, reference this file.

---

## 1. Design Philosophy

**One-liner:** A kid's scratchy crayon drawing of a debt collection office run by
an angry chicken.

### Principles
- **Crayon, not calligraphy.** Everything looks hand-drawn by a 7-year-old. Wobbly
  lines, imperfect shapes, thick strokes, slight rotations. Nothing is straight.
- **Heaven to Hell.** The app transforms from angelic blue calm to literal hellfire
  as rage increases. The shift should be dramatic and unmistakable.
- **The Chicken is the star.** A big cartoon chicken mascot with mouse-tracking eyes
  is always visible. It reacts to rage level and makes the app feel alive.
- **Funny, not mean.** Comedic catharsis — make the user laugh, not feel like they're
  writing a real threat.
- **The letter is real.** The generated letter must look like an actual physical letter
  — paper, torn edges, handwriting, stamp — so users feel confident sharing it.

---

## 2. Color System

### Base Palette

| Token                | Hex       | Usage                                      |
|----------------------|-----------|---------------------------------------------|
| `--ink-black`        | `#1A1A1A` | Primary text, borders, outlines             |
| `--paper-cream`      | `#FDF6E3` | Letter background                           |
| `--pencil-gray`      | `#6B6B6B` | Secondary text, placeholder text            |
| `--sky-blue`         | `#87CEEB` | Rage-1 accent, heavenly vibes               |
| `--cloud-white`      | `#F0F8FF` | Rage-1 background                           |
| `--money-green`      | `#2D6A4F` | Success states, payment accents             |
| `--caution-amber`    | `#F9A825` | Rage-2 accent                               |
| `--angry-red`        | `#D32F2F` | Rage-3/4 accents                            |
| `--hell-red`         | `#8B0000` | Rage-4 deep red                             |
| `--flame-orange`     | `#FF4500` | Rage-4 flame accents                        |

### Rage-Level Classes — DRAMATIC Background Shifts

| Class      | Background                                    | Accent           | Text Color       | Border Style                         |
|------------|-----------------------------------------------|------------------|------------------|--------------------------------------|
| `.rage-1`  | Gradient `#E8F4FD` → `#F0F8FF` (soft sky)     | `--sky-blue`     | `--ink-black`    | 2px dashed `#87CEEB`                 |
| `.rage-2`  | Gradient `#FFF8E1` → `#FFFDE7` (warm cream)   | `--caution-amber`| `--ink-black`    | 2px dashed `#F9A825`                 |
| `.rage-3`  | Gradient `#FFF3E0` → `#FFE0B2` (hot orange)   | `#E65100`        | `--ink-black`    | 3px dashed `#E65100`                 |
| `.rage-4`  | Gradient `#1A0000` → `#4A0000` (hellfire dark) | `--angry-red`    | `#FFFFFF`        | 3px solid `--angry-red`, red glow    |

Transition between levels: `transition: all 0.5s ease` on body/root.

Rage 4 special: add CSS pseudo-element flame shapes at the bottom of the page
(`clip-path` or SVG overlay), faint pulsing red glow on borders.

---

## 3. Typography

All fonts from Google Fonts. All are intentionally scratchy/childlike.

| Token              | Font Family    | Weight | Usage                                |
|--------------------|----------------|--------|--------------------------------------|
| `--font-display`   | Rock Salt      | 400    | Page titles, rage labels, headings   |
| `--font-body`      | Gaegu          | 400    | Letter text, form labels, body copy  |
| `--font-ui`        | Schoolbell     | 400    | Buttons, nav tabs, helper text       |
| `--font-input`     | Coming Soon    | 400    | User input fields                    |

### Scale

| Element          | Size   | Line Height |
|------------------|--------|-------------|
| Page title (h1)  | 2.2rem | 1.3         |
| Section head (h2)| 1.4rem | 1.3         |
| Body / letter    | 1.2rem | 1.8         |
| Buttons          | 1.1rem | 1.4         |
| Captions / meta  | 0.85rem| 1.4         |

---

## 4. Scratchy Art Style Rules

This section defines the "kid's crayon drawing" aesthetic applied to ALL components.

### Borders
- Use `border-style: dashed` on all containers and cards
- Border width: 2–3px
- Border color: `--ink-black` or current rage accent
- Border-radius: 2–4px (barely rounded — kids don't draw perfect curves)

### Shadows
- NO CSS `box-shadow` blur. Instead use **hard offset shadows**:
  `box-shadow: 3px 3px 0px var(--ink-black)`
- This looks like a kid drew a shadow with a marker

### Element Rotation
- Apply slight random rotations to cards, buttons, and decorative elements
- Range: `rotate(-2deg)` to `rotate(2deg)`
- Use CSS `nth-child` selectors to vary rotation per element
- Example: `.card:nth-child(odd) { transform: rotate(-1deg); }`

### Lines and Dividers
- Never use straight `<hr>` lines
- Use squiggly SVG paths or thick dashed borders as dividers
- Decorative underlines under headings should be hand-drawn SVG paths

### Imperfection is the Goal
- If something looks too clean or perfect, it's wrong
- Offset elements by 1-2px from where they "should" be
- Vary padding slightly between similar elements

---

## 5. Layout & Spacing

### Page Structure
- Max content width: **900px**, centered (wider to fit chicken on right)
- Two-column layout: `st.columns([2, 1])` — content left, chicken right
- Horizontal padding: **1.5rem**
- Vertical rhythm: **1rem** base. Sections separated by **2.5rem**.
- Streamlit sidebar: **hidden**
- Streamlit header/footer/hamburger: **hidden**

### Card / Container
- Background: `--paper-cream` or current rage background tint
- Border: per rage class + scratchy style (see §4)
- Padding: **1.5rem**
- Shadow: `3px 3px 0px var(--ink-black)`
- Slight rotation: `rotate(-0.5deg)` to `rotate(0.5deg)`

---

## 6. Components

### 6.1 Rage Slider (Heaven to Hell)

| Attribute        | Specification                                              |
|------------------|------------------------------------------------------------|
| Type             | `st.slider` with CSS override                              |
| Range            | 1–4 (integer steps)                                        |
| Track gradient   | sky-blue → amber → orange → dark-red (left to right)       |
| Thumb            | Circle, 24px, `--ink-black` border, fill = current accent  |
| Labels           | Below slider in Rock Salt at current accent color           |

**Rage Level Labels:**
| Level | Label                                      |
|-------|--------------------------------------------|
| 1     | 😇 Heaven — Sweet and angelic               |
| 2     | 😤 Purgatory — Passive aggressive shade      |
| 3     | 🔥 Inferno — Fed up and furious              |
| 4     | 💀 HELL — Full demonic rage                  |

### 6.2 Input Form

All fields inside a card with scratchy dashed border.

**Fields (in order):**
1. Their Name — text input, required
2. Amount Owed ($) — number input, required
3. How Long They've Owed You — text input, required
4. Your Relationship — dropdown: Best Friend, Roommate, Family, Co-worker,
   Ex-Boyfriend, Ex-Girlfriend, Acquaintance, Frenemy
5. What Happened — text area, optional, max 300 chars
6. Their Email Address — text input, optional (for direct send)
7. Your Venmo/Zelle Handle — text input, optional
8. Rage Level — slider (see §6.1)
9. Family Friendly — checkbox (default: checked)

**Field styling:**
- Background: `#FFF8F0` (warm off-white)
- Font: Coming Soon
- Border: 1px dashed `#D0D0D0`
- Focus border: current rage accent, 2px
- Labels: Gaegu, `--ink-black`

**Submit button:**
- Full width
- Background: current rage accent
- Text: white, Schoolbell
- Labels by rage level: "Write My Letter ✉️" / "Draft the Shade 😤" / "Let Them Have It 🔥" / "UNLEASH HELL 💀"
- Slight rotation: `rotate(-0.5deg)`
- Hover: `scale(1.03)` + darker shade
- Disabled: 50% opacity

### 6.3 Letter Output Box

**Looks like a real physical letter on paper.**

| Attribute         | Specification                                            |
|-------------------|----------------------------------------------------------|
| Background        | `--paper-cream` with subtle CSS noise/grain               |
| Rotation          | `transform: rotate(1deg)` (slightly askew)                |
| Edges             | Torn/rough on all 4 sides via CSS `clip-path` or SVG mask |
| Header            | "TO: {debtor_name}" in Rock Salt, top-left                |
| Stamp             | Scratchy chicken-face doodle in top-right corner, 40×40px |
| Font              | Gaegu 400 weight                                          |
| Font color        | `--ink-black`; at rage 4, `#8B0000`                       |
| Ruled lines       | Faint horizontal lines behind text (notebook paper effect) |
| Padding           | 2rem                                                      |
| Shadow            | `4px 4px 0px var(--ink-black)`                            |
| Max-height        | 500px, overflow-y auto                                    |
| Rage 4 variant    | Paper looks scorched — darker cream `#E8D5B7`, dark edge vignette, reddish ruled lines |

### 6.4 Editable Letter Area

Below the display box, a `st.text_area` pre-filled with the generated letter.
Label: "✏️ Edit your letter before sending"
Font: Coming Soon
This is the version that gets sent/copied/saved.

### 6.5 Action Buttons (Results Page)

Row of buttons below the edit area. Scratchy button styling.

| Button        | Label                  | Style                                    |
|---------------|------------------------|------------------------------------------|
| Copy          | 📋 Copy to Clipboard   | Dashed border, `--ink-black`              |
| Regenerate    | 🔄 Write Me a New One  | Dashed border, `--pencil-gray`            |
| Save          | 💾 Save to History     | Filled, `--money-green` bg                |
| Send Email    | ✉️ Send Directly       | Filled, current rage accent bg            |
| Start Over    | ↩️ Start Over          | Text-only, dashed underline               |

All buttons: Schoolbell font, `3px 3px 0px` hard shadow, slight rotation.
Copy feedback: text swaps to "Copied! ✓" for 2 seconds.

### 6.6 History Page

- Vertical stack of cards, newest first
- Each card: debtor name, amount, rage badge, date, 80-char preview
- Rage badge: pill shape with rage accent bg, white text
  - "😇 LV1", "😤 LV2", "🔥 LV3", "💀 LV4"
- Expand: `st.expander` showing full letter
- Delete: trash icon, top-right, inline "Are you sure?" confirmation
- Empty state: peaceful chicken lying down, centered
  - Text: "No letters yet. Go ruffle some feathers! 🐔" in Schoolbell

### 6.7 Navigation

Three tabs at page top, Schoolbell font.

| Tab      | Label           | Icon |
|----------|-----------------|------|
| Form     | "Write a Letter"| ✏️   |
| Results  | "Your Letter"   | 📨   |
| History  | "Past Letters"  | 📚   |

- Active: `--ink-black`, dashed bottom border 3px in rage accent
- Inactive: `--pencil-gray`, no border
- Each tab label has slight rotation for the kid-drawing feel

---

## 7. Mascot — The Chicken

### Character Description
A big cartoon chicken drawn in scratchy kid-crayon style. Thick, wobbly black
outlines. Simple shapes. Exaggerated expressions. The chicken's EYES FOLLOW THE
USER'S MOUSE CURSOR via JavaScript (implemented as `st.components.v1.html`).

### Colors
- Body: `#FFD700` (bright yellow)
- Beak/legs: `#FF8C00` (orange)
- Comb/wattle: `#FF4444` (red)
- Belly: `#FFF8DC` (cornsilk, lighter yellow)
- Eye whites: `#FFFFFF`
- Pupils: `#1A1A1A` (moves with mouse)
- Outlines: `#1A1A1A`, stroke-width 3–4px, wobbly paths

### Size & Placement
- Approximately 300–400px tall
- Right column of a `[2, 1]` column layout
- Should feel large and prominent — the chicken is the personality of the app
- Ideally sticky/fixed so it stays visible while scrolling content

### Rage States

| Level | Expression & Pose | Special Elements |
|-------|-------------------|------------------|
| 1 (Heaven) | Happy, big smile, relaxed wings, peaceful | Tiny halo above head, pink cheek circles, small heart |
| 2 (Purgatory) | One eyebrow raised, beak slightly open, tapping foot | Tapping quill impatiently, "..." speech bubble |
| 3 (Inferno) | Eyebrows angled down, steam from ears, ruffled feathers | Gripping quill tightly, red-tinted face, sweat drops |
| 4 (Hell) | Devil horns, flame pupils, feathers on fire | Holds pitchfork instead of quill, standing on IOU pile, flames around |

### Eye Tracking Implementation
- Each eye has a white circle (sclera) and a black circle (pupil)
- JavaScript `mousemove` listener calculates angle from eye center to cursor using `Math.atan2`
- Pupil translates within a constrained radius (8–10px) in the direction of the cursor
- Both eyes track independently
- Smooth movement: `transition: transform 0.1s ease-out` on pupils

### Style Rules
- All lines should be slightly wobbly (not perfect SVG arcs — use hand-drawn paths)
- No gradients on the character
- No drop shadows on the character
- Thick outlines (3–4px)
- Flat fills only

---

## 8. Loading Animation

While Claude API generates the letter, show a custom animated loading screen.

**Visual:** A scratchy-drawn chicken sitting at a tiny desk, scribbling. The
quill/pencil oscillates back and forth (CSS `@keyframes`). Small paper scraps
fly off periodically.

**Loading messages** cycle every 2 seconds below the animation:
- Default: "The chicken is thinking really hard...", "Scribbling furiously...",
  "Finding the perfect words...", "Adding extra sass...",
  "Consulting the ancient texts of pettiness..."
- Rage 4: "SUMMONING THE LETTER FROM THE DEPTHS...",
  "THE CHICKEN HAS ENTERED RAGE MODE...",
  "TYPING WITH FURY AND TINY WINGS..."

---

## 9. Animations & Micro-Interactions

| Trigger                    | Animation                                           | Duration   |
|----------------------------|-----------------------------------------------------|------------|
| Rage slider change         | Background cross-fade, accent color transition       | 0.5s ease  |
| Rage slider change         | Chicken SVG/expression swap                          | instant    |
| Submit button hover        | `scale(1.03)`                                        | 0.15s      |
| Letter appearing           | Fade in + slight slide up + rotate to final position | 0.6s ease  |
| Copy → "Copied!"          | Text swap, border flash green                        | 2s total   |
| Delete confirmation        | Inline text swap                                     | instant    |
| Page transition            | `opacity: 0 → 1`                                    | 0.3s       |
| Rage 4 letter box appear   | Shake animation (0.3s, once)                         | 0.3s       |
| Rage 4 border              | Pulsing red glow                                     | 2s infinite|

### Shake Keyframes
```css
@keyframes shake {
  0%, 100% { transform: rotate(1deg) translateX(0); }
  20% { transform: rotate(1deg) translateX(-4px); }
  40% { transform: rotate(1deg) translateX(4px); }
  60% { transform: rotate(1deg) translateX(-3px); }
  80% { transform: rotate(1deg) translateX(3px); }
}
```

---

## 10. Doodle Decorations

Sparse hand-drawn SVG elements. Max 2–3 per visible screen area.

| Element           | Where                          | Notes                       |
|-------------------|--------------------------------|-----------------------------|
| Dollar signs ($)  | Near page title                | Scratchy, slightly rotated  |
| Squiggly underline| Under section headings         | SVG path, not CSS           |
| Envelope doodle   | Near "Send Email" button       | Tiny, ~20×16px              |
| Stars / starburst | Behind rage 3–4 badges         | Spiky, kid-drawn            |
| Flames            | Bottom edge at rage 4          | CSS or SVG                  |
| Clouds            | Top edge at rage 1             | Soft, puffy, simple         |
| Chicken footprints| Subtle page background pattern | Very faint, 3–5% opacity    |

---

## 11. Streamlit CSS Overrides

### Must Override
- Hide all Streamlit chrome (header, footer, hamburger, "Made with Streamlit")
- Replace all fonts with project fonts
- Override `st.slider` track (rage gradient) and thumb
- Override all `st.button` — remove default blue, apply scratchy style
- Override `st.text_input`, `st.text_area`, `st.selectbox` — warm bg, Coming Soon font
- Override `st.spinner` — or replace entirely with custom loading component
- Set page background per rage class
- Override `st.expander` styling for history cards

### Do Not Override
- `st.error` / `st.warning` / `st.success` — re-font only
- Core scrollbar behavior (style only inside letter box)

---

## 12. Do's and Don'ts

### Do
- ✅ Make everything look hand-drawn and slightly messy
- ✅ Make the background shift dramatically between rage levels
- ✅ Make the chicken the star — big, expressive, interactive
- ✅ Let the user edit the letter before sending
- ✅ Make the letter output look like a real physical letter
- ✅ Use hard offset shadows (`3px 3px 0px`) instead of blur shadows
- ✅ Apply slight rotations to elements for the crayon-drawing feel
- ✅ Use CSS variables for all colors for easy rage-level theming
- ✅ Test that Gaegu is readable at body text size

### Don't
- ❌ Use any default Streamlit blue or styling
- ❌ Make anything look too clean, polished, or professional
- ❌ Use perfect circles, straight lines, or even spacing
- ❌ Use blur shadows (`box-shadow` with blur radius)
- ❌ Add heavy animations that distract from reading the letter
- ❌ Use more than 3 decorative doodles per screen area
- ❌ Make the chicken smaller than 300px — it should be prominent
- ❌ Forget rage 4's special treatment (dark bg, inverted text, flames)
- ❌ Skip the torn-paper edges on the letter box
- ❌ Leave any empty/loading/error state unstyled
