#!/usr/bin/env python3
"""Builds /emozu/index.html and /emozu/ru/index.html from one template."""
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


# FAQ: one source for the page and for FAQPage JSON-LD.
FAQ = [
    ('What is Emozu?', 'Что такое Emozu?',
     'A research project. We test whether a soft band on the wrist of an autistic child can warn a parent minutes before a meltdown, at home.',
     'Исследовательский проект. Мы проверяем, может ли мягкий браслет на руке ребёнка с аутизмом предупредить родителя за минуты до срыва, дома.'),
    ('Is it a medical device? Can I buy one?', 'Это медицинское изделие? Можно купить?',
     'No. Emozu is at the research stage. It is not a medical device, it does not diagnose or treat anything, and it is not for sale.',
     'Нет. Emozu на стадии исследования. Это не медицинское изделие, оно ничего не диагностирует и не лечит, и оно не продаётся.'),
    ('How can a band know a meltdown is coming?', 'Как браслет может знать, что скоро срыв?',
     'Published studies see the body change 1 to 10 minutes before an episode: heart rate, skin conductance (EDA) and motion. A model learns that pattern and sends a quiet message to the parent.',
     'Опубликованные работы видят, как тело меняется за 1–10 минут до эпизода: пульс, проводимость кожи (ЭДА) и движение. Модель учит этот рисунок и отправляет родителю тихое сообщение.'),
    ('What does the band measure?', 'Что измеряет браслет?',
     'Heart rate and HRV, skin conductance (EDA), skin temperature and 3-axis motion. There is no screen on the child and no alarm in the room.',
     'Пульс и вариабельность пульса, проводимость кожи (ЭДА), температуру кожи и движение по 3 осям. На ребёнке нет экрана, в комнате нет сигнала тревоги.'),
    ('How accurate is it?', 'Насколько это точно?',
     'Published models reach AUROC 0.71 to 0.87, where 0.5 is a coin flip. The one study that reports alerts found about 2 of 3 were false. So we start silent: record, label, look back. Live alerts come only if the numbers hold.',
     'Опубликованные модели дают AUROC 0,71–0,87, где 0,5 это монетка. Единственная работа, которая считает тревоги, нашла, что примерно 2 из 3 были ложными. Поэтому мы начинаем с тишины: записываем, размечаем, смотрим назад. Живые предупреждения будут, только если цифры выдержат.'),
    ('Why a little friend on top?', 'Зачем маленький друг сверху?',
     'Many children pull a medical sensor off. A friend they like is easier to keep on. The friend also holds the battery, so a child can swap friends and keep the band on.',
     'Многие дети снимают медицинский датчик. Друга, который нравится, носить легче. В друге ещё и аккумулятор, поэтому ребёнок меняет друзей, а браслет остаётся на руке.'),
    ('How can my family join?', 'Как нашей семье подключиться?',
     'Right now the pilot is closed: one child at home. Next come six families from a parent community of 135. Write to us through the form. The form is for adults, and please do not send medical details there.',
     'Сейчас пилот закрытый: один ребёнок дома. Дальше шесть семей из родительского сообщества на 135 семей. Напишите нам через форму. Форма для взрослых, и, пожалуйста, без медицинских данных.'),
    ('I am a clinician, researcher, engineer or investor.', 'Я врач, исследователь, инженер или инвестор.',
     'Write to us. We are looking for clinical psychiatrists for the study, hardware and signal engineers for the prototype, and a $200K pre-seed.',
     'Напишите нам. Мы ищем клинических психиатров для исследования, инженеров по железу и сигналу для прототипа и $200K pre-seed.'),
]


def faq_html(lang):
    i = 0 if lang == 'en' else 1
    out = []
    for k, f in enumerate(FAQ):
        out.append(f'      <details class="qa rv"{" open" if k == 0 else ""}><summary>{f[i]}</summary><p>{f[2 + i]}</p></details>')
    return '\n'.join(out)


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'


def jsonld_home(lang):
    i = 0 if lang == 'en' else 1
    url = SITE + '/' + ('' if lang == 'en' else 'ru/')
    site = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Emozu', 'url': SITE + '/', 'inLanguage': ['en', 'ru'],
            'publisher': {'@type': 'Organization', 'name': 'Emozu', 'url': SITE + '/'}}
    faqld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'url': url, 'inLanguage': lang,
             'mainEntity': [{'@type': 'Question', 'name': f[i], 'acceptedAnswer': {'@type': 'Answer', 'text': f[2 + i]}} for f in FAQ]}
    return ld(site) + '\n' + ld(faqld)


