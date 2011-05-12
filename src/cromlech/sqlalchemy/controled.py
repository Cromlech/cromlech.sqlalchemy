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

    def __init__(self, environ, name, transaction_manager=None,
                                      two_phase=True):
        """
        name is the name of connection parameters in wsgi environ.

        metadata is a SQLAlchemy Metadata which will be associated with
        connection

        If transaction_manager is None we will ask the transaction module
        for the current one.
        """
        self.environ = environ
        self.name = name
        self.two_phase = two_phase
        if transaction_manager is None:
            transaction_manager = transaction.manager
        self.tm = transaction_manager

    def __enter__(self):
        """begin session scope"""
        # get the engine
        self.engine = get_engine(self.name, self.environ)
        # make a session, we make a scoped session in case we want to
        # work on same connection later
        self.session =  scoped_session(sessionmaker(bind=self.engine,
            twophase=self.two_phase, extension=ZopeTransactionExtension()))
        # add to thread
        set_session(self.name, self.session)
        return self.session

    def __exit__(self, type, value, traceback):
        """end session scope
        """
        self.session.flush()
        set_session(self.name, None)


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
    return sessioninfo.session[name]
