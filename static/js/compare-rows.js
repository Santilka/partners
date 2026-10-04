(function(){
  'use strict';

  function init(){
    document.querySelectorAll('.compare-table tr[data-href]').forEach(function(row){
      row.addEventListener('click', function(e){
        if(e.target.closest('a')) return;
        window.open(row.dataset.href, '_blank', 'noopener,noreferrer');
      });
    });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
