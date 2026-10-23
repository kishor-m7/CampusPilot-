---
name: Academic Intelligence
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#464554'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#777586'
  outline-variant: '#c7c4d7'
  surface-tint: '#5148d7'
  primary: '#2a14b4'
  on-primary: '#ffffff'
  primary-container: '#4338ca'
  on-primary-container: '#c1beff'
  inverse-primary: '#c3c0ff'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#553300'
  on-tertiary: '#ffffff'
  tertiary-container: '#744800'
  on-tertiary-container: '#ffb759'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e3dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#100069'
  on-primary-fixed-variant: '#372abf'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  title-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
  code-inline:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0em
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

This design system defines an intelligent, focused, and elevated academic copilot environment. Tailored for collegiate workflows, the visual language merges the structured clarity of high-performance SaaS productivity suites with the intuitive, ambient presence of modern conversational AI assistants.

The target demographic consists of university undergraduate and graduate students juggling modular course loads, strict assignment deadlines, dynamic schedules, and collaborative projects. The interface must inspire calm control, focus, and academic agency—eradicating chaotic cognitive overload through crystalline layout hierarchy, contextual AI summaries, and actionable study workflows.

The aesthetic philosophy centers on **Refined Modern Productivity with Ambient Intelligence**:
- **Surgical Hierarchy**: Content prioritization guided by time sensitivity, academic weight, and focus states.
- **Intentional Contrast**: Crisp neutral foundational layers offset by vivid status signaling and soft, luminous indigo/violet aura gradients that denote generative AI suggestions and conversational copiloting.
- **Structured Precision**: High visual legibility across data-heavy student schedules, dynamic metric counters, and conversational transcripts.

## Colors

The system uses a calibrated palette constructed for day-long screen use, immediate status recognition, and distinct AI affordances:

- **Primary (`#4338CA`, `#4F46E5`)**: Deep, authoritative Indigo serves as the system's anchor. Used for primary interactions, high-emphasis selections, brand anchors, and focused system states.
- **Secondary (`#10B981`)**: Vibrant Emerald used to indicate completed tasks, optimal academic pace, and positive schedule validation.
- **Tertiary (`#F59E0B`)**: Amber accent for impending deadlines, upcoming exam warnings, and time-critical notices.
- **Urgent Accent (`#EF4444`)**: Rose/Red utilized sparingly for overdue deliverables, conflicting time slots, and critical alerts.
- **AI Core Accents & Gradients**: Subtle transitions spanning `linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)` for generative response cards, active prompt triggers, and AI study-assistant indicators.
- **Neutrals & Surfaces**: Off-white Canvas (`#F8FAFC`), structural grouping panels (`#F1F5F9`), crisp elevated card surfaces (`#FFFFFF`), and refined structural border strokes (`#E2E8F0`). Text layers leverage deep slate (`#0F172A`) for primary headings down to muted cool gray (`#64748B`) for secondary metadata.

## Typography

The typography is built entirely upon **Inter**, providing unmatched optical performance across high-density academic agendas, tabular study metrics, and conversational conversational prompts.

- Headings use tightened letter tracking (`-0.015em` to `-0.025em`) with semi-bold to bold weights to establish an assertive, modern tone without aggressive weight shifts.
- Body text utilizes neutral letter-spacing and generous line height (1.42x - 1.5x) to maintain effortless readability during late-night study sessions.
- Monospace-style precision is simulated through tabular numerical alignment for grades, progress metrics, and countdown timers.
- Upper-case styling is reserved strictly for micro status tags, category metadata, and section division banners via `label-sm`.

## Layout & Spacing

The layout architecture relies on a structured, fluid responsive framework engineered for cross-device utility:

- **Desktop (1280px+)**: 12-column adaptive grid with a fixed 260px collapsible persistent navigation sidebar, 24px gutters, and 32px canvas margins. An optional context-aware AI drawer docks on the right (380px fixed width).
- **Tablet (768px - 1279px)**: 8-column grid with a collapsed icon-only rail sidebar (72px), 20px gutters, and 24px margins. Content cards stack into 2-column clusters.
- **Mobile (< 768px)**: 4-column fluid layout with 16px gutters and 16px edge margins. The sidebar collapses into an accessible bottom command bar, prioritizing the student greeting, immediate deadlines, and single-tap voice/chat invocation.