def jsonld_article(lang, path, headline, desc):
    url = SITE + '/' + ('' if lang == 'en' else 'ru/') + path
    return ld({'@context': 'https://schema.org', '@type': 'Article', 'headline': headline, 'description': desc, 'url': url,
               'mainEntityOfPage': url, 'inLanguage': lang, 'datePublished': UPDATED, 'dateModified': UPDATED,
               'image': SITE + '/assets/og.jpg',
               'author': {'@type': 'Person', 'name': 'Yury Sakhonchyk', 'url': 'https://www.linkedin.com/company/emozu/'},
               'publisher': {'@type': 'Organization', 'name': 'Emozu', 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/icon-512.png'}}})


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
    s = s.replace('@FAQ_HTML@', faq_html(lang)).replace('@JSONLD_HOME@', jsonld_home(lang))
    if '@JSONLD_RESEARCH@' in s:
        s = s.replace('@JSONLD_RESEARCH@', jsonld_article(lang, 'research/',
            ['The research behind Emozu', 'Исследование Emozu'][idx],
            ['Four studies that predict episodes in autistic children from a wearable sensor, the home gap, our pilot method and sources.',
             'Четыре работы, которые предсказывают эпизоды у детей с аутизмом по носимому датчику, пробел дома, метод пилота и источники.'][idx]))
    if '@JSONLD_BRIEF@' in s:
        s = s.replace('@JSONLD_BRIEF@', jsonld_article(lang, 'brief/', ['Emozu in one page', 'Emozu на одной странице'][idx],
            ['Emozu one-pager: problem, idea, evidence, plan and ask.', 'Emozu одной страницей: проблема, идея, данные, план и запрос.'][idx]))
    rep = {
        '@LANG@': lang,
        '@A@': up,
        '@SITE@': SITE,
        '@MAIL@': MAIL,
        '@HOME@': (up + ('' if lang == 'en' else 'ru/')) or './',
        '@RUPATH@': '' if lang == 'en' else 'ru/',
        '@ENHREF@': (up + page) or './',
        '@RUHREF@': (up + 'ru/' + page) if lang == 'en' else ('../' + page if depth else './'),
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
for page, t in (('privacy/', tpl_privacy), ('research/', tpl_research), ('brief/', tpl_brief)):
    write(page + 'index.html', render('en', t, 1, page))
    write('ru/' + page + 'index.html', render('ru', t, 1, page))
write('CNAME', DOMAIN + '\n')
LLMS = f"""# Emozu

> Emozu (Emotional Zoo) is a research project from Yerevan, Armenia. It tests whether a soft wristband with a small swappable "friend" on top can warn a parent minutes before a meltdown in an autistic child, at home. Research stage. Not a medical device. Not for sale.

Key facts:
- Published studies (Goodwin 2019, Imbiriba 2023, Kartha 2026 preprint) predict episodes 1 to 10 minutes ahead from a wearable sensor, AUROC 0.71 to 0.87. Together they cover 99 children. None were followed at home.
- In the one study that reports alert precision (Kartha 2026), about 2 of 3 alerts were false. Emozu starts silent: record, label, look back. Live alerts come only if the numbers hold.
- The band reads heart rate and HRV, skin conductance (EDA), skin temperature and 3-axis motion. No screen on the child. The parent gets a quiet message on the phone.
- Seven friends (lamb, turtle, ladybug, hedgehog, whale, firefly, fox) snap on top and hold the battery, so a child can swap friends and keep the band on.
- Status: closed home pilot with one child. Next: closed beta with six families from a parent community of 135. Goal in 6 to 9 months: a study with clinical psychiatrists on 30 to 50 people. Raising $200K pre-seed.
- Founder: Yury Sakhonchyk. Contact: {MAIL}. LinkedIn: https://www.linkedin.com/company/emozu/

## Pages
- [Home]({SITE}/): the short version, with FAQ and a contact form
- [Research]({SITE}/research/): the problem in numbers, the four studies, the home gap, the pilot method, all sources
- [One-pager]({SITE}/brief/): everything on one phone screen
- [Privacy]({SITE}/privacy/)

## Russian
- [Главная]({SITE}/ru/)
- [Исследование]({SITE}/ru/research/)
- [Одна страница]({SITE}/ru/brief/)
"""
write('llms.txt', LLMS)
write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
urls = ['/', '/ru/', '/research/', '/ru/research/', '/brief/', '/ru/brief/', '/privacy/', '/ru/privacy/']
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{UPDATED}</lastmod></url>\n' for u in urls) + '</urlset>\n')
write('404.html', f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Not found · Emozu</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="stylesheet" href="/style.css"></head>
<body><main class="sec"><div class="wrap" style="display:grid;gap:18px;max-width:620px">
<a href="/"><img src="/assets/logo-sm.webp" alt="Emozu" width="202" height="59"></a>
<h1 style="font-size:clamp(32px,4vw,48px)">This page is not here.</h1>
<p class="lead">Такой страницы нет.</p>
<p><a class="btn" href="/">Emozu</a> &nbsp; <a class="btn ghost" href="/ru/">Emozu по-русски</a></p>
</div></main></body></html>
''')
