# -*- coding: utf-8 -*-

import transaction
from components import get_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


class SQLAlchemySession(object):
    """Controled execution using a SQLAlchemy-controller
    connecting the thread to a SQLAlchemy session and anchoring it
    in transaction manager.

    Parameters for connection are taken from wsgi environ under name
    """

    def __init__(self, environ, name, bases,
                        transaction_manager = None, two_phase = True):
        """
        name is the name of connection parameters in wsgi environ.

        bases are associated SQLAlchemy declarative bases

        If transaction_manager is None we will ask the transaction module
        for the current one.
        """
        self.environ = environ
        self.name = name
        self.bases = bases
        if transaction_manager is None:
            transaction_manager = transaction.manager
        self.tm = transaction_manager

    def __enter__(self):
        """begin session scope"""
        conn_url = self.environ['name']
        # get the engine
        self.engine = get_engine(conn_url, self.bases)
        # make a session
        self.session = scoped_session(sessionmaker(bind=engine,
            twophase=two_phase, extension=ZopeTransactionExtension()))
        # add to thread
        set_session(self.name, self.session)

    def __exit__(self, type, value, traceback):
        """end session scope
        """
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