Spacing adheres strictly to an 8px base rhythm (`space-xs` = 4px, `space-sm` = 8px, `space-md` = 16px, `space-lg` = 24px, `space-xl` = 32px) to maintain geometric rhythm across cards, data tables, and input groupings.

## Elevation & Depth

Visual hierarchy employs a multi-tiered surface system using pristine white card planes elevated above the foundational slate-tinted canvas:

- **Level 0 (Canvas)**: Background surface (`#F8FAFC`). Flat, non-interactive ground.
- **Level 1 (Structural Cards & Modules)**: Pure white background (`#FFFFFF`), reinforced with a hairline border (`1px solid #E2E8F0`) and an ambient, low-contrast drop shadow (`0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)`).
- **Level 2 (Hovered Cards & Interactive Controls)**: Subtle upward elevation with enhanced ambient definition (`0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`), signaling immediate clickability.
- **Level 3 (Overlays, Flyouts & Copilot Panels)**: High floating priority (`0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04)`) combined with subtle backdrop filters (`backdrop-filter: blur(8px)`) for modal dismissability.
- **AI Aura Glow**: Generative and real-time assistant elements replace default drop shadows with a localized tinted illumination: `0 0 0 1px rgba(99, 102, 241, 0.2), 0 4px 20px -2px rgba(79, 70, 229, 0.15)`.

## Shapes

The design system adopts a balanced **Rounded (`2`)** geometric profile.

- Default containers, cards, and data surfaces feature an 8px (`0.5rem`) corner radius.
- Large contextual dashboards, study plan blocks, and modal overlays use `rounded-lg` (16px / `1.0rem`) to soften structural corners.
- Interactive elements such as badges, priority pills, filter chips, and primary chat suggestion tags use full-pill treatments (`9999px`) to create an immediate visual contrast against geometric data blocks.

## Components

### Buttons
- **Primary**: Solid Indigo (`#4338CA`), 8px radius, bold label typography (`title-sm`), 10px 18px padding. Hover: `#3730A3` with subtle y-translation (`-0.5px`).
- **AI Action Variant**: Subtle linear gradient (`#4F46E5` to `#7C3AED`) with an embedded spark icon, used for synthesis commands ("Summarize Syllabus", "Draft Study Plan").
- **Secondary**: Pure white fill with `#E2E8F0` border and slate text (`#1E293B`). Hover: `#F8FAFC`.
- **Tertiary / Ghost**: Transparent fill, slate label, 8px radius, highlighting on hover with `#F1F5F9`.

### Chips & Priority Badges
- **Pill Shape**: Radius `9999px`, height 24px, uppercase `label-sm` font.
- **Status Urgent (Overdue/Immediate Exam)**: `#FEF2F2` background, `#EF4444` border/text.
- **Status Approaching (Due Soon)**: `#FFFBEB` background, `#D97706` border/text.
- **Status Complete**: `#ECFDF5` background, `#059669` border/text.
- **AI Insight Chip**: Soft violet surface (`#EEF2FF`), `#4F46E5` text, featuring an automated micro-pulse dot.

### Navigation Sidebar
- Vertical orientation with active indicator consisting of an indigo-tinted surface highlight (`#EEF2FF`), a vertical 3px accent bar on the leading edge (`#4338CA`), and semi-bold indigo text.

### Metric Summary Cards
- White `#FFFFFF` surface with `rounded-md` (8px), enclosing an icon pill, micro-label (`label-md`), high-contrast numerical readout (`headline-lg`), and an inline trending indicator badge displaying completion velocities.

### Input Fields & Quick Search
- Height 42px, background `#FFFFFF`, border `1px solid #CBD5E1`, text `body-md`. Focus state uses zero harsh outlines, substituting an indigo ring: `box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15); border-color: #4F46E5;`.

### Conversational Copilot Elements
- **Assistant Message Bubble**: Pure white surface, subtle indigo perimeter border, featuring automated source citations tagged as clickable micro-pills.
- **User Prompt Bubble**: Soft cool tint (`#F1F5F9`), right-aligned with crisp margins.
- **Input Bar**: Centered dock style, rounded-full container, multi-modal triggers (audio/voice capture, file attachment, text prompt dispatch).