# ForgeSight Industrial IoT Platform

# UI/UX Design Specification

| Document field | Value |
|---|---|
| Version | 1.0 |
| Status | Phase 2 approval candidate |
| Date | 2026-08-05 |
| Design scope | Experience architecture and implementation blueprint only |
| Architecture baseline | Software Architecture Document v2.0 |

---

## 1. Document purpose and design mandate

This document is the single design source of truth for ForgeSight, a commercial Industrial IoT Device Management and Predictive Monitoring Platform. It converts the approved architecture into a complete experience blueprint before frontend development begins. It defines information architecture, role-aware workflows, visual language, responsive behavior, accessibility, component behavior, screen states, data visualizations, and low-fidelity wireframes. It deliberately contains no application implementation.

The experience must allow a user to understand estate health in under ten seconds, recognize abnormal machines immediately, find any authorized device in under five seconds, and act safely under operational pressure. Every decision favors trustworthy status, fast scanning, dense-but-readable data, and explicit consequences over decoration.

### 1.1 Experience principles

| Principle | Design decision | Rationale and acceptance signal |
|---|---|---|
| Truth before polish | Every live value carries freshness; Unknown, Stale, Offline, and Healthy are distinct. | Industrial decisions cannot be based on implied certainty. A user can always answer “when was this measured?” |
| Attention before inventory | Critical conditions and degraded connectivity lead the visual hierarchy; routine inventory recedes. | Exceptions require action, while normal assets mainly require confirmation. Critical items appear within the initial viewport. |
| Context never disappears | Factory, machine/device, time range, timezone, units, live/paused state, and applied filters persist near the page title. | Persistent context prevents acting on the wrong site or time window. |
| Progressive disclosure | Summary, evidence, and administrative controls appear in successive layers. | Managers can scan quickly while engineers can reach raw evidence without making every view overwhelming. |
| Safe action design | Destructive or high-impact actions name the target, consequence, permission, and audit reason. | Prevents accidental quarantine, certificate revocation, or incorrect alert closure. |
| Role-fit, not role-colored | Navigation, default landing content, density, and actions change by role; visual styling remains consistent. | Users see the work they can perform without creating six inconsistent products. |
| Accessible equivalence | Color is always paired with icon and text; charts have summaries and tables; all work is keyboard reachable. | The experience is operable across vision, motor, and situational limitations and meets WCAG 2.2 AA. |
| Calm industrial aesthetic | Dark neutral surfaces, restrained teal/blue accents, subtle elevation, and limited motion. | A calm console supports long shifts and makes abnormal states visually meaningful. |

### 1.2 Product voice and terminology

Labels are concise, factual, and action-led. Use “Acknowledge alert,” “Quarantine device,” and “Generate report,” not vague labels such as “Submit.” Error messages state what happened, what remains safe, and the next recovery action. “Machine” means the physical asset; “device” means the connected identity and sensor/controller attached to it. “Live” means values are within the configured freshness threshold, never merely that a connection exists.

### 1.3 Role-specific experience model

| Role | Default scope and landing emphasis | Visible administration | Operational actions | Deliberate restrictions |
|---|---|---|---|---|
| Super Administrator | All authorized factories; platform posture, critical alerts, certificate risk, service-wide KPIs | Factories, users, security, platform settings, retention and policy | All governed actions within policy | Cannot alter immutable audit history or view private certificate material |
| Factory Administrator | Assigned factories; connectivity, inventory, access and configuration | Local users, machines, devices, certificates, factory settings | Register, configure, quarantine, rotate certificate, manage local access | Cannot grant Super Administrator or weaken mandatory platform controls |
| Factory Manager | Assigned factories; health, production risk, energy, alert ownership and reports | Approved operational rules and schedules | Assign/acknowledge/resolve alerts, request reports, prioritize maintenance | No certificate/private security administration |
| Maintenance Engineer | Assigned equipment; diagnostic evidence, health trends, open work and maintenance history | Maintenance records and approved device commands | Acknowledge/resolve, add maintenance, run approved command, annotate evidence | No identity, factory, retention, or platform policy management |
| Operator | Current factory/line; live status, active alarms and first-response tasks | Personal notification preferences only | Acknowledge, add observational note, use predefined reports | No resolve unless explicitly delegated; no configuration or identity controls |
| Viewer | Assigned read-only scope; dashboards, analytics, inventory and completed reports | Personal profile/display preferences only | Filter, inspect, export only where policy grants | No mutation; disabled actions are generally omitted, not teased |

Role restrictions are explained in-context when a user follows a shared link to inaccessible content. Hiding an action reduces noise; server authorization remains authoritative.

---

## 2. Information architecture and navigation

### 2.1 Global application shell

The desktop shell uses a persistent left sidebar, a 64 px top navigation bar, and a scrollable main workspace. The sidebar establishes module location; the top bar preserves operational scope and utilities. This separation avoids mixing “where I am” with “what I am monitoring.”

**Sidebar order:** Dashboard, Factories, Machines, Devices, Live Monitoring, Analytics, Alerts, Reports, Audit Logs, Device Logs, Security Center, Users, Settings. Notifications and Profile live in the top bar but remain direct routes. Navigation is permission-filtered; unavailable modules do not leave dead destinations.

**Sidebar behavior:** 240 px expanded and 72 px collapsed on desktop. It shows product mark, icon, label, active indicator, nested disclosure only where necessary, and a bottom-aligned help/settings group. Collapse preference persists per user. Tooltips identify icons in collapsed mode. A single highlighted item identifies location; status counts may appear only on Alerts and Notifications so the sidebar does not become a second dashboard.

**Top navigation:** page context on the left; factory selector and time-range selector in the center where relevant; global search, notification bell, help, theme preference, and profile menu on the right. The factory selector says “All authorized factories,” never simply “All.” Theme control supports Dark and System; the dark theme is the product baseline. Search opens a command-style overlay with recent items and grouped Factories, Machines, Devices, Alerts, and Reports.

**Breadcrumbs:** shown for hierarchy depth greater than one, for example `Factories / Bengaluru Plant / Boiler Line / Boiler-02`. The current item is text, ancestors are links, and collapsed middle items remain keyboard accessible. Breadcrumbs are not used on top-level pages because the selected sidebar item already provides that context.

### 2.2 Navigation by role

| Module | Super Admin | Factory Admin | Manager | Engineer | Operator | Viewer |
|---|---:|---:|---:|---:|---:|---:|
| Dashboard, Devices, Analytics, Alerts, Reports, Notifications, Profile | Yes | Yes | Yes | Yes | Yes | Yes, read-only |
| Factories and Machines | Manage all | Manage assigned | Read assigned | Read assigned | Read assigned | Read assigned |
| Live Monitoring | All scopes | Assigned | Assigned | Assigned | Assigned, default | Assigned, read-only |
| Audit Logs | Platform | Assigned scope | Approved events | Own/assigned evidence | Own activity only | If auditor scope granted |
| Device Logs | Platform | Assigned | Read | Diagnostic default | Limited safe logs | Read if granted |
| Security Center | Full | Assigned factory | Posture summary | Device findings relevant to work | Urgent notices only | Hidden unless auditor scope |
| Users | Full | Assigned factory | Read team assignments | Hidden | Hidden | Hidden |
| Settings | Platform and factory | Factory and personal | Approved operational and personal | Personal and maintenance defaults | Personal | Personal |

### 2.3 Cross-product finding and drill-down

Global search opens with `Ctrl/Cmd + K` and accepts ID, asset code, name, tag, location, or alert title. Results show type, parent factory, status, and matching field. Exact device IDs rank first; then prefix/name matches; then tags. Selecting a result opens its canonical detail route and preserves the previous page in browser history. This ranking meets the five-second findability objective without requiring users to remember module structure.

### 2.4 Primary user flows

1. **Critical response:** notification or Dashboard critical card -> Alerts filtered to open critical -> Alert Details -> inspect condition and device evidence -> acknowledge -> assign or act -> verify recovery -> resolve with note. The timeline records every step.
2. **Device diagnosis:** global search -> Device Details -> confirm connection/freshness -> compare live values and historical trend -> inspect certificate/configuration/logs -> add maintenance record or approved command -> verify result.
3. **Estate review:** Dashboard -> choose factory/time -> scan KPIs -> compare Factory Status -> Analytics drill-down -> request a bounded report -> receive completion notification -> download.
4. **Onboarding:** Factory Management -> create factory -> register machine -> register/import device -> issue certificate -> bind machine/location -> observe first telemetry -> confirm live state. Progress indicates incomplete steps without treating an uncommissioned device as failed.
5. **Security investigation:** Security Center finding -> evidence panel -> affected user/device -> Audit Logs correlation -> disposition/assign finding. Evidence remains immutable even after remediation.

---

## 3. Visual foundation

### 3.1 Color system

The palette uses blue-black neutrals to reduce glare, teal as the owned product accent, and conventional semantic colors tuned for dark-surface contrast. Accent color never substitutes for hierarchy, and semantic color never carries meaning without text/icon support.

| Token | HEX | Use | Rationale |
|---|---|---|---|
| Primary 500 | `#20C997` | Primary buttons, active navigation, selected controls | Teal feels technical and controlled, remains distinct from alarm red/amber, and is less visually aggressive than saturated cyan. |
| Primary 400 | `#4DDBB1` | Hover emphasis, data highlight | The lighter step preserves visibility against raised surfaces. |
| Primary 700 | `#137A61` | Pressed state, subtle filled backgrounds | A darker state communicates physical press without motion alone. |
| Secondary 500 | `#4EA1FF` | Links, comparison series, informational actions | Blue follows established enterprise interaction conventions and separates navigational actions from primary completion actions. |
| Success | `#34D399` | Completed, recovered, healthy confirmation | Green has strong learned meaning; the slightly cool tone harmonizes with teal while remaining distinguishable through label/icon. |
| Warning | `#F4B740` | Maintenance due, expiring, degraded | Amber attracts attention without falsely signaling immediate danger. |
| Danger | `#EF5B67` | Critical alerts, destructive actions, failure | A softened red remains urgent on dark surfaces without blooming during long viewing. |
| Info | `#60A5FA` | Informational banners, syncing, guidance | Accessible blue is recognizable as neutral system communication. |
| Background | `#070B12` | App canvas | Near-black blue reduces glare while retaining depth between canvas and surfaces. |
| Sidebar | `#080D15` | Persistent navigation | Slight separation from canvas anchors navigation without a heavy border. |
| Surface | `#0D131D` | Panels and table regions | First elevation step organizes dense information. |
| Card | `#111923` | Cards, widgets, menus | Higher luminance supports grouping and comfortable reading. |
| Elevated | `#16212E` | Dialogs, popovers, selected rows | The brightest neutral sits above content without relying on large shadows. |
| Border | `#263548` | Dividers and controls | Visible on all dark surfaces while remaining secondary to content. |
| Border subtle | `#1B2838` | Card separators, grid lines | Prevents dense dashboards from becoming boxed-in. |
| Text primary | `#E8EEF7` | Headings and primary values | Cool off-white reduces glare versus pure white and targets AA/AAA contrast on core surfaces. |
| Text secondary | `#B6C2D2` | Body copy and metadata | Supports hierarchy while retaining AA contrast at body sizes. |
| Muted text | `#8493A7` | Captions, placeholders, timestamps | Clearly secondary; reserved for nonessential information and not used for critical instructions. |
| Hover | `#182536` | Row/card hover | Subtle luminance change reveals interactivity without shifting layout. |
| Focus | `#5EEAD4` | 2 px focus ring with 2 px offset | High-visibility mint distinguishes keyboard focus from selection. |
| Disabled surface | `#151D28` | Disabled controls | Retains shape while receding from enabled controls. |
| Disabled text | `#66758A` | Disabled labels/icons | Communicates inactivity; nearby help explains permission or prerequisite when needed. |

