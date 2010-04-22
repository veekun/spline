from sqlalchemy import *
from migrate import *

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base(bind=migrate_engine)


class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=20), nullable=False)

class OpenID(TableBase):
    __tablename__ = 'openid'
    openid = Column(Unicode(length=255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))


def upgrade():
    User.__table__.create()
    OpenID.__table__.create()

def downgrade():
    OpenID.__table__.drop()
    User.__table__.drop()
