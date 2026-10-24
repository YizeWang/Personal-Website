# Yize Wang — personal website

Static migration of [yizewang.weebly.com](https://yizewang.weebly.com/), inspired
by the fixed profile sidebar and section layout in
[manymuch.github.io](https://github.com/manymuch/manymuch.github.io).
Content was imported on 2026-10-20. Academic information and the CV are historical
and retain the original wording; they have not been updated to claim a current role.

## Preview

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open [the local preview](http://127.0.0.1:8765/). No package installation or build
is required to view the checked-in HTML. The site has a responsive mobile layout,
automatic dark appearance, keyboard-accessible media viewer, and reduced-motion
support. Navigation, images, external links and CV also work without JavaScript.
Animation posters remain still until clicked; the original GIF then loads in the viewer.

## Edit and verify

- `data/content.json`: all editable biography, education, projects, publications,
  patents, honors, interests, and original external links.
- `scripts/build.py`: renders the content to `index.html` and four old-page redirects.
- `css/site.css`, `js/site.js`: presentation and progressive enhancements.
- `data/education-logos.json`, `images/logos/`: local university logos and their source URLs.
  Degree entries span the page; non-degree entries use smaller logos and paired rows
  on desktop, with a single column on phones.
- `images/previews/`: compressed, still WebP thumbnails (about 2.25 MiB total).
- `images/originals/`, `files/`: 40 imported original files, including animated GIFs,
  the portrait, banner and CV, with byte-identical source files.
- `data/assets.json`: source URLs, dimensions, sizes, and SHA-256 checksums.

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

## Validation of this migration

Local Chromium checks passed for 360, 390, 768, 1024 and 1920 pixel widths,
all original displayed images, GIF viewing, keyboard dismissal and focus restoration,
missing-image fallback/retry, PDF download, all four legacy redirects, deployment
under `/Personal-Website/`, dark appearance, reduced motion, and no-JavaScript
content. Original assets passed SHA-256 verification. Safari and Firefox have not
been tested. Pages activation and the first live deployment still require the
repository setting described above.

University logos identify the institutions for each education entry. ETH uses its
official website wordmark; SJTU uses its official visual identity emblem; Imperial
uses the historical wordmark from Wikimedia Commons; Michigan uses the university
logo supplied by the UMich AI Resources style-guide repository. Source URLs and
intrinsic dimensions are recorded in `data/education-logos.json`. Marks belong to
their respective institutions. The five education logos were checked in Chromium
on desktop, mobile and dark appearance, with no horizontal overflow.
