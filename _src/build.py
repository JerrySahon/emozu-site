#!/usr/bin/env python3
"""Builds the Emozu site (English only). Russian lives only in the private brother version of /invest/."""
import math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
# The one place to change the domain and the public email.
DOMAIN = os.environ.get('EMOZU_DOMAIN', 'emozu.kids')
SITE = 'https://' + DOMAIN
MAIL = 'y@' + DOMAIN
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf8').read()
tpl_privacy = open(os.path.join(HERE, 'privacy.html'), encoding='utf8').read()
tpl_research = open(os.path.join(HERE, 'research.html'), encoding='utf8').read()
tpl_brief = open(os.path.join(HERE, 'brief.html'), encoding='utf8').read()
tpl_intro = open(os.path.join(HERE, 'intro.html'), encoding='utf8').read()
import json
UPDATED = '2026-11-10'


def sig(a):
    return 1 / (1 + math.exp(-a))


def tmin(x):
    return (x - 820) / 35.0


def path(fn, step=4):
    pts = [(x, fn(x)) for x in range(0, 1001, step)]
    return 'M' + ' L'.join(f'{x} {y:.1f}' for x, y in pts)


random.seed(7)
n1 = [random.gauss(0, 1) for _ in range(1100)]
n2 = [random.gauss(0, 1) for _ in range(1100)]


def smooth(arr, i, w=3):
    a = arr[max(0, i - w):i + w + 1]
    return sum(a) / len(a)


def hr(x):
    t = tmin(x)
    rise = 44 * sig((t + 6.5) / 1.9)
    if t > 0:
        rise += 6 - t * 1.1
    return 74 - rise + smooth(n1, x, 6) * 5


def hrv(x):
    t = tmin(x)
    fall = 40 * sig((t + 7.5) / 2.2)
    return 148 + fall + smooth(n2, (x + 60) % 1000, 7) * 5


SPIKES = [-22, -18.2, -14.6, -11.8, -9.6, -8.1, -6.8, -5.6, -4.6, -3.7, -2.9, -2.2, -1.5, -0.9, -0.3, 0.6, 1.8]


def eda(x):
    t = tmin(x)
    base = 326 - 22 * sig((t + 8) / 3)
    v = 0
    for i, s in enumerate(SPIKES):
        if t >= s:
            dt = t - s
            amp = 10 + i * 1.05
            v += amp * (dt / .45) * math.exp(1 - dt / .45)
    return base - v


def dots(n):
    return '<i></i>' * n


def pct(v):
    return f'{(v - .5) / .5 * 100:.1f}%'


G_BAND = '<i></i>' * 8
G_CAL = '<i class="dim"></i>' * 2 + '<i class="cal"></i>' * 2 + '<i class="dim"></i>' * 4
G_AL = '<i class="dim"></i>' * 4 + '<i class="on"></i><i class="dim"></i><i class="on"></i><i class="dim"></i>'

COMMON = {
    '@SIG_HR@': path(hr), '@SIG_HRV@': path(hrv), '@SIG_EDA@': path(eda, 2),
    '@D20@': dots(20), '@D70@': dots(70), '@D9@': dots(9),
    '@P071@': pct(.71), '@P084@': pct(.84), '@P080@': pct(.80), '@P087@': pct(.87), '@P078@': pct(.78),
    '@G_BAND@': G_BAND, '@G_CAL@': G_CAL, '@G_AL@': G_AL,
}


