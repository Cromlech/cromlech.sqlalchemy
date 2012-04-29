# -*- coding: utf-8 -*-

import threading
import transaction
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import ZopeTransactionExtension


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
    return None


TWO_PHASED = frozenset(('postgre', 'postgresql', 'mysql'))


class SQLAlchemySession(object):
    """Controled execution using a SQLAlchemy-controller
    connecting the thread to a SQLAlchemy session and anchoring it
    in transaction manager.

    Parameters for connection are taken from wsgi environ under name
    """

    def __init__(self, engine, transaction_manager=None, two_phase=None):
        """
        If transaction_manager is None we will ask the transaction module
        for the current one.

        If two_phase is none, it will be set to true for mysql and postgre
        false otherwhise.
        """
        if engine is None:
            raise RuntimeError

        if two_phase is None:
            self.two_phase = engine.engine.dialect.name in TWO_PHASED
        elif (two_phase is True and
              not engine.engine.dialect.name in TWO_PHASED):
            raise ValueError(
                'SQL Engine %r : %r does not support two phase commits' %
                (engine.name, engine.engine.dialect.name))
        else:
            self.two_phase = bool(two_phase)

        self.engine = engine
        if transaction_manager is None:
            transaction_manager = transaction.manager
        self.tm = transaction_manager

    def __enter__(self):
        """Begin session scope.
        """
        self.session = scoped_session(sessionmaker(
            bind=self.engine.engine,
            twophase=self.two_phase,
            extension=ZopeTransactionExtension()))

        # add to thread
        set_session(self.engine.name, self.session)
        return self.session

    def __exit__(self, type, value, traceback):
        """end session scope
        """
        self.session.flush()
        set_session(self.engine.name, None)


class SharedSQLAlchemySession(SQLAlchemySession):
    """like SQLAlchemySession but considering that in a thread
    a db_name will always be associated with same url
    so session is opened once
    """

    def __init__(self, engine, *args, **kwargs):
        self.session = get_session(engine.name)
        if self.session is None:
            SQLAlchemySession.__init__(self, engine, *args, **kwargs)

    def __enter__(self):
        if self.session is not None:
            return self.session
        return SQLAlchemySession.__enter__(self)

    def __exit__(self, type, value, traceback):
        """Unlike SQLAlchemySession, no session cleaning.
        """
        self.session.flush()
