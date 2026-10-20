"""One-time source importer. Requires beautifulsoup4 and Pillow; preserves original assets."""
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, re, subprocess
from bs4 import BeautifulSoup
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://yizewang.weebly.com/'
PAGES = ['home', 'education', 'research', 'publication--honors', 'personal']

def fetch(url):
    return subprocess.check_output(['curl', '-fLsS', '--retry', '2', '--max-time', '90', url])

def text(e):
    return e.get_text().replace('\u200b', '').replace('\xa0', ' ').strip()

def clean(e):
    s = BeautifulSoup(str(e), 'html.parser')
    for el in list(s.find_all(True)):
        if el.name not in ['strong', 'em', 'a', 'br']:
            el.unwrap()
        else:
            href = el.get('href')
            el.attrs = {}
            if el.name == 'a' and href:
                el['href'] = urljoin(SOURCE, href)
    return str(s).replace('\u200b', '').replace('\xa0', ' ').strip()

def lines(e):
    return [v.strip() for v in re.split(r'<br\s*/?>', clean(e)) if BeautifulSoup(v, 'html.parser').get_text().strip()]

soups = {p: BeautifulSoup(fetch(SOURCE + ('' if p == 'home' else p + '.html')), 'html.parser') for p in PAGES}
contents = {p: s.select_one('#wsite-content') for p, s in soups.items()}
urls = set()
for s in contents.values():
    for img in s.select('.wsite-image img'):
        urls.add(urljoin(SOURCE, img['src']))
cv = urljoin(SOURCE, contents['home'].select_one('a[href$=".pdf"]')['href'])
urls.add(cv)
# Keep the original home banner as well as all content images.
hero = re.search(r'url\(["\']?([^"\')]+)', soups['home'].select_one('.wsite-header-section')['style']).group(1)
urls.add(urljoin(SOURCE, hero))
assets = {}

def download(url):
    name = Path(urlparse(url).path).name
    relative = ('files/' if name.endswith('.pdf') else 'images/originals/') + name
    target = ROOT / relative
    if not target.exists():
        target.write_bytes(fetch(url))
    record = {'source': url, 'path': relative, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size}
    if not name.endswith('.pdf'):
        with Image.open(target) as im:
            record.update(width=im.width, height=im.height, frames=getattr(im, 'n_frames', 1))
            poster = ImageOps.exif_transpose(im).convert('RGB')
            poster.thumbnail((1100, 800))
            preview = 'images/previews/' + Path(name).stem + '.webp'
            poster.save(ROOT / preview, 'WEBP', quality=86)
            record.update(preview=preview, preview_width=poster.width, preview_height=poster.height)
    return url, record

with ThreadPoolExecutor(max_workers=6) as pool:
    assets = dict(pool.map(download, sorted(urls)))

def image(e):
    im = e.select_one('img')
    a = e.select_one('a[href]')
    caption = text(e.select_one('div'))
    return {'asset': assets[urljoin(SOURCE, im['src'])], 'caption': caption, 'link': a.get('href') if a else None}

research = []
for table in contents['research'].select('table.wsite-multicol-table'):
    if table.find_parent('table'):
        continue
    h = table.select_one('h2')
    research.append({'title': text(h), 'paragraphs': [clean(p) for p in table.select('.paragraph')], 'images': [image(i) for i in table.select('.wsite-image')]})

ed = contents['education'].select('.paragraph')
# Four education entries are separated by double line breaks in the source.
education_blocks = re.split(r'(?:<br/>\s*){2,}', clean(ed[0]))
education_blocks = [b.strip() for b in education_blocks if b.strip()]
assert len(education_blocks) == 4
pub = contents['publication--honors'].select('.paragraph')
pg = contents['personal']
personal = []
for h in pg.select('h2')[1:]:
    images = [image(i) for i in pg.select('.wsite-image') if i.find_previous('h2') == h]
    personal.append({'title': text(h), 'images': images})
email_hex = contents['home'].select_one('[data-cfemail]')['data-cfemail']
b = bytes.fromhex(email_hex)
email = ''.join(chr(c ^ b[0]) for c in b[1:])
data = {
 'source': SOURCE, 'imported': '2026-10-20', 'name': 'Yize Wang', 'email': email,
 'hero': assets[urljoin(SOURCE, hero)], 'portrait': image(contents['home'].select_one('.wsite-image'))['asset'], 'cv': assets[cv],
 'biography': re.split(r'(?:<br/>\s*){2,}', clean(contents['home'].select_one('.paragraph'))),
 'education': [{'html': h, 'date': d} for h, d in zip(education_blocks, ['Sep 2018 – May 2021', 'Jun 2019 – Jul 2019', 'Sep 2014 – Jul 2018 · Rank: 1 / 28', 'Jun 2017 – Sep 2017'])],
 'graduate_courses': list(zip(lines(ed[2]), lines(ed[3]))),
 'undergraduate_courses': list(zip(lines(ed[4]), lines(ed[5]))), 'skills': clean(ed[6]),
 'research': research, 'publications': lines(pub[0]), 'patents': lines(pub[1]), 'honors': list(zip(lines(pub[2]), lines(pub[3]))),
 'personal': personal, 'personal_notice': text(pg.select_one('.paragraph')),
}
assert len(data['research']) == 8
assert len(data['graduate_courses']) == 10 and len(data['undergraduate_courses']) == 15
assert len(data['publications']) == 4 and len(data['patents']) == 4 and len(data['honors']) == 16
(ROOT / 'data/content.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'data/assets.json').write_text(json.dumps(list(assets.values()), ensure_ascii=False, indent=2) + '\n')
print(f'Imported {len(assets)} assets and all five pages; {sum(a["bytes"] for a in assets.values()) / 1024**2:.1f} MiB originals.')
