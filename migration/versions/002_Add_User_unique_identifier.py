import random

from sqlalchemy import *
from migrate import *
import migrate.changeset  # monkeypatches Column

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base(bind=migrate_engine)


class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(length=20), nullable=False)
    unique_identifier = Column(Unicode(length=32), nullable=False)


session = orm.scoped_session(
    orm.sessionmaker(autoflush=True, autocommit=False, bind=migrate_engine))

def upgrade():
    User.__table__.c.unique_identifier.create()

    for user in session.query(User):
        ident = u''.join(random.choice(u'0123456789abcdef') for _ in range(32))
        user.unique_identifier = ident
        session.add(user)

    session.commit()

def downgrade():
    User.__table__.c.unique_identifier.drop()
