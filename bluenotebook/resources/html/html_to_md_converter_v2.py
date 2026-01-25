from html_to_markdown import convert
import os
from bs4 import BeautifulSoup

def convert_html_to_md(html_file, md_file):
    if not os.path.exists(html_file):
        print(f"Error: File not found at {html_file}")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main content container
    content_container = soup.find('div', class_='content-container')
    
    if content_container:
        # Convert the content of the container to markdown
        markdown_content = convert(str(content_container))
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Successfully converted {html_file} to {md_file}")
    else:
        print(f"Error: Could not find content-container in {html_file}")


# Convert French version
convert_html_to_md('aide_en_ligne.html', 'aide_en_ligne.md')

# Convert English version
convert_html_to_md('online_help.html', 'online_help.md')
