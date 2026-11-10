#!/usr/bin/env python3
"""Personal one-pager links and the public /investors/ page, both built from the live /invest/ one-pager.

Run after build.py:   python3 _src/share_pages.py

- /investors/  The one-pager without money, plus an investor terms form. Rows go to the applications
               sheet (page "investors", or "investors via <ref>" when the link came from a share).
- /v/<id>/     A personal copy with money for one person, encrypted. The key travels only in the
               link's #fragment, so the public repo holds ciphertext only. Opens instantly, no form.
               At the bottom: Share, which sends https://emozu.kids/investors/?ref=<ref>.

People live in _src/private/people.json (gitignored):
  [{"name": "Sveta", "ref": "sveta", "id": "cvu4pn3x", "key": "<22 chars base64url>"}]
Personal link: https://emozu.kids/v/<id>/#<key>
Needs _src/private/code.txt (the /invest/ code) to read the current one-pager.
"""
import base64, json, os, re, secrets, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
PRIV = os.path.join(HERE, 'private')
SITE = 'https://emozu.kids'
EP = 'https://script.google.com/macros/s/AKfycbyhIGlPQOx8sifKIHcONOcBHsb5ACOCOTRmmxJkmex7qTfh5ywVS4YmFyzZEAVy8Mk/exec'
MAIL = 'y@emozu.kids'
SHARE_TEXT = "Emozu: a soft band that warns a parent minutes before an autistic child's meltdown."

e64 = lambda b: base64.b64encode(b).decode()


def b64u_dec(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def write(rel, data):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = 'wb' if isinstance(data, bytes) else 'w'
    with open(path, mode, **({} if isinstance(data, bytes) else {'encoding': 'utf8'})) as f:
        f.write(data)


def read_invest():
    """Decrypt the English one-pager and both PDFs from the built /invest/."""
    code = open(os.path.join(PRIV, 'code.txt'), encoding='utf8').read().strip().lower().encode()
    s = open(os.path.join(OUT, 'invest', 'index.html'), encoding='utf8').read()
    head = s.split('<body', 1)[0]
    p = json.loads(re.search(r'<script type="application/json" id="op-payload">(.*?)</script>', s, re.S).group(1).replace('<\\/', '</'))
    k = AESGCM(PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(p['s']), iterations=p['i']).derive(code))
    dec = lambda iv, c: k.decrypt(base64.b64decode(iv), base64.b64decode(c), None)
    body = dec(*p['b'][0]).decode()
    pdf = {}
    for name in ('op.bin', 'op-no.bin'):
        o = json.load(open(os.path.join(OUT, 'invest', name)))
        pdf[name] = dec(o['iv'], o['c'])
    return head, body, pdf


def strip_scripts(html):
    return re.sub(r'<script\b.*?</script>\s*', '', html, flags=re.S)


def deepen(html):
    """Paths built for /invest/ (one level) to a page two levels down."""
    return re.sub(r'((?:src|href)=")\.\./', r'\1../../', html)


def set_meta(head, title, desc, url, robots):
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + desc, head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + title, head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + desc, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', r'\g<1>' + url, head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', r'\g<1>' + url, head)
    head = re.sub(r'(<meta name="robots" content=")[^"]*', r'\g<1>' + robots, head)
    return head


