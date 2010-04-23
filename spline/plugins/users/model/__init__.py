import colorsys
import random

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode

from spline.model.meta import TableBase

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
        for i in range(4):
            h = int(colors_blob[i*6:i*6+2], 16) / 256.0
            l = int(colors_blob[i*6+2:i*6+4], 16) / 256.0
            s = int(colors_blob[i*6+4:i*6+6], 16) / 256.0

            # Cap lightness to 0.25 to 0.75, so it's not too close to white or
            # black
            l = l * 0.5 + 0.25

            # Cap saturation to 0.5 to 1.0, so the color isn't too gray
            s = s * 0.5 + 0.5

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
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relation(User, lazy=False, backref='openids')

