# encoding: utf8
import colorsys
from math import sin, pi
import random

from sqlalchemy import Column, ForeignKey, or_
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relation
from sqlalchemy.orm.session import Session
from sqlalchemy.types import Integer, Unicode

from spline.model.meta import TableBase

class AnonymousUser(object):
    """Fake user object, for when the user isn't actually logged in.

    Tests as false and tries to respond to method calls the expected way.
    """

    def __nonzero__(self):
        return False
    def __bool__(self):
        return False

    def can(self, action):
        """Anonymous users aren't ever allowed to do anything."""
        return False


class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=20), nullable=False)
    unique_identifier = Column(Unicode(length=32), nullable=False)

    def __init__(self, *args, **kwargs):
        # Generate a unique hash if one isn't provided (which it shouldn't be)
        if 'unique_identifier' not in kwargs:
            ident = u''.join(random.choice(u'0123456789abcdef')
                             for _ in range(32))
            kwargs['unique_identifier'] = ident

        super(User, self).__init__(*args, **kwargs)

    _root_user_id = None
    _default_permissions = None
    def can(self, action):
        """Returns True iff this user has permission to do `action`.

        If `_root_user_id` is this user's id, all permissions are allowed.  The
        property is usually set by the spline-users after_setup hook.
        """

        if self.id == self._root_user_id:
            return True

        if action in self.permissions:
            return True

        # Permissions assigned to NULL apply to all roles
        if self._default_permissions is None:
            session = Session.object_session(self)
            self._default_permissions = [
                row.permission
                for row in session.query(RolePermission)
                    .filter_by(role_id=None)
            ]

        return (action in self._default_permissions)

    @property
    def unique_colors(self):
        """Returns a list of (width, '#rrggbb') tuples that semi-uniquely
        identify this user.
        """
        width_blob, colors_blob = self.unique_identifier[0:8], \
                                  self.unique_identifier[8:32]

        widths = []
        for i in range(4):
            width_hex = width_blob[i*2:i*2+2]
            widths.append(int(width_hex, 16))
        total_width = sum(widths)

        ret = []
        last_hue = None
        for i in range(4):
            raw_hue = int(colors_blob[i*6:i*6+2], 16) / 256.0
            if last_hue:
                # Make adjacent hues relatively close together, to avoid green
                # + purple sorts of clashes.
                # Minimum distance is 0.1; maximum is 0.35.  Leaves half the
                # spectrum available for any given color.
                # Change 0.0–0.1 to -0.35–-0.1, 0.1–0.35
                hue_offset = raw_hue * 0.5 - 0.25
                if raw_hue < 0:
                    raw_hue -= 0.1
                else:
                    raw_hue += 0.1

                h = last_hue + raw_hue
            else:
                h = raw_hue
            last_hue = h

            l = int(colors_blob[i*6+2:i*6+4], 16) / 256.0
            s = int(colors_blob[i*6+4:i*6+6], 16) / 256.0

            # Secondary colors are extremely biased against when picking
            # randomly from the hue spectrum.
            # To alleviate this, try to bias hue towards secondary colors.
            # This adjustment is based purely on experimentation; sin() works
            # well because hue is periodic, * 6 means each period is 1/3 the
            # hue spectrum, and the final / 24 is eyeballed
            h += sin(h * pi * 6) / 24

            # Cap lightness to 0.4 to 0.95, so it's not too close to white or
            # black
            l = l * 0.6 + 0.3

            # Cap saturation to 0.5 to 1.0, so the color isn't too gray
            s = s * 0.6 + 0.3

            r, g, b = colorsys.hls_to_rgb(h, l, s)
            color = "#{0:02x}{1:02x}{2:02x}".format(
                int(r * 256),
                int(g * 256),
                int(b * 256),
            )

            ret.append((1.0 * widths[i] / total_width, color))

        return ret

class OpenID(TableBase):
    __tablename__ = 'openid'
    openid = Column(Unicode(length=255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


# Permissions stuff
class Role(TableBase):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Unicode(64), nullable=False)
    icon = Column(Unicode(64), nullable=False)

class UserRole(TableBase):
    __tablename__ = 'user_roles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False, autoincrement=False)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True, nullable=False, autoincrement=False)

class RolePermission(TableBase):
    __tablename__ = 'role_permissions'
    id = Column(Integer, nullable=False, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    permission = Column(Unicode(64), nullable=False)


### Relations
OpenID.user = relation(User, lazy=False, backref='openids')

Role.role_permissions = relation(RolePermission, backref='role')

User.roles = relation(Role, secondary=UserRole.__table__, backref='users')
User.role_permissions = relation(RolePermission,
    primaryjoin=User.id==UserRole.user_id,
    secondary=UserRole.__table__,
    secondaryjoin=UserRole.role_id==RolePermission.role_id,
    foreign_keys=[UserRole.user_id, RolePermission.role_id],
)
User.permissions = association_proxy('role_permissions', 'permission')

UserRole.user = relation(User)
UserRole.role = relation(Role)
