# PACE Website

**paceconsults.co** — Fractional digital advisory for lean businesses.

## What this is

An interactive entry experience that identifies a visitor's business type and surfaces specific operational gaps — before any conversation starts.

**Flow:** Business type → Sub-type → Gap reveal (Screen 3, coming soon)

## Running locally

No install needed. Just open `index.html` in any browser:

```bash
# macOS
open index.html

# Windows
start index.html

# Or drag the file into Chrome/Firefox
```

## Deploying to Vercel

```bash
npm i -g vercel
vercel
# Follow prompts, deploy in ~30 seconds
```

Then add `paceconsults.co` as a custom domain in the Vercel dashboard.

## Project structure

```
pace-website/
├── index.html              ← Entire app (HTML + CSS + JS, single file)
├── vercel.json             ← Vercel deployment config
├── .gitignore
├── README.md
└── PACE_SYSTEM_CONTEXT.md  ← Full system spec for AI-assisted dev sessions
```

## Build status

| Screen | Status |
|--------|--------|
| Screen 1 — 9 business categories | ✅ Complete |
| Screen 2 — SERVICE (12 icons) | ✅ Complete |
| Screen 2 — MANUFACTURING (12 icons) | ✅ Complete |
| Screen 2 — AGRICULTURE (12 icons) | ✅ Complete |
| Screen 2 — LOGISTICS (12 icons) | ✅ Complete |
| Screen 2 — FINANCE (12 icons) | ✅ Complete |
| Screen 2 — CONSTRUCTION (12 icons) | ✅ Complete |
| Screen 2 — RETAIL (12 icons) | ✅ Complete |
| Screen 2 — EDUCATION (12 icons) | ✅ Complete |
| Screen 2 — ENTERTAINMENT (12 icons) | ✅ Complete |
| Screen 3 — Gap Reveal | 🔲 Next |

## Tech

Pure HTML + CSS + JavaScript. No framework. No build step. No dependencies.
