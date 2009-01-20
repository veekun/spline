from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, Unicode

from spline.model.meta import TableBase

class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=20), nullable=False)

class OpenID(TableBase):
    __tablename__ = 'openid'
    openid = Column(Unicode(length=255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relation(User, lazy=False, backref='openids')

