import zope.interface
from zope.comonent import getGlobalSiteManager, queryUtility
from sqlalchemy import create_engine

class IEngineServer(zope.interface.Interface):
    """An engine server just serve a configured sqlAlchemy engine
    """
    engine = zope.interface.Attribute("The SQLAlchemy engine")


class EngineServer(object)
    """Serve a SQLAlchemy engine
    """
    grok.implements(IEngineServer)

    def __init__(self, engine):
        self.engine = engine


def create_engine(url, bases):
    """create an engine server and register it under a name
    corresponding to connexion url

    return the created engine for convenience use.

    bases are all the associated declarative bases that will be initialized.
    """
    engine = create_engine(url, convert_unicode=True)
    if not hasattr(bases, '__iter__'):
        bases = [bases,]
    for base in bases:
        base.create_all(engine)
    gsm = getGlobalSiteManager()
    gsm.registerUtility(EngineServer(engine), IEngineServer, name=url)
    return engine


def get_engine(url, bases):
    """get engine at the cost, if needed, of creating it"""
    if not isinstance(url, unicode):
        url = unicode(url, 'utf-8')
    engine = queryUtility(IEngineServer, name=url)
    if engine is None:
        engine = create_engine(url, bases)
    return engine