### 3.2 Operational status colors

| Status | Color | Shape/icon treatment | Rationale |
|---|---|---|---|
| Online | `#3DDC97` | Filled circle + “Online” | A crisp green communicates confirmed current connectivity. |
| Offline | `#94A3B8` | Slashed circle + “Offline” | Neutral gray avoids confusing connectivity loss with an active critical condition; alarm rules may separately make it critical. |
| Critical | `#FF6673` | Octagon/exclamation + “Critical” | Bright red is reserved for immediate risk and therefore retains salience. |
| Maintenance | `#F7C65C` | Wrench + “Maintenance” | Amber expresses planned attention rather than failure. |
| Inactive | `#64748B` | Hollow circle + “Inactive” | Lower contrast correctly represents intentionally unused inventory. |
| Stale | `#C084FC` | Clock + age | Purple distinguishes delayed data from both Offline and Warning. |
| Unknown | `#A8B0BD` | Question mark + “Unknown” | Neutral styling refuses to infer health when evidence is insufficient. |

Status chips use a tinted 12% background, the full-intensity icon/text, and a border. This triple encoding remains interpretable in grayscale and supports users with color-vision differences.

### 3.3 Typography

**Primary family:** Inter, with system sans-serif fallback. Inter is optimized for UI legibility, has distinct numerals and punctuation, and supports dense enterprise layouts. **Technical/numeric family:** IBM Plex Mono for device IDs, certificate fingerprints, log excerpts, timestamps where alignment matters, and tabular telemetry. Monospace is not used for prose because it slows scanning.

| Style token | Size / line height | Weight | Use and rationale |
|---|---:|---:|---|
| Display | 32 / 40 px | 650 | Login brand statement and exceptional empty states; rare use preserves impact. |
| Heading 1 | 24 / 32 px | 650 | Page title; compact enough to keep operational content above the fold. |
| Heading 2 | 20 / 28 px | 600 | Major sections and dialog titles. |
| Heading 3 | 16 / 24 px | 600 | Card and panel titles; matches dense dashboard rhythm. |
| Subheading | 14 / 20 px | 600 | Table groups and explanatory subheads. |
| Body | 14 / 20 px | 400 | Default UI copy; balances density and long-shift readability. |
| Body compact | 13 / 18 px | 400 | Dense table cells only, never instructional copy. |
| Label | 12 / 16 px | 600 | Form labels and uppercase-free metadata labels. |
| Caption | 12 / 18 px | 400 | Freshness, units, secondary metadata. |
| Micro | 11 / 16 px | 500 | Chart axes and badges; never the sole carrier of a critical message. |
| Button | 13 / 18 px | 600 | Clear, compact controls; sentence case improves rapid recognition. |
| Metric L | 30 / 36 px | 650 | Primary KPI numbers using tabular numerals. |
| Metric M | 22 / 28 px | 650 | Secondary KPIs and live sensor values. |

No body text falls below 12 px. Headings use tight letter spacing (-0.01em equivalent); labels and body use normal spacing. Values use tabular numerals so updates do not visually jitter.

### 3.4 Iconography

Use **Lucide** outline icons at 1.75 px visual stroke. Lucide offers consistent geometry, clear enterprise metaphors, and a broad open set. Filled icons are reserved for selected status, not routine navigation. Icons always have visible labels in primary navigation; icon-only controls require accessible names and tooltips.

| Concept | Lucide icon | Usage rationale |
|---|---|---|
| Dashboard | LayoutDashboard | Recognizable modular overview |
| Factories | Factory | Explicit industrial site metaphor |
| Machines | Cog | Physical moving asset, distinct from electronic device |
| Devices | Cpu | Connected edge identity/sensor |
| Live Monitoring | Activity | Continuous signal without implying health |
| Analytics | ChartNoAxesCombined | Comparative trends and analysis |
| Alerts | TriangleAlert | Caution shape with high recognition |
| Reports | FileChartColumn | Generated analytical document |
| Audit Logs | ScrollText | Durable recorded history |
| Device Logs | SquareTerminal | Technical event stream |
| Security | ShieldCheck | Posture/protection; ShieldAlert for findings |
| Users | UsersRound | Team and access management |
| Settings | Settings | Conventional configuration metaphor |
| Notifications | Bell | Inbox and unread count |
| Profile | CircleUserRound | Personal identity |
| Cloud | Cloud | Cloud connection/service context |
| AWS | CloudCog plus “AWS” text | Avoids relying on a vendor logo and remains clear |

### 3.5 Imagery, texture, and brand expression

The product uses no decorative stock photography inside the operational shell. Login may use a restrained abstract topology of nodes and production lines at low contrast. Data and status remain the visual focus. Glass-like translucency is limited to the global search overlay and authentication panel where no live values sit beneath it; operational cards stay opaque to preserve contrast and prevent visual interference.

---

## 4. Design system tokens

### 4.1 Spacing and sizing

The base unit is 4 px. The spacing scale is 0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, and 80 px. Controls use 8 px internal gaps; related content uses 12-16 px; cards use 16 px compact or 20-24 px standard padding; page sections use 24-32 px gaps. The predictable rhythm helps users visually group dense data without excessive borders.

Control heights are 32 px compact, 40 px standard, and 48 px touch/emphasis. Interactive targets are at least 44 by 44 CSS pixels on touch layouts; compact desktop controls maintain a 44 px focus/click area when possible.

### 4.2 Shape, border, and elevation

| Token | Value | Use and rationale |
|---|---:|---|
| Radius XS | 4 px | Chips and compact code-like labels; technical and precise |
| Radius S | 6 px | Inputs, buttons, table containers |
| Radius M | 10 px | Cards and popovers; premium but not playful |
| Radius L | 14 px | Dialogs and authentication panel |
| Radius pill | 999 px | Status chips and segmented controls only |
| Border | 1 px | Controls, cards where surface contrast is insufficient |
| Elevation 0 | None | Canvas and embedded regions |
| Elevation 1 | 0 2 px 8 px at 18% black | Hovered cards and sticky toolbars |
| Elevation 2 | 0 8 px 24 px at 28% black | Menus and popovers |
| Elevation 3 | 0 18 px 48 px at 38% black | Dialogs; used sparingly so hierarchy remains credible |

### 4.3 Icon, motion, and feedback tokens

Icon sizes are 16 px inline, 18 px controls, 20 px navigation, 24 px card/state emphasis, and 40 px empty-state illustration. Motion durations are 100 ms immediate feedback, 160 ms control/hover, 220 ms panel transitions, and 320 ms complex layout entry. Easing is standard deceleration for entry and acceleration for exit. Motion never delays an action result. Reduced-motion mode removes translation and animated chart drawing, retaining only instant opacity/state changes.

### 4.4 Grid and breakpoints

| Viewport | Columns | Outer margin | Gutter | Shell behavior |
|---|---:|---:|---:|---|
| Wide desktop, 1536 px and above | 12 | 32 px; content max 1600 px | 24 px | 240 px sidebar; 3-4 KPI cards per row; optional split detail |
| Desktop, 1280-1535 px | 12 | 24 px | 24 px | 240/72 px sidebar; standard dashboard |
| Compact desktop, 1024-1279 px | 12 | 20 px | 20 px | Collapsed 72 px sidebar by default; two-column panels |
| Tablet, 768-1023 px | 12 | 20 px | 16 px | Sidebar becomes drawer; controls wrap; two KPI cards per row |
| Large mobile, 480-767 px | 12 | 16 px | 12 px | Single-column flow; bottom-safe sticky primary action where useful |
| Small mobile, 360-479 px | 12 | 12 px | 12 px | Single-column; secondary controls enter overflow menus |

All breakpoints retain a conceptual 12-column grid so component spans are consistent: full width is 12, half is 6, one third is 4, and one quarter is 3. Tablet/mobile components generally span 6 or 12 rather than changing layout mathematics. This eases implementation and keeps hierarchy predictable.

### 4.5 Layout dimensions and density

Top navigation is 64 px desktop and 56 px mobile. Page content starts 24 px below the header on desktop, 20 px on tablet, and 16 px on mobile. Dashboard KPI cards have a 112 px preferred minimum height. Chart cards use 320 px standard height, 240 px compact, and 420 px for primary analysis. Tables display 48 px standard rows or 40 px compact rows selected through a user density preference. Fixed card heights are used only within aligned dashboard rows; detail content grows naturally to prevent clipping.

---

## 5. Component library

### 5.1 Actions and input

| Component | Variants and behavior | Design rationale |
|---|---|---|
| Button | Primary, secondary, quiet, danger, icon, split; default/loading/success/disabled | One primary action per region prevents competing calls to action. Loading preserves width and label context. |
| Text input | Label, optional hint, prefix/suffix, clear, validation; 40 px default | Persistent labels outperform placeholders, especially during error recovery. |
| Select/combobox | Searchable above 10 items; selected count and clear action | Industrial lists are long; search avoids exhaustive scrolling. |
| Checkbox/radio/switch | Checkbox for independent choices, radio for exclusive choices, switch only for immediate reversible settings | Control semantics match consequence and reduce surprises. |
| Date/time range | Presets plus explicit start/end and timezone | Operators need speed; analysts need precision. Timezone remains visible to prevent cross-site mistakes. |
| Search | Local search with scope label; global command search | Separates “search this table” from “find anything in the platform.” |
| Filter bar | High-value filters visible, additional filters in popover, applied chips below | Keeps frequent refinement fast while preventing toolbar overload. |
| Form section | Heading, concise rationale, fields, validation summary, sticky action footer for long forms | Supports scanning and safe correction of multiple errors. |

### 5.2 Content and status

| Component | Anatomy and behavior | Design rationale |
|---|---|---|
| Card | Title, optional description, action, body, footer; interactive cards show hover/focus | A consistent frame supports modular dashboards; border/elevation signals clickability. |
| Metric card | Label, value, unit, delta, comparison period, status, sparkline, freshness | Value without unit/time context is unsafe. Delta uses arrow + text + color. |
| Status chip | Icon, plain-language label, optional age; semantic border/background | Triple encoding enables rapid scan and accessibility. |
| Badge | Neutral categorization only, such as asset type or environment | Separating badges from status prevents labels from appearing alarm-like. |
| Alert card | Severity rail, title, factory/device, condition, age, assignee, status, quick action | High-signal summary supports triage without opening every alert. |
| Avatar | Photo optional; initials fallback; presence is not shown unless truly live | Identity matters for assignment; false presence would mislead. |
| Empty state | Specific icon, what is absent, why it may be absent, safe next action | Distinguishes “no data yet,” “no results,” and “not authorized.” |
| Skeleton | Matches final component geometry; no pulsing in reduced motion | Prevents layout shift and shows that data is loading, not missing. |
| Banner | Info, warning, critical, success; title, concise consequence, action | Page-level state such as stale telemetry must not be buried in a toast. |

### 5.3 Navigation and overlays

Sidebar, top navigation, breadcrumbs, tabs, pagination, stepper, dropdown, popover, tooltip, drawer, and dialog share a single focus model. Escape closes the topmost nonblocking overlay; dialogs trap focus; opening focus starts at the title or first invalid field; closing returns focus to the invoking control. Tooltips explain, never contain required interaction. Destructive confirmation dialogs require an explicit reason when the action is audited and repeat the target in the action label.

### 5.4 Charts and widgets

