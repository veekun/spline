from nose.tools import assert_equal
import gettext
from babel.messages.extract import extract_python
from StringIO import StringIO
from spline import babelplugin
from spline.lib import i18n

class TestTranslations(object):
    """gettext-like Translations class. Reports what gets called instead of
    actually translating"""
    def ugettext(self, message):
        return '|ugettext(%s)' % message

    def ungettext(self, message, plural, n):
        return '|ungettext(%s, %s, %s)' % (message, plural, n)

class ConstTranslations(object):
    """gettext-like Translations class. Always returns the same string"""
    def __init__(self, string):
        self._string = string

    def ugettext(self, message):
        return self._string

    def ungettext(self, message, plural, n):
        return self._string

translation_inputs = [
        (('text',), dict()),
        (('one', 'two'), dict(n=1)),
        (('one', 'two'), dict(n=3)),
        (('a|b|c',), dict()),
        (('a|b|c', 'd|e|f'), dict(n=1)),
        (('a|b|c', 'd|e|f'), dict(n=3)),
        (('text',), dict(context='ctx')),
        (('one', 'two'), dict(n=1, context='ctx')),
        (('one', 'two'), dict(n=3, context='ctx')),
        (('a|b|c',), dict(context='ctx')),
        (('a|b|c', 'd|e|f'), dict(n=1, context='ctx')),
        (('a|b|c', 'd|e|f'), dict(n=3, context='ctx')),
    ]

def test_translation_calls():
    _ = i18n.BaseTranslator(translations=TestTranslations())
    outputs = [
            '|ugettext(text)',
            '|ungettext(one, two, 1)',
            '|ungettext(one, two, 3)',
            '|ugettext(a|b|c)',
            '|ungettext(a|b|c, d|e|f, 1)',
            '|ungettext(a|b|c, d|e|f, 3)',
            'ugettext(ctx|text)',
            'ungettext(ctx|one, ctx|two, 1)',
            'ungettext(ctx|one, ctx|two, 3)',
            'ugettext(ctx|a|b|c)',
            'ungettext(ctx|a|b|c, ctx|d|e|f, 1)',
            'ungettext(ctx|a|b|c, ctx|d|e|f, 3)',
        ]
    for (args, kwargs), out in zip(translation_inputs, outputs):
        print args, kwargs, out
        assert_equal(_(*args, **kwargs), out)

def test_null_translation():
    _ = i18n.BaseTranslator(translations=gettext.NullTranslations())
    outputs = [
            'text',
            'one',
            'two',
            'a|b|c',
            'a|b|c',
            'd|e|f',
            'text',
            'one',
            'two',
            'a|b|c',
            'a|b|c',
            'd|e|f',
        ]
    for (args, kwargs), out in zip(translation_inputs, outputs):
        print args, kwargs, out
        assert_equal(_(*args, **kwargs), out)

def test_const_translation():
    _ = i18n.BaseTranslator(translations=ConstTranslations('pre|in|post'))
    outputs = [
            'pre|in|post',
            'pre|in|post',
            'pre|in|post',
            'pre|in|post',
            'pre|in|post',
            'pre|in|post',
            'in|post',
            'in|post',
            'in|post',
            'in|post',
            'in|post',
            'in|post',
        ]
    for (args, kwargs), out in zip(translation_inputs, outputs):
        print args, kwargs, out
        assert_equal(_(*args, **kwargs), out)


# Extraction tests #

def check_generator(function, args, output):
    actual_output = function(*args)
    actual_output = list(actual_output)
    output = list(output)
    print 'Output is:', actual_output
    print 'Should be:', output
    assert_equal(len(output), len(actual_output))
    for a, b in zip(output, actual_output):
        assert_equal(a, b)

def test_extraction_python():
    func = babelplugin.extract_python
    input = """if True:
        print _('d')
        print _(u'd', n=6, plural='f')
        print _(u'd', context='some_ctx')
        print _('d', n=6, plural='f', context='some_ctx')

        print _('%s') % f
        print _('{s}').format(s=1)
    """.strip()
    output = [
            (2, 'ugettext', 'd', []),
            (3, 'ungettext', (u'd', 'f'), []),
            (4, 'ugettext', u'some_ctx|d', []),
            (5, 'ungettext', ('some_ctx|d', 'f'), []),
            (7, 'ugettext', '%s', ['Py2Format']),
            (8, 'ugettext', '{s}', ['Py3Format']),
        ]
    args = (StringIO(input), ['_'], [], {})
    check_generator(func, args, output)

def test_extraction_mako():
    func = babelplugin.extract_mako
    input = """<html>
        _('d') <!-- not caught -->
        ${_(u'text', context='abc')}
        % for char in _('horse', 'horses', n=1):
            <b>${char}</b>
        % endfor
        </html>
    """
    print input
    output = [
            (3, 'ugettext', 'abc|text', []),
            (4, 'ungettext', ('horse', 'horses'), []),
        ]
    args = (StringIO(input), ['_'], [], {})
    check_generator(func, args, output)