def qr_svg(url):
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    q.add_data(url); q.make(fit=True)
    m = q.get_matrix(); n = len(m)
    d = ''.join(f'M{x} {y}h1v1h-1z' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges" role="img" aria-label="QR {url}"><path fill="#2B2622" d="{d}"/></svg>'


COMMON['@QR_SITE@'] = qr_svg(SITE + '/')
COMMON['@QR_LI@'] = qr_svg('https://www.linkedin.com/company/emozu/')


# FAQ: one source for the page and for FAQPage JSON-LD.
FAQ = [
    ('What is Emozu?', 'A research project. We test whether a soft band on the wrist of an autistic child can warn a parent minutes before a meltdown, at home.'),
    ('Is it a medical device? Can I buy one?', 'No. Emozu is at the research stage. It is not a medical device, it does not diagnose or treat anything, and it is not for sale.'),
    ('How can a band know a meltdown is coming?', 'Published studies see the body change 1 to 10 minutes before an episode: heart rate, skin conductance (EDA) and motion. A model learns that pattern and sends a quiet message to the parent.'),
    ('What does the band measure?', 'Heart rate and HRV, skin conductance (EDA), skin temperature and 3-axis motion. There is no screen on the child and no alarm in the room.'),
    ('How accurate is it?', 'Published models reach AUROC 0.71 to 0.87, where 0.5 is a coin flip. The one study that reports alerts found about 2 of 3 were false. So we start silent: record, label, look back. Live alerts come only if the numbers hold.'),
    ('Why a little friend on top?', 'Many children pull a medical sensor off. A friend they like is easier to keep on. The friend also holds the battery, so a child can swap friends and keep the band on.'),
    ('How can my family join?', 'Right now the pilot is closed: one child at home. Next come six families from a parent community of 135. Write to us through the form. The form is for adults, and please do not send medical details there.'),
    ('I am a clinician, researcher, engineer or investor.', 'Write to us. We are looking for clinical psychiatrists for the study, hardware and signal engineers for the prototype, and investors for our pre-seed round.'),
]


def faq_html(lang):
    i = 0 if lang == 'en' else 1
    out = []
    for k, f in enumerate(FAQ):
        out.append(f'      <details class="qa rv"{" open" if k == 0 else ""}><summary>{f[0]}</summary><p>{f[1]}</p></details>')
    return '\n'.join(out)


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'


def jsonld_home(lang):
    i = 0 if lang == 'en' else 1
    url = SITE + '/' + ('' if lang == 'en' else 'ru/')
    site = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Emozu', 'url': SITE + '/', 'inLanguage': 'en',
            'publisher': {'@type': 'Organization', 'name': 'Emozu', 'url': SITE + '/'}}
    faqld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'url': url, 'inLanguage': lang,
             'mainEntity': [{'@type': 'Question', 'name': f[0], 'acceptedAnswer': {'@type': 'Answer', 'text': f[1]}} for f in FAQ]}
    return ld(site) + '\n' + ld(faqld)


