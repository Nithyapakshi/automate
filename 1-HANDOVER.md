# Project Hub - Handover

How Pakshiraj's personal hub is built and maintained: the public site, the private hub, the publish pipelines, the standing rules, and the routines that keep both fresh. Written for a future maintainer (human or AI agent) picking the system up cold. Last updated 21 Oct 2026.

---

## 1. The two surfaces

| | Public site | Private hub |
|---|---|---|
| Address | automate.pakshiraj.me | Owner-only hosted File (link works only for the owner, after phone sign-in) |
| Host | GitHub Pages (free), repo `Nithyapakshi/automate` | Instinct-hosted File (private build/publish pipeline) |
| Shape | One self-contained `index.html` (~870 KB, minified, inline CSS+JS) | Small React app (TypeScript + JSON data files) |
| Audience | Anyone | Owner only |

The golden rule connecting them: **nothing private ever appears in the public bundle.** No private URLs, no personal data, no links to the private hub. The public site shows private areas only as locked tiles with a generic "visible only to the owner" dialog - no data, no destination.

## 2. Public site anatomy

- Single-page app with hash-routed views (`#ai-news`, `#ai-builders`, `#booklog`, `#races`, `#travel`, `#implemented`, `#jarvis`, and more). The landing page is a tile grid; each tile is labelled Public or Private and routes to its view.
- **AI news & tools** view: the twice-daily digest lives here as dated scan groups ("Scanned 21 Oct 2026, 07:00 Dubai"), newest on top, max 5 items plus at most 1 deep pick per scan. Deep dives link out to public Notion pages.
- **AI Builders** view: cards (`<details class="find">`) in a "Browse by idea" grid with a builder filter. Every card carries a date pill in the name line - exact dates plain ("Blog · 20 Oct 2026"), approximate LinkedIn dates with a tilde ("LinkedIn · ~14 Oct 2026"). Grid is strictly newest-first; same-day ties put exact dates before approximations.
- **Locked private tiles** (Run progress, Habits, and similar) follow one pattern: `data-private-tile` attribute, generic dialog, no content in the bundle.
- The repo also holds `CNAME` (custom domain) and `generate_travel.py` (travel map generator). There is no CI: the only automation is the GitHub Pages deploy on pushes to `main`.

## 3. Private hub anatomy

- Tile home (`/`) plus views: `/health`, `/health/meals`, `/weigh-ins`, `/ai-builders`, `/running` (season, history, upcoming, analysis, training), `/ideas` (+ X-sourced ideas), `/implemented` (+ learning log), `/routines`, `/reminders`, `/prices`, `/billing`, `/booklog` (+ metrics, roadmap), `/jarvis`.
- Data lives in plain JSON files under `src/` (e.g. `ai-builders.json`, `routines-data.json`, `health-data.json`, `running-season-data.json`). Views render from these files, so most content updates are JSON edits, not code changes.
- The AI Builders table in the hub mirrors the public cards in a simpler schema (`builder` / `summary` / `apply` / `url`) and is refreshed alongside public tile changes.
- The **routines board** (`/routines`) is the status page for the standing watches (see section 6): each entry records last run, cadence and a dated note. It is a snapshot board, not a live monitor.
- Some tiles link out to separate owner-only Files (e.g. the Habits dashboard and the Training plan workbook are their own Files with their own maintainers).

## 4. Publish pipelines

### Public site (gated)
1. Branch from **clean current main** (never from a working copy - a dirty base smuggles other pending changes into the PR).
2. Make exactly one change per PR.
3. Verify before opening: byte-preservation outside the intended section, sha256 match between the local build and the branch head (fetch raw at the commit SHA - branch-name URLs are cached), no private URLs or data in the file.
4. Open the PR with a Testing/Risk/Revert comment.
5. **Critic gate: a separate reviewer checks the PR. Nothing merges without a critic PASS and the owner's explicit merge approval.** No exceptions.
6. Squash-merge, then verify live: GitHub Pages deploys in about 1-2 minutes; the site caches aggressively, so fetch with a cache-busting query and hash-compare against the merged file, then spot-check the rendered page.

