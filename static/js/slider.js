(function () {
  var INTERVAL = 5000;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.querySelectorAll('[data-slider]').forEach(function (root) {
    var track = root.querySelector('.hero-slider-track');
    var slides = Array.prototype.slice.call(root.querySelectorAll('[data-slide]'));
    var dots = Array.prototype.slice.call(root.querySelectorAll('[data-dot]'));
    var prev = root.querySelector('.hero-slider-prev');
    var next = root.querySelector('.hero-slider-next');

    if (slides.length < 2) {
      if (prev) prev.style.display = 'none';
      if (next) next.style.display = 'none';
      var dotsWrap = root.querySelector('.hero-slider-dots');
      if (dotsWrap) dotsWrap.style.display = 'none';
      return;
    }

    var index = 0;
    var timer = null;

    function render() {
      track.style.transform = 'translateX(' + (-index * 100) + '%)';
      dots.forEach(function (d, i) {
        d.classList.toggle('is-active', i === index);
        d.setAttribute('aria-selected', i === index ? 'true' : 'false');
      });
    }

    function goTo(i) {
      index = (i + slides.length) % slides.length;
      render();
    }

    function nextSlide() { goTo(index + 1); }
    function prevSlide() { goTo(index - 1); }

    function start() {
      if (reduced) return;
      stop();
      timer = setInterval(nextSlide, INTERVAL);
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }
    function restart() {
      stop();
      start();
    }

    if (next) next.addEventListener('click', function () { nextSlide(); restart(); });
    if (prev) prev.addEventListener('click', function () { prevSlide(); restart(); });

    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        goTo(i);
        restart();
      });
    });

    root.addEventListener('mouseenter', stop);
    root.addEventListener('mouseleave', start);

    root.addEventListener('focusin', stop);
    root.addEventListener('focusout', start);

    // свайп
    var startX = 0, startY = 0, tracking = false;
    track.addEventListener('touchstart', function (e) {
      if (e.touches.length !== 1) return;
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      tracking = true;
      stop();
    }, { passive: true });

    track.addEventListener('touchend', function (e) {
      if (!tracking) return;
      tracking = false;
      var t = e.changedTouches[0];
      var dx = t.clientX - startX;
      var dy = t.clientY - startY;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
        if (dx < 0) nextSlide(); else prevSlide();
      }
      start();
    }, { passive: true });

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else start();
    });

    render();
    start();
  });
})();