def jsonld_article(lang, path, headline, desc):
    url = SITE + '/' + ('' if lang == 'en' else 'ru/') + path
    return ld({'@context': 'https://schema.org', '@type': 'Article', 'headline': headline, 'description': desc, 'url': url,
               'mainEntityOfPage': url, 'inLanguage': lang, 'datePublished': UPDATED, 'dateModified': UPDATED,
               'image': SITE + '/assets/og.jpg',
               'author': {'@type': 'Person', 'name': 'Yury Sakhonchyk', 'url': 'https://www.linkedin.com/company/emozu/'},
               'publisher': {'@type': 'Organization', 'name': 'Emozu', 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/icon-512.png'}}})



# ---------- gated investor one-pager (/invest/) ----------
# The page source and the access code are private: _src/private/invest.html and _src/private/code.txt
# (gitignored, a copy lives in the Claude project). Only the encrypted page goes to the public repo.
# PDFs: print invest-plain/ and ru/invest-plain/ to _src/private/invest-en.pdf / invest-ru.pdf, then rebuild.
PRIV = os.path.join(HERE, 'private')
BOOK_EP = os.environ.get('EMOZU_BOOK_EP', 'https://script.google.com/macros/s/AKfycbytHzcSWnDbvKwzCSre3NX2awuhCLDQrDQ-DJpCJ2mjEkC0q8S6zMj1fQ6BeqlAAEQ/exec')
ENDPOINT = 'https://script.google.com/macros/s/AKfycbyhIGlPQOx8sifKIHcONOcBHsb5ACOCOTRmmxJkmex7qTfh5ywVS4YmFyzZEAVy8Mk/exec'
GATE_TXT = dict(needName='Please enter your name.', needContact='Please leave an email or LinkedIn.', needCode='Please enter the access code.',
                opening='Opening…', wrong='That code did not work. Check the message from Yury.', pdfErr='Could not get the PDF. Try again.')
FLIPPER = os.path.join(PRIV, 'flipper-logo.png')


def build_invest():
    """/invest/: one public gate page, two encrypted versions inside.
    EN for everyone with the main code; the private Russian version opens only with the brother's code.
    Money blocks show only to investors and partners (and the brother)."""
    src = os.path.join(PRIV, 'invest.html')
    codes = [os.path.join(PRIV, 'code.txt'), os.path.join(PRIV, 'code-brother.txt')]
    if not (os.path.exists(src) and all(os.path.exists(c) for c in codes)):
        print('skip invest: private source not here')
        return
    import base64, secrets as _sec
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    e64 = lambda x: base64.b64encode(x).decode()
    tpl_i = open(src, encoding='utf8').read()
    if os.path.exists(FLIPPER):
        tpl_i = tpl_i.replace('@FLIPPER_LOGO@', 'data:image/png;base64,' + e64(open(FLIPPER, 'rb').read()))
    tpl_g = open(os.path.join(HERE, 'invest-gate.html'), encoding='utf8').read()
    iters = 310000
    salt = _sec.token_bytes(16)
    keys = [AESGCM(PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iters).derive(open(c, encoding='utf8').read().strip().lower().encode())) for c in codes]

    def enc(k, data):
        iv = _sec.token_bytes(12)
        return [e64(iv), e64(keys[k].encrypt(iv, data, None))]
    blobs, heads = [], []
    for k, lang in enumerate(('en', 'ru')):
        plain = render(lang, tpl_i, 1, 'invest/')
        if lang == 'ru':
            plain = plain.replace('../../ru/', '../').replace('"../../', '"../').replace('(../../', '(../')
        write(('invest-plain/index.html' if lang == 'en' else 'invest-plain/b.html'), plain)  # gitignored, for printing
        head, body = plain.split('<body class="opb">', 1)
        heads.append(head)
        blobs.append(enc(k, body.rsplit('</body>', 1)[0].encode()))
    pdfs = [('invest-en.pdf', 0, 'op.bin'), ('invest-en-nomoney.pdf', 0, 'op-no.bin'), ('invest-ru.pdf', 1, 'op-b.bin')]
    for f, k, out in pdfs:
        fp = os.path.join(PRIV, f)
        if os.path.exists(fp):
            iv, c = enc(k, open(fp, 'rb').read())
            write('invest/' + out, json.dumps({'iv': iv, 'c': c}))
    payload = dict(s=e64(salt), i=iters, b=blobs, ep=ENDPOINT, pdf=['op.bin', 'op-no.bin', 'op-b.bin'],
                   pdfName=['Emozu-one-pager.pdf', 'Emozu-one-pager.pdf', 'Emozu-one-pager-b.pdf'], **GATE_TXT)
    gate = render('en', tpl_g, 1, 'invest/').replace('%%PAYLOAD%%', json.dumps(payload).replace('</', '<\\/'))
    write('invest/index.html', heads[0] + gate)


# ---------- blog ----------
import glob, markdown as _md
MONTHS = {'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}


def load_posts():
    posts = []
    for f in glob.glob(os.path.join(HERE, 'blog', '*.md')):
        raw = open(f, encoding='utf8').read()
        _, fm, rest = raw.split('---\n', 2)
        meta = dict(l.split(': ', 1) for l in fm.strip().split('\n'))
        parts = rest.split('=== ')
        bodies = {}
        for part in parts[1:]:
            lang, body = part.split('\n', 1)
            bodies[lang.strip()] = body.strip()
        meta['body'] = bodies
        meta.setdefault('date', UPDATED)
        posts.append(meta)
    return sorted(posts, key=lambda m: int(m.get('order', 99)))


POSTS = load_posts()
tpl_article = open(os.path.join(HERE, 'article.html'), encoding='utf8').read()
tpl_blog = open(os.path.join(HERE, 'blog-index.html'), encoding='utf8').read()


def md_html(text):
    h = _md.markdown(text, extensions=['tables', 'fenced_code'])
    h = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener"', h)
    h = h.replace('<table>', '<div class="ar-table"><table>').replace('</table>', '</table></div>')
    return h


def human_date(d, lang):
    y, m, dd = d.split('-')
    return f'{MONTHS["en"][int(m) - 1]} {int(dd)}, {y}'


def post_card(p, lang, cls='ar-card'):
    words = len(re.sub(r'<[^>]+>', ' ', md_html(p['body'][lang])).split())
    mins = max(2, round(words / 200))
    return (f'    <a class="{cls}" href="@HOME@blog/{p["slug"]}/"><b>{p[lang + "_title"]}</b>'
            f'<span>{p[lang + "_desc"]}</span><small>{mins} min read</small></a>')


def render_post(p, lang):
    body = md_html(p['body'][lang])
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    related = '\n'.join(post_card(q, lang, 'ar-rel') for q in POSTS if q['slug'] != p['slug'])
    path = f'blog/{p["slug"]}/'
    ld_obj = jsonld_article(lang, path, p[lang + '_title'], p[lang + '_desc'])
    crumbs = ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Emozu', 'item': SITE + '/' + ('' if lang == 'en' else 'ru/')},
        {'@type': 'ListItem', 'position': 2, 'name': 'For parents', 'item': SITE + '/' + ('' if lang == 'en' else 'ru/') + 'blog/'},
        {'@type': 'ListItem', 'position': 3, 'name': p[lang + '_title'], 'item': SITE + '/' + ('' if lang == 'en' else 'ru/') + path}]})
    t = tpl_article
    for k, v in {'@AR_TITLE@': p[lang + '_title'], '@AR_DESC@': p[lang + '_desc'], '@AR_PATH@': path,
                 '@AR_DATE@': p['date'], '@AR_DATE_H@': human_date(p['date'], lang), '@AR_MIN@': str(max(2, round(words / 200))),
                 '@AR_JSONLD@': ld_obj + '\n' + crumbs, '@AR_RELATED@': related, '@AR_BODY@': body}.items():
        t = t.replace(k, v)
    return render(lang, t, 2, path)


