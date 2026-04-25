/* ====================================================
   PapaiArt — Open Beta Countdown
   Target: 2026-05-22 09:00:00 (local)
   ==================================================== */

const BETA_TARGET = new Date("2026-05-22T09:00:00").getTime();

function updateCountdown() {
    const now = Date.now();
    const diff = BETA_TARGET - now;

    const root = document.querySelector("[data-countdown]");
    if (!root) return;

    if (diff <= 0) {
        root.classList.add("is-live");
        return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const mins = Math.floor((diff / (1000 * 60)) % 60);
    const secs = Math.floor((diff / 1000) % 60);

    const setVal = (sel, val) => {
        const el = root.querySelector(sel);
        if (el) el.textContent = String(val).padStart(2, "0");
    };

    setVal("[data-cd-days]", days);
    setVal("[data-cd-hours]", hours);
    setVal("[data-cd-mins]", mins);
    setVal("[data-cd-secs]", secs);
}

document.addEventListener("DOMContentLoaded", () => {
    updateCountdown();
    setInterval(updateCountdown, 1000);
});
