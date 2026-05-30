# Sharing BR3N Macro Lab

How to give other people a link they can open in any browser.

---

## Option A — GitHub Pages (recommended, free, permanent URL)

**You get:** `https://YOUR_USERNAME.github.io/REPO_NAME/`

### One-time setup

1. **Build the site locally**
   ```bash
   cd ~/fx_regime_lab
   python scripts/build_site.py
   ```

2. **Create a GitHub repo** (e.g. `br3n-macro-lab`) at [github.com/new](https://github.com/new).

3. **Push the project**
   ```bash
   git add .
   git commit -m "Initial BR3N Macro Lab"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/br3n-macro-lab.git
   git push -u origin main
   ```

4. **Enable GitHub Pages**
   - Repo → **Settings** → **Pages**
   - **Source:** GitHub Actions (not “Deploy from branch”)
   - The workflow in `.github/workflows/pages.yml` runs on every push to `main`

5. **Wait ~1–2 minutes**, then open the URL shown under **Settings → Pages**.

### Update after new research

```bash
python scripts/run_research_ladder.py
python scripts/build_site.py
git add reports/publication reports/research_ladder
git commit -m "Update research publication"
git push
```

---

## Option B — Netlify Drop (fastest, no git)

**You get:** a random `*.netlify.app` URL in ~30 seconds.

1. Run `python scripts/build_site.py`
2. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
3. Drag the folder `reports/publication/` onto the page
4. Copy the URL Netlify gives you

Re-upload the folder whenever you refresh the research.

---

## Option C — Streamlit Cloud (live dashboard + research tab)

**You get:** `https://YOUR_APP.streamlit.app`

Good if you want **live charts**, not just the write-up.

1. Push repo to GitHub (same as Option A, steps 2–3)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect the repo, set main file: `streamlit_app.py` (luxury terminal) or `src/dashboard.py` (classic)
4. Deploy — first load builds research data from yfinance (~1–2 min)

Readers use the **Research Note** page in the sidebar for the memo.

---

## Option D — Temporary link (demo / Slack)

While your Mac is on and the server is running:

```bash
python scripts/serve_publication.py   # http://127.0.0.1:8765
```

Install [ngrok](https://ngrok.com) and tunnel:

```bash
ngrok http 8765
```

Share the `https://….ngrok-free.app` URL. Stops when you close ngrok.

---

## Option E — Send a file

Email or Slack **`reports/publication/index.html`**.  
Recipients open it in Chrome/Safari. Links to `memo.html` work if those files are in the **same folder**.

---

## What to share with whom

| Audience | Best option |
|----------|-------------|
| LinkedIn / portfolio | GitHub Pages URL |
| One meeting / quick demo | Netlify Drop or ngrok |
| Risk committee | GitHub Pages + PDF export of memo |
| Technical reviewer | GitHub repo link |

---

## Privacy note

The static site contains **research results only** — no API keys.  
Do not publish `config.yaml` secrets if you add any later. The default config has no secrets.

---

*BR3N Macro Lab · Research only · Not investment advice*
