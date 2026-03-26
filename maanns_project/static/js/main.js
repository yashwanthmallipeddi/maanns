// ══════════════════════════════════════════════
//   MAANS — main.js
// ══════════════════════════════════════════════

// ── Auto-dismiss flash messages after 4 seconds ──
document.addEventListener('DOMContentLoaded', function () {

  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (flash) {
    setTimeout(function () {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(40px)';
      flash.style.transition = '0.4s ease';
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  });

  // ── Rotating Quote on Home Page ──
  if (typeof QUOTES !== 'undefined' && QUOTES.length > 0) {
    const quoteEl  = document.getElementById('rotatingQuote');
    const qdots    = document.querySelectorAll('.qdot');
    let current    = 0;

    function showQuote(index) {
      if (!quoteEl) return;
      quoteEl.style.opacity = '0';
      setTimeout(function () {
        quoteEl.textContent = QUOTES[index];
        quoteEl.style.opacity = '1';
      }, 400);

      qdots.forEach((d, i) => {
        d.classList.toggle('active', i === index);
      });
    }

    // Click on dots
    qdots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        current = parseInt(this.dataset.index);
        showQuote(current);
      });
    });

    // Auto rotate every 3.5 seconds
    setInterval(function () {
      current = (current + 1) % QUOTES.length;
      showQuote(current);
    }, 3500);
  }

});

// ── Toggle Password Visibility ──
function togglePassword(fieldId) {
  const input = document.getElementById(fieldId);
  const icon  = input.parentElement.querySelector('.toggle-pw i');
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.replace('fa-eye-slash', 'fa-eye');
  }
}