Every chart includes title, one-sentence analytical question, plot, legend, units, time range, sampling interval, data quality, last update, tooltip, accessible summary, and “View data table.” Legends toggle series but never remove them from the accessible table. Crosshairs synchronize charts in Device Details and Analytics. Zoom is bounded and resettable. A card-level error never collapses the rest of the dashboard.

### 5.5 Notifications and transient feedback

Toasts appear at the lower-right desktop and lower-center mobile, remain for at least six seconds for informative messages, and persist when recovery is required. Success toasts confirm completed mutation and name the target. Errors include retry or destination to details. A notification-center entry exists for durable or asynchronous results; toasts are not used as the only record of report generation or command completion.

### 5.6 Required component inventory

The implementation library must expose named, documented variants for **Buttons, Cards, Charts, Tables, Forms, Dialogs, Dropdowns, Inputs, Badges, Status Chips, Avatars, Breadcrumbs, Sidebar, Navbar, Widgets, Metric Cards, and Alert Cards**. Each component includes default, hover, focus, active, selected where relevant, loading, disabled, empty where relevant, error, high-contrast, reduced-motion, compact-density, desktop and touch-layout behavior. This explicit inventory prevents page teams from recreating inconsistent primitives.

---

## 6. Enterprise table standard

Tables are the primary tool for large operational datasets. They support local search, server-side sort, filter, pagination, column selection, density, authorized CSV export, authorized PDF export, and a sticky header. PDF uses a report-quality print layout rather than a screenshot of the visible rows. The first identifying column may also remain sticky on wide datasets. Sorting announces direction; filters appear as removable chips; pagination includes current range, total count, page size, and direct page navigation where useful.

| Element | Specification | Rationale |
|---|---|---|
| Header | 40 px, high-contrast label, sort control with text alternative | Keeps meaning visible during vertical scan and supports nonvisual operation. |
| Row | 48 px default, 40 px compact, 64 px when two-line identity is required | Offers user-controlled density without sacrificing touch use. |
| Selection | Checkbox column with selected count and scope-safe bulk action bar | Bulk changes remain explicit and never imply “all” beyond loaded/filtered scope. |
| Primary cell | Name/ID link plus secondary parent context | A row remains understandable when reached through search or export. |
| Status | Icon + label chip, never a colored dot alone | Reliable recognition and accessibility. |
| Numeric data | Right aligned, tabular numerals, unit in header or cell | Supports column comparison and prevents ambiguous telemetry. |
| Actions | One common inline action plus overflow; destructive actions separated | Reduces visual noise and accidental activation. |
| Responsive | Preserve identity, status, severity/health, freshness, and main action; move lesser fields to row detail | Mobile prioritizes operational meaning rather than shrinking unreadable columns. |
| Export | Export current authorized filtered dataset; dialog names format, row estimate, timezone and applied filters | Prevents accidental disclosure and makes exported evidence reproducible. |

**Table states:** loading uses header plus 8-12 row skeletons; empty inventory offers an authorized create/import action; no filter results offers Clear filters; partial result shows a warning without discarding returned rows; error preserves filters and offers Retry; denied state exposes no column data. Pagination resets only when a filter changes, not when a row is opened and closed.

---

## 7. Data visualization specification

### 7.1 Dataset-to-chart mapping

| Dataset | Visualization | Encodings and interaction | Rationale |
|---|---|---|---|
| Temperature over time | Line chart | Time x-axis, degrees y-axis, actual line, threshold bands, anomaly markers | Line position best reveals rate and threshold crossing without implying filled volume. |
| Humidity over time | Area chart | Time x-axis, percent y-axis, restrained transparent fill | Bounded percentage and accumulated visual mass make environmental drift easy to see. |
| Pressure over time | Line chart | Time x-axis, pressure y-axis, safe range band | Precision and sudden changes matter more than volume. |
| Power usage by period/machine | Bar chart | Period/category x-axis, kWh y-axis, comparison outline | Bars support accurate magnitude comparison across discrete periods or assets. |
| Device status distribution | Donut rather than traditional pie | Segment count/percentage, direct labels, center total; adjacent accessible list | Part-to-whole is appropriate for a small fixed status set; the center total anchors scale. |
| Factory health dimensions | Radar chart | Axes for connectivity, machine health, alerts, energy, maintenance, data quality | Useful for a compact multi-dimensional profile; always paired with a scored list because radar angle comparison is imprecise. |
| Machine health score | Gauge | 0-100 semicircle, numeric score, band label, confidence and trend | Familiar at-a-glance condition indicator; the number prevents imprecise reading. |
| Alerts over time | Event timeline | Time axis, severity lanes, markers clustered by interval | Preserves event sequence and bursts better than a simple count line. |
| Top faulty machines | Horizontal bar | Ranked machine names, open-alert/risk measure, direct values | Long asset names remain readable and rank comparison is immediate. |
| Energy usage by source/line | Stacked bar | Period x-axis, kWh y-axis, stable stack categories and total | Shows both total and contribution across a small consistent set of lines/sources. |

Charts never use dual axes unless a clearly labeled analytical comparison makes it unavoidable; normalized small multiples are preferred. No 3D effects, unlabeled smoothing, or decorative gradients are used because they distort industrial readings.

### 7.2 Executive Dashboard metric contract

| Required metric/widget | Presentation | Context and drill-down |
|---|---|---|
| Total Factories | Metric card | Active/maintenance split; opens Factory Management |
| Total Machines | Metric card | Active/maintenance/retired context; opens Machine Management |
| Online/Offline Devices | Paired metric card plus compact donut | Total denominator and last refresh; opens filtered Devices |
| Critical Alerts | Danger metric card | Open count and oldest age; opens open-critical Alerts |
| Machine Health Score | Gauge card | Weighted average, confidence/data quality, delta; opens health Analytics |
| Today's Alerts | Metric card | New/acknowledged/resolved; uses selected factory timezone |
| Power Consumption | Metric card plus sparkline | Current period kWh and prior-period delta; opens energy Analytics |
| Avg Temperature/Humidity/Pressure/RPM/Vibration | Five compact metric cells | Unit, valid-device denominator, trend, freshness; opens matching Analytics tab |
| Recent Alerts | Ranked list | Severity, asset, condition, age, status, assignee; opens Alert Details |
| Recent Activities | Timeline list | Actor, action, resource, relative time; opens permitted audit/activity evidence |
| Live Device Feed | Dense updating list | Device, latest metric, value, quality, freshness; pause visual updates and open device |
| Factory Status | Table/compact cards | Connectivity, health, open critical, power, last update; compare factories |
| Weather, optional | Small contextual widget | External source and timestamp; appears only where weather is operationally relevant |

Dashboard widgets query independently and show independent loading/error states. This avoids making a partial analytical outage look like total platform failure. User customization may reorder secondary widgets, but Critical Alerts, connectivity, and freshness cannot be removed.

---

## 8. Interaction and micro-interaction specification

- Hover adds a subtle surface lift or border change in 160 ms; it never moves surrounding content. Focus is more visible than hover.
- Pressed controls darken immediately in 100 ms. Mutations switch to an in-button progress indicator while keeping the verb visible, such as “Acknowledging…”
- Skeletons mirror final geometry. Full-page spinners are limited to authentication/session restoration; data pages retain shell and context.
- Live values cross-fade over 160 ms and briefly mark the changed cell; critical transitions announce once through a restrained live region and create a durable alert rather than repeatedly animating.
- Filters update results after explicit Apply when queries are expensive; lightweight local searches debounce briefly. Applied-filter count is always visible.
- Tooltips appear after a short intent delay, remain on hover/focus, and explain icons, units, truncated text, or calculation definitions.
- Progress indicators show named steps for device onboarding and report creation. Indeterminate progress is used only when the service cannot provide percentage.
- Confirmation dialogs are reserved for destructive, security-sensitive, or hard-to-reverse actions. Routine saves use inline confirmation rather than modal interruption.
- Optimistic feedback is limited to safe reversible preferences. Alerts, device commands, role changes, and security actions wait for server confirmation.
- Success messages name the completed action and target. Errors preserve user input, provide a correlation reference where appropriate, and explain retry safety.
- Page transitions do not animate. Drawers and dialogs use restrained opacity/scale; charts do not replay animation on every filter change.

---

## 9. Complete page specifications

Every page below defines its complete operational contract. “Denied” states are included where the route may be shared across roles; the application must never fetch protected data merely to decide that it cannot display it.

### 9.1 Login

| Requirement | Specification |
|---|---|
| Purpose | Establish a trusted human session and explain that the user is entering a monitored industrial system. |
| Target users | All six roles; no role is assumed before authentication. |
| Components and layout | A 12-column, full-height page: restrained brand/topology field across columns 1-7 and a 440 px authentication card across columns 8-12. The card contains logo, “Sign in to ForgeSight,” security context, email, password reveal control, Remember this device where policy permits, reset link, primary action, support link, and privacy/security notice. |
| User flow | Enter work email -> enter password -> validation -> Sign in -> optional identity-provider/MFA step defined by deployment -> role-appropriate Dashboard. A return destination is honored only if authorized. |
| Actions and buttons | Primary: Sign in. Secondary links: Forgot password, Contact administrator, Privacy and security. Password reveal is an icon button with a textual accessible name. |
| Widgets, filters, tables, charts, KPIs, cards | One authentication card and one service-status line. No filters, table, chart, or KPI appears because operational information before authentication would disclose system context and distract from the task. |
| Empty, loading, and error states | Initial fields are empty with persistent labels. Loading disables duplicate submission and reads “Signing in…”. Invalid credentials use a generic message; locked/rate-limited state gives a safe retry time; network failure preserves email and offers Retry; session-expired notice explains why sign-in is required. No message reveals whether an account exists. |
| Responsive behavior | Tablet centers a 440 px card over a subdued background. Mobile uses one 12-column card with 16 px margins; brand art becomes a small header and the primary button spans the width. Keyboard opening must not obscure the active field or error. |
| Rationale | A single focused card minimizes cognitive load while the industrial context and monitoring notice build trust. Generic authentication errors prevent account enumeration. |

### 9.2 Forgot Password

| Requirement | Specification |
|---|---|
| Purpose | Request a secure password-reset message without disclosing account membership. |
| Target users | Any unauthenticated user; support escalation is especially relevant for locked operational accounts. |
| Components and layout | Same authentication shell as Login for continuity. The card contains Back to sign in, title, short instruction, work-email input, Send reset instructions, and support guidance. A confirmation state replaces the form within the same card. |
| User flow | Enter email -> submit -> neutral confirmation -> open reset message externally -> return to Login. Repeated requests are throttled with a safe countdown. |
| Actions and buttons | Primary: Send reset instructions. Secondary: Back to sign in; Contact administrator. |
| Widgets, filters, tables, charts, KPIs, cards | One recovery card. No operational data, filter, table, chart, or KPI is exposed. |
| Empty, loading, and error states | Empty uses a work-email example as hint, not placeholder-only labeling. Loading reads “Sending…”. Confirmation says instructions will be sent if the account is eligible. Invalid email is inline; network error offers Retry; rate limit shows when a new attempt is allowed. |
| Responsive behavior | Matches Login; mobile keeps Back and title above the field and uses a full-width primary action. |
| Rationale | Reusing the authentication shell reduces doubt about destination. Neutral confirmation protects identity information without leaving a legitimate user uncertain about the next step. |

### 9.3 Dashboard

