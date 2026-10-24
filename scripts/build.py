"""Build the dependency-free static site from the editable content archive."""
from pathlib import Path
from html import escape as esc
import json, re

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / 'data/content.json').read_text())

def title_words(s):
    """Capitalize each title word without changing acronyms or names."""
    return re.sub(r"(^|[\s-])([a-z])", lambda m: m[1] + m[2].upper(), s)

def img(a, alt, eager=False):
    return f'<img src="{a["preview"]}" alt="{esc(alt, quote=True)}" width="{a["preview_width"]}" height="{a["preview_height"]}" decoding="async" ' + ('fetchpriority="high"' if eager else 'loading="lazy"') + '>'

def figure(i):
    a, caption = i['asset'], title_words(i['caption'])
    link = i['link'] or a['path']
    attrs = 'target="_blank" rel="noopener noreferrer"' if i['link'] else 'data-media'
    motion = '<span class="motion-label">Play animation ↗</span>' if a.get('frames', 1) > 1 else ''
    return f'<figure><a href="{esc(link, quote=True)}" {attrs} aria-label="{esc(caption, quote=True)}">{img(a, caption)}{motion}</a><figcaption>{esc(caption)}</figcaption></figure>'

def section(id, number, title, intro, content):
    return f'<section id="{id}" aria-labelledby="{id}-title"><div class="container"><header class="section-heading"><span class="section-number">{number}</span><div><h2 id="{id}-title">{title_words(title)}</h2><p>{intro}</p></div></header>{content}</div></section>'

nav = [('about', 'About'), ('education', 'Education'), ('research', 'Research'), ('publications', 'Publications & Honors'), ('personal', 'Personal')]
email = esc(d['email'])
parts = ['''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yize Wang · Robotics & Autonomous Driving</title>
<meta name="description" content="Yize Wang's research in robotics, autonomous driving, path planning, optimal control, and mechatronics. Education, publications, and projects.">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#245c4f">
<meta property="og:title" content="Yize Wang · Robotics & Autonomous Driving"><meta property="og:description" content="Robots are reflections of ourselves. Research, education, publications, and life.">
<link rel="icon" href="images/previews/portrait_orig.webp"><link rel="stylesheet" href="css/site.css"><script src="js/site.js" defer></script>
</head><body><a class="skip-link" href="#main">Skip to content</a><aside id="sidebar" aria-label="Profile and navigation"><header>''',
 img(d['portrait'], 'Yize Wang', True),
 f'<h1>Yize Wang</h1><p class="profile-role">Robotics &amp; Autonomous Driving</p><p class="profile-focus">Path Planning · Decision Making<br>Mechanical Engineering</p><div class="profile-links"><a href="mailto:{email}">Email</a><a href="https://github.com/YizeWang">GitHub ↗</a><a href="{d["cv"]["path"]}">CV ↓</a></div></header><nav aria-label="Main navigation">',
 ''.join(f'<a href="#{id}"><span>{label}</span><span aria-hidden="true">{n:02d}</span></a>' for n, (id, label) in enumerate(nav, 1)),
 '<p class="sidebar-note">Robots are reflections<br>of ourselves.</p></nav></aside><main id="main">',
 f'<div class="hero"><img src="{d["hero"]["preview"]}" width="{d["hero"]["preview_width"]}" height="{d["hero"]["preview_height"]}" alt="Yize Wang working on a mechatronics project" fetchpriority="high"><div class="hero-content"><p class="eyebrow">YIZE WANG / PERSONAL WEBSITE</p><p class="hero-title">Serve Our World<br>with Humanoid Robots</p><a href="#research">Explore the research <span aria-hidden="true">↓</span></a></div></div>'
]
about = '<div class="biography">' + ''.join(f'<p>{p}</p>' for p in d['biography']) + '</div>'
about += '<div class="contact-panel"><div><h3>Get In Touch</h3>' + f'<a href="mailto:{email}">{email}</a><br><a href="tel:+8615846625655">+86 158 4662 5655</a></div><a class="button" href="{d["cv"]["path"]}">Download CV <span aria-hidden="true">↗</span></a></div>'
# Keep the original biography intact, while clearly identifying its historical context.
parts.append(section('about', '01', 'About Me', 'Robots are reflections of ourselves.', '<p class="archive-note">Biography and CV preserved from the original website (academic information through 2021).</p>' + about))
ed = '<div class="education-list">'
for e in d['education']:
    ed += f'<article class="education-entry"><p class="date">{e["date"]}</p><div>{e["html"]}</div></article>'
ed += '</div><h3 class="subheading">Skills</h3><p>' + d['skills'] + '</p>'
parts.append(section('education', '02', 'Education', 'Excellent academic performance is never the destination.', ed))
research = '<div class="project-index">' + ''.join(f'<a href="#project-{n}">{n:02d} {esc(title_words(p["title"]))}</a>' for n,p in enumerate(d['research'],1)) + '</div>'
for n,p in enumerate(d['research'],1):
    meta, *body = p['paragraphs']
    research += f'<article class="project" id="project-{n}"><header><span class="project-number">PROJECT {n:02d}</span><h3>{esc(title_words(p["title"]))}</h3><p class="project-meta">{meta}</p></header><div class="project-grid"><div class="project-media">' + ''.join(figure(i) for i in p['images']) + '</div><div class="project-copy">'
    research += ''.join(f'<p>{v}</p>' for v in body) + '</div></div></article>'
parts.append(section('research','03','Research','For tomorrow’s autonomous driving.',research))
pubs = ''
for title,key in [('Publications','publications'),('Patents','patents')]:
    pubs += f'<h3 class="subheading">{title}</h3><ol class="publication-list">'
    pubs += ''.join('<li>' + re.sub(r'^\[\d+\]\s*', '', p) + '</li>' for p in d[key]) + '</ol>'
pubs += '<h3 class="subheading">Selected Honors &amp; Awards</h3><ul class="honors">' + ''.join(f'<li><span>{award}</span><span class="date">{year}</span></li>' for award,year in d['honors']) + '</ul>'
parts.append(section('publications','04','Publications &amp; honors','Writing is thinking.',pubs))
personal = ''
for group in d['personal']:
    personal += f'<h3 class="subheading">{esc(title_words(group["title"]))}</h3><div class="gallery {"life" if group["title"] == "Life" else "favorites"}">' + ''.join(figure(i) for i in group['images']) + '</div>'
personal += f'<p class="smallprint">{esc(d["personal_notice"])}</p>'
parts.append(section('personal','05','Beyond Research','Don’t worry, be happy!',personal))
parts.append('''<footer><span>© Yize Wang</span><a href="#about">Back to top ↑</a></footer></main>
<dialog id="media-viewer" aria-label="Image viewer"><div class="viewer-toolbar"><p id="media-caption"></p><button type="button" id="close-viewer" aria-label="Close image viewer">Close ×</button></div><div id="media-content"></div><p id="media-status" role="status" aria-live="polite"></p><a id="media-original" target="_blank" rel="noopener">Open original ↗</a></dialog></body></html>''')
(ROOT / 'index.html').write_text('\n'.join(parts) + '\n')
for path,target in [('education.html','education'),('research.html','research'),('publication--honors.html','publications'),('personal.html','personal')]:
    (ROOT / path).write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Yize Wang · {target.title()}</title><meta http-equiv="refresh" content="0;url=./index.html#{target}"></head><body><p>This page has moved. <a href="./index.html#{target}">Continue to {target}</a>.</p></body></html>\n')
print('Built index.html and four legacy page redirects.')
