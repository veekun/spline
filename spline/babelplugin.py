import ast
import itertools
from StringIO import StringIO
from mako.template import Template
import mako.ext.babelplugin

_args = "message plural n context".split()

def extract_python(fileobj, keywords, comment_tags, options):
    return extract_from_string(fileobj.read(), keywords, comment_tags, options)

def extract_mako(fileobj, keywords, comment_tags, options):
    # XXX: Hack! When/if bug #136 in Mako is resolved this won't be necessary
    mako.ext.babelplugin.extract_python = extract_python_strip
    return mako.ext.babelplugin.extract(fileobj, keywords, comment_tags, options)

def extract_python_strip(fileobj, keywords, comment_tags, options):
    return extract_from_string(fileobj.read().strip(), keywords, comment_tags, options)

def extract_from_string(string, keywords, comment_tags, options):
    try:
        tree = compile(
                string,
                filename="<input>",
                mode='exec',
                flags=ast.PyCF_ONLY_AST,
                dont_inherit=True
            )
    except SyntaxError:
        if not options.get('block_fragment_hack'):
            # With Mako directives like "% for x in y:", it is possible
            # that we get the "for x in y:" to extract from.
            # Handle this case in a very unclean way for now.
            if string.startswith('else') or string.startswith('elif'):
                string = 'if True: pass\n' + string
            elif string.startswith('except') or string.startswith('finally'):
                string = 'try: pass\n' + string
            string += '\n' + ' ' * 100 + 'pass'
            options = dict(options)
            options['block_fragment_hack'] = True
            return extract_from_string(string, keywords, comment_tags, options)
        else:
            # It seems to be a legitimate syntax error after all
            print string
            raise
    else:
        return from_ast(tree, keywords, options, [])

def from_ast(node, keywords, options, comments):
    if isinstance(node, ast.Call):
        funcname = get_funcname(node.func)
        if funcname in keywords:
            params = {}
            for name, param in itertools.chain(
                    zip(_args, node.args),
                    ((k.arg, k.value) for k in node.keywords),
                ):
                if isinstance(param, ast.Str):
                    params[name] = param
                else:
                    # not a literal string: we don't care about it,
                    # but still want to know if it's there
                    params[name] = None
            message = getstring(params.get('message'))
            context = getstring(params.get('context'))
            if message:
                if context:
                    message = context + '|' + message
                if 'plural' in params:
                    message = (message, getstring(params.get('plural')))
                    # Cheat the function name; the extractor uses it to
                    # distinguish between singular/plutal messages
                    function = 'ungettext'
                else:
                    function = 'ugettext'
                yield node.lineno, function, message, comments
    child_comments = []
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        child_comments.append('Py2Format')
    if isinstance(node, ast.Attribute) and node.attr == 'format':
        child_comments.append('Py3Format')
    for child in ast.iter_child_nodes(node):
        for result in from_ast(child, keywords, options, child_comments):
            yield result

def get_funcname(node):
    if isinstance(node, ast.Name):
        # gettext(...)
        return node.id
    elif isinstance(node, ast.Attribute):
        # someobject.gettext(...)
        # We only care about the attribute name
        return node.attr
    else:
        # something like (lst[0])(...)
        return None

def getstring(maybenode):
    if maybenode is None:
        return None
    else:
        return maybenode.s
