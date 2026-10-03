(function(){
  'use strict';

  function initCompareScroll(){
    const outers = document.querySelectorAll('.compare-outer');
    if(!outers.length) return;

    outers.forEach(function(outer){
      const wrap = outer.querySelector('.compare-wrap');
      if(!wrap) return;

      function update(){
        const maxScroll = wrap.scrollWidth - wrap.clientWidth;

        // Если скроллить некуда — прячем градиент навсегда
        if(maxScroll <= 1){
          outer.classList.add('is-end');
          return;
        }

        // Если доскроллили до правого края (с погрешностью 2px)
        const isEnd = wrap.scrollLeft >= maxScroll - 2;
        outer.classList.toggle('is-end', isEnd);
      }

      wrap.addEventListener('scroll', update, {passive:true});
      window.addEventListener('resize', update, {passive:true});

      // Первичная проверка (после отрисовки)
      requestAnimationFrame(update);
    });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', initCompareScroll);
  } else {
    initCompareScroll();
  }
})();