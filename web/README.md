# Hudra web reader

Next.js app for browsing the Syriac prayers of the Hudra.

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Data is read from `../data` (symlink at `web/data`):
- `catalog.json` — liturgical organization
- `prayers/*.json` — full Syriac text per prayer
