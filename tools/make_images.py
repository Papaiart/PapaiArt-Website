"""
Generate the favicon and the 1200x630 social-share (Open Graph) images.

    python tools/make_images.py

Writes assets/images/favicon.png, assets/images/og/home.png and
assets/images/og/<product>.png. Re-run after changing product colours or hero shots.
Requires Pillow; uses Segoe UI from C:/Windows/Fonts (falls back to Pillow's default font).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from build_site import PRODUCTS  # noqa: E402

IMG = os.path.join(ROOT, 'assets', 'images')
W, H = 1200, 630
BG = (10, 11, 16)


def font(size, bold=True):
    for name in (('segoeuib.ttf', 'seguisb.ttf') if bold else ('segoeui.ttf',)):
        try:
            return ImageFont.truetype(os.path.join('C:/Windows/Fonts', name), size)
        except OSError:
            continue
    return ImageFont.load_default()


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def glow(img, color, center, radius, alpha=150):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.55)))


def grid(img, step=48, alpha=14):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, W, step):
        d.line((x, 0, x, H), fill=(255, 255, 255, alpha))
    for y in range(0, H, step):
        d.line((0, y, W, y), fill=(255, 255, 255, alpha))
    img.alpha_composite(layer)


def favicon():
    mark = Image.open(os.path.join(IMG, 'pa-mark.png')).convert('RGBA')
    for size, name in ((64, 'favicon.png'), (180, 'apple-touch-icon.png'), (512, 'icon-512.png')):
        S = size * 4
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=S // 5, fill=(22, 25, 36, 255))
        m = mark.copy()
        m.thumbnail((int(S * 0.66), int(S * 0.66)), Image.LANCZOS)
        im.alpha_composite(m, ((S - m.width) // 2, (S - m.height) // 2))
        im.resize((size, size), Image.LANCZOS).save(os.path.join(IMG, name))


def og_home():
    im = Image.new('RGBA', (W, H), (*BG, 255))
    grid(im)
    for i, p in enumerate(PRODUCTS):
        glow(im, hex_rgb(p['color']), (120 + i * 160, 560), 120, 70)
    d = ImageDraw.Draw(im)
    mark = Image.open(os.path.join(IMG, 'pa-mark.png')).convert('RGBA')
    mark.thumbnail((70, 70))
    im.alpha_composite(mark, (80, 70))
    d.text((170, 82), 'PapaiArt', font=font(44), fill='white')
    d.text((80, 190), 'Tools for building worlds.', font=font(76), fill='white')
    d.text((82, 290), 'Level design · game engine · terrain · animation · pixel art', font=font(28, False), fill=(170, 178, 196))
    x = 80
    for p in PRODUCTS:
        ic = Image.open(os.path.join(IMG, 'icons', f'{p["id"]}.png')).convert('RGBA').resize((112, 112), Image.LANCZOS)
        im.alpha_composite(ic, (x, 390))
        x += 170
    os.makedirs(os.path.join(IMG, 'og'), exist_ok=True)
    im.convert('RGB').save(os.path.join(IMG, 'og', 'home.png'), optimize=True)


def og_product(p):
    col = hex_rgb(p['color'])
    im = Image.new('RGBA', (W, H), (*BG, 255))
    grid(im)
    glow(im, col, (900, 300), 330, 110)
    shot = Image.open(os.path.join(IMG, 'products', p['id'], p['hero_shot'])).convert('RGBA')
    shot.thumbnail((720, 460), Image.LANCZOS)
    frame = Image.new('RGBA', (shot.width + 4, shot.height + 30), (40, 44, 58, 255))
    fd = ImageDraw.Draw(frame)
    for i in range(3):
        fd.ellipse((12 + i * 18, 9, 22 + i * 18, 19), fill=(90, 96, 112, 255))
    frame.alpha_composite(shot, (2, 28))
    mask = Image.new('L', frame.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, frame.width - 1, frame.height - 1), radius=14, fill=255)
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((560, 150, 560 + frame.width, 150 + frame.height), radius=16, fill=(0, 0, 0, 180))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
    im.paste(frame, (540, 130), mask)
    # left column fades over the screenshot edge
    fade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(fade)
    for x in range(0, 620):
        a = int(255 * max(0, min(1, (620 - x) / 140)))
        fdraw.line((x, 0, x, H), fill=(*BG, a))
    im.alpha_composite(fade)
    d = ImageDraw.Draw(im)
    ic = Image.open(os.path.join(IMG, 'icons', f'{p["id"]}.png')).convert('RGBA').resize((120, 120), Image.LANCZOS)
    im.alpha_composite(ic, (70, 80))
    d.text((72, 232), p['kicker'].upper(), font=font(24), fill=col)
    size = 70 if len(p['name']) < 14 else 58
    d.text((70, 268), p['name'], font=font(size), fill='white')
    words, lines, cur = p['tagline'].split(), [], ''
    f = font(26, False)
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) > 470:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    for i, ln in enumerate(lines[:4]):
        d.text((72, 370 + i * 36), ln, font=f, fill=(185, 192, 208))
    d.text((72, 560), 'papaiart.com', font=font(24), fill=(120, 128, 146))
    im.convert('RGB').save(os.path.join(IMG, 'og', f'{p["id"]}.png'), optimize=True)


if __name__ == '__main__':
    favicon()
    og_home()
    for p in PRODUCTS:
        og_product(p)
    print('favicon + og images written')
