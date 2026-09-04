# 🍏 Apple Design System & Site Builder Training Curriculum

**Target Fleet:** Quill (Copywriting), Keystone (Valuation/CMA), Harbor (Onboarding), FastSiteBuilder Engine  
**Standard:** Apple High-End Industrial & Digital Design (`apple.com`, `apple.com/business`, `apple.com/vision-pro`)  
**Objective:** Transform all generated client sites from generic templates into Apple-caliber luxury web experiences.

---

## 1. Visual DNA & Token Foundations

### Palette & Materials
* **Canvas Background:** Deep Obsidian (`#000000` / `#050507`), secondary surface (`#101014`).
* **Frosted Materials:** `rgba(255, 255, 255, 0.04)` to `rgba(255, 255, 255, 0.08)`, backed by `-webkit-backdrop-filter: blur(24px); backdrop-filter: blur(24px);`.
* **Border Lines:** Hairline borders only: `1px solid rgba(255, 255, 255, 0.08)` (never heavy solid borders or neon glows).
* **Accent & Metal:** Restrained Champagne Gold (`#e5c890` / `#d4af37`), muted Slate (`#86868b`), and crisp White (`#f5f5f7`).

### Typography & Spatial Hierarchy
* **Font Family Stack:** `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif`.
* **Headline Tracking:** Tight negative tracking (`letter-spacing: -0.025em`) for display titles.
* **Lead Scale:**
  * Display 1: `clamp(2.8rem, 5.5vw, 4.8rem)`, `font-weight: 600`, line height `1.08`.
  * Category Eyebrow: `12px – 13px`, uppercase, `letter-spacing: 0.12em`, `font-weight: 600`.
  * Subtitle / Body: `18px – 21px`, `color: #86868b`, line height `1.45`.
* **Chapter Rhythm:** One dominant idea per viewport. Generous whitespace (`padding: 100px 0` minimum).

---

## 2. Interactive Primitives

### Apple Pill Buttons
* `border-radius: 980px` (standard Apple pill).
* Subtle hover reaction: `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);` with `transform: scale(1.02);`.
* Secondary links use text + arrow: `Explore the portfolio ›` in accent gold or Apple blue (`#2997ff`).

### Bento Cards & Micro-Surfaces
* Rounded corners: `border-radius: 28px`.
* Generous internal breathing space: `padding: 2.5rem – 3rem`.
* Content stack: Category label → Punchy headline statement → Concise descriptive copy → Interactive preview.

---

## 3. Copywriting & Tone Rules (Quill Training)

1. **Understated Confidence:** No exclamation points, no cheap hype words ("Revolutionary!", "Insane deals!"). Use period-ended, declarative statements:
   * *Example:* "Naples real estate. Perfectly orchestrated."
   * *Example:* "Precision valuation. Measured in minutes."
2. **Benefit Before Machinery:** Never lead with raw algorithms or database feeds. Lead with client outcomes: discreet privacy, seamless closings, and institutional-grade market data.
3. **Editorial Rhythm:** Short headline + one or two sentences of prose + direct, quiet action.

---

## 4. Analytical Precision Rules (Keystone Training)

1. **Interactive Valuation:** Valuation tools must present smooth, responsive dials or sliders with live reactive currency formatting.
2. **Clean Footnotes:** Every heuristic valuation must include quiet, ethical disclosures (`*Based on recent comparable sales within 1.5 miles. Staged demonstration; official appraisals require physical property inspection.*`).
