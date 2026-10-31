"""Build the dependency-free static site from the editable content archive."""
from pathlib import Path
from html import escape as esc, unescape
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / 'data/content.json').read_text())
career_data = json.loads((ROOT / 'data/career.json').read_text())
css_version = hashlib.sha256((ROOT / 'css/site.css').read_bytes()).hexdigest()[:12]
js_version = hashlib.sha256((ROOT / 'js/site.js').read_bytes()).hexdigest()[:12]
icons_version = hashlib.sha256((ROOT / 'images/social-icons.svg').read_bytes()).hexdigest()[:12]
share_version = hashlib.sha256((ROOT / 'images/social-preview.png').read_bytes()).hexdigest()[:12]
favicon_version = hashlib.sha256((ROOT / 'images/favicon-32.png').read_bytes()).hexdigest()[:12]
site_description = 'Yize Wang is a Senior Software Engineer at NVIDIA, focused on humanoid robots, policy fine-tuning, path planning, optimization, and autonomous driving.'

def title_words(s):
    """Keep articles and short prepositions/conjunctions lowercase within titles."""
    minor = {'the', 'a', 'an', 'and', 'or', 'nor', 'but', 'for', 'so', 'yet', 'as', 'at', 'by',
             'down', 'from', 'in', 'into', 'like', 'near', 'of', 'off', 'on',
             'onto', 'out', 'over', 'past', 'per', 'than', 'till', 'to', 'up',
             'upon', 'via', 'with'}
    words = list(re.finditer(r"(?<![A-Za-z0-9])[A-Za-z]+(?:['’][A-Za-z]+)?", s))
    edges = {words[0].start(), words[-1].start()} if words else set()
    def case_word(match):
        word = match[0]
        if word.lower() in minor and match.start() not in edges:
            return word.lower()
        return word[0].upper() + word[1:]
    return re.sub(r"(?<![A-Za-z0-9])[A-Za-z]+(?:['’][A-Za-z]+)?", case_word, s)

def img(a, alt, eager=False):
    return f'<img src="{a["preview"]}" alt="{esc(alt, quote=True)}" width="{a["preview_width"]}" height="{a["preview_height"]}" decoding="async" ' + ('fetchpriority="high"' if eager else 'loading="lazy"') + '>'

def figure(i):
    a, caption = i['asset'], title_words(i['caption'])
    link = i['link'] or a['path']
    attrs = 'target="_blank" rel="noopener noreferrer"' if i['link'] else 'data-media'
    figure_attrs = ' class="portrait"' if i.get('orientation') == 'portrait' else ''
    inline_asset = {**a, "preview": a["path"], "preview_width": a["width"], "preview_height": a["height"]} if a.get("frames", 1) > 1 else a
    picture = img(inline_asset, caption)
    if i.get('crop'):
        crop = i['crop']
        width, height = crop['width'], crop['height']
        style = f"--crop-ratio:{width}/{height};--crop-image-width:{a['width'] / width * 100:.6f}%;--crop-left:{-crop['x'] / width * 100:.6f}%;--crop-top:{-crop['y'] / height * 100:.6f}%"
        picture = f'<span class="media-crop" style="{style}">{picture}</span>'
    return f'<figure{figure_attrs}><a href="{esc(link, quote=True)}" {attrs} aria-label="{esc(caption, quote=True)}">{picture}</a><figcaption>{esc(caption)}</figcaption></figure>'

def section(id, number, title, intro, content):
    return f'<section id="{id}" aria-labelledby="{id}-title"><div class="container"><header class="section-heading"><span class="section-number">{number}</span><div><h2 id="{id}-title">{title_words(title)}</h2><p>{intro}</p></div></header>{content}</div></section>'

def external_links_new_tab(html):
    """Give every HTTP(S) link the same behavior across all sections."""
    def update(match):
        tag = match[0]
        href = re.search(r'''\bhref\s*=\s*(["'])(.*?)\1''', tag, re.I)
        if not href or not re.match(r'^(?:https?:)?//', unescape(href[2]), re.I):
            return tag
        tag = re.sub(r'''\s+(?:target|rel)\s*=\s*(["']).*?\1''', '', tag, flags=re.I)
        return tag[:-1] + ' target="_blank" rel="noopener noreferrer">'
    return re.sub(r'<a\b[^>]*>', update, html, flags=re.I)

nav = [('career', 'Professional Experience'), ('education', 'Education'), ('research', 'Research'), ('publications', 'Publications'), ('honors', 'Honors'), ('personal', 'Personal')]
email = esc(d['email'])
profile_links = []
for profile in d['profiles']:
    if profile.get('media'):
        attrs = f'data-media data-caption="{esc(profile["caption"], quote=True)}" aria-haspopup="dialog" aria-controls="media-viewer"'
    else:
        attrs = 'target="_blank" rel="noopener noreferrer"'
    profile_links.append(f'<a class="social-link" href="{esc(profile["url"], quote=True)}" title="{esc(profile["name"], quote=True)}" aria-label="{esc(profile["name"], quote=True)}" {attrs}><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="images/social-icons.svg?v={icons_version}#{profile["icon"]}"></use></svg></a>')
