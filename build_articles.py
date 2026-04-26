import os
import re

def build_articles():
    # Read learn.html for template
    with open('learn.html', 'r', encoding='utf-8') as f:
        learn_html = f.read()
    
    # Extract header (up to end of nav)
    header_match = re.search(r'(<!DOCTYPE html>.*?</nav>)', learn_html, re.DOTALL)
    if not header_match:
        print("Could not find header in learn.html")
        return
    header = header_match.group(1)
    
    # Extract footer (from footer to end of file, EXCLUDING the modal)
    # The footer ends at </footer>. We don't want the modal script.
    footer_match = re.search(r'(<footer class="site-footer">.*?</footer>)', learn_html, re.DOTALL)
    if not footer_match:
        print("Could not find footer in learn.html")
        return
    footer = footer_match.group(1)
    footer += "\n</body>\n</html>"
    
    # Extract article cover images
    image_mapping = {}
    cards = re.findall(r'<a class="article-card" href="cikkek/([^"]+)">.*?<img src="([^"]+)"', learn_html, re.DOTALL)
    for filename, img_src in cards:
        image_mapping[filename] = img_src

    # Function to fix relative paths for files in cikkek/ (one level deep)
    def fix_paths(text):
        # Fix assets
        text = re.sub(r'href="assets/', r'href="../assets/', text)
        text = re.sub(r'src="assets/', r'src="../assets/', text)
        # Fix html links
        text = re.sub(r'href="([^"]+\.html)(#[^"]*)?"', r'href="../\1\2"', text)
        return text

    header = fix_paths(header)
    footer = fix_paths(footer)

    cikkek_dir = 'cikkek'
    for filename in os.listdir(cikkek_dir):
        if not filename.endswith('.html'):
            continue
        filepath = os.path.join(cikkek_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract the core article content
        # We look for the first <article> tag and the last </article> tag
        body_match = re.search(r'(<article.*?>.*?</article>)', content, re.DOTALL)
        if body_match:
            inner_content = body_match.group(1)
            # Ensure it has the correct class for styling if it's the main wrapper
            if 'class="article-formatted"' not in inner_content and '<article class=' not in inner_content:
                inner_content = inner_content.replace('<article>', '<article class="article-formatted">')
        else:
            # If no article tag, try to find the content between the first <h1> and the footer
            h1_match = re.search(r'(<h1.*?>.*?)<footer', content, re.DOTALL)
            if h1_match:
                inner_content = f'<article class="article-formatted">{h1_match.group(1)}</article>'
            else:
                inner_content = content # Last resort
            
        # Add banner if image found
        banner_html = ""
        if filename in image_mapping:
            img_src = image_mapping[filename]
            # Make sure img_src is pointing properly when we are in cikkek folder
            if not img_src.startswith('../'):
                img_src = '../' + img_src
                
            banner_html = f"""
        <div style="width: 100%; height: 240px; overflow: hidden; margin-bottom: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <img src="{img_src}" alt="" style="width: 100%; height: 100%; object-fit: cover; object-position: center 30%;">
        </div>
"""

        # Assemble new page
        new_page = f"""{header}

<section class="section" style="padding-top: 120px;">
    <div class="container">
        <a href="../learn.html" class="btn" style="margin-bottom: 24px; display: inline-block;">&larr; <span data-i18n="article.back">Back to Learn</span></a>
        {banner_html}
        {inner_content}
    </div>
</section>

{footer}"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_page)
        print(f"Processed {filename} with banner: {'Yes' if banner_html else 'No'}")

if __name__ == '__main__':
    build_articles()
