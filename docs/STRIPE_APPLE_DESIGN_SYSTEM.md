# 💎 The Stripe × Apple Design System (Apex Luxury Benchmark)

**Core Archetype:** The Fusion of Stripe (Engineered & Disciplined) and Apple (Cinematic & Liquid Glass)  
**Fleet Training Target:** FastSiteBuilder, Quill (Copy), Keystone (Valuation/CMA), Harbor (Intake)

---

## The Matrix: Stripe vs. Apple vs. Apex Fusion

| Feature | Stripe (The Engine) | Apple (The Prestige) | ⚡ Apex Luxury Fusion |
| :--- | :--- | :--- | :--- |
| **Visual Style** | Technical, disciplined, gradient-driven | Cinematic, imagery-led, liquid glass | **Liquid glass cards over subtle radiant gradient mesh & obsidian canvas** |
| **Typography** | Söhne-var, variable, airy | SF Pro, bold, editorial, tight tracking | **High-contrast SF Pro / Inter with negative tracking (-0.025em) and airy line heights** |
| **Motion** | Micro-interactions, fast 150-200ms transitions | Cinematic scroll, spatial UI, quiet reveals | **Fast tactile hover feedback with slow, calm ambient lighting** |
| **Layout** | Strict 8/16px grid, modular bento | Bento + full-bleed cinematic hero | **Cinematic full-bleed hero leading into strict modular bento chapters** |
| **Brand Feel** | Engineered, trustworthy, institutional | Emotional, premium, aspirational | **Institutional-grade trustworthiness with private-client luxury prestige** |

---

## 1. Visual Style & Materials (Liquid Glass + Gradient Cones)
* **Obsidian Canvas:** `#000000` base with Stripe-style multi-stop background cones:
  `radial-gradient(ellipse 80% 50% at 50% -20%, rgba(229, 200, 144, 0.15), transparent 70%)`
* **Liquid Glass Surfaces:**
  `background: rgba(18, 18, 22, 0.65);`  
  `backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);`  
  `border: 1px solid rgba(255, 255, 255, 0.08);`
* **Stripe Micro-Illumination on Hover:**
  Border shifts to `rgba(229, 200, 144, 0.4)` with an inner specular drop-shadow `0 0 30px rgba(229, 200, 144, 0.08)`.

---

## 2. Typography & Hierarchy (Airy + Bold Editorial)
* **Display Titles:** Bold, editorial, clamp sizing (`clamp(2.8rem, 5.5vw, 4.8rem)`), line-height `1.05`, tight tracking (`-0.03em`).
* **Micro-Labels (Stripe Style):** Monospace or high-tracking small caps (`font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; color: #e5c890; font-weight: 600;`).
* **Airy Body (Stripe Style):** Generous line height `1.6`, muted slate `#86868b`, max-width `640px` for effortless reading.

---

## 3. Motion & Micro-Interactions
* **Stripe Pill Buttons:** Pill shape (`980px`), crisp tactile active state (`transform: scale(0.98)` on click, `scale(1.02)` on hover), 200ms cubic bezier.
* **Apple Link Chevrons:** Micro-animated arrow displacement on hover (`gap: 0.35rem` -> `gap: 0.6rem`).
* **Reactive Telemetry (Keystone):** Smooth real-time number rolling with `font-variant-numeric: tabular-nums`.

---

## 4. Modular Bento Layout (8/16px Discipline)
* Strict 8px / 16px grid units for margins, paddings, and gap spacing (`gap: 1.5rem` = 24px, `padding: 2.5rem` = 40px).
* Asymmetric bento cards (2-column span anchor card + 1-column detail cards).
