---
name: DocSureAI
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#444653'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#757684'
  outline-variant: '#c4c5d5'
  surface-tint: '#3755c3'
  primary: '#00288e'
  on-primary: '#ffffff'
  primary-container: '#1e40af'
  on-primary-container: '#a8b8ff'
  inverse-primary: '#b8c4ff'
  secondary: '#006a63'
  on-secondary: '#ffffff'
  secondary-container: '#99efe5'
  on-secondary-container: '#006f67'
  tertiary: '#003d28'
  on-tertiary: '#ffffff'
  tertiary-container: '#00563a'
  on-tertiary-container: '#5bcf9e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#b8c4ff'
  on-primary-fixed: '#001453'
  on-primary-fixed-variant: '#173bab'
  secondary-fixed: '#9cf2e8'
  secondary-fixed-dim: '#80d5cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#00504a'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display:
    fontFamily: Geist
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.025em
  display-mobile:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system establishes an institutional-grade, high-trust visual language tailored for automated document intelligence, redaction, and enterprise privacy compliance. Its primary audience comprises Chief Information Security Officers, legal counsel, and enterprise compliance operations teams who demand uncompromised precision, auditability, and rigor.

The aesthetic fuses **Modern Corporate Minimalism** with technical optical precision. Every element reinforces reliability, cryptographic certitude, and calm authority. Visual clutter, playful startup tropes, neon gradients, and decorative distractions are strictly excluded. The visual rhythm favors expansive breathing room, mathematically balanced borders, crisp typography, and unambiguous status signaling that treats sensitive enterprise data with absolute dignity.

## Colors

The palette relies on deep institutional anchors balanced against neutral slate fields, ensuring zero visual fatigue during high-volume document auditing.

- **Primary (`#1e40af` - Deep Cobalt Indigo):** Serves as the authoritative backbone for key system interactions, active states, key landmarks, and critical focus triggers.
- **Secondary (`#0f766e` - Deep Slate Teal):** Applied to computational metrics, secondary analytics graphs, and data pipeline verification states.
- **Tertiary (`#059669` - Verified Emerald):** Reserved strictly for certified safe conditions: privacy validation checks, successful zero-leakage certifications, and confirmed document redactions.
- **Neutral (`#0f172a` - Deep Slate Charcoal):** Governs primary typography, high-contrast headings, and foundational system structures.

### Functional Roles & Tone Rules
- **Canvas Base:** Pure white (`#ffffff`) for document viewports; slate-50 (`#f8fafc`) for system app frames and secondary side panels.
- **Structural Outlines:** Subtle, calibrated slate border (`#e2e8f0`) to separate dense information panels without creating visual tension.
- **Privacy Redaction Indicators:** High-contrast neutral slate (`#334155`) with hairline emerald pinstripes (`#10b981`) to signify irreversible, certified redaction.
- **Alert Tones:** Restrained amber-600 (`#d97706`) for inspection flags; crimson-700 (`#b91c1c`) strictly for compliance breaches or unmasked PII warnings.

## Typography

Typography prioritizes clarity, structural hierarchy, and scanning efficiency.

- **Primary Headlines (Geist):** Clean, neo-grotesque proportions with tightened tracking that project technological precision without ornamental eccentricities.
- **Body & Continuous Text (Inter):** Highly legible across varied pixel densities; tall x-height minimizes visual fatigue during audit log review and policy reading.
- **Data & Metadata Labels (JetBrains Mono):** Monospaced precision applied selectively to cryptographic hashes, audit record timestamps, document bounding-box coordinates, OCR accuracy percentages, and status chips.

## Layout & Spacing

The layout model implements an 8pt base grid within a responsive 12-column layout. It balances expansive breathing room around top-level workflows with structured, high-density analytical inspection zones.

- **Desktop (1280px+):** Fixed 260px collapsible system navigation panel, followed by a fluid multi-pane workspace (document canvas alongside structured metadata rails). 24px gutters provide optical separation between viewport panes.
- **Tablet (768px - 1279px):** 8-column layout with collapsable context rails transformed into slide-over panels; workspace margin adjusts to 16px.
- **Mobile (< 768px):** 4-column linear reflow. Document viewports prioritize full-width pinch-to-zoom viewports with lower docked action drawers.

Internal components utilize strict spacing increments: `space-xs` (4px) for micro badge padding and icon-to-text relationships; `space-sm` (8px) for field internals and compact list items; `space-md` (16px) for standard card padding; and `space-xl` (32px) for analytical panel separations.

## Elevation & Depth

Visual hierarchy is maintained primarily through structured tonal separation and razor-sharp 1px borders (`#e2e8f0`), eschewing deep drop shadows in favor of a flat, architectural clarity.

