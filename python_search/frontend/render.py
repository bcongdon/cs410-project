from markdown import Markdown

renderer = Markdown(extensions=['urlize', 'markdown.extensions.nl2br'])


def render_as_html(message_text):
    rendered = renderer.convert(message_text)

    for replacement_tag in ('<h1>', '<h2>', '<h3>', '<h4>', '<strong>', '<i>'):
        rendered = rendered.replace(replacement_tag, '<p>')

    for replacement_tag in ('</h1>', '</h2>', '</h3>', '</h4>', '</strong>', '</i>'):
        rendered = rendered.replace(replacement_tag, '</p>')

    return rendered
