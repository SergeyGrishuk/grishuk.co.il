(function () {
  'use strict';

  /* ─── TYPEWRITER ─── */
  function typewriter(el, text, speed, callback) {
    var i = 0;
    var interval = setInterval(function () {
      el.textContent = text.slice(0, ++i);
      if (i >= text.length) {
        clearInterval(interval);
        if (callback) callback();
      }
    }, speed);
  }

  /* ─── MATRIX RAIN ─── */
  function initMatrixRain(canvas) {
    if (!canvas) return;
    var ctx = canvas.getContext('2d');

    function resize() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    var chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノ'.split('');
    var fontSize = 15;
    var cols = Math.floor(canvas.width / fontSize);
    var drops = [];
    for (var c = 0; c < cols; c++) drops[c] = 1;

    function draw() {
      ctx.fillStyle = 'rgba(8,11,16,0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.font = fontSize + 'px monospace';

      for (var i = 0; i < drops.length; i++) {
        var ch = chars[Math.floor(Math.random() * chars.length)];
        var brightness = Math.random();
        ctx.fillStyle = brightness > 0.95
          ? 'rgba(34,211,238,0.25)'
          : 'rgba(34,211,238,' + (0.03 + brightness * 0.04) + ')';
        ctx.fillText(ch, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      }
    }

    setInterval(draw, 60);
  }

  /* ─── FADE-IN OBSERVER ─── */
  function initFadeIns() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.fade-in, .competency-card').forEach(function (el) {
        el.classList.add('visible');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-in, .competency-card').forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ─── INIT ─── */
  document.addEventListener('DOMContentLoaded', function () {
    var nameEl = document.getElementById('hero-name');
    var subEl = document.getElementById('hero-sub');
    var nameCursor = document.getElementById('cursor-name');
    var subCursor = document.getElementById('cursor-sub');

    // Matrix rain
    initMatrixRain(document.getElementById('matrix-canvas'));

    if (nameEl && subEl) {
      // Typewriter sequence
      setTimeout(function () {
        typewriter(nameEl, 'Sergey Grishuk', 55, function () {
          if (nameCursor) nameCursor.style.display = 'none';
          if (subCursor) subCursor.style.display = 'inline-block';

          typewriter(subEl, 'Tech Lead \u00b7 System Architect \u00b7 Security Researcher', 28, function () {
            if (subCursor) subCursor.style.display = 'none';
            document.body.classList.add('loaded');
            setTimeout(initFadeIns, 100);
          });
        });
      }, 300);
    } else {
      // Non-home pages: reveal immediately
      document.body.classList.add('loaded');
      initFadeIns();
    }
  });
})();
