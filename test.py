from importlib import reload  # noqa
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy.types as types

import logging

from hilogenerator import HiLoGenerator, RowPerTableHiLoGenerator

LOGGING_FORMAT = '%(message)s'
logging.basicConfig(format=LOGGING_FORMAT)
log = logging.getLogger(__name__)
logging.getLogger('').setLevel(logging.INFO)


engine = create_engine('postgresql://localhost', echo=True)
Base = declarative_base()


class Repr(object):
    def __repr__(self):
        return "<{}(id={}, name={})>".format(
            self.__class__.__name__,
            self.id, self.name
        )


class Entity(Repr, Base):
    __tablename__ = "entity"

    id = Column(types.Integer(), HiLoGenerator(), primary_key=True)
    name = Column(types.String())


class OtherEntity(Repr, Base):
    __tablename__ = "other_entity"

    id = Column(types.Integer(), HiLoGenerator(), primary_key=True)
    name = Column(types.String())


class AnotherEntity(Repr, Base):
    __tablename__ = "another_entity"

    id = Column(types.Integer(), RowPerTableHiLoGenerator(), primary_key=True)
    name = Column(types.String())


class SomeOtherEntity(Repr, Base):
    __tablename__ = "some_other_entity"

    id = Column(types.Integer(), RowPerTableHiLoGenerator(), primary_key=True)
    name = Column(types.String())


Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)

session = Session()

session.add_all([
    Entity(name="Test"),
    OtherEntity(name="Test"),
    AnotherEntity(name="Test"),
    SomeOtherEntity(name="Test")
])

session.commit()

for i in range(15000):
    session.add(Entity(name="Test"))
    session.add(OtherEntity(name="Test"))
    session.add(AnotherEntity(name="Test"))
    session.add(SomeOtherEntity(name="Test"))

session.commit()