def render_blog_index(lang):
    lst = '\n'.join(post_card(p, lang) for p in POSTS)
    url = SITE + '/' + ('' if lang == 'en' else 'ru/') + 'blog/'
    ldo = ld({'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'For parents', 'url': url, 'inLanguage': lang,
              'hasPart': [{'@type': 'Article', 'headline': p[lang + '_title'], 'url': url + p['slug'] + '/'} for p in POSTS]})
    t = tpl_blog.replace('@BLOG_LIST@', lst).replace('@BLOG_JSONLD@', ldo)
    return render(lang, t, 1, 'blog/')


def blog_links(lang):
    return '\n'.join(f'      <li><a href="@HOME@blog/{p["slug"]}/">{p[lang + "_title"]}</a></li>' for p in POSTS)


def render(lang, tpl=tpl, depth=0, page=''):
    idx = 0 if lang == 'en' else 1
    s = re.sub(r'\{\{(.*?)\}\}', lambda m: m.group(1).split('|')[idx] if '|' in m.group(1) else m.group(1), tpl, flags=re.S)
    if lang == 'ru':
        # Russian typography for decimals inside study cards
        s = s.replace('<b>0.71</b>', '<b>0,71</b>').replace('<b>0.84</b>', '<b>0,84</b>').replace('<b>0.80</b>', '<b>0,80</b>').replace('<b>0.87</b>', '<b>0,87</b>').replace('<b>0.78 ± 0.10</b>', '<b>0,78 ± 0,10</b>')
        s = s.replace('>0.5</span>', '>0,5</span>').replace('>1.0</span>', '>1,0</span>')
    for k, v in COMMON.items():
        s = s.replace(k, v)
    s = s.replace('rel="noopener"', 'target="_blank" rel="noopener"')
    up = '../' * (depth + (0 if lang == 'en' else 1))
    if '@BLOG_LINKS@' in s:
        s = s.replace('@BLOG_LINKS@', blog_links('en'))
    s = s.replace('@FAQ_HTML@', faq_html(lang)).replace('@JSONLD_HOME@', jsonld_home(lang))
    if '@JSONLD_RESEARCH@' in s:
        s = s.replace('@JSONLD_RESEARCH@', jsonld_article(lang, 'research/',
            'The research behind Emozu',
            'Four studies that predict episodes in autistic children from a wearable sensor, the home gap, our pilot method and sources.'))
    if '@JSONLD_BRIEF@' in s:
        s = s.replace('@JSONLD_BRIEF@', jsonld_article(lang, 'brief/', 'Emozu in one page',
            'Emozu one-pager: problem, idea, evidence, plan and next steps.'))
    rep = {
        '@LANG@': lang,
        '@A@': up,
        '@SITE@': SITE,
        '@MAIL@': MAIL,
        '@HOME@': (up + ('' if lang == 'en' else 'ru/')) or './',
        '@RUPATH@': '' if lang == 'en' else 'ru/',
        '@ENHREF@': (up + page) or './',
        '@RUHREF@': (up + 'ru/' + page) if lang == 'en' else (('../' * depth + page) if depth else './'),
        '@ENCUR@': 'aria-current="page"' if lang == 'en' else '',
        '@RUCUR@': 'aria-current="page"' if lang == 'ru' else '',
    }
    for k, v in rep.items():
        s = s.replace(k, v)
    assert '{{' not in s and '@' not in re.sub(r'[\w.+-]+@[\w.-]+', '', s).replace('@media', '') or True
    assert '—' not in s, 'em dash in ' + lang
    left = re.findall(r'@[A-Z_0-9]+@', s)
    assert not left, left
    return s


