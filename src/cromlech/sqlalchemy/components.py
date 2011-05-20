import zope.interface
from zope.component import getGlobalSiteManager, queryUtility
import sqlalchemy


class IEngineServer(zope.interface.Interface):
    """An engine server just serve a configured sqlAlchemy engine
    """
    engine = zope.interface.Attribute("The SQLAlchemy engine")


class EngineServer(object):
    """Serve a SQLAlchemy engine
    """
    zope.interface.implements(IEngineServer)

    def __init__(self, engine):
        self.engine = engine


def create_engine(name, url):
    """create an engine server and register it under a name
    corresponding to connexion url. Also bind all known metadata to it.

    return the created engine for convenience use.

    bases are all the associated declarative bases that will be initialized.
    """
    engine = sqlalchemy.create_engine(url, convert_unicode=True)
    gsm = getGlobalSiteManager()
    gsm.registerUtility(EngineServer(engine), IEngineServer, name=url)
    # bind metadata to this engine
    for m in metadata_base_registry.get(name, []):
        m.bind = engine
    return engine


def get_engine(name, environ=None, default_url=None):
    """get engine corresponding to name

    If needed and if environ as a name key it is created, else a KeyError
    is raised"""
    engine = queryUtility(IEngineServer, name=name)
    if engine is None:
        if environ is not None and name in environ:
            url = environ[name]
        elif default_url is not None:
            url = default_url
        else:
            url = None
        if url is not None:
            if not isinstance(url, unicode):
                url = unicode(url, 'utf-8')
            engine = create_engine(name, url)
        else:
            raise KeyError('No dbengine named %s and no config given' % name)
    else:
        engine = engine.engine
    return engine

# registration of metadata with engines
metadata_base_registry = dict()
