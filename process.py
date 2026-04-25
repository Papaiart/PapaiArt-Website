import os
import re

cikkek_dir = 'cikkek'

for filename in os.listdir(cikkek_dir):
    if not filename.endswith('.html'):
        continue
    filepath = os.path.join(cikkek_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'<!-- ENGLISH ARTICLE -->(.*?)</article>', content, re.DOTALL | re.IGNORECASE)
    if match:
        eng_article = match.group(1).strip()
        
        # Replace inline styles or spans if necessary, but keep it mostly clean.
        
        new_html = f'''<!DOCTYPE html>
<html lang="en">
<body>
    <div class="container">
        <article class="article-formatted">
            {eng_article}
        </article>
    </div>
</body>
</html>'''
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f'Processed {filename}')
    else:
        print(f'English article not found in {filename}')
