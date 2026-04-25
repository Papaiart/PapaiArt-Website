import re

filepath = 'cikkek/capabilities.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<!-- ENGLISH TABLE -->(.*?)$', content, re.DOTALL | re.IGNORECASE)
if match:
    eng_article = match.group(1).strip()
    
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
    print(f'Processed capabilities.html')
else:
    print(f'English article not found in capabilities.html')
