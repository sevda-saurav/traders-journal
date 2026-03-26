// static/js/main.js — Updated with trade helper functions

document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss flash messages after 4 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function (flash) {
        setTimeout(function () {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease';
            setTimeout(function () { flash.remove(); }, 500);
        }, 4000);
    });

    // Run auto-calculate on page load (for edit form)
    autoCalculate();
});


// ── Show/Hide custom market input ─────────────────────────
function toggleCustomMarket(select) {
    const group = document.getElementById('custom_market_group');
    const input = document.getElementById('custom_market');
    if (select.value === 'Other') {
        group.style.display = 'block';
        input.required = true;
    } else {
        group.style.display = 'none';
        input.required = false;
    }
}


// ── Live P&L and R:R preview while user types ─────────────
function autoCalculate() {
    const buy       = parseFloat(document.getElementById('buy_value')?.value);
    const sell      = parseFloat(document.getElementById('sell_value')?.value);
    const target    = parseFloat(document.getElementById('target')?.value);
    const stopLoss  = parseFloat(document.getElementById('stop_loss')?.value);
    const tradeType = document.getElementById('trade_type')?.value;

    const preview   = document.getElementById('calc_preview');
    const pnlEl     = document.getElementById('preview_pnl');
    const rrEl      = document.getElementById('preview_rr');

    // Only calculate if we have all the values
    if (!buy || !sell || !target || !stopLoss || !tradeType) {
        if (preview) preview.style.display = 'none';
        return;
    }

    // Calculate P&L percentage
    let pnl;
    if (tradeType === 'Long') {
        pnl = ((sell - buy) / buy) * 100;
    } else {
        pnl = ((buy - sell) / buy) * 100;
    }

    // Calculate Risk:Reward
    const risk   = Math.abs(buy - stopLoss);
    const reward = Math.abs(target - buy);
    const rr     = risk > 0 ? (reward / risk).toFixed(2) : 0;

    // Display the results
    if (preview) preview.style.display = 'flex';

    if (pnlEl) {
        pnlEl.textContent = pnl.toFixed(2) + '%';
        pnlEl.style.color = pnl >= 0 ? '#00d4aa' : '#fc4f4f';
    }

    if (rrEl) {
        rrEl.textContent  = '1 : ' + rr;
        rrEl.style.color  = '#f6c90e';
    }
}


// ── Image preview before upload ───────────────────────────
function previewImage(input) {
    const preview = document.getElementById('image_preview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src         = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}


// ── Confirm before deleting a trade ──────────────────────
function confirmDelete() {
    return confirm('Are you sure you want to delete this trade? This cannot be undone.');
}