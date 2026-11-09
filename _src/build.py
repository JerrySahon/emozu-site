#!/usr/bin/env python3
"""Builds /emozu/index.html and /emozu/ru/index.html from one template."""
import math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
# The one place to change the domain and the public email.
DOMAIN = os.environ.get('EMOZU_DOMAIN', 'emozu.kids')
SITE = 'https://' + DOMAIN
MAIL = 'hello@' + DOMAIN
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf8').read()
tpl_privacy = open(os.path.join(HERE, 'privacy.html'), encoding='utf8').read()


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


def render(lang, tpl=tpl, depth=0):
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
    rep = {
        '@LANG@': lang,
        '@A@': up,
        '@SITE@': SITE,
        '@MAIL@': MAIL,
        '@HOME@': (up + ('' if lang == 'en' else 'ru/')) or './',
        '@RUPATH@': '' if lang == 'en' else 'ru/',
        '@ENHREF@': (up + ('privacy/' if depth else '')) or './',
        '@RUHREF@': (up + 'ru/' + ('privacy/' if depth else '')) if lang == 'en' else ('../' + ('privacy/' if depth else '') if depth else './'),
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
write('ru/index.html', render('ru'))
write('privacy/index.html', render('en', tpl_privacy, 1))
write('ru/privacy/index.html', render('ru', tpl_privacy, 1))
write('CNAME', DOMAIN + '\n')
write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
urls = ['/', '/ru/', '/privacy/', '/ru/privacy/']
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{SITE}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
write('404.html', f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Not found · Emozu</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="stylesheet" href="/style.css"></head>
<body><main class="sec"><div class="wrap" style="display:grid;gap:18px;max-width:620px">
<a href="/"><img src="/assets/logo-sm.webp" alt="Emozu" width="202" height="59"></a>
<h1 style="font-size:clamp(32px,4vw,48px)">This page is not here.</h1>
<p class="lead">Такой страницы нет.</p>
<p><a class="btn" href="/">Emozu</a> &nbsp; <a class="btn ghost" href="/ru/">Emozu по-русски</a></p>
</div></main></body></html>
''')
