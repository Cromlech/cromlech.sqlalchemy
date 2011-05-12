"""
dbengine will be created at connection time

In code however we want to be able to declare an engine for a declarative class
with its name, so we will register relations between class and engine name
at class creation time.
"""

from sqlalchemy.ext.declarative import DeclarativeMeta

DEFAULT_ENGINE_NAME = 'cromlech.default_db'

engine_bindings = dict()


class RegisteringMeta(DeclarativeMeta):
    """Meta class that also register the class to an engine name
    """
    def __init__(cls, classname, bases, dict_):
        klass = DeclarativeMeta.__init__(cls, classname, bases, dict_)
        engine_name = dict_.get('__dbengine__', DEFAULT_ENGINE_NAME)
        if engine_name not in engine_bindings:
            engine_bindings[engine_name] = []
        engine_bindings[engine_name].append(klass)
        return klass


def declarative_base(*args, **kwargs):
    """our declarative_base creation

    it the same as original declarative_base with a specific meta
    """
    new_kwargs = dict(meta = RegisteringMeta)
    new_kwargs.update((k, v) for k, v in kwargs.items() if k != 'dbengine')

    base = declarative_base(*args, **new_kwargs)
    if 'dbengine' in kwargs:
        base.__dbengine__ = kwargs['dbengine']
    return base

