"""
Pull devlog posts and their images from itch.io into the site.

    python tools/sync_itch.py            # fetch new posts only
    python tools/sync_itch.py --refresh  # re-download every post

Writes data/devlogs.json and assets/images/devlog/*.webp.
Run build_site.py afterwards to regenerate the HTML pages.
Requires: Pillow (pip install pillow). Uses curl for downloads.
"""
import html
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from html.parser import HTMLParser

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'devlogs.json')
IMG_DIR = os.path.join(ROOT, 'assets', 'images', 'devlog')

# itch.io page slug -> site product id (must match PRODUCTS in build_site.py)
ITCH_SLUGS = {
    'papaiart-animation-studio-open-beta': 'animation-studio',
    'papaiart-tools-fps-lab': 'fps-lab',
    'papaiart-tools-level-editor': 'level-editor',
    'papaiart-tools-level-modeller': 'level-modeller',
    'papaiart-tools-terrain-generator': 'terrain-generator',
    'papaiart-pixelpaint-98-pro': 'pixelpaint-98-pro',
}

MAX_IMAGES = 6


def fetch(url):
    r = subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0 (PapaiArt site sync)', url], capture_output=True)
    return r.stdout


class Sanitizer(HTMLParser):
    """Keeps a small whitelist of formatting tags from an itch.io post body."""
    ALLOWED = {'p', 'br', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'code', 'pre', 'blockquote', 'hr', 'a'}
    HEADINGS = {'h1': 'h2', 'h2': 'h2', 'h3': 'h3', 'h4': 'h3', 'h5': 'h3', 'h6': 'h3'}
    DROP = {'script', 'style', 'iframe', 'object', 'embed', 'img', 'figure', 'video'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.DROP:
            if tag not in ('img', 'br', 'hr'):
                self.skip += 1
            return
        if self.skip:
            return
        if tag in self.HEADINGS:
            self.out.append(f'<{self.HEADINGS[tag]}>')
        elif tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith(('http://', 'https://')):
                self.out.append(f'<a href="{html.escape(href)}" target="_blank" rel="noopener">')
            else:
                self.out.append('<a>')
        elif tag in self.ALLOWED:
            self.out.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag in self.DROP:
            if tag not in ('img', 'br', 'hr'):
                self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in self.HEADINGS:
            self.out.append(f'</{self.HEADINGS[tag]}>')
        elif tag in self.ALLOWED and tag not in ('br', 'hr'):
            self.out.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))

    def result(self):
        s = ''.join(self.out)
        s = re.sub(r'<(p|li|h2|h3)>\s*</\1>', '', s)
        s = re.sub(r'(<br>\s*){3,}', '<br><br>', s)
        return s.strip()


def plain(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def save_image(url, dest, maxw=1400):
    if os.path.exists(dest):
        return Image.open(dest).size
    im = Image.open(io.BytesIO(fetch(url)))
    im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(dest, 'WEBP', quality=82, method=6)
    return im.size


def parse_post(page, url, product):
    hdr = re.search(r'<section class="post_header">(.*?)</section>', page, re.S)
    title = plain(re.search(r'<h1[^>]*>(.*?)</h1>', hdr.group(1), re.S).group(1)) if hdr else ''
    date_raw = (re.findall(r'<abbr title="([^"]+)"', page) or [''])[0]
    try:
        date = datetime.strptime(date_raw.split(' @')[0], '%d %B %Y').strftime('%Y-%m-%d')
    except ValueError:
        date = ''
    m = re.search(r'<section class="object_text_widget_widget base_widget user_formatted post_body"[^>]*>(.*?)</section>', page, re.S)
    body_raw = m.group(1) if m else ''
    san = Sanitizer()
    san.feed(body_raw)
    body = san.result()
    s = page.find('<section class="post_images"')
    gallery = re.findall(r'href="(https://img\.itch\.zone/[^"]+/original/[^"]+)"', page[s:page.find('</section>', s)]) if s > 0 else []
    inline = [u for u in re.findall(r'<img[^>]+src="([^"]+)"', body_raw) if 'img.itch.zone' in u]
    videos = list(dict.fromkeys(re.findall(r'youtube(?:-nocookie)?\.com/embed/([\w-]+)', body_raw)))
    pid = re.search(r'/devlog/(\d+)/', url).group(1)
    text = plain(body)
    ver = re.search(r'(\d+\.\d+(?:\.\d+)?)', title)
    return {
        'id': pid,
        'product': product,
        'title': title,
        'date': date,
        'url': url,
        'version': ver.group(1) if ver else '',
        'excerpt': (text[:240].rsplit(' ', 1)[0] + '…') if len(text) > 240 else text,
        'words': len(text.split()),
        'body': body,
        'videos': videos,
        'remote_images': (gallery + inline)[:MAX_IMAGES],
    }


def main():
    refresh = '--refresh' in sys.argv
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    posts = {p['id']: p for p in json.load(open(DATA, encoding='utf-8'))} if os.path.exists(DATA) else {}

    for slug, product in ITCH_SLUGS.items():
        index = fetch(f'https://papaiart.itch.io/{slug}/devlog').decode('utf-8', 'replace')
        urls = sorted(set(re.findall(r'href="(https://papaiart\.itch\.io/' + slug + r'/devlog/\d+/[^"]+)"', index)))
        print(f'{product}: {len(urls)} posts')
        for url in urls:
            pid = re.search(r'/devlog/(\d+)/', url).group(1)
            if pid in posts and not refresh:
                continue
            post = parse_post(fetch(url).decode('utf-8', 'replace'), url, product)
            post['images'] = []
            for i, img in enumerate(post.pop('remote_images')):
                name = f'{pid}-{i + 1}.webp'
                try:
                    w, h = save_image(img, os.path.join(IMG_DIR, name))
                    post['images'].append({'src': name, 'w': w, 'h': h})
                except Exception as e:  # noqa: BLE001 - one broken image should not stop the sync
                    print('  image failed:', img, e)
            posts[pid] = post
            print(f'  + {post["date"]}  {post["title"]}')

    out = sorted(posts.values(), key=lambda p: (p['date'], p['id']), reverse=True)
    json.dump(out, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(out)} posts -> {os.path.relpath(DATA, ROOT)}')


if __name__ == '__main__':
    main()
