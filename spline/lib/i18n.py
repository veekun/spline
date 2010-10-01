# Encoding: UTF-8

import gettext
import pkg_resources
from pylons.i18n.translation import get_lang

class BaseTranslator(object):
    """Spline's translator. A callable object indended to be used as _.

    Use
    ---

    Instead of using gettext's ugettext and ungettext, this object is all
    that's needed, thanks to Python's keyword arguments:
    _('text') => "text"
    (_('%s uxie', '%s uxies', n=num) % num) => "1 uxie" or "2 uxies", etc.
    _(u'Pokémon', context='plural') => u"Pokémon", but will be translated as
        plural in languages where the distinction matters

    Instantiation
    -------------

    Since the set of translations used depends on both the language setting
    and the Spline module doing the translation, we can't very well use Pylons'
    builtin _ function directly.

    Each spline module is expected to subclass BaseTranslator and set some of
    the following class attributtes:
    - package: the package in which to look for i18n. Must be set explicitly.
    - dir: the locale directory within `package`. Defaults to "i18n".
    - domain: the gettext domain used. By default, same as the `package`

    The translator is then instantiated in requests, giving the template
    context (c). (The context is not used now, but it can be useful with
    specialized translation subclasses.)
    Additional parameters are 
    - lang: override the language (by default, current Pylons language is used).
    - translations: override the underlying gettext translations class
        entirely. Used in testing.

    Notes
    -----

    Translations with contexts are marked with '|' in translation files, for
    example _(u'Pokémon', context='plural') looks for the text "plural|Pokémon"
    in the .mo file. This is how it's done in GTK and probably other
    gettext-using projects, so there might be tools that expect it.
    The prefix is stripped if it survives the translation (that is, context was
    used and the '|' is still there after translation); care must be taken in
    the unlikely case that the translation contains '|' that should be there.

    Spline's message extractors must be used to extract messages, naturally.

    Unicode (u*gettext) is used everywhere.
    """
    dir = 'i18n'

    def __init__(self, context=None, languages=None, translations=None):
        if translations is None:
            if languages is None:
                languages = get_lang()
            if languages is None:
                self.translation = gettext.NullTranslations()
            else:
                directory = pkg_resources.resource_filename(
                        self.package,
                        self.dir
                    )
                gettext.bindtextdomain(self.package, directory)
                self.translation = gettext.translation(
                        domain=getattr(self, 'domain', self.package),
                        localedir=directory,
                        languages=languages,
                    )
        else:
            self.translation = translations

    def __call__(self, message, plural=None, n=None, context=None):
        if context:
            prefix = context + u'|'
        else:
            prefix = u''
        if n is None:
            translated = self.translation.ugettext(prefix + message)
        else:
            translated = self.translation.ungettext(
                    prefix + message,
                    prefix + plural,
                    n
                )
        if context:
            prefix, sep, translated = translated.partition('|')
            if not sep:
                translated = prefix
        return translated

class Translator(BaseTranslator):
    "Translator for Spline base templates"
    package = 'spline'
