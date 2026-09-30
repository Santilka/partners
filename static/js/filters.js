document.querySelectorAll('.chip').forEach(function (c) {
  c.addEventListener('click', function () {
    document.querySelectorAll('.chip').forEach(function (x) {
      x.classList.toggle('on', x === c);
      x.setAttribute('aria-pressed', x === c);
    });
    document.querySelectorAll('.card').forEach(function (card) {
      card.hidden = !(c.dataset.f === 'all' || card.dataset[c.dataset.f] === '1');
    });
  });
});
