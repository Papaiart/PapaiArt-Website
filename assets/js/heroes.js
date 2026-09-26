// PapaiArt — animated page headers.
// Each page sets <section class="pa-hero" data-hero="..."> and this module draws
// a scene themed after that product behind the hero content.
// 3D scenes use three.js (resolved through the page's import map); the pixel-art
// hero is plain 2D canvas.

const hero = document.querySelector('[data-hero]');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ------------------------------------------------------------------
// shared helpers
// ------------------------------------------------------------------

function makeNoise(seed = 1) {
    const perm = [...Array(256).keys()];
    let s = seed * 9301 + 49297;
    const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    for (let i = 255; i > 0; i--) {
        const j = Math.floor(rnd() * (i + 1));
        [perm[i], perm[j]] = [perm[j], perm[i]];
    }
    const p = new Uint8Array(512);
    for (let i = 0; i < 512; i++) p[i] = perm[i & 255];
    const g = [[1, 1], [-1, 1], [1, -1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]];
    const F2 = 0.5 * (Math.sqrt(3) - 1), G2 = (3 - Math.sqrt(3)) / 6;
    const c = (gi, x, y) => {
        let t = 0.5 - x * x - y * y;
        if (t < 0) return 0;
        t *= t;
        return t * t * (gi[0] * x + gi[1] * y);
    };
    return (x, y) => {
        const sk = (x + y) * F2;
        const i = Math.floor(x + sk), j = Math.floor(y + sk);
        const t = (i + j) * G2;
        const x0 = x - (i - t), y0 = y - (j - t);
        const i1 = x0 > y0 ? 1 : 0, j1 = 1 - i1;
        const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2;
        const x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2;
        const ii = i & 255, jj = j & 255;
        return 70 * (c(g[p[ii + p[jj]] & 7], x0, y0) +
            c(g[p[ii + i1 + p[jj + j1]] & 7], x1, y1) +
            c(g[p[ii + 1 + p[jj + 1]] & 7], x2, y2));
    };
}

const smooth = (a, b, x) => {
    const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
    return t * t * (3 - 2 * t);
};

function loop(frame) {
    // Runs `frame(t, dt)` only while the hero is on screen and the tab is visible.
    let visible = true, raf = 0, last = performance.now(), t = 0;
    const tick = (now) => {
        const dt = Math.min((now - last) / 1000, 0.05);
        last = now;
        t += dt;
        frame(t, dt);
        raf = requestAnimationFrame(tick);
    };
    const start = () => { if (!raf && visible && !document.hidden) { last = performance.now(); raf = requestAnimationFrame(tick); } };
    const stop = () => { cancelAnimationFrame(raf); raf = 0; };
    if (reduced) { frame(6, 0); return; }
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; visible ? start() : stop(); }).observe(hero);
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
    start();
}

function pointerTracker() {
    const p = { x: 0, y: 0, tx: 0, ty: 0 };
    window.addEventListener('pointermove', (e) => {
        p.tx = e.clientX / innerWidth - 0.5;
        p.ty = e.clientY / innerHeight - 0.5;
    }, { passive: true });
    p.step = () => { p.x += (p.tx - p.x) * 0.05; p.y += (p.ty - p.y) * 0.05; };
    return p;
}

// ------------------------------------------------------------------
// 3D runner
// ------------------------------------------------------------------

async function run3D(canvas, build, accent) {
    let THREE;
    try { THREE = await import('three'); } catch (e) { canvas.remove(); return; }
    let renderer;
    try {
        renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    } catch (e) { canvas.remove(); return; }
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const ctx = { THREE, renderer, accent: new THREE.Color(accent), pointer: pointerTracker() };
    const s = await build(ctx);
    const shift = Number(hero.dataset.shift || 0);

    const resize = () => {
        const w = hero.clientWidth, h = hero.clientHeight;
        renderer.setSize(w, h, false);
        s.camera.aspect = w / h;
        if (shift && w > 980) s.camera.setViewOffset(w, h, -w * shift, 0, w, h);
        else s.camera.clearViewOffset();
        s.camera.updateProjectionMatrix();
    };
    resize();
    new ResizeObserver(resize).observe(hero);

    loop((t, dt) => {
        ctx.pointer.step();
        s.update(t, dt);
        renderer.render(s.scene, s.camera);
    });
}

function wire(THREE, geo, color, opacity = 0.5, additive = true) {
    return new THREE.LineSegments(
        new THREE.WireframeGeometry(geo),
        new THREE.LineBasicMaterial({ color, transparent: true, opacity, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending, depthWrite: false })
    );
}

function edges(THREE, geo, color, opacity = 0.8, angle = 1) {
    return new THREE.LineSegments(
        new THREE.EdgesGeometry(geo, angle),
        new THREE.LineBasicMaterial({ color, transparent: true, opacity })
    );
}

function checkerTexture(THREE, a, b, n = 8, size = 128) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const g = c.getContext('2d');
    const s = size / n;
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
        g.fillStyle = (x + y) % 2 ? a : b;
        g.fillRect(x * s, y * s, s, s);
    }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.magFilter = THREE.NearestFilter;
    tex.anisotropy = 4;
    return tex;
}

