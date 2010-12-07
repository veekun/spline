"""Handles Markdown translation."""
from __future__ import absolute_import

import lxml.html
import lxml.html.clean
import markdown

markdown_extensions = []

def register_extension(extension):
    """Registers the given markdown extension.

    This is global and permanent; use with care!
    """
    if not extension in markdown_extensions:
        markdown_extensions.append(extension)

def translate(raw_text, chrome=False):
    """Takes a unicode string of Markdown source.  Returns HTML."""

    # First translate the markdown
    md = markdown.Markdown(
        extensions=markdown_extensions,
        output_format='xhtml1',
    )

    html = md.convert(raw_text)

    # Then sanitize the HTML -- whitelisting only, thanks!
    # Make this as conservative as possible to start.  Might loosen it up a bit
    # later.
    fragment = lxml.html.fromstring(html)

    if chrome:
        # This is part of the site and is free to use whatever nonsense it wants
        allow_tags = None
    else:
        # This is user content; beware!!
        allow_tags = [
            # Structure
            'p', 'div', 'span', 'ul', 'ol', 'li',

            # Tables
            'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',

            # Embedding
            'a',

            # Oldschool styling
            'strong', 'b', 'em', 'i', 's', 'u',
        ]

    cleaner = lxml.html.clean.Cleaner(
        scripts = True,
        javascript = True,
        comments = True,
        style = True,
        links = True,
        meta = True,
        page_structure = True,
        #processing_instuctions = True,
        embedded = True,
        frames = True,
        forms = True,
        annoying_tags = True,
        safe_attrs_only = True,

        remove_unknown_tags = False,
        allow_tags = allow_tags,
    )
    cleaner(fragment)

    # Autolink URLs
    lxml.html.clean.autolink(fragment)

    # And, done.  Flatten the thing and return it
    return lxml.html.tostring(fragment)
