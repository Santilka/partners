document.querySelectorAll('[data-carousel]').forEach(function (root) {
  var track = root.querySelector('.cards-carousel');
  var prev = root.querySelector('.carousel-prev');
  var next = root.querySelector('.carousel-next');
  var url = root.dataset.moreUrl || '';
  var initIds = root.dataset.ids || '';
  var BATCH = 6, MAXCARDS = 36;
  var seed = Math.random().toString(36).slice(2, 12);
  var offset = 0, loading = false, exhausted = !url, armed = false, idleTimer = 0;
  var U = [], pending = [];

  track.style.position = 'relative';
  track.style.overflowAnchor = 'none';
  Array.prototype.forEach.call(track.querySelectorAll('.card'), function (c, i) {
    c.dataset.i = i;
    U.push(c.cloneNode(true));
  });
  if (!U.length) return;
  BATCH = Math.max(12, Math.ceil(track.clientWidth / step()) * 2);
  MAXCARDS = BATCH * 20;

  function step() {
    var card = track.querySelector('.card');
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return card ? card.offsetWidth + gap : track.clientWidth;
  }

  function go(dir) {
    armed = true;
    fill();
    var s = step();
    var n = Math.max(1, Math.floor(track.clientWidth / s));
    track.scrollBy({ left: dir * n * s, behavior: 'smooth' });
  }

  var snapHold = 0, lock = 0;

  function holdSnap() {
    snapHold++;
    track.style.scrollSnapType = 'none';
  }

  function releaseSnap() {
    if (--snapHold <= 0) {
      snapHold = 0;
      track.style.scrollSnapType = '';
    }
  }

  function flipHold(c) {
    if (!root.classList.contains('flip-ready') || c._hold) return;
    c._hold = true;
    holdSnap();
    var done = function () {
      if (!c._hold) return;
      c._hold = false;
      releaseSnap();
    };
    c.addEventListener('animationend', done, { once: true });
    c.addEventListener('animationcancel', done, { once: true });
    setTimeout(done, 2500);
  }

  function instant(fn) {
    if (!lock) track.style.scrollBehavior = 'auto';
    lock++;
    holdSnap();
    fn();
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        releaseSnap();
        if (--lock === 0) track.style.scrollBehavior = '';
      });
    });
  }

  function skeleton() {
    var c = document.createElement('div');
    c.className = 'card card-skeleton';
    c.setAttribute('aria-hidden', 'true');
    c.innerHTML = '<span class="skeleton-spin"></span>';
    return c;
  }

  function addSkeletons() {
    for (var k = 0; k < BATCH; k++) {
      var c = skeleton();
      pending.push(c);
      track.appendChild(c);
    }
  }

  function fillSkeletons(base) {
    pending.forEach(function (ph, j) {
      if (ph.parentNode === track) track.replaceChild(make((base + j) % U.length), ph);
    });
    pending = [];
  }

  function make(i) {
    var c = U[i].cloneNode(true);
    c.dataset.i = i;
    c.classList.add('shown');
    return c;
  }

  function drop(list) {
    list.forEach(function (c) { track.removeChild(c); });
  }

  function trimLeft() {
    if (track.children.length <= MAXCARDS) return;
    var lim = track.scrollLeft - track.clientWidth * 3, rm = [];
    for (var c = track.firstElementChild; c && track.children.length - rm.length > MAXCARDS; c = c.nextElementSibling) {
      if (c.offsetLeft + c.offsetWidth > lim) break;
      rm.push(c);
    }
    if (!rm.length) return;
    var ref = rm[rm.length - 1].nextElementSibling, x0 = ref.offsetLeft, s0 = track.scrollLeft;
    drop(rm);
    var d = x0 - ref.offsetLeft;
    instant(function () { track.scrollLeft = s0 - d; });
  }

  function trimRight() {
    if (track.children.length <= MAXCARDS) return;
    var lim = track.scrollLeft + track.clientWidth * 4, rm = [];
    for (var c = track.lastElementChild; c && track.children.length - rm.length > MAXCARDS; c = c.previousElementSibling) {
      if (c.offsetLeft < lim) break;
      rm.push(c);
    }
    drop(rm);
  }

  function growLeft() {
    var i = +track.firstElementChild.dataset.i, add = [];
    for (var k = 0; k < BATCH; k++) {
      i = (i - 1 + U.length) % U.length;
      add.unshift(make(i));
    }
    var first = track.firstElementChild, w0 = track.scrollWidth, s0 = track.scrollLeft;
    add.forEach(function (c) { track.insertBefore(c, first); });
    var d = track.scrollWidth - w0;
    instant(function () { track.scrollLeft = s0 + d; });
    trimRight();
  }

  function growRight() {
    if (pending.length) return;
    var i = +track.lastElementChild.dataset.i, add = [];
    while (add.length < BATCH && !(i === U.length - 1 && !exhausted)) {
      i = (i + 1) % U.length;
      add.push(make(i));
    }
    if (add.length) {
      add.forEach(function (c) { track.appendChild(c); });
      trimLeft();
    }
    if (!exhausted && i === U.length - 1) {
      if (!add.length) addSkeletons();
      loadMore();
    }
  }

  function loadMore() {
    if (loading || exhausted) return;
    loading = true;
    var base = U.length;
    fetch(url + '?seed=' + seed + '&offset=' + offset + '&n=' + BATCH + '&exclude=' + encodeURIComponent(initIds), {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var t = document.createElement('template');
        t.innerHTML = d.html;
        Array.prototype.forEach.call(t.content.children, function (c) {
          if (c.classList.contains('card')) U.push(c);
        });
        offset += d.count;
        if (d.done) exhausted = true;
      })
      .catch(function () { exhausted = true; })
      .then(function () {
        loading = false;
        fillSkeletons(base);
        fill();
      });
  }

  function fill(urgent) {
    var w = track.clientWidth, st = step();
    if (!w) return;
    var lim = urgent ? Math.max(w, st * 5) : Math.max(w * 2, st * 8);
    if (track.scrollLeft < lim) growLeft();
    if (track.scrollWidth - track.scrollLeft - w < lim) growRight();
  }

  function onScroll() {
    if (!armed) return;
    var w = track.clientWidth, st = step(), s = track.scrollLeft, r = track.scrollWidth - s - w;
    var lim = Math.max(w, st * 5);
    clearTimeout(idleTimer);
    if (s < lim || r < lim) fill(true);
    else idleTimer = setTimeout(fill, 100);
  }

  function initFlip() {
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce || !('IntersectionObserver' in window)) return;
    root.classList.add('flip-ready');
    var io = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      io.disconnect();
      var s = track.scrollLeft, e = s + track.clientWidth, n = 0;
      track.querySelectorAll('.card').forEach(function (c) {
        var vis = c.offsetLeft + c.offsetWidth > s && c.offsetLeft < e;
        c.style.setProperty('--d', (vis ? Math.min(n++, 8) * 100 : 0) + 'ms');
        c.classList.add('flipped');
        flipHold(c);
      });
    }, { threshold: 0.25 });
    io.observe(root);
  }

  prev.addEventListener('click', function () { go(-1); });
  next.addEventListener('click', function () { go(1); });
  track.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', function () { if (armed) fill(); });
  ['pointerdown', 'wheel', 'keydown', 'touchstart'].forEach(function (ev) {
    root.addEventListener(ev, function () { armed = true; loadMore(); }, { once: true, passive: true });
  });

  var nav = document.createElement('div'), pill = document.createElement('div'), sep = document.createElement('span');
  nav.className = 'carousel-nav';
  pill.className = 'carousel-pill';
  sep.className = 'carousel-sep';
  sep.setAttribute('aria-hidden', 'true');
  pill.appendChild(prev);
  pill.appendChild(sep);
  pill.appendChild(next);
  nav.appendChild(pill);
  root.after(nav);

  prev.disabled = next.disabled = false;
  root.classList.add('has-prev', 'has-next');
  growLeft();
  initFlip();
});