## Rational

A python copy of RedNotebook supporting Markdown as internal format.
ISO fonctionnality with RedNotebook (- Latex)



## Rednotebook

It lets you format, tag and search your entries. You can also add pictures, links and customizable templates, spell check your notes, and export to plain text, HTML or LaTeX. RedNotebook is Free Software under the GPL.

- Insert #hashtags
- Format text bold, italic or underlined
- Insert images, files and links
- Spell check
- Search-as-you-type
- Automatic saving
- Backup to zip archive
- Word clouds with most common words and tags
- Templates
- Export to plain text, HTML or Latex
- Future-proof: data is stored in plain text files
- Private: you own your data
- Translated into more than 30 languages
- Calendar
- 2 columns design

## New fonctionnalities

- side-by-side edition (marldown/preview)
- AI powered (feeds, etc)
- Format as a pdf dairy book


## Existing Code


### markdown-editor
Standalone editor for your local markdown files


https://pypi.org/project/Markdown-Editor/
https://github.com/ncornette/Python-Markdown-Editor

 ```
 pip install markdown-editor
 ```
Extensible
You can import this script as a module to write your own applications based on the markdown editor.

example :

```python
from markdown_editor import web_edit
from markdown_editor.editor import MarkdownDocument

# ...

MY_HTML_HEAD = 'Editor title'

def action_send(document):

    send_markdown_text(document.text)
    # or
    send_raw_html_code(document.getHtml())
    # or
    send_html_with_styles(document.getHtmlPage())

    return html_to_display_as_result, keep_running_local_server

if __name__ == '__main__':
    doc = MarkdownDocument()
    web_edit.start(doc,
        custom_actions=[
                ('Send', action_send),
        ],
        title=MY_HTML_HEAD)
```

### notolog-editor

https://github.com/notolog/notolog-editor