CSS = """<style>
.op-hero-cta{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
@media screen and (max-width:759px){.op-hero-cta{order:6;margin-top:14px}}
.op-share,.op-join{display:grid;gap:12px;margin-top:12px;padding:20px 18px;border-radius:22px;background:#fff;box-shadow:var(--shadow)}
.op-share p,.op-join-lead{font-size:15px;line-height:1.5;color:var(--ink2)}
.op-join-lead{margin-top:8px}
.op-share-row{display:flex;flex-wrap:wrap;gap:8px}
.op-share-to{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.op-share-to a{display:inline-flex;align-items:center;min-height:40px;padding:0 14px;border-radius:99px;box-shadow:inset 0 0 0 1.5px var(--line2);font-size:14.5px;font-weight:550;color:var(--ink);text-decoration:none;transition:box-shadow .2s}
.op-share-to a:hover{box-shadow:inset 0 0 0 1.5px var(--ink)}
.op-share-url{font-size:13px;color:var(--ink3);word-break:break-all}
.op-share-ok{min-height:1.2em;font-size:13.5px;font-weight:650;color:var(--sage-ink)}
.op-share-ok:empty{min-height:0}
.op-join form{display:grid;gap:16px}
.op-join-two{display:grid;gap:16px}
.op-join .gate-f span small,.op-join legend small{font-weight:500;color:var(--ink3)}
.op-join textarea{font:500 16px/1.45 Onest,system-ui,sans-serif;color:var(--ink);padding:12px 14px;border-radius:14px;border:1.5px solid var(--line2);background:var(--bg);outline:none;min-height:88px;width:100%;resize:vertical}
.op-join textarea:focus{border-color:var(--ink);background:#fff}
.op-join input::placeholder,.op-join textarea::placeholder{color:#A69C92}
.op-join .bad input,.op-join fieldset.bad span{box-shadow:inset 0 0 0 1.5px var(--coral)}
.op-join .gate-f.bad input{border-color:var(--coral)}
.op-hint{flex-basis:100%;margin-top:4px;font-size:12.5px;line-height:1.45;color:var(--ink3)}
.op-hint b{color:var(--ink2);font-weight:650}
.op-join-ok{display:grid;gap:12px;padding:18px;border-radius:16px;background:var(--sage-wash);color:var(--sage-ink);font-size:15.5px;line-height:1.5}
.op-join-ok b{color:var(--ink)}
.op-join .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.v-wait{min-height:70vh;display:grid;place-items:center;padding:24px;text-align:center}
.v-wait div{display:grid;gap:12px;justify-items:center;max-width:420px}
.v-wait p{font-size:15.5px;line-height:1.5;color:var(--ink2)}
.v-spin{width:28px;height:28px;border-radius:50%;border:3px solid var(--line2);border-top-color:var(--ink);animation:vspin .8s linear infinite}
@keyframes vspin{to{transform:rotate(1turn)}}
@media (min-width:760px){.op-share,.op-join{grid-template-columns:230px minmax(0,1fr);gap:26px;padding:24px 26px}.op-share h2,.op-join h2{font-size:24px}.op-join-two{grid-template-columns:1fr 1fr}}
html.mo .mo-rv{opacity:0;transform:translateY(18px);transition:opacity .7s ease,transform .8s cubic-bezier(.2,.7,.2,1)}
html.mo .mo-rv.in{opacity:1;transform:none}
html.mo .op-bar-t i{transform:scaleX(0);transform-origin:left center;transition:transform 1.3s cubic-bezier(.2,.7,.2,1) .3s}
html.mo .in .op-bar-t i{transform:none}
html.mo .op-bar b{opacity:0;transition:opacity .5s ease 1.2s}
html.mo .in .op-bar b{opacity:1}
html.mo .op-dots i{opacity:0;transform:scale(.2);transition:opacity .25s ease,transform .45s cubic-bezier(.3,1.6,.5,1)}
html.mo .in .op-dots i{opacity:1;transform:none}
html.mo .op-dots div.h i{animation:none}
html.mo .in .op-dots div.h i{animation:mopulse 1.8s ease-in-out 1.6s 3}
@keyframes mopulse{50%{box-shadow:inset 0 0 0 1.5px var(--blue),0 0 0 6px var(--blue-wash)}}
html.mo .op-sig svg{clip-path:inset(0 100% 0 0);transition:clip-path 2.4s cubic-bezier(.45,0,.2,1) .25s}
html.mo .in .op-sig svg{clip-path:inset(0 0 0 0)}
html.mo .op-sig-band,html.mo .op-sig-w,html.mo .op-sig-e{opacity:0;transition:opacity .7s ease 1.6s}
html.mo .in .op-sig-band,html.mo .in .op-sig-w,html.mo .in .op-sig-e{opacity:1}
html.mo .op-tl::before{transform:scaleX(0);transform-origin:left center;transition:transform 1.4s cubic-bezier(.2,.7,.2,1) .2s}
html.mo .in .op-tl::before{transform:none}
html.mo .op-tl li,html.mo .op-steps li,html.mo .op-plan li{opacity:0;transform:translateY(10px);transition:opacity .55s ease,transform .6s cubic-bezier(.2,.7,.2,1)}
html.mo .in .op-tl li,html.mo .in .op-steps li,html.mo .in .op-plan li{opacity:1;transform:none}
@media print{html.mo .mo-rv,html.mo .op-tl li,html.mo .op-steps li,html.mo .op-plan li,html.mo .op-dots i{opacity:1!important;transform:none!important}html.mo .op-bar-t i,html.mo .op-tl::before{transform:none!important}html.mo .op-sig svg{clip-path:none!important}.op-share,.op-join,.op-hero-cta{display:none!important}}
</style>
"""

