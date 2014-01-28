# -*- coding: utf-8 -*-

import sqlalchemy
from zope.interface import implements, Interface, Attribute


class IEngineServer(Interface):
    """An engine server just serve a configured sqlAlchemy engine
    """
    name = Attribute("The associated engine")
    engine = Attribute("The SQLAlchemy engine")


class EngineServer(object):
    """Serves a SQLAlchemy engine.
    """
    implements(IEngineServer)

    def __init__(self, engine, name=''):
        self.name = name
        self.engine = engine

    def bind(self, base):
        base.metadata.bind = self.engine


def create_engine(url, name):
    """Creates an engine server and binds all known metadatas to it.
    The created engine is then returned, for convenience use.
    """
    engine = EngineServer(
        sqlalchemy.create_engine(url, convert_unicode=True), name=name)
    return engine
