from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Gameshop(Base):
    __tablename__ = 'gameshop'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    list_item = relationship('Game', cascade='all, delete-orphan')

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name': self.name,
           'id': self.id,
       }


class Game(Base):
    __tablename__ = 'list_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(Numeric(10,2))
    genre = Column(String(250))
    gameshop_id = Column(Integer, ForeignKey('gameshop.id'))
    gameshop = relationship(Gameshop)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name': self.name,
           'description': self.description,
           'id': self.id,
           'price': self.price,
           'genre': self.genre,
       }


engine = create_engine('sqlite:///gameshopwusers.db')


Base.metadata.create_all(engine)
