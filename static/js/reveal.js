(function () {
  if (!('IntersectionObserver' in window)) return;
  if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;

  var sel = 'h2.section-title,.section-sub,.eyebrow,.cards-grid:not(.cards-carousel)>.card,' +
    '.ptiles,.more-link,.review,.faq-item,.cta,.seo-text,.compare-outer,.search-results>p';

  var els = [].slice.call(document.querySelectorAll(sel)).filter(function (el) {
    if (el.closest('.hero,.hero-slider,.cards-carousel')) return false;
    return el.getBoundingClientRect().top > innerHeight * 0.92;
  });
  if (!els.length) return;

  els.forEach(function (el) { el.classList.add('reveal'); });

  var io = new IntersectionObserver(function (entries) {
    var i = 0;
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target;
      io.unobserve(el);
      el.style.setProperty('--rd', Math.min(i++, 6) * 70 + 'ms');
      requestAnimationFrame(function () { el.classList.add('is-in'); });

      var done = function () {
        el.removeEventListener('transitionend', onEnd);
        el.classList.remove('reveal', 'is-in');
        el.style.removeProperty('--rd');
      };
      var onEnd = function (ev) {
        if (ev.target === el && ev.propertyName === 'opacity') done();
      };
      el.addEventListener('transitionend', onEnd);
      setTimeout(done, 2400);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  els.forEach(function (el) { io.observe(el); });
})();