| Requirement | Specification |
|---|---|
| Purpose | Communicate authorized estate health in under ten seconds and create direct paths to exceptions. |
| Target users | All roles. Super Admin sees platform scope; Factory Admin sees inventory/connectivity; Manager sees risk/energy; Engineer sees health/maintenance; Operator sees live state/alerts; Viewer sees read-only summaries. |
| Components and layout | Header with title, factory scope, time range, timezone, Live/Stale marker and last update. Row 1 uses four 3-column KPI cards: Factories, Machines, Online/Offline Devices, Critical Alerts. Row 2 uses 4 columns for Machine Health gauge, 4 for Today's Alerts/Power, and 4 for environmental averages. Row 3 uses an 8-column trend chart and 4-column Recent Alerts. Row 4 uses 4-column Factory Status, 4-column Live Device Feed, 4-column Recent Activities. Optional Weather occupies a compact slot only when configured. |
| User flow | Land in saved authorized scope -> scan critical/connectivity/health -> select factory or time -> inspect changed widget -> drill to filtered destination -> browser Back restores dashboard filters and scroll. |
| Actions and buttons | Change scope/time, Refresh, Pause live visual updates, Customize secondary widgets, View all on lists, and role-permitted Generate report. Critical metric cards are links, not buttons nested inside cards. |
| Widgets, filters, tables, charts, KPIs, cards | All metrics in section 7.2 are mandatory. Filters: factory, line, time range, shift, Live/History. Chart: configurable primary trend defaults by role. Factory Status is a compact table; Recent Alerts, Activities, and Live Device Feed are structured lists. |
| Empty, loading, and error states | Widget-shaped skeletons load independently. No assigned factory explains how to contact an administrator. No telemetry distinguishes “commissioning not complete” from “no data in range.” Widget error names the unavailable measure and Retry; stale banner preserves last good data with age; partial failure never zeros a metric. |
| Responsive behavior | Tablet uses two KPI cards per row, then 12-column chart and paired lists. Mobile puts Critical Alerts, connectivity, health, and freshness first; KPI cards become a two-column horizontal group where space allows, charts become full width, and tables become priority-field cards. |
| Rationale | Fixed exception-first ordering supports muscle memory during incidents. Independent cards preserve usefulness during partial outages; role defaults reduce scanning without fragmenting the information model. |

### 9.4 Factory Management

| Requirement | Specification |
|---|---|
| Purpose | Find, compare, create, maintain, archive, and inspect authorized factory sites. |
| Target users | Super Admin manages all; Factory Admin manages assigned sites; Manager/Engineer/Operator/Viewer receive progressively narrower read-only views. |
| Components and layout | Page header with estate summary and permitted Create factory. KPI strip shows Active factories, In maintenance, Critical sites, and Average health. Filter bar precedes a table/card view toggle. Desktop table uses name, code, location/timezone, status, machines, devices online/total, critical alerts, health, power, last update, and actions. Selecting a row opens a right detail panel with site profile, operating status, alert/energy mini-trends, assigned team, and activity. |
| User flow | Search/filter -> compare rows -> open factory detail -> inspect lines/machines/devices -> edit permitted metadata or drill to scoped Dashboard/Alerts. Create flow uses Profile -> Operating context -> Defaults -> Review and create. |
| Actions and buttons | Create factory, Edit, Put in maintenance, Restore active, Archive, Compare selected, Open dashboard, Export. Archive confirmation lists dependent machines/devices and blocks unsafe action. |
| Widgets, filters, tables, charts, KPIs, cards | Filters: status, region, timezone, health band, critical-alert presence, connectivity band. Table follows enterprise standard. Detail panel uses health gauge, 24-hour power sparkline, device-status donut, open-alert list, and metadata cards. |
| Empty, loading, and error states | Empty estate offers Create for authorized admins or contact guidance. No matches offers Clear filters. Skeleton preserves KPI/table geometry. Partial KPI failure leaves inventory usable. Version conflict during edit shows current and attempted values. Denied state exposes no factory names. |
| Responsive behavior | Tablet table keeps name/status/health/connectivity/alerts and moves detail to a full drawer. Mobile defaults to factory cards with name, status, health, devices, critical alerts, and action menu; create/edit is a full-screen step flow. |
| Rationale | Table view supports estate comparison while a nonmodal detail panel maintains list context. Archive dependencies are made visible before consequence. |

### 9.5 Machine Management

| Requirement | Specification |
|---|---|
| Purpose | Manage physical production assets and their relationship to connected devices and maintenance. |
| Target users | Super/Factory Admin manage; Manager and Engineer inspect and update approved operational/maintenance fields; Operator and Viewer read. |
| Components and layout | KPI strip for Total machines, Healthy, Attention needed, Maintenance due, and Uninstrumented. Filter bar and enterprise table show machine name, asset code, factory/line, type, criticality, attached devices, health, operating state, maintenance due, last telemetry, and actions. Detail drawer contains identity, device attachments, health factors, current work/maintenance, alerts, and history. |
| User flow | Choose factory -> search asset code/name -> open row -> inspect attachment and health -> attach/detach permitted device or add maintenance -> verify activity record. Registration uses Identity -> Placement -> Criticality -> Device attachment -> Review. |
| Actions and buttons | Register machine, Edit, Attach device, Add maintenance, Put in maintenance, Return to service, Retire, Export. Retirement is blocked while active devices or open critical alerts remain. |
| Widgets, filters, tables, charts, KPIs, cards | Filters: factory, line, type, criticality, operating state, health band, maintenance status, device attachment. Table is canonical; drawer uses Machine Health gauge, factor list, compact trend, alerts and maintenance cards. |
| Empty, loading, and error states | Empty in a new factory explains registration order. No matches offers Clear filters. Loading skeletons table rows. Attachment conflict identifies the currently bound machine. Stale health says Unknown rather than Healthy. Save conflict supports refresh and compare. |
| Responsive behavior | Tablet reduces columns and uses full-height detail drawer. Mobile uses asset cards prioritizing criticality, health, state, device attachment, and maintenance; multi-step forms are full screen. |
| Rationale | Physical-machine identity remains separate from device identity, preventing operators from treating a sensor replacement as a new asset. Criticality and maintenance are prominent because they determine response priority. |

### 9.6 Device Management

| Requirement | Specification |
|---|---|
| Purpose | Search, register, import, govern, and inspect connected device identities across authorized factories. |
| Target users | Super/Factory Admin manage lifecycle and certificates; Manager/Engineer perform approved operational actions; Operator/Viewer inspect within scope. |
| Components and layout | KPI strip: Total, Online, Offline, Critical health, Certificate expiring, Quarantined. Filter bar and enterprise table show device name/ID, type, factory/machine, connection, health, latest key value, quality, certificate, firmware, last seen, and actions. A saved-view selector supports “Needs attention,” “Certificate risk,” and personal filters. |
| User flow | Search exact ID/name/tag -> refine scope/status -> open Device Details -> perform permitted action. Registration uses Identity -> Factory/machine -> Telemetry profile -> Certificate delivery -> Review; bulk import previews valid/invalid rows before commit. |
| Actions and buttons | Register device, Import CSV, Export, Open details, Quarantine/unquarantine, Assign machine, Rotate certificate, approved bulk tag or maintenance actions. No bulk destructive certificate revocation. |
| Widgets, filters, tables, charts, KPIs, cards | Filters: factory, machine, type, connection, health, certificate, firmware, tag, last-seen age. Table follows section 6; compact device-status donut may accompany KPIs but never replaces counts. |
| Empty, loading, and error states | Empty explains device commissioning and offers Register/Import to admins. Import shows row-level errors and permits exporting the rejection file. Live fields use skeletons then freshness. Partial telemetry error retains inventory. Certificate operation failure gives safe retry guidance and never reveals secret material. |
| Responsive behavior | Tablet preserves identity, machine, connection, health, last seen and main action. Mobile uses cards with Device ID copy control, status, health, latest value/freshness, certificate warning and Open details; advanced filters use a bottom sheet. |
| Rationale | Exact identity and certificate posture sit beside operational status because a device can be connected but untrusted or unhealthy. Saved attention views accelerate daily work. |

### 9.7 Device Details

| Requirement | Specification |
|---|---|
| Purpose | Provide one evidence-centered workspace for understanding, maintaining, and securely operating a device. |
| Target users | All roles within scope; tabs and actions are permission-filtered. Engineer is the primary diagnostic persona; Factory Admin is primary lifecycle persona. |
| Components and layout | Breadcrumb and identity header show device name/ID, connection, health, factory/machine, last seen, and actions. Overview uses a 3-column context rail and 9-column evidence area. Tabs: Overview, Telemetry, Alerts, Configuration, Certificates, Logs, Commands, Maintenance, Activity. A persistent freshness strip shows live/paused, update age, quality and timezone. |
| User flow | Arrive from search/alert -> verify identity and freshness -> scan Health Score and live sensors -> correlate historical charts -> inspect alert/log/config/certificate evidence -> perform authorized command, quarantine, rotation, or maintenance entry -> confirm activity. |
| Actions and buttons | Primary changes by condition: Acknowledge critical alert or Add maintenance. Secondary: Pause/resume view, Compare range, Generate report, approved Send command. Restricted overflow: Edit metadata, Quarantine/unquarantine, Rotate/revoke certificate. High-impact actions require target and audit reason. |
| Widgets, filters, tables, charts, KPIs, cards | Machine Info card includes asset, factory/line, type, criticality and location. Live Sensor Values show temperature, humidity, pressure, RPM, vibration and power with units/quality/freshness. Historical charts synchronize time crosshair and range/interval. Certificate Status includes state, serial/fingerprint, issuer, expiry and last rotation; private key never appears. Other exact elements: firmware version, connection status/history, geospatial/text location, related alerts, device logs, recent commands with state, Health Score with confidence/factors, and Maintenance History. Tables are used for alerts, logs, commands and maintenance; charts follow section 7. |
| Empty, loading, and error states | Each tab loads independently. Missing sensor value is “Unknown — no valid sample,” not zero. Stale/offline banner remains across tabs. No alerts/commands/maintenance states explain absence. Reconnecting preserves last good values with age. Command timeout remains Pending/Unknown until reconciled. Certificate error reveals no secret. Unauthorized tab is absent; unauthorized direct link shows safe denied state. |
| Responsive behavior | Tablet stacks context rail above a two-column sensor grid and uses horizontally scrollable tabs. Mobile places identity/status/freshness first, sensors in two columns, health next, then one chart at a time; each tab becomes an anchored section picker and destructive actions live in a clearly labeled overflow menu. |
| Rationale | Identity, freshness and health never scroll out of initial context. Tabs separate evidence types while synchronized charts and correlation links support diagnosis without opening multiple tools. |

### 9.8 Live Monitoring

| Requirement | Specification |
|---|---|
| Purpose | Observe current authorized device state with minimal latency while keeping live, stale, paused and disconnected conditions unmistakable. |
| Target users | Operator and Engineer primary; Manager monitors exceptions; Admin and Viewer inspect. |
| Components and layout | Sticky live-status bar shows connection, last message, visual update mode, selected factory/line, and device count. View toggle selects dense table or monitoring grid. Critical-only mode is prominent but clearly signals hidden normal devices. Grid cards show device/machine, connection, health, selected metric/value/unit, threshold, sparkline, quality and freshness. |
| User flow | Select factory/line -> choose metric -> monitor -> optionally pause visual updates -> identify change -> open Device Details or Alert Details -> return with context preserved. Reconnect triggers canonical refetch before “Live” returns. |
| Actions and buttons | Pause/resume visual updates, Critical only, Grid/Table, Choose metric, Open device, Open alert, Full-screen monitoring. Pause affects rendering only and explicitly says alert processing continues. |
| Widgets, filters, tables, charts, KPIs, cards | KPIs: Devices in view, Online, Stale, Critical, message rate. Filters: factory, line, machine, device type, connection, health, metric, quality, tags. Table includes sparkline and freshness. Grid cards are resizable only across predefined density choices to preserve hierarchy. |
| Empty, loading, and error states | Connecting uses a calm inline progress state. Reconnecting banner shows attempt and keeps aged values. No devices in scope differs from no filter results. A single device failure marks its card without stopping the feed. Permission loss safely clears live data. Browser resource pressure recommends reducing scope rather than silently dropping updates. |
| Responsive behavior | Tablet grid uses two cards per row; table keeps identity, health, value and age. Mobile defaults to critical/attention cards with a device count summary; full inventory is a virtualized list, filters use a bottom sheet, and visual pause remains thumb-reachable. |
| Rationale | Explicit visual pause and freshness prevent a frozen screen from appearing live. A user-selected primary metric avoids six tiny unreadable values per card. |

