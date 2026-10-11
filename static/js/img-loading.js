(function () {
  var seen = new WeakSet();

  function watch(img) {
    var m = img.closest('.card-media');
    if (!m || seen.has(img)) return;
    seen.add(img);
    if (img.complete) {
      m.classList.remove('is-loading');
      if (img.getAttribute('src') && !img.naturalWidth) m.classList.add('is-broken');
      return;
    }
    m.classList.add('is-loading');
    img.addEventListener('load', function () { m.classList.remove('is-loading'); }, { once: true });
    img.addEventListener('error', function () {
      m.classList.remove('is-loading');
      m.classList.add('is-broken');
    }, { once: true });
  }

  function scan(root) {
    if (root.nodeType !== 1) return;
    if (root.matches('.card-media img')) watch(root);
    root.querySelectorAll('.card-media img').forEach(watch);
  }

  scan(document.documentElement);
  new MutationObserver(function (list) {
    list.forEach(function (r) { r.addedNodes.forEach(scan); });
  }).observe(document.body, { childList: true, subtree: true });
})();
