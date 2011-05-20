# -*- coding: utf-8 -*-

import transaction
import threading
from components import get_engine, metadata_base_registry
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import ZopeTransactionExtension


def deferred_bind(metadata, name):
    """tells that Metadata must be bind to engine corresponding to
    database config registered under name

    If dbengine is not yet created,
    the binding will be done as soon as dbengine will be created
    """
    if name not in metadata_base_registry:
        metadata_base_registry[name] = set()
    if metadata not in metadata_base_registry:
        metadata_base_registry[name].add(metadata)
        try:
            engine = get_engine(name)
            metadata.bind(engine)
        except KeyError:
            # engine does not exist, binding will be done at creation time
            pass


class SQLAlchemySession(object):
    """Controled execution using a SQLAlchemy-controller
    connecting the thread to a SQLAlchemy session and anchoring it
    in transaction manager.

    Parameters for connection are taken from wsgi environ under name
    """

    def __init__(self, environ, name, default_url=None,
                                     transaction_manager=None, two_phase=None):
        """
        name is the name of connection parameters in wsgi environ

        default url may indicate a default_url if name is not found in environ
        (eg. a global configuration).

        metadata is a SQLAlchemy Metadata which will be associated with
        connection

        If transaction_manager is None we will ask the transaction module
        for the current one.

        If two_phase is none, it will be set to true for mysql and postgre
        false otherwhise.
        """
        self.environ = environ
        self.name = name
        self.two_phase = two_phase
        self.default_url = default_url
        if transaction_manager is None:
            transaction_manager = transaction.manager
        self.tm = transaction_manager

    def __enter__(self):
        """begin session scope"""
        # get the engine
        self.engine = get_engine(self.name, self.environ, self.default_url)
        # make a session, we make a scoped session in case we want to
        # work on same connection later
        if self.two_phase is None:
            if self.engine.dialect.name in ('postgre', 'postgresql', 'mysql'):
                self.two_phase = True
            else :
                self.two_phase = False

        self.session = scoped_session(sessionmaker(bind=self.engine,
            twophase=self.two_phase, extension=ZopeTransactionExtension()))
        # add to thread
        set_session(self.name, self.session)
        return self.session

    def __exit__(self, type, value, traceback):
        """end session scope
        """
        self.session.flush()
        set_session(self.name, None)


class SharedSQLAlchemySession(SQLAlchemySession):
    """like SQLAlchemySession but considering that in a thread
    a db_name will always be associated with same url
    so session is opened once
    """

    def __init__(self, environ, name, *args, **kwargs):
        self.session = get_session(name)
        if self.session is None:
            SQLAlchemySession.__init__(self, environ, name,
                                                    *args, **kwargs)

    def __enter__(self):
        if self.session is not None:
            return self.session
        else:
            return SQLAlchemySession.__enter__(self)

    def __exit__(self, type, value, traceback):
        self.session.flush()
        # and no session cleaning !


class SessionInfo(threading.local):
    """Serve SQLAlchemy Session by name
    """

    def __init__(self):
        self.session = dict()


sessioninfo = SessionInfo()


def set_session(name, session=None):
    """set the session in thread"""
    if session is not None:
        sessioninfo.session[name] = session
    else:
        del sessioninfo.session[name]


def get_session(name):
    """get SQLAlchemy session by name"""
    if name in sessioninfo.session:
        return sessioninfo.session[name]
    else:
        return None
