---
name: CortxOS Matrix
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#00687a'
  on-secondary: '#ffffff'
  secondary-container: '#57dffe'
  on-secondary-container: '#006172'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#23005c'
  on-tertiary-container: '#9466ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: -0.015em
  title-sm:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: -0.005em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: '0'
  code-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: '0'
  metric-val:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-xs:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-dense: 0.5rem
  margin: 1.5rem
  margin-dense: 0.75rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

The design system embodies the precision, clarity, and spatial depth of an advanced multi-agent runtime environment. It reconciles two opposing visual paradigms: an ultra-clean, architectural porcelain workspace for structural controls and whiteboarding, paired with an immersive, obsidian technical cockpit for execution traces, telemetry, and terminal runtimes.

The visual style merges technical minimalism with targeted cyber-glassmorphism. Surfaces are razor-sharp, demarcated by ultra-thin hairline borders, subtle translucent backdrops, and luminous chromatic indicators. The system evokes absolute predictability, high-bandwidth communication, and machine-grade agency, engineered specifically for engineers orchestrating concurrent AI workforces.

## Colors

The system uses an asymmetric dual-canvas strategy:

- **Workspace Base (Porcelain Light):** `#ffffff` for elevated control cards and panels, resting over `#f8fafc` and `#f1f5f9` structural canvas surfaces, bounded by structural `#e2e8f0` stroke dividers.
- **Compute Canvas & Terminals (Obsidian Slate):** Deep technical zones transition into `#090d16` and `#0f172a`, providing deep contrast for live execution loops, streaming traces, and memory states.
- **Agent Identity Spectrum:**
  - **Systems Engineer:** `#f97316` (Cyber Orange) — runtime operations, infrastructure orchestration, build states.
  - **Auditor / Planner:** `#10b981` (Emerald Cyber Green) — verification nodes, static analysis, policy validation.
  - **Researcher:** `#8b5cf6` (Royal Neon Purple) — context retrieval, memory synthesis, vector routing.
  - **Astra (Simulation / 3D):** `#06b6d4` (Electric Cyan) — spatial coordinates, viewport manipulation, frame telemetry.
- **System States:** Error (`#ef4444`), Alert (`#f59e0b`), Syncing (`#06b6d4`).

## Typography

Typography enforces a strict cognitive divide:
1. **Inter** powers narrative layout, UI navigation, settings, and spatial hierarchy. It maintains low-profile legibility without editorial intrusion.
2. **JetBrains Mono** powers all machine output: runtime logs, telemetry readouts, token telemetry, coordinates, and agent thought-chains. 

Weights stay disciplined: regular (`400`) for structural documentation, medium (`500`) for navigation and keys, and semi-bold (`600`) reserved exclusively for system statuses and active focus targets.

## Layout & Spacing

Designed primarily for widescreen desktop workstations (1440px to 4K displays). The screen space is organized into a modular multi-pane workbench:

- **Docked Structural Rails:** 48px to 64px collapsible navigation ribbons on extreme flanks.
- **Dynamic Split Viewports:** Adjustable CSS Grid-based split panels with 1px border dividers (`gutter-dense: 0.5rem` internal clearance) for simultaneous tracking of canvas viewports and console logs.
- **Floating Overlays:** Floating HUD elements preserve a 24px inset (`margin: 1.5rem`) from display perimeters.
- **Rhythm:** Dense 4px baseline (`space-xs` through `space-xl`) optimizing data density and horizontal viewport efficiency.

## Elevation & Depth

Depth is established through crisp surface layering, selective translucent glassmorphism, and structural 1px borders rather than diffuse heavy shadows:

- **Level 0 (Canvas Base):** Flat `#f8fafc` porcelain or `#090d16` terminal ground.
- **Level 1 (Docked Containers & Workspaces):** Solid `#ffffff` or `#0f172a` surfaces with a crisp `1px solid #e2e8f0` (or `rgba(255,255,255,0.08)` in dark regions). Zero drop shadows.
- **Level 2 (Floating Canvas Overlays & Action Pills):** `rgba(255, 255, 255, 0.82)` or `rgba(15, 23, 42, 0.75)` with `backdrop-filter: blur(12px)`, flanked by a delicate `1px solid rgba(255, 255, 255, 0.3)` or `rgba(255, 255, 255, 0.12)` rim highlight. Shadow: `0 4px 20px -2px rgba(15, 23, 42, 0.08)`.
- **Level 3 (Modal Runtime Overlays & Context Inspections):** Solid card elevation with `box-shadow: 0 12px 32px -4px rgba(15, 23, 42, 0.16)`.

## Shapes

The design system maintains an engineered, industrial geometric aesthetic:
- **Panels, Cards, Terminals:** Strict `0.25rem` (4px) to `0.5rem` (8px) corners, maintaining crisp tool-like boundaries.
- **Telemetry Chips, Control Overlays, and Agent Badges:** Fully circular/pill radius (`9999px`) to immediately distinguish ephemeral state, active agents, and interactive tool controls from structural grid windows.

## Components

### Buttons & Interactive Controls
- **System Action Buttons:** Height 28px/32px, font `body-sm` or `code-sm`, border-radius 4px. Primary variant uses solid `#0f172a` with `#ffffff` text. Secondary variant uses white background with `1px solid #e2e8f0`.
- **Floating Canvas Chips:** Pill-shaped (`rounded-full`), glassmorphic background with 12px blur, housing inline icon + micro-label (`code-sm`). Used for `Fit Room`, `Center Focus`, and `Zoom 100%`.

### Agent Status & Metric Badges
- Continuous telemetry readouts (FPS, Latency, Memory, Active Tokens) configured as compact pills with monospaced text (`metric-val`), featuring an active 6px glowing indicator dot mapped to the agent's signature hex color.

### Reasoning Trace & Terminal Panels
- Monospaced stream log (`#090d16` background) with collapsible accordion steps indicating agent reasoning passes. Step headers feature agent avatar pills alongside micro duration indicators (`142ms`). Inset code diff blocks use high-contrast syntax highlighting over `#020617`.

### Knowledge Node Cards
- Interactive canvas elements composed of Level 1 white surfaces, top-bordered with a 2px accent strip in the owning agent's signature tone. Backlink counters and connection pins render as `label-xs` tags anchored to card perimeters.

### Form Inputs & Filters
- Compact 28px high inputs, `code-sm` typography, zero inner shadow, styled with a neutral `#e2e8f0` border that illuminates to electric cyan (`#06b6d4`) or agent color upon active focus.