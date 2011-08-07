# Encoding: UTF-8

import os
import gettext
import pkg_resources
from pylons.i18n.translation import get_lang
import spline.i18n.en

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

    @classmethod
    def available_languages(cls):
        """Return the available languages (not including the default)
        """
        available_languages = []
        for root, dirs, files in os.walk(pkg_resources.resource_filename(
                        cls.package,
                        cls.dir
                    )):
            components = root.split(os.sep)
            if components[-1] == 'LC_MESSAGES':
                if cls.package + '.po' in files:
                    available_languages.append(components[-2])
        return available_languages

    def __init__(self, context=None, languages=None, translations=None):
        self.context = context
        if translations is None:
            if languages is None:
                languages = get_lang()
            if languages is None:
                self.translation = gettext.NullTranslations()
                self.language = None
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
                self.language = languages[0]
        else:
            self.translation = translations
            self.language = None

    def __call__(self, message, plural=None, n=None, context=None, comment=None):
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
        return handle_template(translated, self.language)

def handle_template(message, language='en'):
    if message and message[0] == '@':
        if language:
            try:
                mod = __import__('spline.i18n.' + language, fromlist='Template')
                Template = mod.Template
            except (ImportError, AttributeError), e:
                Template = spline.i18n.en.Template
        else:
            Template = spline.i18n.en.Template
        return Template(message[1:])
    return message

class NullTranslator(object):
    """Looks like a Translator, quacks like a Translator, but doesn't actually
    translate
    """
    def __init__(*stuff, **more_stuff):
        pass

    def __call__(self, message, *stuff, **more_stuff):
        return handle_template(message)

class Translator(BaseTranslator):
    "Translator for Spline base templates"
    package = 'spline'