// ------------------------------------------------------------------
// 3D scenes
// ------------------------------------------------------------------

const SCENES_3D = {

    // Home page: an endless wireframe landscape with one floating object per product.
    async hub({ THREE, pointer }) {
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x0a0b10, 14, 70);
        const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);

        const noise = makeNoise(7);
        const geo = new THREE.PlaneGeometry(170, 100, 130, 70);
        geo.rotateX(-Math.PI / 2);
        geo.translate(0, 0, -34);
        const pos = geo.attributes.position;
        const base = Float32Array.from(pos.array);
        const stops = [0x1e9cf0, 0x2fb574, 0xffc800, 0xe8a33d, 0x9d8cff, 0x19b3b3].map((c) => new THREE.Color(c));
        const colors = new Float32Array(pos.count * 3);
        const tmp = new THREE.Color();
        for (let i = 0; i < pos.count; i++) {
            const u = (base[i * 3] + 85) / 170 * (stops.length - 1);
            const k = Math.min(stops.length - 2, Math.floor(u));
            tmp.copy(stops[k]).lerp(stops[k + 1], u - k);
            colors.set([tmp.r, tmp.g, tmp.b], i * 3);
        }
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        const land = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, wireframe: true, transparent: true, opacity: 0.32 }));
        scene.add(land);

        const { TeapotGeometry } = await import('three/addons/geometries/TeapotGeometry.js');
        const floaters = [];
        const add = (obj, x, y, z, spin) => { obj.position.set(x, y, z); obj.userData = { y, spin }; scene.add(obj); floaters.push(obj); };

        add(wire(THREE, new TeapotGeometry(0.9, 4), 0x1e9cf0, 0.38), -9.6, 3.3, -4, [0.1, 0.25]);
        add(wire(THREE, new THREE.IcosahedronGeometry(0.85, 1), 0x2fb574, 0.45), 9.4, 2.6, -5, [0.2, 0.15]);

        const sector = new THREE.Shape([[-1, -0.8], [0.4, -1], [1.1, -0.2], [0.8, 0.9], [-0.3, 1.1], [-1.2, 0.3]].map(([x, y]) => new THREE.Vector2(x, y)));
        add(edges(THREE, new THREE.ExtrudeGeometry(sector, { depth: 0.9, bevelEnabled: false }), 0xffc800, 0.75), -9.6, 4.6, -9, [0.35, 0.2]);

        const csg = new THREE.Group();
        csg.add(edges(THREE, new THREE.BoxGeometry(1.5, 1.5, 1.5), 0xb9adff, 0.8));
        csg.add(edges(THREE, new THREE.BoxGeometry(0.7, 1.9, 0.7), 0xff5a6e, 0.8));
        add(csg, 9.8, 5.2, -10, [0.25, 0.3]);

        add(wire(THREE, new THREE.ConeGeometry(1.1, 1.4, 7, 3), 0xe8a33d, 0.45), -4.6, 5.3, -12, [0, 0.3]);

        const px = new THREE.Group();
        const heart = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...'];
        const cube = new THREE.BoxGeometry(0.2, 0.2, 0.2);
        heart.forEach((row, y) => [...row].forEach((ch, x) => {
            if (ch !== 'X') return;
            const e = edges(THREE, cube, 0x19d3d3, 0.9);
            e.position.set((x - 3) * 0.22, (2.5 - y) * 0.22, 0);
            px.add(e);
        }));
        add(px, 4.8, 5.6, -13, [0, 0.4]);


        const look = new THREE.Vector3();
        return {
            scene, camera,
            update(t) {
                const off = t * 3.2;
                for (let i = 0; i < pos.count; i++) {
                    const x = base[i * 3], z = base[i * 3 + 2];
                    const n = noise(x * 0.045, (z - off) * 0.045) * 0.65 + noise(x * 0.11, (z - off) * 0.11) * 0.35;
                    const valley = 0.12 + 0.88 * smooth(5, 26, Math.abs(x));
                    pos.array[i * 3 + 1] = -3.6 + Math.pow(n * 0.5 + 0.5, 1.7) * 11 * valley;
                }
                pos.needsUpdate = true;
                floaters.forEach((o, i) => {
                    o.position.y = o.userData.y + Math.sin(t * 0.7 + i * 1.3) * 0.25;
                    o.rotation.x += o.userData.spin[0] * 0.01;
                    o.rotation.y += o.userData.spin[1] * 0.01;
                });
                camera.position.set(pointer.x * 2, 2.4 - pointer.y * 1, 12);
                look.set(pointer.x * 0.6, 1.6, 0);
                camera.lookAt(look);
            },
        };
    },

    // Animation Studio: the Utah teapot with 2D pencil strokes drawn in 3D space around it.
    async animation({ THREE, accent, pointer }) {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
        const { TeapotGeometry } = await import('three/addons/geometries/TeapotGeometry.js');

        const rig = new THREE.Group();
        scene.add(rig);
        const teapot = wire(THREE, new TeapotGeometry(1.25, 6, true, true, true, false, true), 0x5fb8f5, 0.34);
        teapot.position.y = -0.1;
        rig.add(teapot);

        const grid = new THREE.GridHelper(24, 24, 0x2a4f73, 0x16263a);
        grid.position.y = -1.45;
        grid.material.transparent = true;
        grid.material.opacity = 0.6;
        rig.add(grid);
        const axis = (a, b, c) => {
            const g = new THREE.BufferGeometry().setFromPoints([a, b]);
            rig.add(new THREE.Line(g, new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: 0.55 })));
        };
        axis(new THREE.Vector3(-12, -1.44, 0), new THREE.Vector3(12, -1.44, 0), 0xe0435a);
        axis(new THREE.Vector3(0, -1.44, -12), new THREE.Vector3(0, -1.44, 12), 0x3d7bff);

        // pencil strokes: thin tubes revealed segment by segment
        const strokes = [];
        const R = (a) => Math.sin(a * 12.9898) * 0.5;
        for (let k = 0; k < 6; k++) {
            const pts = [];
            const r = 1.9 + k * 0.22, y0 = -0.9 + k * 0.38, turns = 0.55 + R(k + 1) * 0.3;
            for (let i = 0; i <= 12; i++) {
                const a = k * 1.3 + i / 12 * Math.PI * 2 * turns;
                pts.push(new THREE.Vector3(Math.cos(a) * r, y0 + Math.sin(i * 0.9 + k) * 0.35, Math.sin(a) * r));
            }
            const curve = new THREE.CatmullRomCurve3(pts);
            const geo = new THREE.TubeGeometry(curve, 160, 0.011 + (k % 2) * 0.006, 5);
            const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: k % 3 === 0 ? 0xffffff : accent, transparent: true, opacity: 0.85 }));
            mesh.userData = { total: geo.index.count, offset: k * 0.9 };
            geo.setDrawRange(0, 0);
            rig.add(mesh);
            strokes.push(mesh);
        }

        // a scene camera gizmo, as seen in the viewport
        const cam = new THREE.Group();
        const c = [[0, 0, 0], [-0.45, 0.28, -0.7], [0.45, 0.28, -0.7], [0.45, -0.28, -0.7], [-0.45, -0.28, -0.7]].map((p) => new THREE.Vector3(...p));
        const segs = [0, 1, 0, 2, 0, 3, 0, 4, 1, 2, 2, 3, 3, 4, 4, 1].map((i) => c[i]);
        segs.push(new THREE.Vector3(-0.2, 0.34, -0.7), new THREE.Vector3(0, 0.52, -0.7), new THREE.Vector3(0, 0.52, -0.7), new THREE.Vector3(0.2, 0.34, -0.7));
        cam.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(segs), new THREE.LineBasicMaterial({ color: 0xffb347, transparent: true, opacity: 0.8 })));
        cam.position.set(-3.1, 1.6, 2.4);
        cam.lookAt(0, 0, 0);
        rig.add(cam);

        return {
            scene, camera,
            update(t) {
                teapot.rotation.y = t * 0.18;
                rig.rotation.y = Math.sin(t * 0.12) * 0.35;
                strokes.forEach((m) => {
                    const cyc = ((t * 0.16 + m.userData.offset * 0.1) % 1.25);
                    const on = Math.min(1, cyc / 0.8);
                    const count = Math.floor(on * m.userData.total / 30) * 30;
                    m.geometry.setDrawRange(0, count);
                    m.material.opacity = cyc > 1 ? 0.85 * (1 - (cyc - 1) / 0.25) : 0.85;
                });
                camera.position.set(pointer.x * 1.4, 1.5 - pointer.y * 0.8, 7.2);
                camera.lookAt(0, 0.1, 0);
            },
        };
    },

    // FPS Lab: an endless corridor of door frames over a glowing navigation-cell floor.
    fps({ THREE, pointer }) {
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x0a0b10, 4, 36);
        const camera = new THREE.PerspectiveCamera(62, 1, 0.1, 100);
        const GREEN = 0x6fd49a, SP = 4, N = 12;

        const world = new THREE.Group();
        scene.add(world);
        const arch = new THREE.Shape();
        arch.moveTo(-2, 0); arch.lineTo(-2, 2.6); arch.absarc(0, 2.6, 2, Math.PI, 0, true); arch.lineTo(2, 0);
        arch.lineTo(2.35, 0); arch.lineTo(2.35, 2.6); arch.absarc(0, 2.6, 2.35, 0, Math.PI, false); arch.lineTo(-2.35, 0);
        const frameGeo = new THREE.EdgesGeometry(new THREE.ExtrudeGeometry(arch, { depth: 0.35, bevelEnabled: false, curveSegments: 16 }), 20);
        for (let i = 0; i < N; i++) {
            const f = new THREE.LineSegments(frameGeo, new THREE.LineBasicMaterial({ color: GREEN, transparent: true, opacity: 0.7 }));
            f.position.set(0, -1.6, -i * SP);
            world.add(f);
        }
        // walls and ceiling rails
        const rails = [];
        [[-2.35, -1.6], [2.35, -1.6], [-2.35, 1], [2.35, 1]].forEach(([x, y]) => rails.push(new THREE.Vector3(x, y, 6), new THREE.Vector3(x, y, -N * SP)));
        scene.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(rails), new THREE.LineBasicMaterial({ color: GREEN, transparent: true, opacity: 0.35 })));

        // nav volume cells on the floor
        const cols = 8, rows = N * 8, cell = 0.5;
        const cells = new THREE.InstancedMesh(new THREE.PlaneGeometry(cell * 0.86, cell * 0.86).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.55, depthWrite: false, blending: THREE.AdditiveBlending }), cols * rows);
        const m = new THREE.Matrix4(), col = new THREE.Color();
        let k = 0;
        for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
            m.makeTranslation((c - cols / 2 + 0.5) * cell, -1.58, -r * cell + 2);
            cells.setMatrixAt(k, m);
            cells.setColorAt(k++, col.setRGB(0.1, 0.35, 0.2));
        }
        world.add(cells);

        // a nav agent walking the corridor ahead
        const agent = wire(THREE, new THREE.CapsuleGeometry(0.28, 0.8, 3, 8), 0xffffff, 0.6);
        scene.add(agent);

        return {
            scene, camera,
            update(t) {
                const travel = t * 2.6;
                world.position.z = travel % SP;
                let i = 0;
                for (let r = 0; r < rows; r++) {
                    const z = -r * cell + 2 + world.position.z;
                    for (let c = 0; c < cols; c++) {
                        const wave = Math.max(0, Math.sin(z * 0.9 - t * 3 + Math.abs(c - 3.5) * 0.6));
                        cells.setColorAt(i++, col.setRGB(0.05 + wave * 0.25, 0.22 + wave * 0.6, 0.12 + wave * 0.35));
                    }
                }
                cells.instanceColor.needsUpdate = true;
                agent.position.set(Math.sin(t * 0.8) * 1.1, -0.95 + Math.abs(Math.sin(t * 4)) * 0.05, -9 + Math.sin(t * 0.4) * 2);
                agent.rotation.y = t;
                const bob = Math.sin(t * 5.2) * 0.04;
                camera.position.set(pointer.x * 0.8 + Math.sin(t * 2.6) * 0.03, 0.1 + bob - pointer.y * 0.4, 3);
                camera.lookAt(pointer.x * 2.5, 0 - pointer.y * 1.2, -10);
            },
        };
    },

    // Level Editor: sectors drawn on a 2D grid that extrude into walls as the camera tilts to 3D.
    editor({ THREE, pointer }) {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200);
        const YELLOW = 0xffc800, RED = 0xff2a2a;

        const grid = new THREE.GridHelper(64, 64, 0x2c2c2c, 0x1a1a1a);
        scene.add(grid);

        const sectors = [
            { pts: [[-9, -5], [-3, -5], [-3, -1.5], [-1, -1.5], [-1, 1], [-3, 1], [-3, 4], [-9, 4]], h: 3 },
            { pts: [[-1, -1.5], [3, -1.5], [3, 1], [-1, 1]], h: 2.2 },
            { pts: [[3, -3.5], [5, -5.5], [8, -5.5], [10, -3.5], [10, 3], [8, 5], [5, 5], [3, 3]], h: 3.6 },
            { pts: [[-7, 4], [-5, 4], [-5, 8], [-7, 8]], h: 1.6 },
            { pts: [[5.5, -1.5], [7.5, -1.5], [7.5, 1.5], [5.5, 1.5]], h: 0.8, floor: 0.5 },
        ];
        const rise = new THREE.Group();
        scene.add(rise);
        const vertPts = [];
        sectors.forEach((s, si) => {
            const floor = s.floor || 0;
            const ring = s.pts.map(([x, z]) => new THREE.Vector3(x, floor, z));
            const shape = new THREE.Shape(s.pts.map(([x, z]) => new THREE.Vector2(x, -z)));
            const fill = new THREE.Mesh(new THREE.ShapeGeometry(shape).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0x8a5a1c, transparent: true, opacity: 0.16, side: THREE.DoubleSide, depthWrite: false }));
            fill.position.y = floor + 0.01;
            scene.add(fill);
            const segs = [], tops = [], verts = [];
            ring.forEach((a, i) => {
                const b = ring[(i + 1) % ring.length];
                segs.push(a, b);
                tops.push(new THREE.Vector3(a.x, s.h, a.z), new THREE.Vector3(b.x, s.h, b.z));
                verts.push(a, new THREE.Vector3(a.x, s.h, a.z));
                vertPts.push(a);
            });
            const lineMat = new THREE.LineBasicMaterial({ color: YELLOW, transparent: true, opacity: 0.95 });
            scene.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(segs), lineMat));
            // top outline and vertical edges scale up from the floor
            const up = new THREE.Group();
            up.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(tops), new THREE.LineBasicMaterial({ color: YELLOW, transparent: true, opacity: 0.55 })));
            up.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(verts), new THREE.LineBasicMaterial({ color: 0xffe27a, transparent: true, opacity: 0.35 })));
            // translucent walls
            const wallGeo = new THREE.BufferGeometry();
            const wp = [];
            ring.forEach((a, i) => {
                const b = ring[(i + 1) % ring.length];
                wp.push(a.x, floor, a.z, b.x, floor, b.z, b.x, s.h, b.z, a.x, floor, a.z, b.x, s.h, b.z, a.x, s.h, a.z);
            });
            wallGeo.setAttribute('position', new THREE.Float32BufferAttribute(wp, 3));
            up.add(new THREE.Mesh(wallGeo, new THREE.MeshBasicMaterial({ color: 0xffb000, transparent: true, opacity: 0.05, side: THREE.DoubleSide, depthWrite: false })));
            up.userData.floor = floor;
            rise.add(up);
            if (si === 0) {
                const sel = new THREE.BufferGeometry().setFromPoints([ring[0], ring[ring.length - 1]]);
                scene.add(new THREE.Line(sel, new THREE.LineBasicMaterial({ color: RED })));
            }
        });
        const points = new THREE.Points(new THREE.BufferGeometry().setFromPoints(vertPts), new THREE.PointsMaterial({ color: 0xffffff, size: 7, sizeAttenuation: false }));
        points.position.y = 0.02;
        scene.add(points);
        // player start
        const start = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.8, 3).rotateX(Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0x3dff7a }));
        start.position.set(-6, 0.2, 0);
        scene.add(start);

        return {
            scene, camera,
            update(t) {
                const tilt = 0.5 - 0.5 * Math.cos(t * 0.32);            // 0 = plan view, 1 = 3D
                const ext = smooth(0.15, 0.85, tilt);
                rise.children.forEach((g) => {
                    g.scale.y = Math.max(0.001, ext);
                    g.position.y = g.userData.floor * (1 - ext);
                });
                const yaw = t * 0.07 + pointer.x * 0.6;
                const pitch = THREE.MathUtils.lerp(1.52, 0.62, tilt) - pointer.y * 0.15;
                const dist = THREE.MathUtils.lerp(26, 22, tilt);
                camera.position.set(Math.sin(yaw) * Math.cos(pitch) * dist, Math.sin(pitch) * dist, Math.cos(yaw) * Math.cos(pitch) * dist);
                camera.lookAt(0.5, 0, 0);
                start.rotation.y = t;
            },
        };
    },

    // Level Modeller: checker-textured CSG blocks, red negative brushes and a spiral staircase.
    modeller({ THREE, pointer }) {
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x14111c, 18, 48);
        const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 200);
        scene.add(new THREE.HemisphereLight(0xcfc4ff, 0x1b1426, 1.1));
        const sun = new THREE.DirectionalLight(0xfff1d6, 2.2);
        sun.position.set(6, 10, 4);
        scene.add(sun);

        const tex = checkerTexture(THREE, '#8f8aa3', '#b9b4c9');
        const mat = (rx, ry) => {
            const t = tex.clone();
            t.repeat.set(rx, ry);
            t.needsUpdate = true;
            return new THREE.MeshLambertMaterial({ map: t });
        };
        const root = new THREE.Group();
        scene.add(root);

        const grid = new THREE.GridHelper(60, 60, 0x4b4260, 0x2a2438);
        grid.position.y = -0.01;
        root.add(grid);

        // a room with a doorway: walls built around the cutter gap
        const box = (w, h, d, x, y, z) => {
            const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(Math.max(w, d) / 1.5, h / 1.5));
            m.position.set(x, y + h / 2, z);
            root.add(m);
            return m;
        };
        box(8, 0.4, 7, 0, 0, 0);
        box(8, 3.4, 0.4, 0, 0.4, -3.3);
        box(0.4, 3.4, 7, -3.8, 0.4, 0);
        box(0.4, 3.4, 2.6, 3.8, 0.4, -2.2);
        box(0.4, 3.4, 2.0, 3.8, 0.4, 2.5);
        box(0.4, 1.2, 1.8, 3.8, 2.6, 0.1);

        const cutterMat = new THREE.LineBasicMaterial({ color: 0xff4d6d, transparent: true, opacity: 0.9 });
        const cutter = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.2, 2.2, 1.8)), cutterMat);
        cutter.position.set(3.8, 1.5, 0.1);
        root.add(cutter);
        const windowCut = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(2.2, 1.2, 1)), cutterMat);
        windowCut.position.set(-0.6, 2.2, -3.3);
        root.add(windowCut);

        // spiral staircase
        const stairs = new THREE.Group();
        const stepMat = mat(1, 0.3);
        for (let i = 0; i < 22; i++) {
            const step = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.16, 0.55), stepMat);
            const a = i * 0.36;
            step.position.set(Math.cos(a) * 1.05, 0.5 + i * 0.2, Math.sin(a) * 1.05);
            step.rotation.y = -a;
            stairs.add(step);
        }
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 5.2, 16), mat(1, 4));
        pole.position.y = 2.6;
        stairs.add(pole);
        stairs.position.set(-1.2, 0, 0.2);
        root.add(stairs);

        // floating primitives with wireframe overlays
        const orb = new THREE.Mesh(new THREE.SphereGeometry(0.8, 24, 16), mat(4, 2));
        orb.position.set(7.2, 3.2, -1.5);
        root.add(orb);
        const orbCut = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(0.9, 0.9, 0.9)), cutterMat);
        root.add(orbCut);
        const pos = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.CylinderGeometry(0.7, 0.7, 1.6, 12)), new THREE.LineBasicMaterial({ color: 0x9d8cff }));
        pos.position.set(6.5, 1.2, 3.8);
        root.add(pos);

        return {
            scene, camera,
            update(t) {
                cutterMat.opacity = 0.55 + Math.sin(t * 3) * 0.35;
                stairs.rotation.y = t * 0.25;
                orb.rotation.y = t * 0.4;
                orbCut.position.set(7.2 + Math.sin(t * 0.9) * 0.6, 3.2 + Math.cos(t * 0.7) * 0.4, -1.5 + 0.4);
                orbCut.rotation.set(t * 0.3, t * 0.5, 0);
                pos.rotation.y = -t * 0.3;
                const yaw = 0.7 + Math.sin(t * 0.1) * 0.45 + pointer.x * 0.5;
                camera.position.set(Math.sin(yaw) * 17, 8.5 - pointer.y * 3, Math.cos(yaw) * 17);
                camera.lookAt(1.5, 1.6, 0);
            },
        };
    },

    // Terrain Generator: land rises out of the sea, holds, sinks and regenerates with a new seed.
    terrain({ THREE, pointer }) {
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x14100c, 26, 70);
        const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 300);
        scene.add(new THREE.HemisphereLight(0xffe2b8, 0x1d2a33, 1.0));
        const sun = new THREE.DirectionalLight(0xffc98a, 2.6);
        sun.position.set(-12, 9, -6);
        scene.add(sun);

        const S = 34, SEG = 150;
        const geo = new THREE.PlaneGeometry(S, S, SEG, SEG);
        geo.rotateX(-Math.PI / 2);
        const pos = geo.attributes.position;
        const colors = new Float32Array(pos.count * 3);
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        const land = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0, flatShading: false }));
        scene.add(land);
        const contour = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xe8a33d, wireframe: true, transparent: true, opacity: 0.06 }));
        scene.add(contour);

        const water = new THREE.Mesh(new THREE.PlaneGeometry(200, 200).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0x1f5d6e, roughness: 0.25, metalness: 0.1, transparent: true, opacity: 0.82 }));
        water.position.y = 0.6;
        scene.add(water);

        const pal = { sand: new THREE.Color(0xcdb68b), grass: new THREE.Color(0x5d7d3a), forest: new THREE.Color(0x3c5a2b), rock: new THREE.Color(0x7b6b5a), snow: new THREE.Color(0xeeeae2) };
        const c = new THREE.Color();
        let seed = 3, noise = makeNoise(seed), lastCycle = -1;
        const heights = new Float32Array(pos.count);

        const generate = () => {
            for (let i = 0; i < pos.count; i++) {
                const x = pos.array[i * 3], z = pos.array[i * 3 + 2];
                let h = 0, amp = 1, f = 0.06;
                for (let o = 0; o < 5; o++) {
                    const n = 1 - Math.abs(noise(x * f + seed * 10, z * f));
                    h += n * n * amp;
                    amp *= 0.5; f *= 2.05;
                }
                const r = Math.hypot(x, z) / (S * 0.5);
                heights[i] = Math.max(0, h * 6.2 - 1.2) * (1 - smooth(0.55, 1, r)) - smooth(0.7, 1, r) * 1.5;
            }
        };
        generate();

        return {
            scene, camera,
            update(t) {
                const CYCLE = 16, tt = t + CYCLE * 0.3;     // start with the land already risen
                const cycle = Math.floor(tt / CYCLE), ph = (tt % CYCLE) / CYCLE;
                if (cycle !== lastCycle) {
                    if (lastCycle !== -1) { seed++; noise = makeNoise(seed); generate(); }
                    lastCycle = cycle;
                }
                const g = reduced ? 1 : smooth(0, 0.3, ph) * (1 - smooth(0.88, 1, ph));
                for (let i = 0; i < pos.count; i++) {
                    const y = heights[i] * g - 1.4 * (1 - g);
                    pos.array[i * 3 + 1] = y;
                    if (y < 0.9) c.copy(pal.sand);
                    else if (y < 2.2) c.copy(pal.grass).lerp(pal.forest, smooth(1.2, 2.2, y));
                    else if (y < 4.4) c.copy(pal.forest).lerp(pal.rock, smooth(2.2, 3.6, y));
                    else c.copy(pal.rock).lerp(pal.snow, smooth(4.4, 5.4, y));
                    colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
                }
                pos.needsUpdate = true;
                geo.attributes.color.needsUpdate = true;
                geo.computeVertexNormals();
                water.position.y = 0.6 + Math.sin(t * 0.8) * 0.04;
                const yaw = t * 0.06 + pointer.x * 0.6;
                camera.position.set(Math.sin(yaw) * 30, 15 - pointer.y * 5, Math.cos(yaw) * 30);
                camera.lookAt(0, 1, 0);
            },
        };
    },
};