### 9.9 Analytics

| Requirement | Specification |
|---|---|
| Purpose | Explore environmental, energy, utilization, performance, alert, fault, health, and connectivity patterns with defensible context. |
| Target users | Manager and Engineer primary; Admin configures scope; Operator uses bounded presets; Viewer explores read-only. |
| Components and layout | Page header and query bar remain sticky. Tabs: Overview, Environment, Energy, Utilization, Performance, Alerts, Faulty Machines, Health, Connectivity. Query bar contains factory/machine/device, metric, time range, interval, comparison, timezone and Apply. A 12-column canvas uses a primary 8-column chart and 4-column summary/insight card, followed by full-width supporting charts and a data table. |
| User flow | Choose analytical question/tab -> set scope/range/interval -> Apply -> inspect quality and summary -> hover/synchronize/zoom -> compare prior period or peer -> open device/factory/alert -> optionally request report with the same query. Query state is URL-addressable when safe. |
| Actions and buttons | Apply, Reset, Save view, Compare, Annotate view where granted, View data table, Download chart image for internal use, Request report. Export retains scope/range/units/timezone metadata. |
| Widgets, filters, tables, charts, KPIs, cards | Uses every mapping in section 7.1: temperature line, humidity area, pressure line, power bar, device-status donut, factory radar plus score list, machine gauge, alert timeline, faulty-machine horizontal bar, energy stacked bar. KPIs vary by tab and include valid-sample count, missing-data rate, average/peak, change, threshold time and confidence where applicable. |
| Empty, loading, and error states | Chart-shaped skeletons preserve controls. No data explains scope/range and offers broader range if authorized. Sparse/low-quality data displays coverage and does not draw misleading interpolation. Partial series failure remains labeled. Query timeout allows narrower range/retry. Unknown health is never folded into healthy. |
| Responsive behavior | Tablet stacks the 8/4 regions and keeps query controls in a collapsible strip. Mobile uses an Apply-filters sheet, one full-width chart at a time, swipe-free tab selector, concise summary before plot, and a separate accessible data-table view. |
| Rationale | Question-based tabs and explicit Apply prevent an undifferentiated chart wall and unnecessary expensive queries. Visible quality and accessible tables make analytical conclusions auditable. |

### 9.10 Reports

| Requirement | Specification |
|---|---|
| Purpose | Request, schedule, track, securely download, and audit bounded report artifacts. |
| Target users | Super/Factory Admin and Manager manage permitted schedules; Engineer/Operator request predefined reports; Viewer accesses approved completed reports if policy grants. |
| Components and layout | Header with Generate report. KPI strip shows Queued, Processing, Completed today, Failed, and Expiring soon. Tabs separate Report jobs and Schedules. Enterprise table shows report name/type, scope, range/timezone, requester, state/progress, created/completed, expiry, size and actions. A right detail panel shows parameters, progress steps, checksum, access history and failure details. |
| User flow | Generate report -> choose type -> scope -> time/range -> format -> optional schedule -> review authorization/estimated size -> submit -> track asynchronously -> notification -> reauthorize -> receive short-lived download. Retry reuses visible parameters. |
| Actions and buttons | Generate report, Create schedule, Retry, Cancel queued job, Download, Copy checksum, Expire artifact, Edit/pause schedule. Download is absent until complete and always obtains a fresh authorized ticket. |
| Widgets, filters, tables, charts, KPIs, cards | Filters: state, type, factory, requester, created range, schedule, expiry. Table follows section 6. Progress detail is a stepper, not a chart. No analytical chart appears because this page manages artifacts rather than interpreting telemetry. |
| Empty, loading, and error states | First-use empty explains report types and offers Generate. Processing updates without row movement. Failure names safe cause and Retry. Expired item retains metadata but no download. Authorization change removes access. Download-link expiry offers Generate new link rather than rerunning the report. |
| Responsive behavior | Tablet retains name, scope, state, progress and completion. Mobile uses job cards with state/progress and a full-screen detail route; report creation is a step flow and download remains a deliberate labeled button. |
| Rationale | Separating asynchronous job state from analytical content prevents users from assuming a queued report is complete. Expiry and checksum make downloaded evidence trustworthy and secure. |

---

### 9.11 Alerts

| Requirement | Specification |
|---|---|
| Purpose | Triage, assign, acknowledge, investigate, and resolve operational alerts without losing event history. |
| Target users | Manager owns prioritization; Engineer investigates/resolves; Operator acknowledges and notes; Admin governs; Viewer reads. |
| Components and layout | Page header includes Open-alert count and last update. KPI cards show Critical open, High open, Unacknowledged, Assigned to me, and Breached response target. A required filter bar exposes Severity, Factory, Status, Time, and Device, with additional Assignee, Machine, Source and rule filters. View tabs switch among Alert Cards, Alert Table, and Alert Timeline. Desktop default is a 5-column alert list and 7-column preview panel; the canonical table is available for bulk review. |
| User flow | Arrive from notification/dashboard -> filters retain originating context -> scan severity/age/condition -> open preview -> acknowledge -> assign/investigate -> open full Alert Details -> resolve only after condition/reason review. Optimistic mutation is not used. |
| Actions and buttons | Required Acknowledge and Resolve; also Assign, Add comment, Suppress where permitted, Open device, Open details, Export, and approved bulk acknowledge/assign. Resolve dialog shows active-condition warning and requires resolution note/category. |
| Widgets, filters, tables, charts, KPIs, cards | Alert Cards include severity rail, title, condition, factory/machine/device, first/last seen, status, assignee and quick action. Alert Table adds ID, rule/source, occurrence count and updated time. Alert Timeline uses severity lanes and clustering. Filters are Severity, Factory, Status, Time, Device plus assignee/machine/source. |
| Empty, loading, and error states | “No open alerts” is a positive scoped state with time/factory context; no filter results offers Clear filters. Skeletons preserve list and preview. Live update does not reorder a row while keyboard focus is inside it; a New alerts banner lets the user refresh ordering. Version conflict shows latest status/assignee and keeps draft comment. Partial counts are labeled. |
| Responsive behavior | Tablet defaults to table/list with preview as drawer. Mobile uses stacked Alert Cards ordered by severity then age, sticky applied-filter count, full-screen filter sheet, and a full-route detail; Acknowledge is the visible quick action while Resolve remains in details to prevent accidental closure. |
| Rationale | Multiple views serve triage, comparison and temporal investigation without three separate modules. Stable ordering during interaction prevents an urgent live feed from moving the user’s target. |

### 9.12 Alert Details

| Requirement | Specification |
|---|---|
| Purpose | Present the complete condition, evidence, ownership, and immutable response history for one alert. |
| Target users | Manager, Engineer and Operator act within permission; Admin investigates governance; Viewer reads. |
| Components and layout | Header shows severity, status, title, alert ID, factory/machine/device, age and assignee. An 8-column evidence area contains condition summary, current value versus threshold, synchronized context chart, source rule, occurrence data and device snapshot. A 4-column action rail contains ownership, response target, Acknowledge/Assign/Resolve, and related links. Below, a full-width chronological timeline contains trigger, notifications, assignments, acknowledgements, comments, suppression and resolution. |
| User flow | Confirm target and active condition -> inspect evidence/freshness -> open device if deeper diagnosis is needed -> acknowledge -> assign/comment -> take external or approved platform action -> verify condition -> resolve with reason. Browser Back restores alert-list filters. |
| Actions and buttons | Acknowledge, Assign/reassign, Add comment, Open device, Open rule where permitted, Suppress with duration/reason, Resolve, Reopen where policy permits, Copy alert link, Export evidence. All mutations show actor/time in timeline after confirmation. |
| Widgets, filters, tables, charts, KPIs, cards | KPI/evidence cards: current value, threshold/duration, occurrences, time open, response target, device health. Chart: metric line with threshold band and trigger marker. No page-level filters; chart range presets provide evidence windows. Related alerts use a compact table. Timeline is mandatory. |
| Empty, loading, and error states | Loading prioritizes identity/status skeleton before chart. Missing telemetry explains evidence gap and marks health Unknown. Deleted/retired source remains referenced with immutable snapshot. Version conflict refreshes current status before resubmission. Active-condition warning does not forbid resolve if policy allows but makes consequence explicit. Denied state reveals no alert metadata. |
| Responsive behavior | Tablet stacks action rail above evidence when action is required. Mobile orders severity/status, primary action, condition/current value, evidence chart, context and timeline; timeline details expand on demand. Destructive/suppression dialogs become full-screen sheets. |
| Rationale | Evidence precedes closure, reducing reflexive resolution. The immutable timeline supports handoffs and post-incident review while keeping current ownership immediately visible. |

### 9.13 Audit Logs

| Requirement | Specification |
|---|---|
| Purpose | Query immutable evidence of privileged and security-relevant human/system actions. |
| Target users | Super Admin platform-wide; Factory Admin within scope; Manager/Engineer receive approved evidence; Operator sees own limited activity; Viewer only with auditor permission. |
| Components and layout | Restricted-access banner explains immutability and timezone. Filter/query bar sits above an enterprise table with timestamp, actor, action, resource type/name, factory, result, source, correlation ID and change summary. Selecting a row opens a detail drawer with before/after redacted fields, request context, related events and integrity metadata. |
| User flow | Set bounded time range -> filter actor/action/resource/result -> search correlation/reference -> inspect event -> follow related evidence -> export current authorized result if granted. Filters are encoded in a shareable authorized URL. |
| Actions and buttons | Apply filters, Clear, Save query, Copy correlation ID, Open related resource, Export controlled evidence. There are no edit or delete actions. |
| Widgets, filters, tables, charts, KPIs, cards | KPI cards: Events in range, Failed/denied actions, Security-relevant events, Unique actors. Filters: time, factory, actor, role, action category, resource type/ID, result, source, correlation ID. Table is primary; an optional event-count histogram supports query orientation but never replaces records. |
| Empty, loading, and error states | Empty range states that no matching events were recorded in selected authorized scope. Retention boundary explains earliest available date. Loading uses row skeletons. Query timeout suggests narrowing range. Redacted values explicitly say Redacted. Integrity/ingestion concern displays a critical evidence banner, never a fabricated empty table. |
| Responsive behavior | Tablet keeps time, actor, action, resource and result; details open full height. Mobile uses event cards with timestamp/actor/action/resource/result and a full detail route; complex filters are a full-screen sheet. Export remains permission-gated. |
| Rationale | A query-first, immutable table matches forensic work. Explicit redaction and retention prevent absence from being misread as evidence that an action did not happen. |

### 9.14 Device Logs