# Shared page script: scroll motion, the floating button, sharing.
JS_COMMON = r"""
var $$ = function(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
function motion(){
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('mo');
  var els = $$('.op-hero-txt > *:not(.op-print-logo), .op-hero-fig, .op-row, .op-gal figure, .op-ask, .op-share, .op-join, .op-foot');
  els.forEach(function(el){ el.classList.add('mo-rv'); });
  $$('.op-hero-txt > *').forEach(function(el, i){ el.style.transitionDelay = (i * 90) + 'ms'; });
  $$('.op-gal figure').forEach(function(el, i){ el.style.transitionDelay = (i * 130) + 'ms'; });
  $$('.op-dots div').forEach(function(d){ $$('i', d).forEach(function(el, k){ el.style.transitionDelay = (250 + k * 13) + 'ms'; }); });
  $$('.op-tl li').forEach(function(el, i){ el.style.transitionDelay = (350 + i * 170) + 'ms'; });
  $$('.op-steps li, .op-plan li').forEach(function(el){ var i = Array.prototype.indexOf.call(el.parentNode.children, el); el.style.transitionDelay = (150 + i * 130) + 'ms'; });
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (!e.isIntersecting) return; e.target.classList.add('in'); io.unobserve(e.target); countUp(e.target); });
  }, { rootMargin: '0px 0px -8% 0px', threshold: .12 });
  els.forEach(function(el){ io.observe(el); });
}
function countUp(root){
  $$('.op-steps b', root).forEach(function(b, i){
    var t = b.textContent.trim(); if (!/^\d+$/.test(t) || +t < 3) return;
    var n = +t, t0 = 0; b.textContent = '0';
    setTimeout(function(){ requestAnimationFrame(function f(ts){ if (!t0) t0 = ts; var p = Math.min(1, (ts - t0) / 1300); b.textContent = Math.round(n * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(f); }); }, 200 + i * 130);
  });
}
function fab(target){
  var f = document.querySelector('.op-fab'), t = document.querySelector(target);
  if (!f || !t) return;
  var tin = false, upd = function(){ f.classList.toggle('off', tin || window.scrollY < 520); };
  if ('IntersectionObserver' in window) new IntersectionObserver(function(e){ tin = e[0].isIntersecting; upd(); }, { threshold: .05 }).observe(t);
  window.addEventListener('scroll', upd, { passive: true }); upd();
}
function share(url){
  var box = document.querySelector('.op-share'); if (!box) return;
  var ok = $$('.op-share-ok', box)[0], text = __TEXT__, enc = encodeURIComponent;
  var say = function(m){ ok.textContent = m; setTimeout(function(){ ok.textContent = ''; }, 2600); };
  var copy = function(){
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject())
      .then(function(){ say('Link copied.'); })
      .catch(function(){ var r = document.createRange(); r.selectNodeContents($$('.op-share-url', box)[0]); var s = getSelection(); s.removeAllRanges(); s.addRange(r); say('Link selected, copy it.'); });
  };
  $$('[data-share]', box).forEach(function(b){ b.addEventListener('click', function(){
    if (navigator.share) navigator.share({ title: 'Emozu', text: text, url: url }).catch(function(){}); else copy();
  }); });
  $$('[data-copy]', box).forEach(function(b){ b.addEventListener('click', copy); });
  var to = { tg: 'https://t.me/share/url?url=' + enc(url) + '&text=' + enc(text),
             wa: 'https://wa.me/?text=' + enc(text + ' ' + url),
             li: 'https://www.linkedin.com/sharing/share-offsite/?url=' + enc(url),
             mail: 'mailto:?subject=' + enc('Emozu') + '&body=' + enc(text + '\n\n' + url) };
  $$('[data-to]', box).forEach(function(a){ a.href = to[a.getAttribute('data-to')]; });
}
function post(body){
  return fetch(__EP__, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(body) });
}
""".replace('__TEXT__', json.dumps(SHARE_TEXT)).replace('__EP__', json.dumps(EP))