// ------------------------------------------------------------------
// 2D runner + scenes
// ------------------------------------------------------------------

function run2D(canvas, scene, accent) {
    const g = canvas.getContext('2d');
    const state = { w: 0, h: 0, dpr: 1, accent, pointer: pointerTracker() };
    const resize = () => {
        state.dpr = Math.min(devicePixelRatio, 2);
        state.w = hero.clientWidth;
        state.h = hero.clientHeight;
        canvas.width = state.w * state.dpr;
        canvas.height = state.h * state.dpr;
        g.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
        scene.resize?.(state, g);
    };
    const go = () => {
        resize();
        new ResizeObserver(resize).observe(hero);
        loop((t, dt) => { state.pointer.step(); scene.draw(g, state, t, dt); });
    };
    (document.fonts?.ready || Promise.resolve()).then(go);
}

const SCENES_2D = {

    // PixelPaint 98 Pro: a Win98-style window where pixel art gets painted one pixel at a time.
    pixelpaint: (() => {
        const SPRITES = [
            {
                pal: { k: '#1b1b1b', w: '#ffffff', r: '#e8413c', R: '#a31d1d', p: '#ffb3c7', s: '#f5d7a1' },
                rows: [
                    '.....kkkkkk.....', '...kkrrrrrrkk...', '..krrwwrrrrrrk..', '.krrwwwrrrwwrrk.',
                    '.krrrwrrrrwwwrk.', 'krrrrrrrrrrwrrrk', 'kRrrrwwrrrrrrrRk', 'kRRrwwwwrrrrrRRk',
                    '.kkkkkkkkkkkkkk.', '....kssssssk....', '....kskssksk....', '....kssssssk....',
                    '....ksspssk.....', '.....kssssk.....', '......kkkk......', '................',
                ],
            },
            {
                pal: { k: '#1b1b1b', b: '#1e88e5', B: '#0d5aa7', w: '#ffffff', g: '#c0c0c0' },
                rows: [
                    '................', '.......kk.......', '......kwwk......', '...kkkkbbkkkk...',
                    '..kbbbbbbbbbbk.k', '.kbbwbbbbbbbbbkk', 'kbbwbbbbbbbbbbkb', 'kbbbbbbbbbbbbbkb',
                    'kBbbbbbbbbbbbBkk', 'kBBbbbbbbbbbBBk.', '.kBBbbbbbbbBBk..', '..kkBBBBBBBBkk..',
                    '....kkkkkkkk....', '................', '................', '................',
                ],
            },
            {
                pal: { k: '#1b1b1b', y: '#ffd23f', o: '#f08a24', w: '#ffffff', g: '#3fb36b', G: '#23804a' },
                rows: [
                    '................', '.......kk.......', '......kyyk......', '......kyyk......',
                    '.kkkkkyyyykkkkk.', '.kyyyyyyyyyyyyk.', '..kyyywyywyyyk..', '...kyyyyyyyyk...',
                    '....kyyoooyk....', '...kyyyyyyyyk...', '...kyyykkyyyk...', '..kyyk....kyyk..',
                    '..kkk......kkk..', '......kGGk......', '.....kggggk.....', '......kkkk......',
                ],
            },
        ];
        let cell = 16, ox = 0, oy = 0, win = null;
        return {
            resize(s) {
                const area = Math.min(s.h * 0.62, s.w * (s.w > 980 ? 0.36 : 0.8));
                cell = Math.max(8, Math.floor(area / 16));
                const size = cell * 16;
                const cx = s.w > 980 ? s.w * 0.72 : s.w / 2;
                ox = Math.round(cx - size / 2);
                oy = Math.round(s.h * 0.5 - size / 2 + 14);
                win = { x: ox - 18, y: oy - 52, w: size + 36, h: size + 88 };
            },
            draw(g, s, t) {
                g.fillStyle = '#006b6b';
                g.fillRect(0, 0, s.w, s.h);
                // desktop dither grid
                g.fillStyle = 'rgba(255,255,255,.035)';
                const step = 24;
                for (let y = 0; y < s.h; y += step) for (let x = (y / step) % 2 ? step / 2 : 0; x < s.w; x += step) g.fillRect(x, y, 3, 3);

                const px = s.pointer.x * 10, py = s.pointer.y * 8;
                g.save();
                g.translate(px, py);
                bevelBox(g, win.x, win.y, win.w, win.h);
                const grad = g.createLinearGradient(win.x, 0, win.x + win.w, 0);
                grad.addColorStop(0, '#000080'); grad.addColorStop(1, '#1084d0');
                g.fillStyle = grad;
                g.fillRect(win.x + 4, win.y + 4, win.w - 8, 22);
                g.fillStyle = '#fff';
                g.font = 'bold 12px Tahoma, Verdana, sans-serif';
                g.textBaseline = 'middle';
                g.fillText('PixelPaint 98 Pro - sprite.png', win.x + 10, win.y + 15);
                ['✕', '□', '_'].forEach((ch, i) => {
                    const bx = win.x + win.w - 24 - i * 20;
                    bevelBox(g, bx, win.y + 7, 16, 14);
                    g.fillStyle = '#000'; g.font = 'bold 10px Tahoma, sans-serif'; g.fillText(ch, bx + 4, win.y + 14);
                });
                g.fillStyle = '#000';
                g.font = '12px Tahoma, Verdana, sans-serif';
                ['File', 'Edit', 'Image', 'Layer', 'Scripts'].reduce((x, m) => { g.fillText(m, x, win.y + 38); return x + g.measureText(m).width + 14; }, win.x + 10);

                const size = cell * 16;
                // transparent checkerboard canvas
                for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) {
                    g.fillStyle = (x + y) % 2 ? '#d9d9d9' : '#f2f2f2';
                    g.fillRect(ox + x * cell, oy + y * cell, cell, cell);
                }
                const PER = 12, spr = SPRITES[Math.floor(t / PER) % SPRITES.length], ph = (t % PER) / PER;
                const filled = [];
                spr.rows.forEach((row, y) => [...row].forEach((ch, x) => { if (ch !== '.') filled.push([x, y, spr.pal[ch]]); }));
                const shown = Math.floor(smooth(0.02, 0.62, ph) * filled.length);
                const fade = 1 - smooth(0.9, 1, ph);
                g.globalAlpha = fade;
                for (let i = 0; i < shown; i++) {
                    const [x, y, c] = filled[i];
                    g.fillStyle = c;
                    g.fillRect(ox + x * cell, oy + y * cell, cell, cell);
                }
                g.globalAlpha = 1;
                g.strokeStyle = 'rgba(0,0,0,.08)';
                g.lineWidth = 1;
                g.beginPath();
                for (let i = 1; i < 16; i++) {
                    g.moveTo(ox + i * cell + 0.5, oy); g.lineTo(ox + i * cell + 0.5, oy + size);
                    g.moveTo(ox, oy + i * cell + 0.5); g.lineTo(ox + size, oy + i * cell + 0.5);
                }
                g.stroke();
                // pencil cursor on the last painted pixel
                const cur = filled[Math.min(filled.length - 1, Math.max(0, shown - 1))];
                if (cur && ph < 0.66) drawPencil(g, ox + cur[0] * cell + cell * 0.6, oy + cur[1] * cell + cell * 0.4);
                // palette strip
                const pal = Object.values(spr.pal);
                pal.forEach((c, i) => { bevelBox(g, win.x + 12 + i * 22, win.y + win.h - 28, 18, 18, true); g.fillStyle = c; g.fillRect(win.x + 15 + i * 22, win.y + win.h - 25, 12, 12); });
                g.restore();
            },
        };
        function bevelBox(g, x, y, w, h, inset = false) {
            g.fillStyle = '#c0c0c0';
            g.fillRect(x, y, w, h);
            g.fillStyle = inset ? '#808080' : '#ffffff';
            g.fillRect(x, y, w, 2); g.fillRect(x, y, 2, h);
            g.fillStyle = inset ? '#ffffff' : '#404040';
            g.fillRect(x, y + h - 2, w, 2); g.fillRect(x + w - 2, y, 2, h);
        }
        function drawPencil(g, x, y) {
            g.save();
            g.translate(x, y);
            g.rotate(-Math.PI / 4);
            g.fillStyle = '#1b1b1b'; g.beginPath(); g.moveTo(0, 0); g.lineTo(6, -5); g.lineTo(6, 5); g.fill();
            g.fillStyle = '#f5d7a1'; g.beginPath(); g.moveTo(3, -2.5); g.lineTo(12, -6); g.lineTo(12, 6); g.lineTo(3, 2.5); g.fill();
            g.fillStyle = '#ffd23f'; g.fillRect(12, -6, 30, 12);
            g.fillStyle = '#c9a100'; g.fillRect(12, 2, 30, 4);
            g.fillStyle = '#bdbdbd'; g.fillRect(42, -6, 6, 12);
            g.fillStyle = '#ff8fab'; g.fillRect(48, -6, 8, 12);
            g.strokeStyle = '#1b1b1b'; g.lineWidth = 1.5; g.strokeRect(12, -6, 44, 12);
            g.restore();
        }
    })(),

};

// ------------------------------------------------------------------
// boot
// ------------------------------------------------------------------

if (hero) {
    const canvas = document.createElement('canvas');
    canvas.className = 'pa-hero__canvas';
    canvas.setAttribute('aria-hidden', 'true');
    hero.prepend(canvas);
    const kind = hero.dataset.hero;
    const accent = getComputedStyle(hero).getPropertyValue('--p').trim() || '#1e9cf0';
    if (SCENES_2D[kind]) run2D(canvas, SCENES_2D[kind], accent);
    else if (SCENES_3D[kind]) run3D(canvas, SCENES_3D[kind], accent);
}
