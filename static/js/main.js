document.addEventListener('DOMContentLoaded', function () {

    // ── Auto-dismiss flash messages ───────────────────────
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function (flash) {
        setTimeout(function () {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease';
            setTimeout(function () { flash.remove(); }, 500);
        }, 4000);
    });

    console.log('Trader Journal loaded ✅');
});


// ── Mobile nav toggle ─────────────────────────────────────
function toggleNav() {
    var navLinks = document.getElementById('nav-links');
    navLinks.classList.toggle('nav-open');
}

// Close nav when clicking outside
document.addEventListener('click', function(e) {
    var nav      = document.getElementById('nav-links');
    var toggle   = document.querySelector('.nav-toggle');
    if (nav && toggle) {
        if (!nav.contains(e.target) && !toggle.contains(e.target)) {
            nav.classList.remove('nav-open');
        }
    }
});


// ── Show/Hide custom market input ─────────────────────────
function toggleCustomMarket(select) {
    var group = document.getElementById('custom_market_group');
    var input = document.getElementById('custom_market');
    if (select && group && input) {
        if (select.value === 'Other') {
            group.style.display = 'block';
            input.required = true;
        } else {
            group.style.display = 'none';
            input.required = false;
        }
    }
}


// ── Live P&L and R:R preview ──────────────────────────────
function autoCalculate() {
    var buy      = parseFloat(document.getElementById('buy_value')?.value);
    var sell     = parseFloat(document.getElementById('sell_value')?.value);
    var target   = parseFloat(document.getElementById('target')?.value);
    var stopLoss = parseFloat(document.getElementById('stop_loss')?.value);
    var type     = document.getElementById('trade_type')?.value;
    var preview  = document.getElementById('calc_preview');
    var pnlEl    = document.getElementById('preview_pnl');
    var rrEl     = document.getElementById('preview_rr');

    if (!buy || !sell || !target || !stopLoss || !type) {
        if (preview) preview.style.display = 'none';
        return;
    }

    var pnl = type === 'Long'
        ? ((sell - buy) / buy) * 100
        : ((buy - sell) / buy) * 100;

    var risk   = Math.abs(buy - stopLoss);
    var reward = Math.abs(target - buy);
    var rr     = risk > 0 ? (reward / risk).toFixed(2) : 0;

    if (preview) preview.style.display = 'flex';
    if (pnlEl) {
        pnlEl.textContent = pnl.toFixed(2) + '%';
        pnlEl.style.color = pnl >= 0 ? '#00d4aa' : '#fc4f4f';
    }
    if (rrEl) {
        rrEl.textContent = '1 : ' + rr;
        rrEl.style.color = '#f6c90e';
    }
}


// ── Image preview before upload ───────────────────────────
function previewImage(input) {
    var preview = document.getElementById('image_preview');
    if (input.files && input.files[0] && preview) {
        var reader = new FileReader();
        reader.onload = function(e) {
            preview.src           = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}


// ── Confirm delete ────────────────────────────────────────
function confirmDelete() {
    return confirm(
        'Are you sure you want to delete this trade?\n' +
        'This cannot be undone.'
    );
}