# Handover: automate.pakshiraj.me (public site)

How the public site in this repository is built and maintained. Written for a future maintainer (human or AI agent) picking it up cold. Last updated 21 Oct 2026.

---

## 1. What this repo is

Source of the static site served at **automate.pakshiraj.me**, hosted free on GitHub Pages. There is no build step and no CI: pushing to `main` triggers the GitHub Pages deploy, which typically takes 1-2 minutes.

Repository contents:

| Path | Purpose |
|---|---|
| `index.html` | The entire site: one self-contained page (~870 KB, minified) with inline CSS and JavaScript. Every view, style and interaction lives here. |
| `CNAME` | Maps the GitHub Pages deployment to the custom domain. |
| `generate_travel.py` | Regenerates only the Travel view's markup inside `index.html` from an approved visited-country projection (see section 4). |
| `README.md` | Repo stub. |

## 2. index.html anatomy

- **Single-page app with hash-routed views.** The landing page is a tile grid; each tile routes to a view identified by a `data-view` attribute (`#ai-news`, `#ai-builders`, `#booklog`, `#races`, `#travel`, `#implemented`, `#ideas`, `#jarvis`, and others).
- **Tiles are labelled Public or Private.** Private tiles follow one locked pattern: a `data-private-tile` attribute and a generic "visible only to the owner" dialog. They carry no data, no links and no destinations in the bundle - the locked tile is the entire implementation.
- **The golden rule: nothing private ever appears in this file.** No personal data, no private URLs, no links to owner-only content anywhere in the bundle. Check this on every change.
- **AI news view** (`#ai-news`): dated scan groups ("Scanned 21 Oct 2026, 07:00 Dubai"), newest on top, at most 5 items plus at most 1 deep pick per scan. Never pad a slate to fill slots.
- **AI Builders view** (`#ai-builders`): cards (`<details class="find">`) in a filterable grid, strictly newest-first. Every card carries a date pill: exact dates plain ("Blog · 20 Oct 2026"), approximate dates with a tilde ("LinkedIn · ~14 Oct 2026"). Same-day ties put exact dates before approximations.
- **Travel view** (`#travel`): a countries map regenerated only by `generate_travel.py` (below).

## 3. How changes land on the domain

1. **Branch from clean current `main`.** Never build a change file from a working copy - a dirty base smuggles other pending changes into the PR.
2. **One change per PR.**
3. **Verify before opening the PR:**
   - Byte-preservation: outside the intended section, the file is identical to `main`.
   - sha256 match between the local build and the branch head - fetch raw content at the commit SHA, because branch-name raw URLs are cached.
   - No private URLs or personal data anywhere in the file.
4. **Open the PR with a Testing/Risk/Revert comment.**
5. **Critic gate: a separate reviewer checks every PR. Nothing merges without a critic PASS and the owner's explicit merge approval.**
6. Squash-merge, then **verify live**: fetch the site with a cache-busting query parameter (it caches aggressively), hash-compare against the merged file, and spot-check the rendered page. Expect 1-2 minutes of Pages deploy lag after a merge.
7. **Back-to-back PRs touching `index.html`**: merging the first makes the second unmergeable. Fix by rebuilding the second change as a fresh branch from the new `main` - branch history, not content, is what conflicts.

## 4. generate_travel.py

Refreshes only the Travel view's markup inside `index.html` from a reviewed visited-country projection (`--projection`, a JSON file of `{countries: [...], count: N}`; `--check` re-validates the projection embedded in the current file). Guardrails baked into the script: country names only (validated against its ISO catalog), no dates, no photos, no booking ingestion - a booking is not a visit, and upstream must verify actual travel before a country is added. Changes still land through the normal PR flow in section 3.

## 5. Operational gotchas (learned the hard way)

- **GitHub web upload flow**: uploading a file whose name already exists on the target branch stages it with a `1-` prefix rather than overwriting (and can do so even without a collision). The dance is: upload, commit to a new branch, delete the old file if one exists, rename the staged file to its real name - verifying each commit landed via the contents API. The rename fails with "file already exists" if the delete did not commit first.
- **Commit dialogs** on GitHub's web UI are not always in the accessibility tree; an inline error banner pushes the green commit button down - screenshot before clicking by coordinates.
- **raw.githubusercontent caches by branch name**; always verify content at the commit SHA.
- **The live site caches aggressively**; verify with a cache-bust parameter after every merge.
- **Pre-merge screenshots without deploying**: `htmlpreview.github.io/?<github blob URL>#<view-hash>` renders the SPA, including hash-routed views.