- **Surface Level 0 (Base App Canvas):** `#f8fafc`. Houses outer layouts, table backgrounds, and global rails.
- **Surface Level 1 (Panels & Cards):** Solid `#ffffff` bordered by 1px solid `#e2e8f0`. Shadow: `0 1px 2px 0 rgba(15, 23, 42, 0.04)`.
- **Surface Level 2 (Dropdowns, Floating Filters, Context Menus):** Solid `#ffffff` bordered by 1px solid `#cbd5e1`. Diffuse elevation: `0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)`.
- **Surface Level 3 (Modal Dialogs & Redaction Confirmations):** Solid `#ffffff` with a subtle slate-tinted backdrop blur (`rgba(15, 23, 42, 0.35)` with 4px blur). Shadow: `0 12px 32px -4px rgba(15, 23, 42, 0.12), 0 4px 12px -2px rgba(15, 23, 42, 0.06)`.
- **Document Viewport Layer:** Neutral slate backdrop (`#0f172a` at 95% opacity) for document canvas isolation, ensuring scanned documents render with optical fidelity.

## Shapes

The design system standardizes on a calibrated shape scale that balances contemporary softness with strict enterprise structure.

- **Base Radius (`rounded-md`, 0.5rem / 8px):** Applied to form fields, secondary buttons, action menus, and individual table selection rows.
- **Container Radius (`rounded-lg`, 1rem / 16px):** Standard for analytical cards, modular metric tiles, document overview cards, and floating inspector panes.
- **Outer Shell Radius (`rounded-xl`, 1.5rem / 24px):** Reserved for primary viewport surfaces, system boundary cards, and large workflow containers.
- **Micro Radius (0.25rem / 4px):** Applied exclusively to metadata chips, compliance badges, monospaced code blocks, and bounding-box focus highlights.
- **Circular/Pill (Full):** Used strictly for radio selectors, live status dots, and avatar user badges.

## Components

### Buttons
- **Primary:** Background `#1e40af`, text `#ffffff`, border 1px solid transparent. Hover state shifts to `#1d4ed8`; active state `#1e3a8a`. Focus ring: 2px offset with `#3b82f6`. Height 40px, padding `0.5rem 1rem`.
- **Secondary / Outline:** Background `#ffffff`, text `#0f172a`, border 1px solid `#e2e8f0`. Hover: background `#f8fafc`, border `#cbd5e1`.
- **Destructive / Redact Trigger:** Background `#ffffff`, text `#b91c1c`, border 1px solid `#fecaca`. Hover: background `#fef2f2`, border `#ef4444`.

### Status Badges & Chips
Composed with font `JetBrains Mono`, size 11px, weight 500, uppercase letter spacing, padding `2px 8px`, border radius 4px.
- **Completed / Verified:** Background `#ecfdf5`, text `#065f46`, border 1px solid `#a7f3d0`. Includes a 6px solid emerald dot.
- **Processing:** Background `#eff6ff`, text `#1e40af`, border 1px solid `#bfdbfe`. Includes a pulsating indigo micro-indicator.
- **Pending / In Queue:** Background `#f8fafc`, text `#475569`, border 1px solid `#e2e8f0`.
- **Redacted / Masked:** Background `#0f172a`, text `#f8fafc`, border 1px solid `#334155`. Displays an active padlock glyph.

### Form Inputs & Selectors
- **Text & Search Fields:** Height 40px, background `#ffffff`, border 1px solid `#cbd5e1`, text `#0f172a`. Placeholder `#94a3b8`. Focus transitions to border `#1e40af` with an ambient ring: `0 0 0 3px rgba(30, 64, 175, 0.12)`.
- **Checkboxes & Radios:** Dimensions 16x16px. Border 1.5px solid `#94a3b8`. Checked state: background `#1e40af` with crisp white check vector.

### Cards & Container Panels
- Base card utilizes white surface background, 1px solid `#e2e8f0`, radius 16px (`rounded-lg`), padded with 24px.
- Header bars within cards are partitioned with a bottom border of 1px solid `#f1f5f9` and 16px bottom margin.

### Specialized System Components
- **Document Viewport Inspector:** Features an overlay layer rendering coordinate bounding boxes for detected PII. Boxes use hairline 1.5px borders (`#3b82f6` for detected text, `#059669` for validated redaction) with semi-transparent tint fills (`rgba(59, 130, 246, 0.08)`).
- **Audit Verification Stamp:** Cryptographic validation strip showing algorithm, hash, timestamp, and operator signature, styled in monospaced body-sm typography with an emerald safety border.