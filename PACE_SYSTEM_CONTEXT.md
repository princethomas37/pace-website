# PACE — Full System Context Document
> Drop this file into Cursor as project context. It captures every design decision, logic rule, data structure, user flow, animation system, and build state so development can resume exactly where it left off.

---

## 1. WHAT PACE IS

**PACE** is a fractional digital advisory consultancy — not a vendor, not an agency. It goes outbound with research-based, specific observations about what a client's operation is missing. It then solves those gaps across the full digital/operational ecosystem: websites, software, automation, AI, revenue operations, and marketing.

The name is a methodology acronym:
- **P** — Problem (identify the gap the client hasn't noticed)
- **A** — Architect (design the solution)
- **C** — Consult (advisory engagement)
- **E** — Execute (build or implement)

**Founder:** Prince (sole operator)  
**Domain:** `paceconsults.co`  
**Hosting:** Vercel (free tier)  
**Email:** Zoho (free tier)  
**Active clients:** General contractor in Ohio (fuel pump construction), real estate accounting firm in Houston.

Growth is reputation-driven, not geography-bound. Both domestic (US) and international clients are in scope.

---

## 2. THE WEBSITE — PURPOSE AND PHILOSOPHY

The PACE website is **not** a traditional landing page. It is an **interactive entry experience** that:

1. Forces the visitor to self-identify their business type
2. Then self-identify their specific sub-type
3. Then arrives at a "realization moment" — a gap reveal screen that surfaces specific, research-backed operational problems PACE has observed in their exact business type
4. Positions PACE as already knowing their world before they've said a word

This approach encodes the PACE brand promise directly into the UX: PACE comes in already knowing what's wrong. The website demonstrates that before a single conversation happens.

---

## 3. TECH STACK

| Layer | Choice | Reason |
|-------|--------|--------|
| Language | Vanilla HTML + CSS + JS | No build step, no framework overhead, deploys as a single file |
| Animations | Canvas 2D API (per-cell `requestAnimationFrame`) | Full control, no library weight, performant |
| Font | Inter (Google Fonts CDN) | Clean, modern, variable weight |
| Hosting | Vercel free tier | Zero-config deploy, CDN edge, HTTPS automatic |
| Email | Zoho free tier | Custom domain email (`hello@paceconsults.co`) |
| Domain | `paceconsults.co` | ~1,135 INR/year |

**Single-file architecture:** The entire interactive entry experience lives in one `pace.html` file. No bundler, no npm, no build pipeline. Deploy = push file to Vercel.

---

## 4. DESIGN SYSTEM

### Colors
```js
var PR = 'rgba(167,139,250,';   // Purple  — primary accent
var CY = 'rgba(34,211,238,';    // Cyan    — secondary accent
var WH = 'rgba(255,255,255,';   // White   — text / neutral strokes
```
Background: `#07071a` (near-black deep navy)

### Typography
- Font: **Inter**
- Weights used: 300, 400, 600, 700, 800, 900
- Category labels: `font-weight: 900; letter-spacing: 0.18–0.22em; text-transform: uppercase`
- Sub-labels: `font-weight: 400; letter-spacing: 0.08–0.1em; color: rgba(255,255,255,0.28–0.38)`
- Question headers: `font-weight: 900; letter-spacing: 0.18em; font-size: clamp(18px, 3.5vw, 34px)`

### Background
Three drifting radial gradient orbs (CSS animation, `pointer-events: none`):
- Orb 1: Purple, top-left, 560px, 22s drift cycle
- Orb 2: Blue, bottom-right, 420px, 27s drift cycle
- Orb 3: Deep purple, center, 320px, 19s drift cycle

### Canvas Icon Specs
- **Screen 1 (category icons):** `160 × 80px` canvas, displayed at `160 × 80px`
- **Screen 2 (sub-type icons):** `96 × 52px` canvas, displayed at `96 × 52px`

---

## 5. SCREEN ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│  SCREEN 1                                                   │
│  "WHAT DO YOU DO?"                                          │
│  3×3 grid — 9 business categories                          │
│  Each cell: canvas icon (160×80) + label + sub-label       │
│  → User clicks one → slide-left transition → SCREEN 2      │
└─────────────────────────────────────────────────────────────┘
         ↓ click on category
┌─────────────────────────────────────────────────────────────┐
│  SCREEN 2  (one per category, 9 total)                      │
│  "WHAT KIND OF [CATEGORY]?"                                 │
│  4×3 grid — 12 sub-types                                   │
│  Each cell: canvas icon (96×52) + label + sub-label        │
│  → User clicks one or more → [Screen 3 — NOT YET BUILT]   │
│  ← Back button (top-left) → slide-right back to Screen 1   │
└─────────────────────────────────────────────────────────────┘
         ↓ click on sub-type
┌─────────────────────────────────────────────────────────────┐
│  SCREEN 3  ← NOT YET BUILT                                 │
│  The "Gap Reveal" / Realization Moment                      │
│  Shows 3–5 specific operational gaps PACE has observed     │
│  in that exact business type + sub-type combination        │
│  CTA: "Let's talk" / book a call / contact form            │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. NAVIGATION LOGIC

```js
// State
var current = 'screen1';   // tracks which screen is visible

// Screen IDs
// Screen 1:  id="screen1"
// Screen 2s: id="s2-service", id="s2-manufacturing", id="s2-agriculture",
//            id="s2-logistics", id="s2-finance", id="s2-construction",
//            id="s2-retail", id="s2-education", id="s2-entertainment"

// CSS transition classes
.vis    → transform: translateX(0);     opacity: 1;  (visible)
.out-l  → transform: translateX(-100%); opacity: 0;  (exited left)
.out-r  → transform: translateX(100%);  opacity: 0;  (waiting right)

// Forward (Screen 1 → Screen 2)
navigateTo(key):
  1. Add .out-l to current screen
  2. Remove .out-r from target screen, add .vis
  3. Build grid 2 for that key (lazy — only builds DOM once)
  4. Show back button

// Back (Screen 2 → Screen 1)
goBack():
  1. Add .out-r to current Screen 2
  2. Remove .out-l from Screen 1, add .vis
  3. Hide back button

// Transition duration: 0.65s cubic-bezier(0.77, 0, 0.18, 1)
```

---

## 7. ANIMATION SYSTEM

### Core Rule
Icons animate **only on hover**. They freeze on `mouseleave` — they do not reset to `t=0`, they hold the last rendered frame.

### Implementation Pattern (both grids)
```js
var animT = 0;
var raf = null;

cell.addEventListener('mouseenter', function() {
  if (raf) cancelAnimationFrame(raf);
  function loop() {
    animT += 0.04;                          // ~60fps increment
    item.draw(ctx, canvasW, canvasH, animT);
    raf = requestAnimationFrame(loop);
  }
  loop();
});

cell.addEventListener('mouseleave', function() {
  if (raf) { cancelAnimationFrame(raf); raf = null; }
  // frame holds — no redraw
});
```

### At-Rest State
Each icon is drawn once at `t=0` when the cell is built. This gives a static but fully-rendered initial state.

### Draw Function Signature
```js
function dXxx(ctx, w, h, t) {
  ctx.clearRect(0, 0, w, w);
  // ... draw at time t
  // t increments by 0.04 per frame (~60fps)
  // use Math.sin(t * speed) for oscillation
  // use (t * speed) % 1 for looping progress
}
```

### Staggered Entry Animation
```js
// Grid 1: items fade+slide up with 75ms between each
setTimeout(function() { cell.classList.add('in'); }, 60 + idx * 75);

// Grid 2: tighter, 35ms between each
setTimeout(function() { cell.classList.add('in'); }, 30 + idx * 35);

// CSS:
.g1-item { opacity: 0; transform: translateY(18px); }
.g1-item.in { animation: up 0.5s ease forwards; }
@keyframes up { to { opacity: 1; transform: translateY(0); } }
```

---

## 8. DATA ARCHITECTURE

### Screen 1 — s1Data
```js
var s1Data = [
  { name: 'SERVICE',       sub: 'Any service business',  key: 'service',       draw: dService       },
  { name: 'MANUFACTURING', sub: 'Build or make things',  key: 'manufacturing', draw: dManufacturing },
  { name: 'AGRICULTURE',   sub: 'Grow or produce',       key: 'agriculture',   draw: dAgriculture   },
  { name: 'LOGISTICS',     sub: 'Move or ship things',   key: 'logistics',     draw: dLogistics     },
  { name: 'FINANCE',       sub: 'Money and information', key: 'finance',       draw: dFinance       },
  { name: 'CONSTRUCTION',  sub: 'Build or develop',      key: 'construction',  draw: dConstruction  },
  { name: 'RETAIL',        sub: 'Sell products',         key: 'retail',        draw: dRetail        },
  { name: 'EDUCATION',     sub: 'Teach or train',        key: 'education',     draw: dEducation     },
  { name: 'ENTERTAINMENT', sub: 'Music, media, content', key: 'entertainment', draw: dEntertainment },
];
```

### Screen 2 — s2Data Structure
```js
var s2Data = {
  [key]: [
    { n: 'DISPLAY NAME', s: 'sub-label text', draw: functionRef },
    ...  // 12 items per category
  ]
}
```

### Screen 2 Sub-type Catalogue

**SERVICE (12):** IT & TECH, CONSULTING, LEGAL, ACCOUNTING, MARKETING, HEALTHCARE, STAFFING, CLEANING, SECURITY, HOSPITALITY, FOOD SERVICE, CREATIVE

**MANUFACTURING (12):** FOOD & BEV, ELECTRONICS, TEXTILES, CHEMICALS, METAL & STEEL, AUTOMOTIVE, FURNITURE, MEDICAL, CONSTRUCTION, PLASTICS, PRINT & PAPER, AGRI-PROC

**AGRICULTURE (12):** CROP FARMING, LIVESTOCK, DAIRY, POULTRY, AQUACULTURE, HORTICULTURE, ORGANIC, PROCESSING, PLANTATION, SEED SUPPLY, IRRIGATION, EXPORT/TRADE

**LOGISTICS (12):** ROAD/TRUCKING, AIR FREIGHT, SEA/OCEAN, RAIL, WAREHOUSING, LAST MILE, COLD CHAIN, CUSTOMS, SUPPLY CHAIN, MOVING, E-COMM FULFIL, FREIGHT FWDG

**FINANCE (12):** BANKING, INSURANCE, INVESTMENT, ACCOUNTING, FINTECH, LENDING, WEALTH MGMT, PAYMENTS, CRYPTO, RISK, TRADING, MICROFINANCE

**CONSTRUCTION (12):** RESIDENTIAL, COMMERCIAL, INFRASTRUCTURE, ELECTRICAL, PLUMBING, INTERIOR, RENOVATION, DEMOLITION, REAL ESTATE, CIVIL ENG, ENVIRONMENTAL, FUEL/ENERGY

**RETAIL (12):** APPAREL, ELECTRONICS, GROCERY, HARDWARE, PHARMACY, FURNITURE, JEWELRY, SPORTING, E-COMMERCE, AUTO PARTS, BOOKS/STAT, HOME DECOR

**EDUCATION (12):** K-12, HIGHER ED, VOCATIONAL, ED-TECH, CORP TRAINING, TUTORING, LANGUAGE, TEST PREP, ARTS & MUSIC, SPORTS, EARLY CHILD, SPECIAL ED

**ENTERTAINMENT (12):** MUSIC, FILM & VIDEO, GAMING, LIVE EVENTS, STREAMING, SOCIAL MEDIA, PUBLISHING, PHOTOGRAPHY, ANIMATION, THEATRE, SPORTS MEDIA, ADVERTISING

---

## 9. DRAW FUNCTION REGISTRY

### Screen 1 — Category Icons (160×80)
| Function | Category | What it shows |
|----------|----------|---------------|
| `dService()` | SERVICE | Two figures handshaking, data nodes arc between them |
| `dManufacturing()` | MANUFACTURING | 3-gear system + conveyor belt with boxes + sparks |
| `dAgriculture()` | AGRICULTURE | Plant growing from soil, swaying, blooming petals |
| `dLogistics()` | LOGISTICS | Truck moving right with rolling wheels + motion lines |
| `dFinance()` | FINANCE | Candlestick chart, 6 candles, moving average, up arrow |
| `dConstruction()` | CONSTRUCTION | Building being constructed + crane with swinging load |
| `dRetail()` | RETAIL | Shopping bag with handle pulse + sparkle |
| `dEducation()` | EDUCATION | Open book with mortarboard floating above |
| `dEntertainment()` | ENTERTAINMENT | Equalizer bars + floating music note |

### Screen 2 — SERVICE Sub-types (96×52)
| Function | Sub-type | Animation |
|----------|----------|-----------|
| `ds2IT()` | IT & TECH | Monitor with scrolling code lines + blinking cursor |
| `ds2Consulting()` | CONSULTING | Clipboard with staggered checkmarks appearing |
| `ds2Legal()` | LEGAL | Scales of justice rocking, pans rising/falling |
| `ds2Accounting()` | ACCOUNTING | Ledger two-column with numbers ticking up |
| `ds2Marketing()` | MARKETING | Megaphone with expanding signal rings |
| `ds2Healthcare()` | HEALTHCARE | Medical cross + ECG heartbeat line |
| `ds2Staffing()` | STAFFING | Org-chart nodes, dots traveling edges |
| `ds2Cleaning()` | CLEANING | Spray bottle with mist dots + floating bubbles |
| `ds2Security()` | SECURITY | Shield pulsing glow + padlock with keyhole |
| `ds2Hospitality()` | HOSPITALITY | Hotel building + lit windows + pulsing gold stars |
| `ds2FoodService()` | FOOD SERVICE | Cloche dome with curling steam wisps |
| `ds2Creative()` | CREATIVE | Pen tool drawing a bezier path + color palette |

### Screen 2 — MANUFACTURING Sub-types (96×52)
| Function | Sub-type | Animation |
|----------|----------|-----------|
| `dm2FoodBev()` | FOOD & BEV | Cans on conveyor + fill nozzle dripping |
| `dm2Electronics()` | ELECTRONICS | PCB with traces, blinking pads, signal pulse |
| `dm2Textiles()` | TEXTILES | Loom weave grid + shuttle moving across rows |
| `dm2Chemicals()` | CHEMICALS | Flask with liquid, bubbles rising, steam |
| `dm2Metal()` | METAL & STEEL | I-beam + welding torch arc + sparks |
| `dm2Automotive()` | AUTOMOTIVE | Car silhouette + spinning wheels + motion lines |
| `dm2Furniture()` | FURNITURE | Chair profile + wood-grain shimmer |
| `dm2Medical()` | MEDICAL | Syringe with plunger + fill + cross badge |
| `dm2ConstrMat()` | CONSTRUCTION | Bricks stacking in bond pattern, rows fade in |
| `dm2Plastics()` | PLASTICS | Injection mold cycling open→inject→close |
| `dm2PrintPaper()` | PRINT & PAPER | Rollers rotating, paper feeding with print dots |
| `dm2AgriProc()` | AGRI-PROC | Millstone spinning + grain falling + flour bag |

### Screen 2 — AGRICULTURE Sub-types (96×52)
| Function | Sub-type | Animation |
|----------|----------|-----------|
| `da2CropFarming()` | CROP FARMING | 7 wheat stalks swaying, grain heads with petals |
| `da2Livestock()` | LIVESTOCK | Cow silhouette with swishing tail + spots |
| `da2Dairy()` | DAIRY | Milk bottle fill level oscillating + drip |
| `da2Poultry()` | POULTRY | Egg in nest wobbles, cracks, chick peeks out |
| `da2Aquaculture()` | AQUACULTURE | 2 fish swimming in arcs, tail wag, bubbles |
| `da2Horticulture()` | HORTICULTURE | Fruit tree with swaying branches, ripening fruit |
| `da2Organic()` | ORGANIC | Leaf swaying with pulsing cert badge + checkmark |
| `da2Processing()` | PROCESSING | Jars on conveyor, label arm applies label |
| `da2Plantation()` | PLANTATION | Bush rows on hillside with picker figure |
| `da2SeedSupply()` | SEED SUPPLY | Packet pouring seeds + sprout growing |
| `da2Irrigation()` | IRRIGATION | Spinning sprinkler with water arc droplets |
| `da2ExportTrade()` | EXPORT/TRADE | Globe spinning with trade route arcs |

### Screen 2 — LOGISTICS Sub-types (96×52)
| Function | Sub-type | Animation |
|----------|----------|-----------|
| `dl2Road()` | ROAD/TRUCKING | Semi-truck rolling, spinning wheels, exhaust smoke |
| `dl2Air()` | AIR FREIGHT | Cargo plane banking + bobbing, engine trails |
| `dl2Sea()` | SEA/OCEAN | Cargo ship on waves, stacked containers, smoke |
| `dl2Rail()` | RAIL | Locomotive on tracks, telegraph poles passing |
| `dl2Warehousing()` | WAREHOUSING | Shelving racks + forklift scanning/lifting |
| `dl2LastMile()` | LAST MILE | Delivery scooter with rider + package on rack |
| `dl2ColdChain()` | COLD CHAIN | Refrigerated container, snowflakes, temp gauge |
| `dl2Customs()` | CUSTOMS | Document stack + stamp descending + ink approval |
| `dl2SupplyChain()` | SUPPLY CHAIN | 4-node pipeline, dots traveling, KPI bar |
| `dl2Moving()` | MOVING | Dolly with 4 stacked boxes rolling, motion lines |
| `dl2EComm()` | E-COMM FULFIL | Box with flaps, scanner beam sweeping barcode |
| `dl2FreightFwd()` | FREIGHT FWDG | Ship/truck/plane icons cycling with mode label |

### Screen 2 — FINANCE, CONSTRUCTION, RETAIL, EDUCATION, ENTERTAINMENT
**Status: Text-only (no draw functions yet). Same pattern applies — add draw refs and 12 functions per category.**

---

## 10. BUILD STATUS

### ✅ COMPLETE
- Screen 1: All 9 category cells with canvas icons, hover animation, staggered entry
- Screen 2 HTML shells: All 9 screens exist in DOM (`id="s2-[key]"`)
- Screen 2 Icons: SERVICE (12/12), MANUFACTURING (12/12), AGRICULTURE (12/12), LOGISTICS (12/12)
- Navigation: Slide-left/slide-right transitions, back button
- Background: 3-orb drifting glassmorphism
- Mobile: 2-column collapse on screens < 580px
- `buildGrid2()` upgraded to mount canvas + hover animation when `draw` ref exists
- Helper functions: `drawGear()`, `drawFish()`, `drawStar()`

### 🔲 IN PROGRESS / TODO

#### Immediate Next Steps
1. **Screen 2 icons — FINANCE** (12 sub-types): BANKING, INSURANCE, INVESTMENT, ACCOUNTING, FINTECH, LENDING, WEALTH MGMT, PAYMENTS, CRYPTO, RISK, TRADING, MICROFINANCE
2. **Screen 2 icons — CONSTRUCTION** (12): RESIDENTIAL, COMMERCIAL, INFRASTRUCTURE, ELECTRICAL, PLUMBING, INTERIOR, RENOVATION, DEMOLITION, REAL ESTATE, CIVIL ENG, ENVIRONMENTAL, FUEL/ENERGY
3. **Screen 2 icons — RETAIL** (12): APPAREL, ELECTRONICS, GROCERY, HARDWARE, PHARMACY, FURNITURE, JEWELRY, SPORTING, E-COMMERCE, AUTO PARTS, BOOKS/STAT, HOME DECOR
4. **Screen 2 icons — EDUCATION** (12): K-12, HIGHER ED, VOCATIONAL, ED-TECH, CORP TRAINING, TUTORING, LANGUAGE, TEST PREP, ARTS & MUSIC, SPORTS, EARLY CHILD, SPECIAL ED
5. **Screen 2 icons — ENTERTAINMENT** (12): MUSIC, FILM & VIDEO, GAMING, LIVE EVENTS, STREAMING, SOCIAL MEDIA, PUBLISHING, PHOTOGRAPHY, ANIMATION, THEATRE, SPORTS MEDIA, ADVERTISING

#### Screen 3 — Gap Reveal (NOT STARTED)
See Section 12 below.

#### Post-Screen-3
- Pricing model integration
- Full website beyond the entry experience
- Contact / booking flow

---

## 11. USER JOURNEY — COMPLETE FLOW

```
[User lands on paceconsults.co]
        │
        ▼
[SCREEN 1 loads]
  Background orbs drift slowly
  "WHAT DO YOU DO?" fades in
  9 category cells stagger up (60ms + 75ms × index)
  Each cell: canvas icon drawn at t=0
        │
        │  User hovers a cell
        │  → animT starts incrementing (0.04/frame)
        │  → canvas redraws each frame
        │  User moves mouse away
        │  → RAF cancelled, frame frozen
        │
        │  User CLICKS a category (e.g. LOGISTICS)
        ▼
[SCREEN 1 slides left, SCREEN 2 "s2-logistics" slides in from right]
  Back button appears (top-left, 38px circle)
  "WHAT DO YOU MOVE?" header fades in
  12 sub-type cells stagger up (30ms + 35ms × index)
  Each cell: 96×52 canvas icon drawn at t=0
        │
        │  User hovers a sub-type cell
        │  → same hover/freeze animation pattern
        │
        │  User clicks BACK
        │  → Screen 2 slides right, Screen 1 slides back in
        │  → Back button hides
        │
        │  User CLICKS a sub-type (e.g. COLD CHAIN)
        ▼
[SCREEN 3 — NOT YET BUILT]
  Transition: slide-left (Screen 2 exits left, Screen 3 enters from right)
  State captured: { category: 'logistics', subtype: 'cold-chain' }
  Shows 3–5 gap observations specific to that combination
  CTA appears: "Let's talk" / "Book a 30-min call"
```

---

## 12. SCREEN 3 — DESIGN SPEC (Not Built)

### Purpose
The "realization moment." The visitor has self-identified. Now PACE demonstrates it already knows their world.

### Content Model
Each `category + subtype` combination maps to 3–5 gap observations. Example for `logistics + cold-chain`:

```
We've seen cold-chain operators lose 12–18% margin to:

  ◎  No real-time temp breach alerting across handoff points
  ◎  Carrier compliance tracked in spreadsheets, not systems
  ◎  Last-mile proof-of-delivery gaps creating dispute backlogs
  ◎  Customer-facing tracking portals that are 3rd-party white-labels
     with your competitors' branding in the footer

Sound familiar?
[Let's talk →]
```

### UX Rules for Screen 3
- Each gap observation enters with a staggered reveal (one by one, ~300ms apart)
- The tone is direct, specific, non-salesy — reads like a colleague who's seen this before
- No generic claims ("we help businesses grow") — every bullet is industry-specific
- CTA: Primary = "Book a 30-min call" (links to Calendly or similar) / Secondary = "See how we work"
- Back button stays visible (same pattern as Screen 2)
- State must pass through: which `category` + which `subtype` was selected

### State Passing Pattern
```js
// When user clicks a sub-type in Grid 2:
var userSelection = { category: currentCategoryKey, subtype: item.key };
navigateToScreen3(userSelection);
```

### Gap Content Architecture
```js
var gapData = {
  'logistics-cold-chain': [
    { headline: 'Temp breach alerting', detail: '...' },
    { headline: 'Carrier compliance', detail: '...' },
    ...
  ],
  'service-it': [...],
  // 9 categories × 12 sub-types = 108 gap sets total
}
```

---

## 13. CSS CLASS REFERENCE

```css
/* Screens */
.screen          → fixed, full-viewport, flex column centered
.screen.vis      → translateX(0), opacity 1, pointer-events all
.screen.out-l    → translateX(-100%), opacity 0, pointer-events none
.screen.out-r    → translateX(100%), opacity 0, pointer-events none

/* Grid 1 */
.grid1           → CSS grid, repeat(3, 1fr), width min(870px, 92vw)
.g1-item         → flex column, align center, cursor pointer
.g1-item.in      → animation: up 0.5s ease forwards
.g1-item canvas  → 160×80px
.g1-name         → font-size clamp(9px, 1.1vw, 11px), weight 800, spacing 0.22em
.g1-sub          → font-size clamp(7px, 0.9vw, 9px), weight 400, opacity 0.32

/* Grid 2 */
.grid2           → CSS grid, repeat(4, 1fr), width min(880px, 94vw)
.g2-item         → flex column, align center, cursor pointer
.g2-item.in      → animation: up 0.4s ease forwards
.g2-item canvas  → 96×52px
.g2-name         → font-size clamp(8px, 0.95vw, 10px), weight 800, spacing 0.18em
.g2-sub          → font-size clamp(7px, 0.8vw, 8.5px), weight 400, opacity 0.28

/* Back button */
.back-btn        → fixed top-left, 38px circle, background rgba(255,255,255,0.06)
.back-btn.show   → opacity 1, pointer-events all

/* Mobile breakpoint: 580px */
.grid1, .grid2 → repeat(2, 1fr) on mobile
.g1-item canvas → 110×55px on mobile
```

---

## 14. JS FUNCTION REFERENCE

```js
// ── GRID BUILDERS ──
buildGrid1()              // Builds Screen 1 DOM, draws icons at t=0, attaches hover
buildGrid2(key)           // Builds Screen 2 DOM for given key (lazy, runs once)

// ── NAVIGATION ──
navigateTo(key)           // Screen 1 → Screen 2[key], shows back button
goBack()                  // Screen 2 → Screen 1, hides back button

// ── HELPERS ──
drawGear(ctx, x, y, r, teeth, color, lineWidth)
drawFish(ctx, x, y, direction, color, size, t)
drawStar(ctx, x, y, r, alpha)

// ── LIFECYCLE ──
document.addEventListener('DOMContentLoaded', buildGrid1)
```

---

## 15. HTML DOM STRUCTURE

```html
<body>
  <div class="orbs">
    <div class="orb orb1"></div>
    <div class="orb orb2"></div>
    <div class="orb orb3"></div>
  </div>

  <button class="back-btn" id="backBtn">← SVG arrow</button>

  <!-- Screen 1 -->
  <div class="screen vis" id="screen1">
    <div class="question"><h2>WHAT DO YOU DO?</h2><p>select your business type to begin</p></div>
    <div class="grid1" id="grid1">
      <!-- 9 .g1-item cells built by buildGrid1() -->
    </div>
  </div>

  <!-- 9 Screen 2 shells (one per category key) -->
  <div class="screen out-r" id="s2-service">
    <div class="question"><h2>WHAT KIND OF SERVICE?</h2><p>select all that apply</p></div>
    <div class="grid2" id="g2-service">
      <!-- 12 .g2-item cells built by buildGrid2('service') on first navigation -->
    </div>
  </div>
  <!-- ... s2-manufacturing, s2-agriculture, s2-logistics, s2-finance,
           s2-construction, s2-retail, s2-education, s2-entertainment -->

  <!-- Screen 3 shell (not yet in DOM) -->
  <!-- <div class="screen out-r" id="screen3"> ... </div> -->
</body>
```

---

## 16. ADDING NEW DRAW FUNCTIONS — PATTERN

To add icons for a new category (e.g. FINANCE), follow this exact pattern:

```js
// Step 1: Define all 12 draw functions ABOVE the DATA block
// Use the `function` keyword (not const/let) so they hoist
function df2Banking(ctx, w, h, t) {
  ctx.clearRect(0, 0, w, h);
  var cx = w/2, cy = h/2;
  // ... draw at time t (96×52 canvas)
  // t increments 0.04/frame; at-rest state = t=0
}
// ... df2Insurance, df2Investment, etc.

// Step 2: Wire into s2Data
finance: [
  { n: 'BANKING',    s: 'Retail, commercial', draw: df2Banking    },
  { n: 'INSURANCE',  s: 'Life, general',      draw: df2Insurance  },
  // ...
],

// Step 3: No other changes needed — buildGrid2() handles canvas creation
//         and hover animation automatically when item.draw exists
```

---

## 17. DEPLOYMENT

```bash
# Current deploy target: Vercel free tier
# Project connected to: paceconsults.co

# To deploy:
# 1. Log into Vercel dashboard
# 2. Upload pace.html as output (or push to connected GitHub repo)
# 3. Vercel auto-assigns HTTPS + CDN edge

# File location: pace.html (single file, self-contained)
# No build step, no package.json, no node_modules
```

---

## 18. WHERE WE LEFT OFF (Resume Point)

**Last completed session:**
- Screen 2 LOGISTICS icons: All 12 functions written and wired into `s2Data.logistics`
- `pace.html` is the working file at `/mnt/user-data/outputs/pace.html`

**Immediate next task:**
Add Screen 2 icons for **FINANCE** — 12 sub-types:
1. `df2Banking` — Bank columns/vault with pulsing safe dial
2. `df2Insurance` — Umbrella covering assets in rain
3. `df2Investment` — Portfolio pie chart with animated slice expand
4. `df2Accounting` — Ledger (same pattern as ds2Accounting but finance-flavored)
5. `df2Fintech` — Mobile phone with payment tap + NFC rings
6. `df2Lending` — Coins stack with growth arrow
7. `df2WealthMgmt` — Diamond with facet gleam animation
8. `df2Payments` — Card swipe + contactless wave
9. `df2Crypto` — Coin with blockchain links + hash pulse
10. `df2Risk` — Shield + scales with warning pulse
11. `df2Trading` — Dual-ticker tape + candlestick (smaller version of main finance icon)
12. `df2Microfinance` — Hands cupping a small coin + growth sprout

**Then:** CONSTRUCTION → RETAIL → EDUCATION → ENTERTAINMENT

**Then:** Screen 3 — Gap Reveal design + content architecture (108 gap sets across 9×12)

---

## 19. KEY DECISIONS — DO NOT UNDO

These are locked decisions from prior design sessions:

| Decision | Rule |
|----------|------|
| Aesthetic | Deep navy/purple glassmorphism, drifting orbs |
| Font | Inter only, no other fonts |
| Grid 1 layout | 3×3, NO bounding rectangles around cells |
| Grid 2 layout | 4×3, same no-border rule |
| Transitions | Slide-left forward, slide-right back. Screen exits left, next enters from right |
| Icon hover | Animate on mouseenter, FREEZE (not reset) on mouseleave |
| Mobile | Grids collapse to 2 columns at 580px |
| Canvas approach | Vanilla Canvas 2D API — no libraries |
| File structure | Single HTML file — no framework, no build step |
| Color palette | PR (purple), CY (cyan), WH (white) — no other accent colors |
| Brand tone | Outbound, research-based, specific observations. Never generic. |

---

*End of PACE System Context Document*
*Last updated: After Screen 2 LOGISTICS icons completion*
