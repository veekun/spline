import re
import logging

start_and_def = re.compile(r'(^|<%def [^>]*>)')

def i18n_preprocessor(text):
    """Append code to set _ to each <%def>, and to the start of file.
    """
    # The added code should basically do this:
    #     try:
    #         _ = i18n.Translator(c)
    #     except (NameError, AttributeError):
    #         pass
    #
    # However, adding multiple lines to the template will mess up line numbers,
    # making template debugging a nightmare. So we delegate to a function in h.
    if text.startswith(('%', '##')):
        # Unfortunately, if the template begins with e.g. "% if", or a comment,
        # there's no choice but to add the code on a new line
        # (Generally these are very simple templates that don't import anything)
        # And after a <%def> we're always safe.
        text = '\n' + text
    text = start_and_def.sub(r'\1<% _ = h.get_translator(lambda: i18n, c) %>', text)
    return text