### Private hub (standing authority)
1. Always **checkout the latest published revision first** - another agent may have published since your last read. A stale checkout silently reverts their work on publish (this has happened twice in one day).
2. Edit, then build, then open the preview URL in a browser and click through the changed views (screenshots for anything visual).
3. Publish with the generation check: if the generation moved since your checkout, someone else published - rebase onto a fresh checkout, never force.

## 5. Standing rules

- The private hub stays private. The public site carries no private data, ever.
- Designs go mockup-first; the owner picks before anything is built.
- Public-site PRs get the critic gate every time.
- Digest slates: max 5 items + max 1 deep pick; never pad a slate to fill slots.
- Trials are free-only, each one approved individually. Deep-dive reports end with exactly one trial recommendation.
- No spend anywhere without explicit approval.
- Scorecard and hub data cells: only mark what is backed by a record or the owner's word; unclear days stay unmarked rather than guessed.
- Approximate dates are labelled approximate (the tilde convention); never present a derived date as exact.

## 6. Routines and watchdogs

Standing scheduled work (all times Asia/Dubai):

| Routine | Cadence | What it does |
|---|---|---|
| AI digest | Daily 07:00 and 16:00 | Refresh board evidence, scan news, publish slate (PR for public tile), email the digest, evaluate deep-pick candidates |
| Training scorecard | Nightly 22:30 | Mark the day's training cells from records; green = followed plan, light red = missed, amber = travel/break; unclear stays blank |
| Research lens | Sunday 06:00 | Weekly research review |
| Audit | Saturday 10:00 | Weekly consistency audit |
| Jarvis claims drift | Sunday 09:00 | Check the Jarvis page's claims against reality |

Additional agent-maintained pieces with their own owners: the Habits dashboard File (daily morning refresh after the habit check), the Health/food data, the Training plan File. Coordinate through the owner when two agents need the same File - always re-checkout before publishing.

## 7. Operational gotchas (learned the hard way)

- **GitHub web upload flow**: uploading `index.html` to a branch that already has one stages it as `1-index.html` - it never overwrites silently. The dance is: upload, commit to a new branch, delete the old `index.html`, rename `1-index.html` to `index.html`, verifying each commit landed (the contents API is your friend). The rename fails with "file already exists" if the delete did not commit first.
- **Commit dialogs** on GitHub's web UI are not always in the accessibility tree; if an inline error banner appears, it pushes the green commit button down - screenshot before clicking by coordinates.
- **raw.githubusercontent caches by branch name**; always verify content at the commit SHA.
- **automate.pakshiraj.me caches aggressively**; verify with a cache-bust parameter and expect 1-2 minutes of Pages lag after a merge.
- **Pre-merge screenshots** without deploying: `htmlpreview.github.io/?<github blob URL>#<view-hash>` renders the SPA, including hash-routed views.
- **Private Files sit behind phone sign-in**; for verification use a scoped 15-minute preview URL for the exact revision. File pages send `frame-ancestors 'none'` - they cannot be embedded in iframes - and app content is served from per-revision origins, so any hardcoded embed or link to a revision URL breaks on the next publish.
- **Back-to-back PRs touching the same file**: merging one makes the other unmergeable. Fix by rebuilding the second change as a fresh branch from the new main - branch history, not content, is what conflicts.

## 8. Open work (as of 21 Oct 2026)

- **/private + Share CTA**: research delivered - the only free way to a sign-in-gated `/private` on the domain is moving DNS to Cloudflare and gating with Cloudflare Access, with share links as unguessable revocable URLs. Awaiting the owner's decision; nothing built.
- **Habits-in-Health tab**: considered and rejected by the owner (21 Oct) - Habits stays its own tile on both surfaces.
- **Oct 12/13 James posts**: cards shipped in PR #56.

---

*Maintenance contacts and private File links are intentionally omitted from this document.*
