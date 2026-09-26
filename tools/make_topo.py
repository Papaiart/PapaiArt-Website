"""
Generate the seamless topographic contour pattern used as the page background.

    python tools/make_topo.py [seed]

Writes assets/images/topo.svg. The height field is a sum of cosines with integer
frequencies, so it is periodic and the tile repeats without visible seams.
Requires numpy and scikit-image.
"""
import os
import sys

import numpy as np
from skimage import measure

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'images', 'topo.svg')

L = 1200          # tile size in px
N = 240           # samples per tile edge
PAD = 60          # extra samples around the tile so contours run well past the edges
LEVELS = 12


def field(seed):
    rng = np.random.default_rng(seed)
    idx = np.arange(-PAD, N + PAD)
    u = idx / N
    X, Y = np.meshgrid(u, u)
    h = np.zeros_like(X)
    for _ in range(18):
        kx, ky = rng.integers(-3, 4, size=2)
        if kx == 0 and ky == 0:
            continue
        k = np.hypot(kx, ky)
        h += np.cos(2 * np.pi * (kx * X + ky * Y) + rng.uniform(0, 2 * np.pi)) / k ** 1.5
    return (h - h.min()) / (h.max() - h.min())


def smooth_path(pts):
    """Catmull-Rom through the contour points, emitted as cubic Bezier segments."""
    closed = np.allclose(pts[0], pts[-1])
    if closed:
        pts = pts[:-1]
    n = len(pts)
    get = (lambda i: pts[i % n]) if closed else (lambda i: pts[min(max(i, 0), n - 1)])
    d = [f'M{pts[0][0]:.1f} {pts[0][1]:.1f}']
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = get(i - 1), get(i), get(i + 1), get(i + 2)
        c1 = p1 + (p2 - p0) / 6
        c2 = p2 - (p3 - p1) / 6
        d.append(f'C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    if closed:
        d.append('Z')
    return ''.join(d)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    h = field(seed)
    scale = L / N
    paths = []
    for i, level in enumerate(np.linspace(0.06, 0.94, LEVELS)):
        for c in measure.find_contours(h, level):
            pts = measure.approximate_polygon(c, tolerance=0.35)
            if len(pts) < 4:
                continue
            xy = np.stack([(pts[:, 1] - PAD) * scale, (pts[:, 0] - PAD) * scale], axis=1)
            width = 1.6 if i % 5 == 0 else 1.0          # every fifth line is an index contour
            paths.append(f'<path d="{smooth_path(xy)}" stroke-width="{width}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{L}" height="{L}" viewBox="0 0 {L} {L}">'
           f'<g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round">{"".join(paths)}</g></svg>\n')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'{len(paths)} contours, {len(svg) // 1024} KB -> {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