def share_block(url, who):
    shown = url.replace('https://', '')
    return f"""
  <section class="op-share" id="share" aria-labelledby="share-h">
    <div><span class="op-lab">Share</span><h2 id="share-h">Know someone who should see this?</h2></div>
    <div>
      <p>Send them Emozu. They get this page without the numbers and can tell us on what terms they would join.</p>
      <div class="op-share-row" style="margin-top:12px"><button class="btn" type="button" data-share>Share Emozu</button><button class="btn ghost" type="button" data-copy>Copy link</button></div>
      <ul class="op-share-to" style="margin-top:12px" aria-label="Send with">
        <li><a data-to="tg" target="_blank" rel="noopener">Telegram</a></li><li><a data-to="wa" target="_blank" rel="noopener">WhatsApp</a></li><li><a data-to="li" target="_blank" rel="noopener">LinkedIn</a></li><li><a data-to="mail">Email</a></li>
      </ul>
      <p class="op-share-url" style="margin-top:10px">{shown}</p>
      <p class="op-share-ok" role="status" aria-live="polite"></p>
    </div>
  </section>
"""


def chips(name, items, kind='radio', checked=None):
    out = []
    for v in items:
        c = ' checked' if v == checked else ''
        out.append(f'<label><input type="{kind}" name="{name}" value="{v}"{c}><span>{v}</span></label>')
    return ''.join(out)


JOIN = f"""
  <section class="op-join" id="join" aria-labelledby="join-h">
    <div><span class="op-lab">Join the round</span><h2 id="join-h">On what terms would you join?</h2>
      <p class="op-join-lead">We are raising a pre-seed round. Tell us how you would like to take part. Yury replies within 48 hours.</p></div>
    <form id="join-form" novalidate>
      <div class="op-join-two">
        <label class="gate-f"><span>Name</span><input name="name" autocomplete="name" required></label>
        <label class="gate-f"><span>Email, Telegram or LinkedIn</span><input name="contact" autocomplete="email" autocapitalize="none" spellcheck="false" required></label>
      </div>
      <label class="gate-f"><span>Company or fund <small>optional</small></span><input name="org" autocomplete="organization"></label>
      <fieldset class="gate-roles"><legend>You are</legend>{chips('type', ['Angel', 'Fund', 'Family office', 'Company', 'Clinic or hospital', 'Other'])}</fieldset>
      <fieldset class="gate-roles" data-need="ticket"><legend>Ticket</legend>{chips('ticket', ['Under $10K', '$10K to $25K', '$25K to $50K', '$50K to $100K', '$100K+'])}</fieldset>
      <fieldset class="gate-roles"><legend>How you would invest</legend>{chips('instrument', ['SAFE', 'Convertible note', 'Equity', 'Not sure yet'], checked='Not sure yet')}
        <p class="op-hint"><b>SAFE:</b> shares later, at the next round, with a cap or a discount. <b>Convertible note:</b> a loan that turns into shares. <b>Equity:</b> shares now, at an agreed valuation.</p></fieldset>
      <label class="gate-f"><span>Your terms <small>optional</small></span><input name="terms" placeholder="Valuation cap, discount, pro-rata, board seat"></label>
      <fieldset class="gate-roles"><legend>When</legend>{chips('when', ['Now', 'In 1 to 3 months', 'At the next round'])}</fieldset>
      <fieldset class="gate-roles"><legend>Beyond money <small>pick any</small></legend>{chips('help', ['Clinics and hospitals', 'Hardware and manufacturing', 'Sales and distribution', 'Intros to investors', 'Advice'], kind='checkbox')}</fieldset>
      <label class="gate-f"><span>Anything else <small>optional</small></span><textarea name="note" rows="3"></textarea></label>
      <div class="hp" aria-hidden="true"><label>Company <input name="company" tabindex="-1" autocomplete="off"></label></div>
      <p class="op-cta" style="display:flex"><button class="btn" type="submit">Send</button></p>
      <p class="gate-err" role="alert" aria-live="polite"></p>
      <p class="gate-fine">Not a commitment and not an offer of securities. We use this only to reply to you. <a href="../privacy/">How we handle it</a></p>
    </form>
  </section>
"""

