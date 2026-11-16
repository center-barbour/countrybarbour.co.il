/* בארבור · אב טיפוס 8 · מדיה חיה, מעבר בין תמונות ותפריט */
(function () {
  'use strict';
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function isV(m) { return m && m.tagName === 'VIDEO'; }
  function play(v) { try { var p = v.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {} }

  /* תפריט במובייל */
  $$('.menu').forEach(function (b) {
    b.addEventListener('click', function () {
      var n = document.getElementById(b.getAttribute('aria-controls'));
      var o = n.classList.toggle('open');
      b.setAttribute('aria-expanded', o ? 'true' : 'false');
    });
  });

  /* כותרת עליונה: שקופה מעל הפתיחה, לבנה אחרי גלילה */
  var hdr = document.querySelector('.top');
  function onScroll() { document.body.classList.toggle('scrolled', window.scrollY > 30); }
  if (hdr) { window.addEventListener('scroll', onScroll, { passive: true }); onScroll(); }

  /* פס המחלקות הנע: עצירה והפעלה */
  $$('.marq').forEach(function (mq) {
    var b = mq.querySelector('.marq-pp');
    if (RM) mq.classList.add('stopped');
    function lab() { b.setAttribute('aria-label', mq.classList.contains('stopped') ? 'הפעלת הפס הנע' : 'עצירת הפס הנע'); }
    if (b) { b.addEventListener('click', function () { mq.classList.toggle('stopped'); lab(); }); lab(); }
    /* נגישות: קישור שמקבל מיקוד מהמקלדת נגלל למרכז הפס, כדי שלא ייחתך בשוליים או מתחת לכפתור */
    var view = mq.querySelector('.marq-view'), track = mq.querySelector('.marq-track');
    mq.addEventListener('focusin', function (ev) {
      var a = ev.target; if (!view || !a.closest || !a.closest('.marq-track')) return;
      if (track) track.style.animation = 'none';   /* בזמן ניווט במקלדת הפס עומד במקומו ההתחלתי */
      requestAnimationFrame(function () {
        var r = a.getBoundingClientRect(), v = view.getBoundingClientRect();
        view.scrollLeft += (r.left + r.width / 2) - (v.left + v.width / 2);
      });
    });
    mq.addEventListener('focusout', function (ev) {
      if (ev.relatedTarget && mq.contains(ev.relatedTarget)) return;
      if (track) track.style.animation = '';
      if (view) view.scrollLeft = 0;
    });
  });

  /* שכבות מדיה בתוך מסגרת: מעבר רך, וידאו מתנגן רק כשהוא גלוי */
  function Media(frame) {
    var ms = $$('.m', frame), i = -1, live = false, onEnd = null;
    ms.forEach(function (m, k) {
      if (isV(m)) m.addEventListener('ended', function () { if (k === i && onEnd) onEnd(); });
    });
    function anim() { ms.forEach(function (m) { m.style.animationPlayState = live ? 'running' : 'paused'; }); }
    return {
      get n() { return ms.length; },
      get i() { return i; },
      get cur() { return ms[i]; },
      onEnd: function (f) { onEnd = f; },
      go: function (n, loop) {
        var old = ms[i]; i = n;
        ms.forEach(function (m, k) { m.classList.toggle('on', k === n); });
        var c = ms[n];
        if (isV(c)) {
          c.loop = !!loop; c.preload = 'auto';
          try { c.currentTime = 0; } catch (e) {}
          if (live) play(c);
        }
        if (old && old !== c && isV(old)) setTimeout(function () { if (!old.classList.contains('on')) old.pause(); }, 1100);
        var nx = ms[(n + 1) % ms.length];
        if (isV(nx) && nx.preload === 'none') nx.preload = 'auto';
        anim();
      },
      loop: function (on) { if (isV(ms[i])) ms[i].loop = on; },
      live: function (on) {
        live = on; var c = ms[i];
        if (isV(c)) { if (on) play(c); else c.pause(); }
        anim();
      }
    };
  }

  function ppLabel(btn, on) { if (btn) btn.setAttribute('aria-label', on ? 'עצירת התנועה' : 'הפעלת התנועה'); }

  /* רוטטור: תמונה/וידאו + לשוניות + פאנלים. וידאו מתקדם כשהוא נגמר, תמונה אחרי interval */
  $$('[data-rot]').forEach(function (root) {
    var media = Media($$('.frame', root)[0]);
    var pns = $$('[data-pn]', root), tabs = $$('[role="tab"]', root), pp = root.querySelector('.pp');
    var interval = +root.getAttribute('data-rot') || 6500;
    var auto = true, live = !RM, timer = null;
    function set(n) {
      media.go(n, !auto);
      pns.forEach(function (p, k) { p.hidden = k !== n; });
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === n ? 'true' : 'false'); t.tabIndex = k === n ? 0 : -1; });
      schedule();
    }
    function next() { set((media.i + 1) % media.n); }
    function schedule() {
      clearTimeout(timer);
      if (!live || !auto || media.n < 2) return;
      if (isV(media.cur)) {
        var v = media.cur, d = (v.duration && isFinite(v.duration)) ? v.duration : 0;
        timer = setTimeout(next, Math.max(d * 1000 + 400, 9000) + 2000); /* רשת ביטחון אם ended לא מגיע */
      } else timer = setTimeout(next, interval);
    }
    media.onEnd(function () { if (live && auto) next(); });
    function setLive(on) {
      live = on; root.classList.toggle('paused', !on); ppLabel(pp, on);
      media.live(on); schedule();
    }
    if (pp) pp.addEventListener('click', function () { setLive(!live); });
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { auto = false; media.loop(true); set(k); });
      t.addEventListener('keydown', function (e) {
        var n = null, last = tabs.length - 1, cur = media.i;
        if (e.key === 'ArrowLeft') n = cur === last ? 0 : cur + 1;      /* בעברית: שמאלה = הבא */
        else if (e.key === 'ArrowRight') n = cur === 0 ? last : cur - 1;
        else if (e.key === 'Home') n = 0; else if (e.key === 'End') n = last;
        if (n !== null) { e.preventDefault(); auto = false; media.loop(true); set(n); tabs[n].focus(); }
      });
    });
    set(0); setLive(live);
  });

})();
