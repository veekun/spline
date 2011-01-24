from spline.i18n.formatter import Formatter, BaseWord

class Word(BaseWord):
    @property
    def begins_with_vowel(self):
        return self and self[0].lower() in 'aeiou'

@Word.add_to_dictionary('a')
@Word.add_to_dictionary('an')
class IndefiniteArticle(Word):
    interesting_categories = ['begins_with_vowel']

    def inflect(self, begins_with_vowel=None, **kwargs):
        if begins_with_vowel is None:
            return self
        elif begins_with_vowel:
            return IndefiniteArticle(self[0] + 'n')
        else:
            return IndefiniteArticle(self[0])

formatter = Formatter('en', Word)

class Template(unicode):
    def format(self, *args, **kwargs):
        return formatter.format(self, *args, **kwargs)
