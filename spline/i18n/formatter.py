"""
From http://docs.python.org/library/string.html#formatstrings:

    "Format specifications" are used within replacement fields contained within
    a format string to define how individual values are presented (see Format
    String Syntax). They can also be passed directly to the built-in format()
    function. Each formattable type may define how the format specification is
    to be interpreted.
    [...]

    A general convention is that an empty format string ("") produces the same
    result as if you had called str() on the value. A non-empty format string
    typically modifies the result.

The language formatter introduces a Word type that with a special format syntax,
and a Template type that overrides .format() to enable formatting even simple
(Unicode) strings and allow some more magic.

There are two things to do in formatting:
1) Guessing the relevant grammatical categories of a given word, and
2) Changing the word into a given form

Additionally, we migh want to create a new word (e.g. a posessive adjective),
and then conjugate that.

The conversion specification (the part after "!") specifies what the word
is, if it's given as a str/unicode. It has the same format as the format
specification, below.

The format specification (the part after the first ':' in the template) is
composed of parts separated by ':'. The source may be left out along
with the '>', Both contain a comma-separated list of either [key1=]key2=value
constructs. Bare values are shortcuts specified by the language.

The value may be in the form *ref, in which case the corresponding entry in
the arguments is taken; this only works when a Template is formatted. When
used as a bare value, all interesting categories are used.

The field name may begin with '=', in which case it is literal. For example,
in English, "{=a:*obj} {obj}" will provide a word with its indefinite article.

"""

import string

class Formatter(string.Formatter):
    def __init__(self, lang, word_class, shortcuts={}):
        self.lang = lang
        self.word_class = word_class
        self.shortcuts = shortcuts

    def vformat(self, format_string, args, kwargs):
        used_args = set()
        result = self._vformat(format_string, args, kwargs, used_args, 2)
        self.check_unused_args(used_args, args, kwargs)
        return result

    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth):
        """This function does the actual work of formatting.

        Mostly reused from string.Formatter._vformat """
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting

                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion, args, kwargs)

                # expand the format spec, if needed
                format_spec = self._vformat(format_spec, args, kwargs,
                                            used_args, recursion_depth-1)

                # format the object and append to the result
                result.append(self.format_field(obj, format_spec, args, kwargs))

        return ''.join(result)

    def get_field(self, field_name, args, kwargs):
        if field_name.startswith("="):
            return field_name[1:], None
        else:
            return super(Formatter, self).get_field(field_name, args, kwargs)

    def convert_field(self, value, conversion=None, args=(), kwargs=frozenset()):
        # we only deal with words
        spec = self.parse_spec(None, conversion, args, kwargs)
        return self.word_class.create(value, **spec)

    def format_field(self, word, format_spec, args=(), kwargs=frozenset()):
        for spec in format_spec.split(':'):
            word = word.inflect(**self.parse_spec(word, spec, args, kwargs))
        return word

    def parse_spec(self, word, spec, args, kwargs):
        if not spec:
            return {}
        result = {}
        for item in spec.split(','):
            keys, sep, val = item.rpartition('=')
            if keys:
                keys = keys.split('=')
            else:
                keys = []
            if val.startswith('*'):
                val, a = self.get_field(val[1:], args, kwargs)
                val = self.convert_field(val)
                if not keys and word:
                    keys = word.interesting_categories
                for key in keys:
                    result[key] = getattr(val, key)
            elif keys:
                for key in keys:
                    result[key] = val
            else:
                result.update(self.shortcuts[val])
        return result

class BaseWord(unicode):
    interesting_categories = {}
    dictionary = {}

    def __init__(self, word, **props):
        for key, value in props.items():
            setattr(self, key, value)

    @classmethod
    def create(cls, word, **props):
        if isinstance(word, cls):
            return word
        elif word in cls.dictionary:
            return cls.dictionary[word]
        elif ' ' in word:
            return cls.phrase.create(cls.create(w, **props) for w in word.split(' '))
        else:
            return cls.guess_type(word, **props)(word, **props)

    @classmethod
    def guess_type(cls, word, **props):
        return cls

    def inflect(self, **kwargs):
        return self

    @classmethod
    def add_to_dictionary(cls, word):
        if 'dictionary' not in cls.__dict__:
            cls.dictionary = {}
        def decorator(word_class):
            cls.dictionary[word] = word_class(word)
            return word_class
        return decorator

class BasePhrase(BaseWord):
    @classmethod
    def create(cls, words):
        words = tuple(words)
        r = cls(' '.join(words))
        r.words = words
        return r

    def inflect(self, **kwargs):
        return ' '.join(w.inflect(**kwargs) for w in self.words)

BaseWord.phrase = BasePhrase

def parse_bool(b):
    if b and str(b) in '1 t true y yes True'.split():
        return True
    else:
        return False
