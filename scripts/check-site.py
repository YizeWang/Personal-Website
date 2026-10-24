"""Validate every published local link, image, anchor, and imported original."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.refs = []
        self.images = []
        self.errors = []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: self.errors.append('Duplicate id: ' + a['id'])
            self.ids.add(a['id'])
        for key in ('src','href'):
            if a.get(key): self.refs.append(a[key])
        if tag == 'img':
            for key in ('alt','width','height'):
                if not a.get(key): self.errors.append('Image missing ' + key)
            self.images.append(a)

docs = {p.name: Document(p) for p in ROOT.glob('*.html')}
errors = []
for name, doc in docs.items():
    errors.extend(f'{name}: {s}' for s in doc.errors)
    for ref in doc.refs:
        u = urlsplit(ref)
        if u.scheme or u.netloc: continue
        target = unquote(u.path) or name
        path = ROOT / target
        if not path.is_file(): errors.append(f'{name}: Missing file: {ref}')
        elif u.fragment and path.name in docs and u.fragment not in docs[path.name].ids:
            errors.append(f'{name}: Missing anchor: {ref}')
    for a in doc.images:
        if urlsplit(a['src']).scheme: errors.append(f'{name}: Remote image dependency: {a["src"]}')
assets = json.loads((ROOT / 'data/assets.json').read_text())
for a in assets:
    path = ROOT / a['path']
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != a['sha256']:
        errors.append('Original asset changed or missing: ' + a['path'])
    if a.get('preview') and not (ROOT / a['preview']).is_file():
        errors.append('Missing preview: ' + a['preview'])
data = json.loads((ROOT / 'data/content.json').read_text())
for key, expected in [('education',5),('research',8),('publications',4),('patents',4),('honors',16)]:
    if len(data[key]) != expected: errors.append(f'{key}: expected {expected} records')
main = docs['index.html']
for id in ['career','education','research','publications','personal']:
    if id not in main.ids: errors.append('Missing section: ' + id)
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(docs)} HTML pages, {len(main.images)} page images, all local references and anchors, {len(assets)} original asset checksums, and all migrated content counts.')
