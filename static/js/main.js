// static/js/main.js
// ─────────────────────────────────────────────────────────
// This file will hold JavaScript that runs on every page.
// For now, it's just a placeholder with one small feature:
// auto-hiding flash messages after 4 seconds.
// ─────────────────────────────────────────────────────────

// Wait for the page to fully load before running our code
document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss flash messages after 4 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function (flash) {
        setTimeout(function () {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease';
            // Remove from DOM after the fade animation
            setTimeout(function () { flash.remove(); }, 500);
        }, 4000);
    });

    console.log('Trader Journal JS loaded ✅');
});