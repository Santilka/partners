(function () {
  var header = document.querySelector('header');
  if (!header || !('IntersectionObserver' in window)) return;

  var sentinel = document.createElement('div');
  sentinel.setAttribute('aria-hidden', 'true');
  sentinel.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:20px;pointer-events:none';
  document.body.insertBefore(sentinel, document.body.firstChild);

  new IntersectionObserver(function (entries) {
    var atTop = entries[entries.length - 1].isIntersecting;
    header.classList.toggle('is-scrolled', !atTop);
    if (!header.classList.contains('hdr-ready')) {
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { header.classList.add('hdr-ready'); });
      });
    }
  }).observe(sentinel);
})();