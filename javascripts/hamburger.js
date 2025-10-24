/* Small shared hamburger/menu initializer
   - Finds all .hamburger buttons and their aria-controls target
   - Toggles .open on the target nav container
   - Keeps aria-expanded in sync
   - Closes the menu when a link inside the nav is clicked (mobile convenience)
*/
(function(){
  function initHamburgers(){
    var btns = document.querySelectorAll('.hamburger');
    for (var i = 0; i < btns.length; i++) {
      (function(btn){
        var navId = btn.getAttribute('aria-controls');
        var nav = navId ? document.getElementById(navId) : btn.nextElementSibling;
        if (!nav) return;
        btn.addEventListener('click', function(){
          var isOpen = btn.getAttribute('aria-expanded') === 'true';
          btn.setAttribute('aria-expanded', String(!isOpen));
          nav.classList.toggle('open');
        });
        // Close menu when a nav link is clicked (useful on mobile)
        var links = nav.querySelectorAll('a');
        for (var j = 0; j < links.length; j++) {
          links[j].addEventListener('click', function(){
            nav.classList.remove('open');
            btn.setAttribute('aria-expanded','false');
          });
        }
      })(btns[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHamburgers);
  } else {
    initHamburgers();
  }
})();