JS_JOIN = r"""
(function(){
  var f = document.getElementById('join-form'); if (!f) return;
  var err = f.querySelector('.gate-err'), ref = (new URLSearchParams(location.search).get('ref') || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 30);
  var val = function(n){ var x = f.querySelector('input[name="' + n + '"]:checked'); return x ? x.value : ''; };
  var vals = function(n){ return $$('input[name="' + n + '"]:checked', f).map(function(x){ return x.value; }); };
  var bad = function(el, msg){ el.classList.add('bad'); err.textContent = msg; var i = el.querySelector('input'); if (i) i.focus(); el.scrollIntoView({ block: 'center', behavior: 'smooth' }); };
  f.addEventListener('input', function(e){ var b = e.target.closest('.bad'); if (b) { b.classList.remove('bad'); err.textContent = ''; } });
  f.addEventListener('change', function(e){ var b = e.target.closest('.bad'); if (b) { b.classList.remove('bad'); err.textContent = ''; } });
  f.addEventListener('submit', function(e){
    e.preventDefault();
    var el = f.elements, name = el.name.value.trim(), contact = el.contact.value.trim();
    if (!name) return bad(el.name.closest('.gate-f'), 'Please enter your name.');
    if (!contact) return bad(el.contact.closest('.gate-f'), 'Please leave an email, Telegram or LinkedIn.');
    if (!val('ticket')) return bad(f.querySelector('[data-need="ticket"]'), 'Please pick a ticket size.');
    var parts = [['Type', val('type')], ['Org', el.org.value.trim()], ['Ticket', val('ticket')], ['Instrument', val('instrument')], ['Terms', el.terms.value.trim()], ['When', val('when')], ['Help', vals('help').join(', ')], ['Note', el.note.value.trim()], ['Ref', ref]];
    var message = parts.filter(function(p){ return p[1]; }).map(function(p){ return p[0] + ': ' + p[1]; }).join(' | ');
    var btn = f.querySelector('button[type=submit]'); btn.disabled = true; btn.textContent = 'Sending…'; err.textContent = '';
    post({ role: 'Investor', name: name, contact: contact, message: message, link: location.href, page: 'investors' + (ref ? ' via ' + ref : ''), company: el.company.value, file: null })
      .then(function(r){ return r.json(); }).then(function(r){
        if (!r.ok) throw 0;
        var safe = contact.replace(/[<>&"]/g, '');
        f.outerHTML = '<div class="op-join-ok" role="status"><p><b>Thank you, ' + name.replace(/[<>&"]/g, '') + '.</b> Yury will reply to ' + safe + ' within 48 hours.</p><p class="op-cta" style="display:flex"><a class="btn" href="../intro/">Book a call now</a></p></div>';
      })
      .catch(function(){ err.textContent = 'Could not send. Try again or write to __MAIL__.'; btn.disabled = false; btn.textContent = 'Send'; });
  });
  if (ref) { var K = 'emozu-inv-ref-' + ref; try { if (!localStorage.getItem(K)) { localStorage.setItem(K, '1'); post({ role: 'Investor', name: '(opened)', contact: '', message: 'Opened /investors/ from a shared link', link: location.href, page: 'investors via ' + ref, company: '', file: null }).catch(function(){}); } } catch (e) {} }
})();
""".replace('__MAIL__', MAIL)


