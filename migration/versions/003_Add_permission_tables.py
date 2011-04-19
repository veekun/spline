from sqlalchemy import *
from migrate import *
import migrate.changeset  # monkeypatches Column

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
TableBase = declarative_base()


class User(TableBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)


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


def upgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine
    Role.__table__.create()
    UserRole.__table__.create()
    RolePermission.__table__.create()

def downgrade(migrate_engine):
    TableBase.metadata.bind = migrate_engine
    RolePermission.__table__.drop()
    UserRole.__table__.drop()
    Role.__table__.drop()
