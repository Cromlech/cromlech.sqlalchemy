# -*- coding: utf-8 -*-

import sqlalchemy
from zope.interface import implements, Interface, Attribute
from zope.component import getSiteManager, queryUtility


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
        sqlalchemy.create_engine(url, convert_unicode=True, query_cache_size=1200, echo=False), name=name)
    return engine


def register_engine(engine):
    assert IEngineServer.providedBy(engine)
    gsm = getSiteManager()
    name = engine.name  # we use the explicitly set name or ''
    gsm.registerUtility(engine, IEngineServer, name=name)


def create_and_register_engine(url, name):
    engine = create_engine(url, name)
    register_engine(engine)
    return engine


def query_engine(name):
    # A ComponentLookupError is raise in case of problem.
    return queryUtility(IEngineServer, name=name)
