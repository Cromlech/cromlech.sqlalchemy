# -*- coding: utf-8 -*-

import sqlalchemy
from zope.interface import implements, Interface, Attribute
from zope.component import getGlobalSiteManager, queryUtility


class IEngineServer(Interface):
    """An engine server just serve a configured sqlAlchemy engine
    """
    engine = Attribute("The SQLAlchemy engine")


class EngineServer(object):
    """Serves a SQLAlchemy engine.
    """
    implements(IEngineServer)

    def __init__(self, engine):
        self.engine = engine


def create_engine(url, name):
    """Creates an engine server and binds all known metadatas to it.
    The created engine is then returned, for convenience use.
    """
    engine = sqlalchemy.create_engine(url, convert_unicode=True)
    # bind metadata to this engine
    for m in metadata_base_registry.get(name, []):
        m.bind = engine
    return engine


def register_engine(engine, name):
    gsm = getGlobalSiteManager()
    gsm.registerUtility(EngineServer(engine), IEngineServer, name=name)


def create_and_register_engine(url, name):
    engine = create_engine(url, name)
    register_engine(engine, name)
    return engine


def query_engine(name):
    # A ComponentLookupError is raise in case of problem.
    return queryUtility(IEngineServer, name=name)


# registration of metadata with engines
metadata_base_registry = dict()