social_links = '<div class="social-links" aria-label="Social profiles">' + ''.join(profile_links) + '</div>'

parts = [f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yize Wang · Robotics & Autonomous Driving</title>
<meta name="description" content="{esc(site_description, quote=True)}">
<link rel="canonical" href="https://yizewang.github.io/">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#245c4f">
<meta property="og:title" content="Yize Wang · Robotics & Autonomous Driving"><meta property="og:description" content="{esc(site_description, quote=True)}">
<meta property="og:type" content="website"><meta property="og:url" content="https://yizewang.github.io/">
<meta property="og:image" content="https://yizewang.github.io/images/social-preview.png?v={share_version}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/png"><meta property="og:image:alt" content="Yize Wang — Robotics and Autonomous Driving">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Yize Wang · Robotics & Autonomous Driving"><meta name="twitter:description" content="{esc(site_description, quote=True)}"><meta name="twitter:image" content="https://yizewang.github.io/images/social-preview.png?v={share_version}"><meta name="twitter:image:alt" content="Yize Wang — Robotics and Autonomous Driving">
<link rel="icon" href="favicon.ico?v={favicon_version}" type="image/x-icon" sizes="32x32"><link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png?v={favicon_version}"><link rel="icon" type="image/png" sizes="192x192" href="images/favicon-192.png?v={favicon_version}"><link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon.png?v={favicon_version}"><link rel="stylesheet" href="css/site.css?v={css_version}"><script src="js/site.js?v={js_version}" defer></script>
</head><body><a class="skip-link" href="#main">Skip to content</a><aside id="sidebar" aria-label="Profile and navigation"><header>''',
 img(d['portrait'], 'Yize Wang', True),
 f'<h1>Yize Wang</h1><p class="profile-role">Robotics &amp; Autonomous Driving</p><p class="profile-focus">Humanoid Robots · Policy Fine-Tuning<br>Path Planning · Optimization</p><div class="profile-contact"><a href="mailto:{email}">{email}</a><a href="tel:{esc(d["phone"], quote=True)}">{esc(d["phone_display"])}</a></div>{social_links}</header><nav aria-label="Main navigation">',
 ''.join(f'<a href="#{id}"><span>{label}</span><span aria-hidden="true">{n:02d}</span></a>' for n, (id, label) in enumerate(nav, 1)),
 '</nav></aside><main id="main">',
 f'<div class="hero"><img src="{d["hero"]["preview"]}" width="{d["hero"]["preview_width"]}" height="{d["hero"]["preview_height"]}" alt="Yize Wang working on a mechatronics project" fetchpriority="high"><div class="hero-content"><p class="eyebrow">YIZE WANG / PERSONAL WEBSITE</p><p class="hero-title">Robots are reflections<br>of ourselves.</p></div></div>'
]
def career_highlights(items, term_links=None):
    rendered = []
    for item in items:
        text = esc(item)
        for label, url in (term_links or {}).items():
            text = re.sub(r'\b' + re.escape(label) + r'\b',
                          lambda match: f'<a href="{esc(url, quote=True)}">{match[0]}</a>', text)
        rendered.append(f'<li>{text}</li>')
    return '<ul class="career-highlights">' + ''.join(rendered) + '</ul>'

career = '<div class="career-list">'
for entry in career_data['entries']:
    date_at_company = entry.get('date_placement') == 'company'
    logo = career_data['logos'][entry['company']]
    career += '<article class="career-entry"><div class="career-entry-heading"><div class="career-logo">' + img(logo, entry['company'] + ' logo') + '</div><div class="career-identity">'
    if date_at_company:
        career += f'<header class="career-company-heading"><h3>{esc(entry["company"])}</h3><p class="date">{esc(entry["date"])}</p></header>'
    else:
        career += f'<h3>{esc(entry["company"])}</h3>'
    metadata = [f'<span class="career-role">{esc(entry["role"])}</span>']
    for key in ('department', 'team', 'location'):
        if entry.get(key):
            metadata.append(f'<span class="career-{key}">{esc(entry[key])}</span>')
    position_date = '' if date_at_company else f'<p class="date">{esc(entry["date"])}</p>'
    career += '<header class="career-heading"><p class="career-meta">' + ''.join(metadata) + '</p>' + position_date + '</header></div></div><div class="career-position">'
    if entry.get('highlights'):
        career += career_highlights(entry['highlights'])
    for project in entry.get('projects', []):
        career += f'<div class="career-project"><header><div><h4>{esc(title_words(project["title"]))}</h4>'
        if project.get('role'):
            career += f'<p class="career-project-role">{esc(project["role"])}</p>'
        career += '</div>'
        if project.get('date'):
            career += f'<p class="date">{esc(project["date"])}</p>'
        career += '</header>' + career_highlights(project['highlights'], project.get('highlight_links')) + '</div>'
    career += '</div></article>'
career += '</div>'
parts.append(section('career', '01', 'Professional Experience', 'Robotics, autonomous driving, and software engineering.', career))
ed = '<div class="education-list">'
for e in d['education']:
    kind = 'education-primary' if e['kind'] == 'degree' else 'education-secondary'
    body = e['html']
    if e.get('courses'):
        label = esc(e['courses_title'])
        courses = f'<details class="courses"><summary aria-label="{label}" title="{label}">Courses</summary><div class="table-scroll"><table><caption>{label} and Grades</caption><thead><tr><th scope="col">Course</th><th scope="col">Grade</th></tr></thead><tbody>'
        for course, grade in e['courses']:
            code, name = course.split(' ', 1)
            courses += f'<tr><td><span class="course-code">{esc(code)}</span> {esc(title_words(name))}</td><td>{esc(grade)}</td></tr>'
        courses += '</tbody></table></div></details>'
        before, rank = body.rsplit('<strong>', 1)
        body = before + '<div class="degree-stats"><strong>' + rank + courses + '</div>'
    ed += f'<article class="education-entry {kind}"><div class="education-body">{body}</div><p class="date">{e["date"]}</p></article>'
ed += '</div>'
parts.append(section('education', '02', 'Education', 'Excellent academic performance is never the destination.', ed))
research = '<div class="project-index">' + ''.join(f'<a href="#{p.get("id", f"project-{n}")}">{n:02d} {esc(title_words(p["title"]))}</a>' for n,p in enumerate(d['research'],1)) + '</div>'
for n,p in enumerate(d['research'],1):
    meta, *body = p['paragraphs']
    meta = re.sub(r'</?strong>', '', meta)
    meta_rows = re.split(r'<br\s*/?>', meta)
    meta = ''.join(f'<span class="project-meta-row{ " project-meta-keywords" if row.startswith("Keywords:") else "" }">{row}</span>' for row in meta_rows)
    project_id = p.get('id', f'project-{n}')
    research += f'<article class="project" id="{esc(project_id, quote=True)}"><header><span class="project-number">PROJECT {n:02d}</span><h3>{esc(title_words(p["title"]))}</h3><p class="project-meta">{meta}</p></header><div class="project-grid"><div class="project-media">' + ''.join(figure(i) for i in p['images']) + '</div><div class="project-copy">'
    research += ''.join(f'<p>{v}</p>' for v in body) + '</div></div></article>'
parts.append(section('research','03','Research','For tomorrow&#39;s robotics and autonomous driving.',research))
pubs = ''
for title,key in [('Paper','publications'),('Patents','patents')]:
    pubs += f'<h3 class="subheading">{title}</h3><ol class="publication-list">'
    pubs += ''.join('<li>' + re.sub(r'^\[\d+\]\s*', '', p) + '</li>' for p in d[key]) + '</ol>'
parts.append(section('publications','04','Publications','Writing is thinking.',pubs))
def award_label(award):
    text = unescape(re.sub(r'<[^>]+>', '', award))
    name, separator, details = text.partition('(')
    tag = "strong" if "<strong>" in award else "span"
    label = f'<{tag}>{esc(name.strip())}</{tag}>'
    if separator:
        label += f' <span class="award-detail">{esc(separator + details)}</span>'
    return label

honors = '<ul class="honors">' + ''.join(f'<li><span>{award_label(award)}</span><span class="date">{year}</span></li>' for award,year in d['honors']) + '</ul>'
parts.append(section('honors','05','Honors','Honors are a byproduct of the journey, not the destination.',honors))
personal = ''
for group in d['personal']:
    personal += f'<h3 class="subheading">{esc(title_words(group["title"]))}</h3><div class="gallery {"life" if group["title"] == "Life" else "favorites"}">' + ''.join(figure(i) for i in group['images']) + '</div>'
personal += f'<p class="smallprint">{esc(d["personal_notice"])}</p>'
parts.append(section('personal','06','Personal','Don’t worry, be happy!',personal))
parts.append('''<footer><span>© Yize Wang</span><a href="#main">Back to top ↑</a></footer></main>
<dialog id="media-viewer" aria-label="Image viewer"><div class="viewer-toolbar"><p id="media-caption"></p><button type="button" id="close-viewer" aria-label="Close image viewer">Close ×</button></div><div id="media-content"></div><p id="media-status" role="status" aria-live="polite"></p><a id="media-original" target="_blank" rel="noopener">Open original ↗</a></dialog></body></html>''')
(ROOT / 'index.html').write_text(external_links_new_tab('\n'.join(parts) + '\n'))
for path,target in [('education.html','education'),('research.html','research'),('publication--honors.html','publications'),('personal.html','personal')]:
    (ROOT / path).write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Yize Wang · {target.title()}</title><meta http-equiv="refresh" content="0;url=./index.html#{target}"></head><body><p>This page has moved. <a href="./index.html#{target}">Continue to {target}</a>.</p></body></html>\n')
print('Built index.html and four legacy page redirects.')