def investors_page(head, body, pdf_no):
    body = strip_scripts(body)
    body = re.sub(r'<span class="op-money">.*?</span>', '', body, flags=re.S)
    body = re.sub(r'\s*<section class="op-ask op-money">.*?</section>', '', body, flags=re.S)
    body = re.sub(r'<a class="op-pdf" href="#pdf" data-pdf>PDF</a>', '<a class="op-pdf" href="emozu-one-pager.pdf" download="Emozu-one-pager.pdf">PDF</a>', body)
    body = re.sub(r'(<p class="op-short">.*?</p>)', r'\1\n      <p class="op-hero-cta"><a class="btn" href="#join">Tell us your terms</a><a class="btn ghost" href="../intro/">Book a call</a></p>', body, count=1, flags=re.S)
    nxt = re.search(r'<section class="op-ask op-next">.*?</section>', body, re.S).group(0)
    nxt2 = re.sub(r'<p class="op-cta">.*?</p>', '<p class="op-cta"><a class="btn" href="#join">Tell us your terms</a> <a class="btn ghost" href="../intro/">Book a call</a></p>', nxt, flags=re.S)
    nxt2 = nxt2.replace('Looking for clinicians and families for the beta.', 'We are raising a pre-seed round for it.')
    body = body.replace(nxt, nxt2 + JOIN)
    body = re.sub(r'<a class="op-fab" href="[^"]*">[^<]*</a>', '<a class="op-fab" href="#join">Tell us your terms</a>', body)
    for bad in ('500K', '$500', 'op-money', 'The ask'):
        assert bad not in body, 'money left on /investors/: ' + bad
    head = set_meta(head, 'Emozu · for investors', 'A soft band that warns a parent before a meltdown. Tell us on what terms you would join the pre-seed round.', SITE + '/investors/', 'noindex,follow')
    head = head.replace('</head>', CSS + '</head>')
    html = head + '<body class="opb nomoney">\n' + body + '\n<script>' + JS_COMMON + '\nmotion();fab("#join");\n' + JS_JOIN + '</script>\n</body>\n</html>\n'
    write('investors/index.html', html)
    write('investors/emozu-one-pager.pdf', pdf_no)


SHELL = """<body class="opb">
<main class="v-wait" id="v-wait"><div><span class="v-spin" aria-hidden="true"></span><p>Opening your copy…</p></div></main>
<noscript><p style="padding:24px;text-align:center">Please turn on JavaScript to open this page, or see <a href="../../investors/">emozu.kids/investors</a>.</p></noscript>
<script type="application/json" id="v-payload">%%PAYLOAD%%</script>
<script>
%%COMMON%%
(function(){
  var P = JSON.parse(document.getElementById('v-payload').textContent), LS = 'emozu-v-' + P.id;
  var b64 = function(s){ s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; var b = atob(s), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; };
  var fromHash = location.hash.slice(1), saved = null; try { saved = localStorage.getItem(LS); } catch (e) {}
  var key = fromHash || saved;
  function closed(){
    document.getElementById('v-wait').innerHTML = '<div><img src="../../assets/logo-sm.webp" alt="Emozu" width="101" height="30"><p>This page is a personal copy and opens only from the link Yury sent. The open version is here:</p><a class="btn" href="../../investors/">emozu.kids/investors</a></div>';
  }
  if (!key || !window.crypto || !crypto.subtle) return closed();
  var k;
  crypto.subtle.importKey('raw', b64(key), 'AES-GCM', false, ['decrypt'])
    .then(function(kk){ k = kk; return crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(P.b[0]) }, k, b64(P.b[1])); })
    .then(function(buf){
      document.body.className = 'opb';
      document.body.innerHTML = new TextDecoder().decode(buf);
      motion(); fab('.op-ask'); share(P.share);
      window.scrollTo(0, 0);
      try { localStorage.setItem(LS, key); } catch (e) {}
      if (fromHash && history.replaceState) history.replaceState(null, '', location.pathname + location.search);
      var pdf = document.querySelector('[data-pdf]');
      if (pdf) pdf.addEventListener('click', function(e){
        e.preventDefault(); pdf.textContent = '…';
        fetch(P.pdf, { cache: 'no-store' }).then(function(r){ return r.json(); })
          .then(function(o){ return crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(o.iv) }, k, b64(o.c)); })
          .then(function(u){ var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([u], { type: 'application/pdf' })); a.download = 'Emozu-one-pager.pdf'; document.body.appendChild(a); a.click(); setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 4000); })
          .catch(function(){ alert('Could not get the PDF. Try again.'); })
          .then(function(){ pdf.textContent = 'PDF'; });
      });
      try { if (!localStorage.getItem(LS + '-seen')) { localStorage.setItem(LS + '-seen', '1'); post({ role: 'Investor', name: P.name, contact: '', message: 'Opened the personal one-pager', link: location.origin + location.pathname, page: 'personal ' + P.ref, company: '', file: null }).catch(function(){}); } } catch (e) {}
    })
    .catch(function(){ if (!fromHash) { try { localStorage.removeItem(LS); } catch (e) {} } closed(); });
})();
</script>
</body>
</html>
"""


