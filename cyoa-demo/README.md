# Linguistics CYOA Demo

This folder contains a static desktop-first demo site for three linguistics pathways:

- `Lemmatization`
- `Pronoun Resolution`
- `Presuppositions`

The site is intentionally framework-free so it stays lightweight, reliable, and easy to deploy to GitHub Pages.

## Stack

- Static `HTML`
- Modular browser `JavaScript`
- One shared `CSS` design system
- No backend
- No database
- No build dependency required

## Local Run

From the repo root:

```bash
cd cyoa-demo
python3 -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

Using a local server is recommended because the site uses ES modules.

## Build

No build step is required.

The deployable site is the folder itself:

- `index.html`
- `css/`
- `js/`

If you want a separate publish artifact, copy the contents of `cyoa-demo/` into a publish directory such as `docs/`.

## GitHub Pages Deployment

### Option 1: Publish with a `docs/` folder

1. Copy the contents of `cyoa-demo/` into `docs/` at the repo root.
2. In GitHub, go to `Settings -> Pages`.
3. Set the source to `Deploy from a branch`.
4. Choose the branch you want, then choose `/docs`.

### Option 2: Publish with GitHub Actions

1. Keep `cyoa-demo/` as the source folder.
2. Add a Pages workflow that uploads `cyoa-demo/` as the static artifact.
3. In `Settings -> Pages`, set the source to `GitHub Actions`.

Because all links are relative and the site uses hash-based navigation, it is GitHub Pages-friendly without extra routing config.

## Where To Edit Content Later

Content and scores are separated from presentation so you can swap values without rewriting the UI.

### Site-wide landing content

- `js/data/site.js`

### Lemmatization pathway

- `js/data/lemmatization.js`

Edit these sections there:

- `introExamples`
- `grid`
- `bestRun`
- `subgroupTable`

### Pronoun resolution pathway

- `js/data/pronoun.js`

Edit these sections there:

- `englishSetup.results`
- `promptOptions`
- `lowResourceResults`
- `robustness`

### Presuppositions pathway

- `js/data/presuppositions.js`

Edit these sections there:

- `challenge`
- `promptCards`
- `prompts`
- `ranking`
- `classBalance`

## Presentation Layer

Shared UI and interaction logic lives in:

- `js/app.js`
- `js/components.js`
- `js/state.js`
- `css/styles.css`

## Notes On Current Assumptions

- The three walkthrough spec documents were treated as the source of truth for flow and teaching goals.
- The presuppositions pathway currently uses the 10 prompts named in the spec, even though the repo contains additional later files.
- The lemmatization subgroup comparison uses a shared `n = 300` slice so the subgroup lesson is a like-for-like model comparison and still preserves the spec's main conclusion that irregular forms are the hardest category across models.