| Requirement | Specification |
|---|---|
| Purpose | Inspect authorized technical device events for diagnosis while protecting secrets and platform internals. |
| Target users | Engineer primary; Super/Factory Admin governance; Manager reads summarized evidence; Operator receives safe limited logs; Viewer only if granted. |
| Components and layout | Scope bar fixes factory/device and bounded time before querying. A histogram shows event volume by level; below, a virtualized log table displays timestamp, level, device, event category, safe message, correlation/trace reference and ingestion delay. A detail pane shows structured safe fields, adjacent events and links to alert/device. Live tail is off by default and visibly distinct when enabled. |
| User flow | Choose device/time -> select level/category -> search safe message/correlation ID -> inspect event -> expand context -> open related alert/device. Enable Live tail explicitly; Pause preserves current position. |
| Actions and buttons | Apply, Pause/resume live tail, Copy safe field/correlation ID, Add to incident note, Open related resource, Export bounded authorized logs. No command execution occurs from the log page. |
| Widgets, filters, tables, charts, KPIs, cards | KPIs: Event count, Error count, Warning count, Ingestion delay p95. Filters: factory, device, machine, time, level, event category, correlation ID, text search. Chart: event-volume histogram. Table uses monospace only for timestamp/IDs/message fragments. |
| Empty, loading, and error states | No events identifies scope/time and may suggest a broader window. Streaming reconnect retains paused data and marks a gap. Redacted values say Redacted by policy. Query error preserves filters. Excessive volume requires narrower scope; it never silently samples without disclosure. |
| Responsive behavior | Tablet stacks histogram and table; detail becomes drawer. Mobile defaults to timestamp/level/device/message cards with expandable safe fields; live tail is disabled until deliberately enabled and automatically pauses when the app is backgrounded. |
| Rationale | Bounded queries protect performance and reduce accidental data exposure. Separating observation from command execution prevents diagnostic context from becoming an unsafe control surface. |

### 9.15 Security Center

| Requirement | Specification |
|---|---|
| Purpose | Prioritize identity, certificate, device-trust and access-control risks and connect them to verifiable evidence. |
| Target users | Super Admin primary; Factory Admin sees assigned scope; Manager sees posture summary; Engineer sees relevant device findings; Operator sees urgent instructions; Viewer only with auditor scope. |
| Components and layout | Posture header shows scope, assessment freshness and overall band with explanation. KPI row: Open critical findings, Certificates expiring, Quarantined devices, Failed sign-ins, Privileged changes. A 7-column findings table/list pairs with a 5-column evidence panel. Supporting cards show certificate-expiry distribution, authentication-failure trend, quarantined devices, recent privileged changes and security guidance. |
| User flow | Scan critical count -> filter category/severity -> select finding -> inspect source evidence and affected resources -> assign owner -> open related device/user/audit event -> remediate outside or through permitted governed action -> disposition with reason -> verify posture refresh. |
| Actions and buttons | Assign, Change disposition, Add note, Open evidence, Open affected resource, Quarantine where authorized, Rotate certificate via Device Details, Export evidence, Open runbook. Findings are never deleted. |
| Widgets, filters, tables, charts, KPIs, cards | Filters: severity, status/disposition, factory, category, affected type, owner, first/last seen. Table: severity, finding, affected resource, factory, first/last seen, owner, state. Charts: expiry horizontal bands, failed-auth line, findings by category bar. Cards never expose keys, secrets or unnecessary topology. |
| Empty, loading, and error states | “No open findings” says assessment time and coverage, not “secure.” Stale assessment shows warning. Evidence unavailable retains finding and Retry. Permission-limited panels explain scope without naming excluded resources. Partial source failure does not reduce count to zero. |
| Responsive behavior | Tablet stacks evidence below findings. Mobile starts with critical KPIs and finding cards; evidence opens full route; dense posture charts become ranked lists with optional chart view. Critical action stays visible but requires confirmation. |
| Rationale | Findings lead to source evidence rather than a decorative security score. “No findings” is carefully worded because absence of detection is not proof of safety. |

### 9.16 Notifications

| Requirement | Specification |
|---|---|
| Purpose | Provide a durable personal inbox for operational alerts, reports, assignments, security notices and system outcomes. |
| Target users | All roles; content is recipient- and scope-specific. |
| Components and layout | Header shows unread count and Mark all read. A 4-column category list/count area pairs with an 8-column inbox on wide desktop. Notification rows/cards show unread marker, severity/category icon, title, concise source, factory/device context, relative and absolute time, delivery state where relevant, and primary destination. Preference summary links to Settings. |
| User flow | Open bell -> preview newest -> open inbox -> filter unread/category/severity/time -> select notification -> mark read automatically after content opens -> navigate to source -> return with position preserved. |
| Actions and buttons | Open source, Mark read/unread, Mark all read with confirmation for large counts, Dismiss where allowed, Update preferences. Mandatory security/critical routes may be marked read but not disabled in preferences. |
| Widgets, filters, tables, charts, KPIs, cards | KPIs/counts: Unread, Critical, Assignments, Reports ready. Filters: unread state, category, severity, factory, time. List/card is canonical; no chart is used because recency and actionability matter more than distribution. |
| Empty, loading, and error states | Empty inbox says new activity will appear here; zero unread celebrates quietly without hiding older items. Skeleton rows retain timestamps. Delivery-provider failure appears only where relevant and does not imply in-app notification failure. Deleted source shows a safe historical summary. |
| Responsive behavior | Tablet collapses categories into filter chips. Mobile is a single chronological card list; filter sheet and Mark all read live in header overflow; tapping the bell preview uses a bottom sheet. |
| Rationale | A durable inbox complements transient toasts and supports shift changes. Source navigation, not notification management, remains the dominant action. |

### 9.17 Settings

| Requirement | Specification |
|---|---|
| Purpose | Configure personal, factory and platform behavior within explicit inheritance and security bounds. |
| Target users | All users manage permitted personal settings; Manager/Factory Admin manage approved factory defaults; Super Admin manages platform policy. |
| Components and layout | A left section index and 9-column form area. Sections: Appearance, Locale/timezone/units, Data freshness/display, Notifications, Factory operational defaults, Alert defaults, Security/session policy, Retention, Integrations references. Every nonpersonal field shows source: Platform enforced, Factory inherited, or Custom override. Sticky footer appears only when unsaved changes exist. |
| User flow | Select section -> inspect current value/source -> change permitted field -> inline validate -> Review changes for policy-sensitive groups -> Save -> confirmation with version. Restore inherited/default shows exactly what will replace custom values. |
| Actions and buttons | Save changes, Discard, Restore inherited/default, Preview effect, View change history. Security/retention changes require reason and stronger confirmation; secrets are represented only by configured/not configured references. |
| Widgets, filters, tables, charts, KPIs, cards | Forms and policy cards are primary. Notification channel table lists category/channel/mandatory source. Retention summary card displays enforced minimum/maximum. No KPI or analytical chart is used because this is configuration, not monitoring. |
| Empty, loading, and error states | Settings skeleton preserves section index. Unsupported/denied section is omitted. Validation appears inline and in summary. Version conflict compares saved versus current and does not overwrite silently. Service error keeps draft locally for the session. Mandatory bound error explains the governing policy. |
| Responsive behavior | Tablet replaces left index with sticky section select. Mobile uses one section per route, full-width controls and a bottom sticky Save; policy source remains visible under every governed field. |
| Rationale | Visible inheritance prevents users from believing an ineffective local change overrides platform policy. Grouped, infrequent saves are safer than immediate switches for consequential settings. |

### 9.18 Profile

| Requirement | Specification |
|---|---|
| Purpose | Let a user understand identity/scope and manage safe personal preferences and sessions. |
| Target users | All roles; role and factory scope are read-only here. |
| Components and layout | Header has avatar/initials, name, email and role. Two-column desktop layout: Personal details and Preferences on the left; Assigned factories/permissions summary and Active sessions/security activity on the right. Notification preferences link to Settings. Session cards show device/browser, approximate location, created/last active, and current-session label. |
| User flow | Review identity/scope -> update name/timezone/display preference -> Save -> review sessions -> revoke another session or sign out all -> confirm current-session consequence. Access change directs to administrator rather than presenting an unusable control. |
| Actions and buttons | Edit profile, Save, Change password through identity flow, Revoke session, Sign out all other sessions, Sign out, Contact administrator. Role/scope values offer explanatory tooltip, not edit affordance. |
| Widgets, filters, tables, charts, KPIs, cards | Profile, scope, preference and session cards. Compact recent-security-activity list. No filters, KPI or charts because personal context is small and direct. |
| Empty, loading, and error states | Avatar falls back to initials. No extra sessions states that only the current session is active. Loading uses card skeletons. Revocation failure keeps session visible and offers Retry. Concurrent profile edit shows latest saved values. |
| Responsive behavior | Tablet and mobile stack identity, preferences, scopes, then sessions. Mobile session actions use explicit buttons rather than tiny overflow icons; current-session warning remains adjacent to destructive sign-out action. |
| Rationale | Keeping access read-only prevents self-escalation expectations. Session visibility provides useful security control without turning Profile into a platform administration page. |

### 9.19 User Management

| Requirement | Specification |
|---|---|
| Purpose | Govern human identities, roles, factory scopes and active sessions within grantor bounds. |
| Target users | Super Admin full scope; Factory Admin assigned factories. Manager may see read-only team assignment where policy grants; other roles do not see the route. |
| Components and layout | KPI row: Active users, Invited/pending, Disabled, Privileged, Sessions revoked recently. Filter bar and enterprise table show user, email, role, assigned factories, status, last sign-in, active sessions and actions. Detail drawer includes identity, roles/scopes, invitation/account state, sessions, recent activity and audit link. Create/edit uses step sections with a permission-impact summary. |
| User flow | Search email/name -> open user -> compare role/scope -> edit within grantor bounds -> review effective access -> save with reason -> optional revoke sessions -> verify audit event. Invite/create follows identity -> role -> factories -> review. |
| Actions and buttons | Add/invite user, Edit role/scope, Disable, Restore, Resend invite, Revoke sessions, Open audit events, Export authorized directory. Self-demotion/scope removal and last-Super-Admin changes show blocking or heightened warnings. |
| Widgets, filters, tables, charts, KPIs, cards | Filters: status, role, factory, invitation state, last-sign-in range. Table follows section 6. Effective-access card summarizes modules and factory scope in plain language. No chart is necessary; exact identity records matter more than aggregate visualization. |
| Empty, loading, and error states | Empty offers Add user only to eligible admins. No results offers Clear filters. Invite conflict avoids revealing out-of-scope membership. Version conflict compares current role/scope. Last active Super Admin rule blocks save with recovery guidance. Failed session revocation does not falsely report completion. |
| Responsive behavior | Tablet narrows the table and moves detail to full drawer. Mobile uses user cards with role/status/factories and full-screen edit steps; effective-access review is required before Save. |
| Rationale | An effective-access summary is easier to verify than raw permissions. Guardrails are placed before save because access mistakes have broad consequences. |

### 9.20 404 / Unavailable Route

| Requirement | Specification |
|---|---|
| Purpose | Recover safely when a route does not exist, was removed, or cannot be resolved without implying whether a protected resource exists. |
| Target users | Authenticated and unauthenticated users; available destinations depend on session. |
| Components and layout | Centered compact state card in the relevant shell. It shows a route icon, “Page not found,” a neutral explanation, correlation/reference when useful, and recovery actions. Authenticated shell remains visible only when session is valid. |
| User flow | Invalid route -> see neutral state -> Go to Dashboard or Go back -> optionally use global search. If authentication is required, Sign in replaces Dashboard. A protected unknown/denied resource uses the same safe wording where enumeration risk exists. |
| Actions and buttons | Primary: Go to Dashboard or Sign in. Secondary: Go back, Search, Contact support. |
| Widgets, filters, tables, charts, KPIs, cards | One state card; no operational widget, filter, table, chart or KPI is shown because fabricated context could mislead or disclose protected information. |
| Empty, loading, and error states | This is a terminal empty/error state and therefore has no loading skeleton. If route resolution is still occurring, the shell shows a brief neutral progress state before deciding; it does not flash 404 during session restoration. |
| Responsive behavior | The card spans at most 6 columns desktop and 12 mobile, stays above the fold, and uses full-width primary action on small screens. |
| Rationale | Neutral wording balances recovery with anti-enumeration. Keeping the valid authenticated shell provides orientation without pretending the missing page has data. |

