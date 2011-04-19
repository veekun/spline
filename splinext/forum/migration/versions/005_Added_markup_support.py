from sqlalchemy import *
from migrate import *
import migrate.changeset

from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()

class Post(TableBase):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    raw_content = Column(Unicode(5120), nullable=False, server_default=u'')
    content = Column(Unicode(5120), nullable=False)


def upgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine
    conn = migrate_engine.connect()

    # Create the column with an empty-string default, copy the old column's
    # contents to the new one then remove the default
    Post.__table__.c.raw_content.create(connection=conn)
    conn.execute(
        update(Post.__table__,
            values={ Post.__table__.c.raw_content: Post.__table__.c.content },
        )
    )
    Post.__table__.c.raw_content.alter(server_default=None, connection=conn)

def downgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine

    Post.__table__.c.raw_content.drop()