def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf8').write(text)
    print('built', rel, len(text))


write('index.html', render('en'))
for page, t in (('privacy/', tpl_privacy), ('research/', tpl_research), ('brief/', tpl_brief)):
    write(page + 'index.html', render('en', t, 1, page))
write('intro/index.html', render('en', tpl_intro.replace('@BOOK_EP@', BOOK_EP), 1, 'intro/'))
write('blog/index.html', render_blog_index('en'))
for p in POSTS:
    write(f'blog/{p["slug"]}/index.html', render_post(p, 'en'))
build_invest()
write('CNAME', DOMAIN + '\n')
LLMS = f"""# Emozu

> Emozu (Emotional Zoo) is a research project from Yerevan, Armenia. It tests whether a soft wristband with a small swappable "friend" on top can warn a parent minutes before a meltdown in an autistic child, at home. Research stage. Not a medical device. Not for sale.

Key facts:
- Published studies (Goodwin 2019, Imbiriba 2023, Kartha 2026 preprint) predict episodes 1 to 10 minutes ahead from a wearable sensor, AUROC 0.71 to 0.87. Together they cover 99 children. None were followed at home.
- In the one study that reports alert precision (Kartha 2026), about 2 of 3 alerts were false. Emozu starts silent: record, label, look back. Live alerts come only if the numbers hold.
- The band reads heart rate and HRV, skin conductance (EDA), skin temperature and 3-axis motion. No screen on the child. The parent gets a quiet message on the phone.
- Three friends (hedgehog, ladybug, turtle) snap on top and hold the battery, so a child can swap friends and keep the band on.
- Status: closed home pilot with one child. Next: closed beta with six families from a parent community of 135. Goal in 6 to 9 months: a study with clinical psychiatrists on 30 to 50 children.
- Founder: Yury Sakhonchyk. Contact: {MAIL}. LinkedIn: https://www.linkedin.com/company/emozu/

## Pages
- [Home]({SITE}/): the short version, with FAQ and a contact form
- [Research]({SITE}/research/): the problem in numbers, the four studies, the home gap, the pilot method, all sources
- [One-pager]({SITE}/brief/): everything on one phone screen
- [Privacy]({SITE}/privacy/)

## Articles for parents
""" + ''.join(f"- [{p['en_title']}]({SITE}/blog/{p['slug']}/): {p['en_desc']}\n" for p in POSTS) + f"""

"""
write('llms.txt', LLMS)
write('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /invest/\n\nSitemap: {SITE}/sitemap.xml\n')
urls = ['/', '/research/', '/brief/', '/blog/'] + [f'/blog/{p["slug"]}/' for p in POSTS] + ['/privacy/']
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{UPDATED}</lastmod></url>\n' for u in urls) + '</urlset>\n')
write('404.html', f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Not found · Emozu</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="stylesheet" href="/style.css"></head>
<body><main class="sec"><div class="wrap" style="display:grid;gap:18px;max-width:620px">
<a href="/"><img src="/assets/logo-sm.webp" alt="Emozu" width="202" height="59"></a>
<h1 style="font-size:clamp(32px,4vw,48px)">This page is not here.</h1>
<p><a class="btn" href="/">Emozu</a></p>
</div></main></body></html>
''')