---

## 10. Accessibility specification

ForgeSight targets **WCAG 2.2 Level AA** across authentication, shell, all pages, overlays, charts and exported report interfaces. Accessibility is a definition-of-done requirement, not a later theme adjustment.

### 10.1 Keyboard and focus

- A visible Skip to main content link is first in focus order. Landmarks identify navigation, header, main, search and complementary panels.
- All functionality works with keyboard alone. Logical focus follows reading order, not visual grid coordinates. No positive tab-index ordering is introduced.
- Focus uses the dedicated `#5EEAD4` ring and is never removed. Sticky headers do not obscure focused content.
- Sidebar arrows expand/collapse groups; Escape closes transient overlays; dialogs trap focus and return it to the invoker; table row selection does not steal focus after live refresh.
- Global search shortcut is documented and does not override a browser/assistive-technology command. Every shortcut has a menu-accessible alternative.
- Drag-only reordering is never required. Dashboard customization and column order offer keyboard move controls.

### 10.2 Screen readers and semantics

- One clear page heading names every route; section headings are hierarchical. Breadcrumbs and pagination expose current location/state.
- Native semantic controls and tables are the baseline. Names combine visible label, object and state, such as “Acknowledge critical alert Boiler-02 overheating.”
- Status is spoken as label plus age: “Offline, last seen 18 minutes ago.” Live regions are polite and rate-limited; rapidly changing telemetry is not continuously announced. Users can request the latest value on focus.
- Sort direction, selected rows, expanded panels, loading/busy state, validation links and asynchronous completion are programmatically exposed.
- Icons that duplicate visible text are decorative. Icon-only controls have concise accessible names; tooltips do not replace them.
- Canvas/SVG chart rendering has a concise text summary and a fully operable data table with series, timestamp, value, unit and quality.

### 10.3 Contrast, color, and readability

- Normal text and interactive boundaries meet at least 4.5:1 contrast; large text meets at least 3:1; focus indicators and meaningful graphics meet at least 3:1 against adjacent colors. Token combinations are tested rather than inferred from individual swatches.
- Color is never the sole signal. Severity uses icon, label and color; trends use arrow, signed value and description; chart series use line pattern/marker plus color where series may overlap.
- Text can resize to 200% and layout reflows at 400% zoom without loss of actions or information. Dense tables may use a labeled horizontal region when reflow would destroy relationships.
- The default body size is 14 px with 20 px line height and never falls below 12 px for meaningful UI text. Long identifiers can wrap/copy without pushing actions off-screen.

### 10.4 Forms, errors, and time-sensitive interaction

- Every field has a persistent label, instructions before entry where needed, required/optional status, programmatic description, and error tied to the field.
- Submit failure moves focus to an error summary whose links focus each invalid field. Correct values remain intact.
- Timeouts warn users before session expiry and offer an Extend session action. No operational form loses an unsaved draft without warning.
- Authentication errors avoid account enumeration while still explaining recovery. Destructive confirmations describe consequence and target; typed confirmation is reserved for exceptional irreversible operations and supports paste.
- Pointer gestures have single-pointer alternatives; targets meet 44 by 44 px on touch. Motion can be reduced, and no content flashes more than three times per second.

### 10.5 Chart and telemetry accessibility

Each chart answers a stated question and announces range, unit, key high/low/change, threshold breaches, missing-data percentage and last update. Keyboard users can move between meaningful points or open the data table; they are not forced through thousands of samples. Data quality and Unknown samples remain explicit. Machine Health gauge includes score, band, confidence and contributing factors in text. Factory radar includes a ranked dimension list because geometric area is not precise enough on its own.

### 10.6 Accessibility verification scenarios

1. A keyboard-only Operator signs in, selects a factory, finds a critical alert, acknowledges it, opens the device, pauses live visual updates and signs out without a pointer.
2. A screen-reader user identifies whether a device is Online, Stale, Offline or Unknown; reads the latest value with unit/freshness; then accesses the equivalent historical chart table.
3. At 400% zoom on a 1280 px viewport, a Manager can filter Alerts, open details, assign an Engineer and read the immutable timeline without hidden controls.
4. In reduced-motion and forced-color/high-contrast conditions, focus, selection, severity and loading remain distinguishable.
5. Validation, session timeout, report completion, live-feed reconnect and version conflict are announced once with an actionable recovery path.

---

## 11. Responsive adaptation matrix

The per-page behavior in section 9 is authoritative. This matrix provides a compact implementation check across every screen.

| Page | Desktop | Tablet | Mobile |
|---|---|---|---|
| Login | Brand field + 440 px card | Centered card | Single full-width card, compact brand |
| Forgot Password | Brand field + recovery card | Centered card | Single card, full-width action |
| Dashboard | Four-up KPIs, 8/4 analytics | Two-up KPIs, stacked chart | Exception-first single flow |
| Factory Management | Table + side detail | Reduced table + drawer | Priority factory cards |
| Machine Management | Dense table + asset drawer | Reduced table + drawer | Machine cards + step forms |
| Device Management | Dense table + saved views | Priority columns | Device cards + filter sheet |
| Device Details | 3/9 context/evidence + tabs | Stacked context + tabs | Identity, freshness, sensors, one chart |
| Live Monitoring | Grid/table with sticky live bar | Two-up grid | Attention cards, virtualized list |
| Analytics | Sticky query, 8/4 chart/summary | Stacked query/results | Filter sheet, one chart, table route |
| Reports | Job table + detail panel | Priority columns + drawer | Job cards + full-screen steps |
| Alerts | List/preview plus table/timeline | List + detail drawer | Alert cards + full detail route |
| Alert Details | 8/4 evidence/action | Stacked action/evidence | Severity, action, evidence, timeline |
| Audit Logs | Query table + detail | Reduced table + drawer | Event cards + detail route |
| Device Logs | Histogram + virtual table/detail | Stacked plot/table | Safe log cards, deliberate live tail |
| Security Center | Findings + evidence and posture | Stacked findings/evidence | Critical-first finding cards |
| Notifications | Category rail + inbox | Filter chips + inbox | Chronological card list |
| Settings | Section rail + form | Section selector + form | One section/route + sticky Save |
| Profile | Two-column cards | Stacked cards | Identity-to-sessions single flow |
| User Management | Table + access drawer | Reduced table + drawer | User cards + review steps |
| 404 | Compact centered state | Compact centered state | Full-width state/action |

Across tablet/mobile, factory scope, status, freshness, severity and the primary safe action are never moved behind overflow. Secondary exports, column controls and low-frequency administration may enter labeled overflow menus.

---

## 12. Low-fidelity wireframes

Wireframes show hierarchy and placement, not color or final copy. `NAV` represents the permission-filtered sidebar; bracketed labels represent interactive controls.

### 12.1 Login

```text
+--------------------------------------------------------------+
| FORGESIGHT                                    System status o |
| Industrial operations, trusted and observable                |
|                         +-------------------------------+    |
|  abstract factory map   | Sign in to ForgeSight         |    |
|  and secure data flow   | Work email [______________]   |    |
|                         | Password   [___________] [eye] |    |
|                         | [ ] Remember this device       |    |
|                         | [        Sign in          ]    |    |
|                         | Forgot password | Support      |    |
|                         +-------------------------------+    |
+--------------------------------------------------------------+
```

### 12.2 Forgot Password

```text
+--------------------------------------------------------------+
| FORGESIGHT                                                    |
|                         +-------------------------------+    |
|  secure recovery       | <- Back to sign in             |    |
|  context               | Reset your password            |    |
|                         | Work email [______________]    |    |
|                         | [ Send reset instructions ]    |    |
|                         | Eligible accounts receive mail |    |
|                         | Contact administrator          |    |
|                         +-------------------------------+    |
+--------------------------------------------------------------+
```

### 12.3 Dashboard

```text
+------+-------------------------------------------------------+
| NAV  | Dashboard  [All authorized v] [24h v] LIVE  Search [] |
|      | [Factories] [Machines] [Online/Offline] [CRITICAL]    |
|      | [Health gauge] [Today's alerts + Power] [Env avg]     |
|      | +--------------------------------+------------------+ |
|      | | Primary trend / quality       | Recent alerts    | |
|      | +--------------------------------+------------------+ |
|      | [Factory status] [Live device feed] [Recent activity] |
|      | Updated 8 sec ago; timezone and units                  |
+------+-------------------------------------------------------+
```

### 12.4 Factory Management

```text
+------+-------------------------------------------------------+
| NAV  | Factories                         [Create factory]     |
|      | [Active] [Maintenance] [Critical] [Average health]    |
|      | Search[] Status[v] Region[v] Health[v] [Compare]      |
|      | +------------------------------+--------------------+ |
|      | | Name | Status | Dev | Alert  | Factory detail     | |
|      | | Plant A  ON     18/20   1    | Profile / Health   | |
|      | | Plant B  MAINT  12/14   0    | Power / Team       | |
|      | +------------------------------+ Activity / Actions | |
+------+-------------------------------------------------------+
```

### 12.5 Machine Management

```text
+------+-------------------------------------------------------+
| NAV  | Machines                         [Register machine]    |
|      | [Total] [Healthy] [Attention] [Maintenance] [No dev]  |
|      | Search[] Factory[v] Line[v] Criticality[v] Health[v]  |
|      | +-------------------------------+-------------------+ |
|      | | Asset | Type | Health | Device| Machine detail    | |
|      | | B-02    Boiler  42      2     | Identity / gauge  | |
|      | | CNC-7   CNC     89      1     | Devices / work    | |
|      | +-------------------------------+ Alerts / history  | |
+------+-------------------------------------------------------+
```

### 12.6 Device Management

```text
+------+-------------------------------------------------------+
| NAV  | Devices                [Import CSV] [Register device]  |
|      | [Total] [Online] [Offline] [Critical] [Cert risk]     |
|      | Saved: [Needs attention v] Search ID/name/tag [____]  |
|      | Factory[v] Connection[v] Health[v] Certificate[v]     |
|      | ID     Machine  Conn   Health  Value   Cert  Last seen |
|      | DV-20  Boiler2  Online Critical 98 C   OK    4 sec     |
|      | DV-31  CNC7     Offline Unknown --     12d   18 min    |
+------+-------------------------------------------------------+
```

### 12.7 Device Details

```text
+------+-------------------------------------------------------+
| NAV  | Factories / Plant A / Boiler-02 / DV-20       [More]  |
|      | DV-20  ONLINE  CRITICAL  Health 42  Seen 4 sec ago    |
|      | [Overview][Telemetry][Alerts][Cert][Logs][Maintenance]|
|      | +--------------+------------------------------------+ |
|      | | Machine info | Temp 98C  Hum 61%  Press 8.2bar    | |
|      | | Location     | RPM 1450  Vib 9.1  Power 42kW      | |
|      | | Firmware     | Historical synchronized charts     | |
|      | | Certificate  | Alerts | Commands | Maintenance    | |
+------+-------------------------------------------------------+
```

### 12.8 Live Monitoring

