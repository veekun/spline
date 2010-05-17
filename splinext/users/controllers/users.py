import logging
import unicodedata

from wtforms import Form, ValidationError, fields, validators, widgets

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect_to
from routes import request_config
from sqlalchemy.orm.exc import NoResultFound

from spline.model import meta
from spline.lib import helpers as h
from spline.lib.base import BaseController, render
from splinext.users import model as users_model

log = logging.getLogger(__name__)


class ProfileEditForm(Form):
    name = fields.TextField(u'Display name', [validators.Required()])

    def validate_name(form, field):
        if not 1 < len(field.data) <= 20:
            raise ValidationError("Name can't be longer than 20 characters")

        any_real_characters = False
        for char in field.data:
            cat = unicodedata.category(char)

            # Non-spacing marks and spaces don't count as letters
            if cat not in ('Mn', 'Zs'):
                any_real_characters = True

            # Disallow control characters, format characters, non-assigned,
            # private use, surrogates, spacing-combining marks (for Arabic,
            # etc), enclosing marks (millions sign), line-spacing,
            # paragraph-spacing.
            # This also, thankfully, includes the RTL characters.
            if cat in ('Cc', 'Cf', 'Cn', 'Co', 'Cs', 'Mc', 'Me', 'Zl', 'Zp'):
                raise ValidationError("Please don't play stupid Unicode tricks")

class UsersController(BaseController):

    def list(self):
        c.users = meta.Session.query(users_model.User) \
            .order_by(users_model.User.id.asc())
        return render('/users/list.mako')

    def profile(self, id, name=None):
        """Main user profile.

        URL is /users/id:name, where 'name' only exists for readability and is
        entirely optional and ignored.
        """

        c.page_user = meta.Session.query(users_model.User).get(id)
        if not c.page_user:
            abort(404)

        return render('/users/profile.mako')

    def profile_edit(self, id, name=None):
        """Main user profile editing."""
        c.page_user = meta.Session.query(users_model.User).get(id)
        if not c.page_user:
            abort(404)

        # XXX could use some real permissions
        if c.page_user != c.user:
            abort(403)

        c.form = ProfileEditForm(request.params,
            name=c.page_user.name,
        )

        if request.method != 'POST' or not c.form.validate():
            return render('/users/profile_edit.mako')


        c.page_user.name = c.form.name.data

        meta.Session.add(c.page_user)
        meta.Session.commit()

        h.flash('Saved your profile.', icon='tick')

        redirect_to(controller='users', action='profile',
                    id=c.page_user.id, name=c.page_user.name,
                    _code=303)
