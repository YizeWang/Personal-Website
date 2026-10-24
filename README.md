# Yize Wang — personal website

Static migration of [yizewang.weebly.com](https://yizewang.weebly.com/), inspired
by the fixed profile sidebar and section layout in
[manymuch.github.io](https://github.com/manymuch/manymuch.github.io).
Content was imported on 2026-10-20. Career Experience is based on the CV supplied by the owner, dated 2026-07-31.
Education and research details retain the separately approved website edits.

## Preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open [the local preview](http://127.0.0.1:8765/). No package installation or build
is required to view the checked-in HTML. The site has a responsive mobile layout,
automatic dark appearance, keyboard-accessible media viewer, and reduced-motion
support. Navigation, images, and contact/profile links also work without JavaScript.
Animation posters remain still until clicked; the original GIF then loads in the viewer.

## Edit and verify

- `data/career.json`: career roles and achievements extracted from the owner’s CV.
  The original DOCX is not published.
- `data/content.json`: editable education, projects, publications,
  patents, honors, interests, and original external links.
- `scripts/build.py`: renders the content to `index.html` and four old-page redirects.
- `css/site.css`, `js/site.js`: presentation and progressive enhancements.
- Degree entries span the page; non-degree entries use smaller type and paired
  rows on desktop, with a single column on phones. Graduate and undergraduate
  courses are attached to their corresponding degrees in native disclosure widgets,
  collapsed by default. The former Skills block has been removed.
- `images/previews/`: compressed, still WebP thumbnails (about 2.25 MiB total).
- `images/originals/`: 39 imported original images, including animated GIFs,
  the portrait and banner, with byte-identical source files.
- Sidebar contact details and GitHub, Google Scholar, LinkedIn, and WeChat links are
  editable in `data/content.json`; SVG profile icons are stored locally.
  The user-provided WeChat QR image opens in the existing accessible media viewer
  and remains available as a normal image link without JavaScript.
  The CV download and main-content contact panel have been removed.
- `data/assets.json`: source URLs, dimensions, sizes, and SHA-256 checksums.

The builder versions stylesheet, script, and social-icon URLs using content hashes
so browsers fetch updated assets after each change.

After editing content, run:

```sh
python3 scripts/build.py
python3 scripts/check-site.py
node --check js/site.js
```

The checker validates every local HTML reference, section anchor, image metadata,
original-file checksum, and expected content counts (8 projects, 4 publications,
4 patents and 16 honors).

`scripts/import-weebly.py` is the optional one-time importer (requires
`beautifulsoup4` and `Pillow`). Re-running it overwrites content from the old site;
normal editing and deployment require only standard-library Python.

## Publish to GitHub Pages

This checkout is connected to `YizeWang/Personal-Website`. Its Pages URL will be:

**https://yizewang.github.io/Personal-Website/**

1. In the repository's **Settings → Pages → Build and deployment**, set **Source**
   to **GitHub Actions**. This initial repository setting requires GitHub admin access.
2. Under **Actions → Deploy GitHub Pages**, use **Run workflow** after enabling Pages,
   or push a new commit to `main`.
3. The workflow builds and validates the site, then publishes only the website
   files. Subsequent pushes to `main` redeploy automatically.

The workflow uses GitHub's official configure/upload/deploy Pages actions.
See [GitHub's publishing source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

For the root address **https://yizewang.github.io/**, the repository must instead
be named **YizeWang.github.io**. This project uses relative asset paths and supports
either deployment without code changes. No canonical URL is hard-coded until the
final repository address is chosen.

The old `/education.html`, `/research.html`, `/publication--honors.html`, and
`/personal.html` paths redirect to their new sections under the new host. Redirecting
the original Weebly domain itself requires changing that site in Weebly.

## Content and design attribution

Site content and personal project media are migrated from Yize Wang's original site.
Book, film, television and game images retain their original external attribution
links and noncommercial-use notice. Layout inspiration: Jiaxin (Jimmy) Zhang's
portfolio and [Read Only by HTML5 UP](https://html5up.net/read-only),
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
No reference-site biography, contact details, or project assets are included.
The former About Me section has been replaced by Career Experience as section 01.

## Validation of this migration

Local Chromium checks passed for 360, 390, 768, 1024 and 1920 pixel widths,
all original displayed images, GIF viewing, keyboard dismissal and focus restoration,
missing-image fallback/retry, all four legacy redirects, deployment
under `/Personal-Website/`, dark appearance, reduced motion, and no-JavaScript
content. Original assets passed SHA-256 verification. Safari and Firefox have not
been tested. Pages activation and the first live deployment still require the
repository setting described above.
