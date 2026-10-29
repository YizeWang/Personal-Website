# Yize Wang — Personal Website

[Visit the website](https://yizewang.github.io/)

## Edit

- `data/career.json` — Career experience.
- `data/content.json` — Education, research, publications, honors, and interests.
- `css/site.css` and `js/site.js` — Styling and interactions.
- `images/` — Original images and optimized previews; sources are recorded in `data/assets.json`.

## Build and Preview

```sh
python3 scripts/build.py
python3 scripts/check-site.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open [localhost:8765](http://127.0.0.1:8765/). Building requires only Python's standard library.

## Deploy

Push to `main`; GitHub Actions builds, checks, and deploys the site to GitHub Pages.

## Credits

Layout inspiration: [Jiaxin (Jimmy) Zhang](https://github.com/manymuch/manymuch.github.io) and [Read Only by HTML5 UP](https://html5up.net/read-only) ([CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)). Third-party images link to their sources.
