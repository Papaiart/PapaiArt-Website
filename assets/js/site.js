// PapaiArt — shared page behaviour (nav, lightbox, video, filters, reveal)
document.documentElement.classList.add('js');

// ---------- mobile nav ----------
const nav = document.querySelector('.pa-nav');
const toggle = document.querySelector('.pa-nav__toggle');
if (nav && toggle) {
    toggle.addEventListener('click', () => {
        const open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', String(open));
        document.body.style.overflow = open ? 'hidden' : '';
    });
}

// ---------- lite YouTube embeds (no third-party request until clicked) ----------
document.querySelectorAll('.pa-video[data-yt]').forEach((el) => {
    const id = el.dataset.yt;
    el.style.backgroundImage = `url(https://i.ytimg.com/vi/${id}/hqdefault.jpg)`;
    el.addEventListener('click', () => {
        if (el.querySelector('iframe')) return;
        const f = document.createElement('iframe');
        f.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
        f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen';
        f.allowFullscreen = true;
        f.title = el.dataset.title || 'Video';
        el.innerHTML = '';
        el.appendChild(f);
    }, { once: true });
});

// ---------- lightbox ----------
const zoomables = [...document.querySelectorAll('[data-zoom]')];
if (zoomables.length) {
    const box = document.createElement('div');
    box.className = 'pa-lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.innerHTML = `
        <img alt="">
        <button class="pa-lightbox__close" aria-label="Close">✕</button>
        <button class="pa-lightbox__prev" aria-label="Previous">‹</button>
        <button class="pa-lightbox__next" aria-label="Next">›</button>
        <div class="pa-lightbox__count"></div>`;
    document.body.appendChild(box);
    const img = box.querySelector('img');
    const count = box.querySelector('.pa-lightbox__count');
    let group = [], idx = 0, lastFocus = null;

    const show = (i) => {
        idx = (i + group.length) % group.length;
        const el = group[idx];
        img.src = el.dataset.zoom;
        img.alt = el.querySelector('img')?.alt || el.alt || '';
        count.textContent = `${idx + 1} / ${group.length}`;
        box.querySelector('.pa-lightbox__prev').hidden = group.length < 2;
        box.querySelector('.pa-lightbox__next').hidden = group.length < 2;
    };
    const open = (el) => {
        const g = el.dataset.group;
        group = g ? zoomables.filter((z) => z.dataset.group === g) : [el];
        lastFocus = document.activeElement;
        show(group.indexOf(el));
        box.classList.add('is-open');
        document.body.style.overflow = 'hidden';
        box.querySelector('.pa-lightbox__close').focus();
    };
    const close = () => {
        box.classList.remove('is-open');
        document.body.style.overflow = '';
        lastFocus?.focus();
    };
    zoomables.forEach((el) => el.addEventListener('click', (e) => { e.preventDefault(); open(el); }));
    box.querySelector('.pa-lightbox__close').addEventListener('click', close);
    box.querySelector('.pa-lightbox__prev').addEventListener('click', () => show(idx - 1));
    box.querySelector('.pa-lightbox__next').addEventListener('click', () => show(idx + 1));
    box.addEventListener('click', (e) => { if (e.target === box) close(); });
    document.addEventListener('keydown', (e) => {
        if (!box.classList.contains('is-open')) return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') show(idx - 1);
        if (e.key === 'ArrowRight') show(idx + 1);
    });
}

// ---------- devlog filters ----------
const filters = document.querySelectorAll('.pa-filter');
if (filters.length) {
    const items = document.querySelectorAll('[data-product]');
    const months = document.querySelectorAll('.pa-month');
    const apply = (prod) => {
        filters.forEach((f) => f.classList.toggle('is-active', f.dataset.filter === prod));
        items.forEach((it) => { it.hidden = prod !== 'all' && it.dataset.product !== prod; });
        months.forEach((m) => {
            const grid = m.nextElementSibling;
            m.hidden = grid && ![...grid.children].some((c) => !c.hidden);
            if (grid) grid.hidden = m.hidden;
        });
        const url = new URL(location.href);
        if (prod === 'all') url.searchParams.delete('p'); else url.searchParams.set('p', prod);
        history.replaceState(null, '', url);
    };
    filters.forEach((f) => f.addEventListener('click', () => apply(f.dataset.filter)));
    const initial = new URLSearchParams(location.search).get('p');
    if (initial && document.querySelector(`.pa-filter[data-filter="${CSS.escape(initial)}"]`)) apply(initial);
}

// ---------- reveal on scroll ----------
const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && reveals.length) {
    const io = new IntersectionObserver((entries) => {
        entries.forEach((en) => {
            if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
        });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach((el) => io.observe(el));
} else {
    reveals.forEach((el) => el.classList.add('is-in'));
}

// ---------- showcase screenshot straightens as it scrolls into view ----------
const showcase = document.querySelector('.prod-showcase .pa-window');
if (showcase && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let ticking = false;
    const update = () => {
        const r = showcase.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (innerHeight - r.top) / (innerHeight * 0.75)));
        showcase.style.setProperty('--tilt', `${(1 - p) * 22}deg`);
        ticking = false;
    };
    window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener('resize', update);
    update();
}
