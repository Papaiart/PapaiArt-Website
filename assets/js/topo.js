// PapaiArt — living topographic background.
// A height field made of slowly phase-shifting cosine waves is contoured every frame
// (marching squares), so the lines drift, merge and split like a changing landscape.
// Tinted with the page accent (--p); one static frame when reduced motion is requested.
(() => {
    const canvas = document.createElement('canvas');
    canvas.className = 'pa-topo';
    canvas.setAttribute('aria-hidden', 'true');
    const g = canvas.getContext('2d');
    if (!g) return;
    document.body.prepend(canvas);
    document.documentElement.classList.add('has-topo');

    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const accent = getComputedStyle(document.body).getPropertyValue('--p').trim() || '#1e9cf0';
    const CELL = 12;            // px between samples
    const PERIOD = 1000;        // px, wavelength of the lowest frequency
    const LEVELS = 12;
    const FPS = 30;

    // wave components: integer frequencies (like the static tile), random phase and drift speed
    let seed = 7;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    const waves = [];
    while (waves.length < 16) {
        const kx = Math.round(rnd() * 6 - 3), ky = Math.round(rnd() * 6 - 3);
        if (!kx && !ky) continue;
        const k = Math.hypot(kx, ky);
        waves.push({
            fx: 2 * Math.PI * kx / PERIOD, fy: 2 * Math.PI * ky / PERIOD,
            a: 1 / Math.pow(k, 1.5),
            phase: rnd() * Math.PI * 2,
            speed: (0.04 + rnd() * 0.1) * (rnd() < 0.5 ? -1 : 1),
        });
    }
    const amp = waves.reduce((s, w) => s + w.a, 0);

    let w = 0, h = 0, dpr = 1, cols = 0, rows = 0;
    let field, cx, sx, cy, sy;
    const resize = () => {
        dpr = Math.min(devicePixelRatio || 1, 2);
        w = innerWidth; h = innerHeight;
        canvas.width = Math.round(w * dpr);
        canvas.height = Math.round(h * dpr);
        cols = Math.ceil(w / CELL) + 2;
        rows = Math.ceil(h / CELL) + 2;
        field = new Float32Array(cols * rows);
        cx = new Float32Array(cols); sx = new Float32Array(cols);
        cy = new Float32Array(rows); sy = new Float32Array(rows);
        if (reduced) draw(0);
    };

    function sample(t) {
        const ox = t * 9, oy = scrollY * 0.22 + t * 5;          // slow drift + scroll parallax
        field.fill(0);
        for (const wv of waves) {
            const ph = wv.phase + wv.speed * t;
            for (let i = 0; i < cols; i++) {
                const a = wv.fx * (i * CELL + ox) + ph;
                cx[i] = Math.cos(a); sx[i] = Math.sin(a);
            }
            for (let j = 0; j < rows; j++) {
                const b = wv.fy * (j * CELL + oy);
                cy[j] = Math.cos(b) * wv.a; sy[j] = Math.sin(b) * wv.a;
            }
            // cos(a + b) = cos a cos b - sin a sin b
            for (let j = 0, o = 0; j < rows; j++) {
                const c = cy[j], s = sy[j];
                for (let i = 0; i < cols; i++, o++) field[o] += cx[i] * c - sx[i] * s;
            }
        }
        const k = 0.5 / (amp * 0.62);
        for (let o = 0; o < field.length; o++) field[o] = field[o] * k + 0.5;
    }

    // marching-squares edge pairs per case; edges: 0 top, 1 right, 2 bottom, 3 left
    const CASES = [[], [3, 0], [0, 1], [3, 1], [1, 2], [3, 0, 1, 2], [0, 2], [3, 2],
        [2, 3], [0, 2], [0, 1, 2, 3], [1, 2], [1, 3], [0, 1], [3, 0], []];

    function contour(level, path) {
        const f = field;
        const pt = (e, i, j, v0, v1, v2, v3) => {
            let t;
            switch (e) {
                case 0: t = (level - v0) / (v1 - v0); return [(i + t) * CELL, j * CELL];
                case 1: t = (level - v1) / (v2 - v1); return [(i + 1) * CELL, (j + t) * CELL];
                case 2: t = (level - v3) / (v2 - v3); return [(i + t) * CELL, (j + 1) * CELL];
                default: t = (level - v0) / (v3 - v0); return [i * CELL, (j + t) * CELL];
            }
        };
        for (let j = 0; j < rows - 1; j++) {
            const r0 = j * cols, r1 = r0 + cols;
            for (let i = 0; i < cols - 1; i++) {
                const v0 = f[r0 + i], v1 = f[r0 + i + 1], v2 = f[r1 + i + 1], v3 = f[r1 + i];
                const c = (v0 > level) | ((v1 > level) << 1) | ((v2 > level) << 2) | ((v3 > level) << 3);
                if (c === 0 || c === 15) continue;
                const edges = CASES[c];
                for (let n = 0; n < edges.length; n += 2) {
                    const a = pt(edges[n], i, j, v0, v1, v2, v3), b = pt(edges[n + 1], i, j, v0, v1, v2, v3);
                    path.moveTo(a[0], a[1]);
                    path.lineTo(b[0], b[1]);
                }
            }
        }
    }

    function draw(t) {
        sample(t);
        g.setTransform(dpr, 0, 0, dpr, -CELL * dpr, -CELL * dpr);
        g.clearRect(0, 0, w + CELL * 2, h + CELL * 2);
        g.strokeStyle = accent;
        g.lineJoin = g.lineCap = 'round';
        const thin = new Path2D(), thick = new Path2D();
        for (let l = 0; l < LEVELS; l++) contour(0.06 + l * (0.88 / (LEVELS - 1)), l % 4 === 0 ? thick : thin);
        g.lineWidth = 1; g.stroke(thin);
        g.lineWidth = 1.7; g.stroke(thick);
    }

    resize();
    addEventListener('resize', resize);
    if (reduced) return;

    let raf = 0, last = 0, t = 20;
    const tick = (now) => {
        raf = requestAnimationFrame(tick);
        if (now - last < 1000 / FPS) return;
        const dt = Math.min((now - last) / 1000, 0.1);
        last = now;
        t += dt;
        draw(t);
    };
    const start = () => { if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); } };
    const stop = () => { cancelAnimationFrame(raf); raf = 0; };
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
    draw(t);
    start();
})();
