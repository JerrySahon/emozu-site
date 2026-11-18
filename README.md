# Emozu site

Live: https://emozu.kids (EN) and https://emozu.kids/ru/ (RU).

- Edit copy in `_src/template.html` (each string is `{{en|ru}}`), privacy in `_src/privacy.html`.
- Build: `python3 _src/build.py`. It writes both languages, privacy pages, 404, sitemap, robots and CNAME.
- Domain and public email live in one place: `DOMAIN` in `_src/build.py`.
- Deploy: push to `main`. GitHub Pages serves the repo root.
- Form: posts to the Apps Script web app "Emozu form" (`data-endpoint` in the template). Entries land in the Google Sheet "Emozu applications".
- Quiz deep links: `https://emozu.kids/#quiz` (EN) and `https://emozu.kids/?lang=ru#quiz` (RU). Quiz answers stay in memory only; the existing contact form receives only the adult's contact and explicit intent.
- Crowdfunding switch: set `CAMPAIGN_URL` in `quiz.js` only after a verified live payment page exists. Until then the support path asks for the launch link and states the $20,000 goal and $10 starting contribution.
- Product images are renders from the canon v1 set (emozu-kb, 02-zhelezo/renders, round 17). Swap them for the Blender studio renders when those are final.