def personal_page(person, head, body, pdf_money):
    pid, ref, name = person['id'], person['ref'], person['name']
    key = AESGCM(b64u_dec(person['key']))
    body = strip_scripts(body)
    body = re.sub(r'\s*<section class="op-ask op-next">.*?</section>', '', body, flags=re.S)
    body = re.sub(r'<span class="op-tag">[^<]*</span>', f'<span class="op-tag">For {name} · Nov 2026</span>', body, count=1)
    ask = re.search(r'<section class="op-ask op-money">.*?</section>', body, re.S).group(0)
    ask2 = re.sub(r'<p class="op-cta">.*?</p>', f'<p class="op-cta"><a class="btn" href="../intro/">Book a call</a> <a class="btn ghost" href="mailto:{MAIL}">{MAIL}</a></p>', ask, flags=re.S)
    share_url = f'{SITE}/investors/?ref={ref}'
    body = body.replace(ask, ask2 + share_block(share_url, name))
    body = re.sub(r'<a class="op-fab" href="[^"]*">[^<]*</a>', '<a class="op-fab" href="../intro/">Book a call</a>', body)
    body = deepen(body)

    def enc(data):
        iv = secrets.token_bytes(12)
        return [e64(iv), e64(key.encrypt(iv, data, None))]
    write(f'v/{pid}/op.bin', json.dumps(dict(zip(('iv', 'c'), enc(pdf_money)))))
    payload = dict(id=pid, name=name, ref=ref, share=share_url, pdf='op.bin', b=enc(body.encode()))
    h = set_meta(head, f'Emozu · for {name}', 'Your copy of the Emozu one-pager.', f'{SITE}/v/{pid}/', 'noindex,nofollow')
    h = re.sub(r'\s*<link rel="canonical"[^>]*>', '', h)
    h = deepen(h).replace('</head>', CSS + '</head>')
    page = h + SHELL.replace('%%PAYLOAD%%', json.dumps(payload).replace('</', '<\\/')).replace('%%COMMON%%', JS_COMMON)
    assert '500K' not in page
    write(f'v/{pid}/index.html', page)
    return f'{SITE}/v/{pid}/#{person["key"]}'


def main():
    if not os.path.exists(os.path.join(PRIV, 'code.txt')):
        print('skip share pages: _src/private/code.txt not here'); return
    head, body, pdf = read_invest()
    investors_page(head, body, pdf['op-no.bin'])
    print('built /investors/')
    pp = os.path.join(PRIV, 'people.json')
    if os.path.exists(pp):
        for person in json.load(open(pp, encoding='utf8')):
            print(person['name'] + ': ' + personal_page(person, head, body, pdf['op.bin']))
    else:
        print('skip personal pages: _src/private/people.json not here')


if __name__ == '__main__':
    main()
