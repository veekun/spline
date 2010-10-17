"""Flash message implementation.

Based on webhelpers.pylonslib.flash from WebHelpers 1.2, except that they
needlessly restricted the metadata for a single flash message, and working
around it was horrifically ugly.
"""

from webhelpers.html import escape

__all__ = ["Flash", "Message"]

class Message(object):
    """A message returned by ``Flash.pop_messages()``.

    Converting the message to a string returns the message text. Instances
    also have the following attributes:

    * ``message``: the message text.
    * ``category``: the category specified when the message was created.
    * ``icon``: the icon to show along with the message.
    """

    def __init__(self, category, message, icon):
        self.category = category
        self.message = message
        self.icon = icon

    def __str__(self):
        return self.message

    __unicode__ = __str__

    def __html__(self):
        return escape(self.message)


class Flash(object):
    """Accumulate a list of messages to show at the next page request.
    """

    # List of allowed categories.  If None, allow any category.
    categories = ["warning", "notice", "error", "success"]

    # Default category if none is specified.
    default_category = "notice"

    # Mapping of categories to icons.
    default_icons = dict(
        warning='exclamation-frame',
        notice='balloon-white',
        error='cross-circle',
        success='tick',
    )

    def __init__(self, session_key="flash", categories=None, default_category=None):
        """Instantiate a ``Flash`` object.

        ``session_key`` is the key to save the messages under in the user's
        session.

        ``categories`` is an optional list which overrides the default list
        of categories.

        ``default_category`` overrides the default category used for messages
        when none is specified.
        """
        self.session_key = session_key
        if categories is not None:
            self.categories = categories
        if default_category is not None:
            self.default_category = default_category
        if self.categories and self.default_category not in self.categories:
            raise ValueError("unrecognized default category %r" % (self.default_category,))

    def __call__(self, message, category=None, icon=None, ignore_duplicate=False):
        """Add a message to the session.

        ``message`` is the message text.

        ``category`` is the message's category. If not specified, the default
        category will be used.  Raise ``ValueError`` if the category is not
        in the list of allowed categories.

        ``icon`` is the icon -- a filename from the Fugue icon set, without the
        file extension.

        If ``ignore_duplicate`` is true, don't add the message if another
        message with identical text has already been added. If the new
        message has a different category than the original message, change the
        original message to the new category.
        """

        if not category:
            category = self.default_category
        elif self.categories and category not in self.categories:
            raise ValueError("unrecognized category %r" % (category,))

        if not icon:
            icon = self.default_icons[category]

        # Don't store Message objects in the session, to avoid unpickling
        # errors in edge cases.
        new_message_dict = dict(message=message, category=category, icon=icon)
        from pylons import session
        messages = session.setdefault(self.session_key, [])
        # ``messages`` is a mutable list, so changes to the local variable are
        # reflected in the session.
        if ignore_duplicate:
            for i, m in enumerate(messages):
                if m['message'] == message:
                    if m['category'] != category or m['icon'] != icon:
                        messages[i] = new_message_dict
                        session.save()
                    return    # Original message found, so exit early.

        messages.append(new_message_dict)
        session.save()

    def pop_messages(self):
        """Return all accumulated messages and delete them from the session.

        The return value is a list of ``Message`` objects.
        """
        from pylons import session
        messages = session.pop(self.session_key, [])
        session.save()
        return [Message(**m) for m in messages]
