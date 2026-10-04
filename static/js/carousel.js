document.querySelectorAll('[data-carousel]').forEach(function (root) {
  var track = root.querySelector('.cards-carousel');
  var prev = root.querySelector('.carousel-prev');
  var next = root.querySelector('.carousel-next');

  function step() {
    var card = track.querySelector('.card');
    var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return card ? card.offsetWidth + gap : track.clientWidth;
  }

  function update() {
    var hasPrev = track.scrollLeft > 2;
    var hasNext = track.scrollLeft + track.clientWidth < track.scrollWidth - 2;
    prev.disabled = !hasPrev;
    next.disabled = !hasNext;
    root.classList.toggle('has-prev', hasPrev);
    root.classList.toggle('has-next', hasNext);
  }

  function go(dir) {
    var s = step();
    var n = Math.max(1, Math.floor(track.clientWidth / s));
    track.scrollBy({ left: dir * n * s, behavior: 'smooth' });
  }

  prev.addEventListener('click', function () { go(-1); });
  next.addEventListener('click', function () { go(1); });
  track.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
});