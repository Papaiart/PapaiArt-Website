import * as THREE from 'https://esm.sh/three@0.160.0';
import { TeapotGeometry } from 'https://esm.sh/three@0.160.0/examples/jsm/geometries/TeapotGeometry';

const heroEl = document.querySelector('.hero, .about-hero');
if (heroEl) {
    const canvas = document.createElement('canvas');
    canvas.className = 'hero__canvas';
    canvas.setAttribute('aria-hidden', 'true');

    const grid = document.createElement('div');
    grid.className = 'hero__grid';
    grid.setAttribute('aria-hidden', 'true');

    heroEl.prepend(grid);
    heroEl.prepend(canvas);

    let renderer;
    try {
        renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    } catch (e) {
        canvas.remove();
    }

    if (renderer) {
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
        camera.position.z = 3.8;

        const additive = THREE.AdditiveBlending;

        const teapotGeo = new TeapotGeometry(1.15, 5, true, true, true, false, true);
        const teapot = new THREE.LineSegments(
            new THREE.WireframeGeometry(teapotGeo),
            new THREE.LineBasicMaterial({ color: 0x5fb8f5, transparent: true, opacity: 0.26, blending: additive })
        );
        teapot.position.y = -0.2;
        scene.add(teapot);

        const knot = new THREE.LineSegments(
            new THREE.WireframeGeometry(new THREE.TorusKnotGeometry(0.7, 0.18, 100, 14)),
            new THREE.LineBasicMaterial({ color: 0x1e9cf0, transparent: true, opacity: 0.20, blending: additive })
        );
        knot.position.set(3.8, -1.25, -0.4);
        scene.add(knot);

        const oct = new THREE.LineSegments(
            new THREE.WireframeGeometry(new THREE.OctahedronGeometry(0.55, 0)),
            new THREE.LineBasicMaterial({ color: 0xef233c, transparent: true, opacity: 0.22, blending: additive })
        );
        oct.position.set(-3.9, 1.3, 0.3);
        scene.add(oct);

        const torus = new THREE.LineSegments(
            new THREE.WireframeGeometry(new THREE.TorusGeometry(0.45, 0.14, 12, 24)),
            new THREE.LineBasicMaterial({ color: 0x5fb8f5, transparent: true, opacity: 0.15, blending: additive })
        );
        torus.position.set(-3.5, -1.25, 0.2);
        scene.add(torus);

        const ico = new THREE.LineSegments(
            new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(0.4, 0)),
            new THREE.LineBasicMaterial({ color: 0x1e9cf0, transparent: true, opacity: 0.18, blending: additive })
        );
        ico.position.set(3.5, 1.3, 0.3);
        scene.add(ico);

        const meshes = [teapot, knot, oct, torus, ico];
        const speeds = [
            { x: 0.07, y: 0.11, z: 0.05 },
            { x: -0.12, y: 0.15, z: 0.0 },
            { x: 0.20, y: 0.0, z: 0.10 },
            { x: 0.05, y: -0.18, z: 0.0 },
            { x: 0.10, y: 0.10, z: 0.0 },
        ];

        const resize = () => {
            const w = heroEl.clientWidth;
            const h = heroEl.clientHeight;
            renderer.setSize(w, h, false);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
        };
        resize();
        window.addEventListener('resize', resize);

        let targetX = 0, targetY = 0, smoothX = 0, smoothY = 0;
        window.addEventListener('pointermove', (e) => {
            targetX = (e.clientX / window.innerWidth - 0.5);
            targetY = (e.clientY / window.innerHeight - 0.5);
        }, { passive: true });

        const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

        let lastTime = performance.now();
        const tick = (now) => {
            const dt = Math.min((now - lastTime) * 0.001, 0.05);
            lastTime = now;

            smoothX += (targetX - smoothX) * 0.05;
            smoothY += (targetY - smoothY) * 0.05;

            if (!reduced) {
                meshes.forEach((m, i) => {
                    m.rotation.x += dt * speeds[i].x;
                    m.rotation.y += dt * speeds[i].y;
                    m.rotation.z += dt * speeds[i].z;
                });
            }

            scene.position.x = smoothX * 0.5;
            scene.position.y = -smoothY * 0.4;

            renderer.render(scene, camera);
            requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }
}
