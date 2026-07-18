# Deploying to GitHub Pages

The site is a fully static Next.js export (`web/out`).

## One-time GitHub setup

1. Push this repo to GitHub.
2. **Settings → Pages → Build and deployment → Source:** GitHub Actions.
3. Ensure Actions can write to Pages (the workflow requests `pages: write`).

## Automatic deploys

Push to `main` or `master` runs [`.github/workflows/pages.yml`](../.github/workflows/pages.yml).

- Repo named `owner.github.io` → site at `https://owner.github.io/`
- Any other repo name → site at `https://owner.github.io/<repo>/` (sets `BASE_PATH`)

## Local static build

```bash
cd web
npm ci
npm run build          # writes web/out
npm run serve:static   # http://localhost:3010
```

For a project-site base path locally:

```bash
BASE_PATH=/hudra.org npm run build
```

## Password

The UI asks for password `marthoma` (sessionStorage). This is a light gate only — all files are still public on Pages.