```text
+------+-------------------------------------------------------+
| NAV  | Live Monitoring [Plant A v] CONNECTED  3 sec  [Pause] |
|      | [Devices 20] [Online 18] [Stale 1] [Critical 1]      |
|      | Metric [Temperature v] [Critical only] [Grid|Table]  |
|      | +----------------+ +----------------+ +-------------+ |
|      | | DV-20 CRITICAL | | DV-21 ONLINE  | | DV-22 STALE | |
|      | | 98 C / 4 sec   | | 34 C / 2 sec  | | 41 C / 62s  | |
|      | | ----spark----- | | ----spark---- | | ---spark---  | |
|      | +----------------+ +----------------+ +-------------+ |
+------+-------------------------------------------------------+
```

### 12.9 Analytics

```text
+------+-------------------------------------------------------+
| NAV  | Analytics   Overview Environment Energy Health ...    |
|      | Factory[v] Device[v] Metric[v] Range[v] Interval[v]   |
|      | Compare[v] Timezone IST                      [Apply]   |
|      | +--------------------------------+------------------+ |
|      | | Temperature line + thresholds  | Summary / quality| |
|      | |                                | Avg Peak Missing | |
|      | +--------------------------------+------------------+ |
|      | | Supporting chart + accessible data table           | |
+------+-------------------------------------------------------+
```

### 12.10 Reports

```text
+------+-------------------------------------------------------+
| NAV  | Reports                         [Generate report]      |
|      | [Queued] [Processing] [Complete today] [Failed]       |
|      | [Report jobs] [Schedules]  State[v] Type[v] Time[v]   |
|      | +-------------------------------+-------------------+ |
|      | | Name | Scope | State | Progress| Report detail     | |
|      | | Daily  PlantA  Ready   100%   | Parameters         | |
|      | | Energy PlantB  Run      62%   | Steps / checksum  | |
|      | +-------------------------------+ [Download]        | |
+------+-------------------------------------------------------+
```

### 12.11 Alerts

```text
+------+-------------------------------------------------------+
| NAV  | Alerts         [Critical 6] [Unack 9] [Assigned me 4] |
|      | Severity[v] Factory[v] Status[v] Time[v] Device[v]    |
|      | [Cards] [Table] [Timeline]                             |
|      | +--------------------------+-------------------------+ |
|      | | CRIT Boiler-02  12 min   | Over-temperature       | |
|      | | HIGH CNC-07     31 min   | Condition / threshold  | |
|      | | WARN Pump-04    44 min   | Assignee / evidence    | |
|      | +--------------------------+ [Acknowledge] [Resolve] | |
+------+-------------------------------------------------------+
```

### 12.12 Alert Details

```text
+------+-------------------------------------------------------+
| NAV  | Alerts / ALT-1042  CRITICAL  OPEN    Boiler-02        |
|      | +----------------------------------+----------------+ |
|      | | 98 C > 90 C for 8 min           | Owner: Unset   | |
|      | | Metric line -- trigger -- now    | SLA: 12 min   | |
|      | | Device snapshot / rule / quality | [Acknowledge] | |
|      | | Related alerts                   | [Assign]       | |
|      | +----------------------------------+ [Resolve]      | |
|      | Timeline: Trigger > Notify > Comment > Action         |
+------+-------------------------------------------------------+
```

### 12.13 Audit Logs

```text
+------+-------------------------------------------------------+
| NAV  | Audit Logs   Immutable evidence   Earliest: 90d       |
|      | Time[v] Factory[v] Actor[v] Action[v] Result[v]       |
|      | Search resource/correlation [___________] [Apply]     |
|      | +-----------------------------------+---------------+ |
|      | | Time | Actor | Action | Resource  | Event detail  | |
|      | | 10:42  Asha    UPDATE   DV-20     | Before/after  | |
|      | | 10:39  System  DENY     User-7    | Correlation   | |
|      | +-----------------------------------+ Related events| |
+------+-------------------------------------------------------+
```

### 12.14 Device Logs

```text
+------+-------------------------------------------------------+
| NAV  | Device Logs [Plant A v] [DV-20 v] [Last 1h v] [Apply]|
|      | [Events] [Errors] [Warnings] [Ingestion p95]          |
|      | Event volume histogram                 [Live tail off]|
|      | +-----------------------------------+---------------+ |
|      | | Time | Level | Device | Message   | Safe fields   | |
|      | | 10:42  ERROR   DV-20    timeout   | Correlation   | |
|      | | 10:41  INFO    DV-20    sample    | Related alert | |
|      | +-----------------------------------+---------------+ |
+------+-------------------------------------------------------+
```

### 12.15 Security Center

```text
+------+-------------------------------------------------------+
| NAV  | Security Center  Posture: ATTENTION  Assessed 2m ago  |
|      | [Critical] [Cert expiry] [Quarantined] [Failed login] |
|      | Severity[v] Category[v] Factory[v] Owner[v] State[v]  |
|      | +-------------------------------+-------------------+ |
|      | | Finding | Resource | Seen |   | Finding evidence  | |
|      | | CRIT cert expiry DV-20  1h   | Source / timeline | |
|      | | HIGH auth surge User-7  4h   | Owner / runbook   | |
|      | +-------------------------------+ [Assign][Open]    | |
+------+-------------------------------------------------------+
```

### 12.16 Notifications

```text
+------+-------------------------------------------------------+
| NAV  | Notifications  12 unread               [Mark all read]|
|      | +--------------+------------------------------------+ |
|      | | All       28 | * CRITICAL Boiler-02        2m     | |
|      | | Alerts    14 | * Report “Daily health” ready 8m   | |
|      | | Assigned   5 |   Device DV-31 recovered     14m   | |
|      | | Reports    4 |   Security finding assigned  22m   | |
|      | | Security   5 |                                    | |
|      | +--------------+------------------------------------+ |
+------+-------------------------------------------------------+
```

### 12.17 Settings

```text
+------+-------------------------------------------------------+
| NAV  | Settings                                              |
|      | +----------------+-----------------------------------+|
|      | | Appearance     | Data freshness                    ||
|      | | Locale & units | Stale after [60 sec]              ||
|      | | Notifications  | Source: Platform enforced         ||
|      | | Factory defaults| Offline after [180 sec]           ||
|      | | Security       | Source: Factory override          ||
|      | | Retention      |          [Discard] [Save changes] ||
|      | +----------------+-----------------------------------+|
+------+-------------------------------------------------------+
```

### 12.18 Profile

```text
+------+-------------------------------------------------------+
| NAV  | Profile                                               |
|      | [AS] Asha Singh  asha@example  Maintenance Engineer  |
|      | +---------------------------+-----------------------+ |
|      | | Personal details         | Assigned factories    | |
|      | | Timezone / display       | Effective role        | |
|      | | Notification preferences | Active sessions       | |
|      | | [Save profile]           | This device [Current] | |
|      | +---------------------------+ [Revoke others]       | |
+------+-------------------------------------------------------+
```

### 12.19 User Management

```text
+------+-------------------------------------------------------+
| NAV  | Users                               [Add user]         |
|      | [Active] [Pending] [Disabled] [Privileged]            |
|      | Search[] Role[v] Factory[v] Status[v]                  |
|      | +-------------------------------+-------------------+ |
|      | | User | Role | Factories | Seen| Effective access  | |
|      | | Asha   Engineer  Plant A   2m | Modules / scopes  | |
|      | | Ravi   Manager   Plant A,B 1h | Sessions/activity | |
|      | +-------------------------------+ [Edit] [Disable]  | |
+------+-------------------------------------------------------+
```

### 12.20 404 / Unavailable Route

```text
+------+-------------------------------------------------------+
| NAV  |                                                       |
|      |              +---------------------------+            |
|      |              |       Page not found      |            |
|      |              | The destination may have |            |
|      |              | moved or be unavailable. |            |
|      |              | [ Go to Dashboard ]      |            |
|      |              | [Go back] [Search]       |            |
|      |              +---------------------------+            |
+------+-------------------------------------------------------+
```

---

## 13. State, content, and trust model

### 13.1 Canonical data-state language

| State | Required presentation | Forbidden presentation |
|---|---|---|
| Live | “Live,” last update age, connection icon, configured freshness context | Unqualified green dot |
| Paused view | Persistent “Visual updates paused” banner and Resume; alerts continue | Frozen values that still say Live |
| Reconnecting | Attempt state, last good data with age, API availability note | Clearing all values to zero |
| Stale | Stale label, age, clock icon, configured reason; value remains visually secondary | Treating the last value as current |
| Offline | Offline label, last seen, connection-history link | Automatically calling machine health Critical unless rule says so |
| Unknown | Unknown label and specific evidence gap | Substituting zero, neutral gauge midpoint, or Healthy |
| Partial failure | Page/widget warning identifies missing source; returned data remains usable | Whole-page error when independent data is valid |
| Denied | Neutral access message, safe navigation and request-access guidance | Fetching then masking protected fields |
| Version conflict | Latest saved state, user draft, changed fields and safe resolution | Silent last-write-wins overwrite |

### 13.2 Writing standards

- Headings are nouns or outcomes; buttons use verb + object; status text uses plain language.
- Dates show local format with timezone; hover/focus reveals ISO UTC when evidence precision matters. Relative time is always paired with absolute time in details.
- Numbers use locale-aware separators, stable decimals based on sensor profile, and visible units. Unknown values use an em dash only when a nearby label explicitly says Unknown.
- Alerts name condition and asset: “Boiler-02 temperature above 90 °C,” not “Threshold exceeded.”
- Destructive dialog copy follows Target -> Consequence -> Preconditions -> Audit reason -> Explicit action.
- Avoid blame, alarmist punctuation, unexplained acronyms and claims such as “safe” or “healthy” without evidence coverage.

### 13.3 Permission presentation

If a user can view but not mutate, the action is normally absent and the page reads naturally as inspection. If an action is visible because it explains a workflow but has a temporary prerequisite, it is disabled with an adjacent reason and recovery. If the limitation is authorization, shared-link access returns a safe access page; no tooltip enumerates higher-privilege data. Export, bulk operations and direct links apply the same factory scope as the screen.

---

## 14. Design acceptance and frontend handoff

### 14.1 Required acceptance scenarios

- Every one of the six roles receives only its authorized navigation, actions, scope and data while retaining a coherent product experience.
- An Operator can identify estate state in under ten seconds and a critical condition from the first Dashboard viewport.
- A user can find an authorized device by exact ID/name/tag in under five seconds through global search.
- Live, paused, reconnecting, stale, offline, inactive, maintenance, critical and unknown states remain visually and programmatically distinct.
- Each of the 20 documented routes implements purpose, audience, components, layout, flow, actions, widgets/buttons, filters, tables/charts/KPIs/cards, empty/loading/error states and responsive behavior exactly as specified.
- Every chart includes unit, range, interval, quality, freshness, summary and accessible table. Every table includes search, sort, pagination, filters, column selection, sticky header and authorized export where applicable.
- Keyboard, screen reader, zoom, contrast, reduced-motion, touch-target, form-error and timeout scenarios in section 10 pass at WCAG 2.2 AA.
- High-impact actions show target, consequence and audit reason; success appears only after authoritative confirmation.
- Private keys, secrets, unauthorized resource names and immutable-audit mutation controls never appear.

### 14.2 Handoff package definition

The frontend team should convert this document into named design-system primitives, page frames and testable interaction states while preserving the approved architecture vocabulary and authorization boundaries. Visual design review should validate token contrast in rendered context; content design review should validate alert/risk wording; engineering review should validate each data contract, quality/freshness value and responsive priority before implementation begins. Any proposed deviation that changes information hierarchy, safety behavior, role access, data meaning or responsive priority requires a documented design decision and stakeholder approval.

This specification is the complete UI/UX design blueprint—containing no implementation code—ready for the frontend team to implement after Phase 2 approval.
