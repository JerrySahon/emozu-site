/* Emozu site. Calm motion only: GSAP + ScrollTrigger + SplitText + Flip, Lenis on desktop. */
(function () {
  'use strict';
  var root = document.documentElement;
  var hasMotion = root.classList.contains('motion') && window.gsap && window.ScrollTrigger;
  window.__emozuReady = true;
  if (!hasMotion) root.classList.remove('motion');

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var isWide = function () { return matchMedia('(min-width:1400px)').matches; };

  /* ---------- rail: which group are we in ---------- */
  var railLinks = $$('.rail a');
  var rail = $('.rail');
  function setActive(id) {
    railLinks.forEach(function (a) {
      var on = a.getAttribute('href') === '#' + id;
      a.classList.toggle('on', on);
      if (on) {
        a.setAttribute('aria-current', 'true');
        if (rail && !isWide()) {
          var target = a.offsetLeft - (rail.clientWidth - a.offsetWidth) / 2;
          rail.scrollTo({ left: target, behavior: 'smooth' });
        }
      } else {
        a.removeAttribute('aria-current');
      }
    });
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) setActive(e.target.id); });
    }, { rootMargin: '-40% 0px -55% 0px' });
    railLinks.forEach(function (a) {
      var s = $(a.getAttribute('href'));
      if (s) io.observe(s);
    });
  }

  /* ---------- header hides on scroll down, phones and tablets only ---------- */
  var top = $('.top');
  var mob = $('.mob-cta');
  var writeSec = $('#write');
  var last = 0;
  function onScroll() {
    var y = window.scrollY || 0;
    if (top) {
      top.classList.toggle('scrolled', y > 8);
      if (!isWide()) {
        if (y > last + 6 && y > 240) top.classList.add('hide');
        else if (y < last - 6 || y < 240) top.classList.remove('hide');
      }
    }
    if (mob && writeSec) {
      var r = writeSec.getBoundingClientRect();
      mob.classList.toggle('show', y > 500 && r.top > innerHeight * 0.8);
    }
    last = y;
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- form ---------- */
  initForm();

  /* ---------- study cards work even without motion ---------- */
  initStudies(false);

  if (!hasMotion) return;

  /* ---------- motion ---------- */
  var gsap = window.gsap;
  var ST = window.ScrollTrigger;
  gsap.registerPlugin(ST);
  if (window.SplitText) gsap.registerPlugin(window.SplitText);
  if (window.Flip) gsap.registerPlugin(window.Flip);
  gsap.defaults({ ease: 'power2.out' });

  /* smooth scroll, desktop mouse only */
  var lenis = null;
  if (window.Lenis && matchMedia('(pointer:fine)').matches) {
    lenis = new window.Lenis({ lerp: 0.13, smoothWheel: true });
    window.__emozuLenis = lenis;
    lenis.on('scroll', ST.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      var t = id.length > 1 && $(id);
      if (!t) return;
      if (lenis) {
        e.preventDefault();
        lenis.scrollTo(t, { offset: -84, duration: 1.1 });
        history.replaceState(null, '', id);
      }
      if (top && id !== '#hero') top.classList.add('hide');
    });
  });

  function ready(fn) {
    var run = function () { fn(); };
    if (document.fonts && document.fonts.ready) {
      Promise.race([document.fonts.ready, new Promise(function (r) { setTimeout(r, 1200); })]).then(run);
    } else run();
  }

  ready(function () {
    /* kinetic split on headings */
    $$('[data-split]').forEach(function (el) {
      gsap.set(el, { visibility: 'visible' });
      if (!window.SplitText) { gsap.from(el, { opacity: 0, y: 20, duration: .7 }); return; }
      var isH1 = el.tagName === 'H1';
      window.SplitText.create(el, {
        type: 'lines',
        linesClass: 'ln',
        mask: 'lines',
        autoSplit: true,
        onSplit: function (self) {
          return gsap.from(self.lines, {
            yPercent: 105, duration: isH1 ? 1 : .85, ease: 'power3.out', stagger: isH1 ? .09 : .07, delay: isH1 ? .1 : 0,
            scrollTrigger: isH1 ? null : { trigger: el, start: 'top 86%', once: true }
          });
        }
      });
    });

    /* soft reveals */
    ST.batch('.rv', {
      start: 'top 90%',
      once: true,
      onEnter: function (els) {
        gsap.to(els, { opacity: 1, y: 0, duration: .75, stagger: .07, overwrite: true, clearProps: 'transform' });
      }
    });

    /* hero: floating cards drift apart a little */
    if (document.querySelector('.hero-fig')) {
    gsap.from('.float.phone', { y: 24, opacity: 0, duration: 1, delay: .5 });
    gsap.from('.float.zero', { y: -14, opacity: 0, duration: .9, delay: .85 });
    gsap.to('.float.phone', { yPercent: -10, ease: 'none', scrollTrigger: { trigger: '.hero-fig', start: 'top 20%', end: 'bottom top', scrub: true } });
    gsap.to('.float.zero', { yPercent: 34, ease: 'none', scrollTrigger: { trigger: '.hero-fig', start: 'top 20%', end: 'bottom top', scrub: true } });
    }

    /* bars grow */
    $$('.bars').forEach(function (b) {
      gsap.to($$('.bt i', b), { scaleX: 1, duration: 1, ease: 'power3.out', stagger: .05, scrollTrigger: { trigger: b, start: 'top 82%', once: true } });
    });

    /* parent numbers: scroll-linked deck stack */
    var cards = $$('.scard');
    cards.forEach(function (c, i) {
      var next = cards[i + 1];
      if (!next) return;
      gsap.to(c, {
        scale: .94 - (cards.length - i) * .004,
        rotateX: -5,
        ease: 'none',
        scrollTrigger: { trigger: next, start: 'top bottom-=40', end: 'top top+=200', scrub: .4 }
      });
    });

    /* band callouts */
    var band = $('.band-main');
    if (band) {
      var tb = gsap.timeline({ scrollTrigger: { trigger: band, start: 'top 72%', once: true } });
      tb.to($$('svg line', band), { opacity: 1, duration: .5, stagger: .08 }, 0)
        .to($$('.call', band), { opacity: 1, duration: .5, stagger: .08 }, .15);
    }

    /* phone screens come alive */
    if (document.querySelector('.notif')) gsap.to('.notif', { opacity: 1, y: 0, duration: .8, ease: 'back.out(1.3)', scrollTrigger: { trigger: '.phones', start: 'top 70%', once: true } });
    gsap.to('.dayline .col i', { scaleY: 1, duration: .5, stagger: .1, ease: 'power1.inOut', scrollTrigger: { trigger: '.phones', start: 'top 70%', once: true } });
    gsap.to('.works .bt i', { scaleX: 1, duration: .9, stagger: .12, ease: 'power3.out', scrollTrigger: { trigger: '.phones', start: 'top 65%', once: true } });

    /* where this goes: cards rise */
    if (document.querySelector('.goes-track')) gsap.from('.gc', { y: 46, opacity: 0, duration: .85, stagger: .14, scrollTrigger: { trigger: '.goes-track', start: 'top 80%', once: true } });

    /* signal chart: the playhead walks toward the episode */
    var sig = $('.sig');
    if (sig) {
      var clip = $('#sigClip rect'), head = $('#sigHead'), zone = $('.sig-zone');
      var edges = $$('.sig-edge'), ep = $('.sig-ep'), win = $('.sig-win');
      var epLabel = $('.sig-ax .ep');
      gsap.set([zone].concat(edges, [ep, win, epLabel]), { opacity: 0 });
      var tl = gsap.timeline({ scrollTrigger: { trigger: sig, start: 'top 78%', end: 'bottom 62%', scrub: .5 } });
      tl.fromTo(clip, { attr: { width: 0 } }, { attr: { width: 1000 }, ease: 'none', duration: 1 }, 0)
        .fromTo(head, { attr: { x1: 0, x2: 0 } }, { attr: { x1: 1000, x2: 1000 }, ease: 'none', duration: 1 }, 0)
        .to([zone, edges[0]], { opacity: 1, duration: .05 }, .45)
        .to([edges[1], win], { opacity: 1, duration: .05 }, .68)
        .to([ep, epLabel], { opacity: 1, duration: .03 }, .8);
    }

    /* study scales: dots land */
    $$('.scale').forEach(function (s) {
      gsap.to($$('.pt', s), { scale: 1, duration: .6, stagger: .12, ease: 'back.out(2)', scrollTrigger: { trigger: s, start: 'top 90%', once: true } });
    });

    /* the catalogue: 99 dots, one child each, then the empty frame */
    var dots = $('.dgroups');
    if (dots) {
      var td = gsap.timeline({ scrollTrigger: { trigger: dots, start: 'top 74%', once: true } });
      td.to($$('.dotgrid i', dots), { opacity: 1, scale: 1, duration: .35, ease: 'back.out(2)', stagger: { amount: 1, from: 'start' } }, 0)
        .to('.home', { opacity: 1, duration: .6 }, .95)
        .from('.home b', { scale: 1.5, duration: .7, ease: 'power3.out' }, .95);
    }

    /* pilot chart */
    var g = $('.gantt');
    if (g) gsap.to($$('i', g), { scaleX: 1, duration: .5, stagger: .012, ease: 'power2.out', scrollTrigger: { trigger: g, start: 'top 82%', once: true } });
    var ow = $('.owlet i');
    if (ow) gsap.to(ow, { scaleX: 1, duration: 1.1, ease: 'power2.inOut', scrollTrigger: { trigger: ow, start: 'top 88%', once: true } });

    /* roadmap line follows scroll */
    var road = $('.road');
    if (road) {
      var line = $('.road-line i');
      var mm = gsap.matchMedia();
      mm.add('(min-width:1000px)', function () {
        gsap.fromTo(line, { scaleX: 0, scaleY: 1 }, { scaleX: 1, ease: 'none', scrollTrigger: { trigger: road, start: 'top 75%', end: 'bottom 60%', scrub: .5 } });
      });
      mm.add('(max-width:999px)', function () {
        gsap.fromTo(line, { scaleY: 0, scaleX: 1 }, { scaleY: 1, ease: 'none', scrollTrigger: { trigger: road, start: 'top 70%', end: 'bottom 70%', scrub: .5 } });
      });
    }

    /* magnetic chips, mouse only */
    if (matchMedia('(pointer:fine)').matches) {
      $$('.magnet').forEach(function (m) {
        var mx = gsap.quickTo(m, 'x', { duration: .45, ease: 'power3' });
        var my = gsap.quickTo(m, 'y', { duration: .45, ease: 'power3' });
        m.addEventListener('pointermove', function (e) {
          var r = m.getBoundingClientRect();
          mx((e.clientX - r.left - r.width / 2) * .22);
          my((e.clientY - r.top - r.height / 2) * .32);
        });
        m.addEventListener('pointerleave', function () { mx(0); my(0); });
      });
    }

    initStudies(true);
    if (location.hash && lenis) {
      var h = $(location.hash);
      if (h) lenis.scrollTo(h, { offset: -84, immediate: true });
    }
    ST.refresh();
  });

  /* ---------- helpers ---------- */
  function initStudies(useFlip) {
    var wrap = $('.studies');
    if (!wrap || wrap.dataset.bound === (useFlip ? '2' : '1') || (useFlip === false && wrap.dataset.bound)) return;
    wrap.dataset.bound = useFlip ? '2' : '1';
    wrap._flip = useFlip && !!window.Flip;
    if (wrap._ok) return;
    wrap._ok = true;
    wrap.addEventListener('click', function (e) {
      var btn = e.target.closest('.study-toggle');
      if (!btn) return;
      var card = btn.closest('.study');
      var cards = $$('.study', wrap);
      var opening = !card.classList.contains('open');
      var Flip = wrap._flip ? window.Flip : null;
      var state = Flip ? Flip.getState(cards) : null;
      wrap.classList.toggle('has-open', opening);
      cards.forEach(function (c) {
        var on = c === card && opening;
        c.classList.toggle('open', on);
        var b = $('.study-toggle', c);
        b.setAttribute('aria-expanded', on ? 'true' : 'false');
        b.textContent = on ? b.dataset.close : b.dataset.open;
      });
      if (Flip) {
        Flip.from(state, {
          duration: .55, ease: 'power2.inOut', absolute: false, simple: false, nested: true,
          onComplete: function () { window.ScrollTrigger.refresh(); }
        });
        if (opening) window.gsap.from($('.study-more', card), { opacity: 0, y: 8, duration: .4, delay: .25 });
      }
      if (opening) {
        var top = card.getBoundingClientRect().top;
        if (top < 80 || top > innerHeight * .55) {
          var y = (window.scrollY || 0) + top - 90;
          if (window.__emozuLenis) window.__emozuLenis.scrollTo(y, { duration: .8 });
          else window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }
    });
  }

  function initForm() {
    var form = $('#writeForm');
    if (!form) return;
    var msg = $('.form-msg', form);
    var hint = $('.role-hint', form);
    var ta = $('textarea', form);
    var file = $('input[type=file]', form);
    var drop = $('.drop', form);
    var fname = $('.fname', form);
    var fclear = $('.fclear', form);
    var dropDefault = fname ? fname.textContent : '';
    var MAX = 10 * 1024 * 1024;
    var d = form.dataset;

    function say(text, cls) {
      msg.textContent = text || '';
      msg.className = 'form-msg' + (cls ? ' ' + cls : '');
    }

    $$('input[name="role"]', form).forEach(function (r) {
      r.addEventListener('change', function () {
        if (hint) hint.textContent = r.dataset.hint || '';
        if (ta && r.dataset.ph) ta.placeholder = r.dataset.ph;
      });
    });

    function showFile() {
      var f = file.files && file.files[0];
      if (!f) { fname.textContent = dropDefault; fname.style.fontWeight = ''; fclear.hidden = true; return; }
      if (f.size > MAX) { say(d.errSize, 'err'); file.value = ''; showFile(); return; }
      say('');
      fname.textContent = f.name;
      fclear.hidden = false;
    }
    if (file) {
      file.addEventListener('change', showFile);
      fclear.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); file.value = ''; showFile(); });
      ['dragenter', 'dragover'].forEach(function (t) { drop.addEventListener(t, function () { drop.classList.add('over'); }); });
      ['dragleave', 'drop'].forEach(function (t) { drop.addEventListener(t, function () { drop.classList.remove('over'); }); });
    }

    function readFile(f) {
      return new Promise(function (resolve, reject) {
        if (!f) { resolve(null); return; }
        var fr = new FileReader();
        fr.onload = function () { resolve({ name: f.name, type: f.type, data: String(fr.result).split(',')[1] }); };
        fr.onerror = function () { reject(new Error('read')); };
        fr.readAsDataURL(f);
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var role = $('input[name="role"]:checked', form);
      var contact = form.elements.contact.value.trim();
      var text = form.elements.message.value.trim();
      var link = form.elements.link.value.trim();
      var picked = file && file.files && file.files[0];
      if (!contact) { say(d.errContact, 'err'); form.elements.contact.focus(); return; }
      if (!text && !link && !picked) { say(d.errEmpty, 'err'); form.elements.message.focus(); return; }

      var btn = $('button[type=submit]', form);
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = d.sending;
      say('');

      var ctrl = 'AbortController' in window ? new AbortController() : null;
      var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 120000) : null;

      readFile(picked).then(function (f) {
        /* text/plain keeps this a simple request, so the browser sends no preflight */
        return fetch(d.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          signal: ctrl ? ctrl.signal : undefined,
          body: JSON.stringify({
            role: role ? role.value : '',
            name: form.elements.name.value.trim(),
            contact: contact,
            message: text,
            link: link,
            page: d.page,
            company: form.elements.company.value,
            file: f
          })
        });
      }).then(function (r) {
        return r.json();
      }).then(function (res) {
        if (!res.ok) throw new Error(res.error || 'server');
        var box = $('#sentBox');
        form.hidden = true;
        box.hidden = false;
        box.focus({ preventScroll: true });
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
        /* the form just collapsed, so bring the thank-you message back into view */
        box.scrollIntoView({ block: 'center', behavior: 'instant' });
      }).catch(function (err) {
        say(err && err.message === 'size' ? d.errSize : d.errSend, 'err');
        btn.disabled = false;
        btn.textContent = label;
      }).then(function () {
        if (timer) clearTimeout(timer);
      });
    });
  }
})();
