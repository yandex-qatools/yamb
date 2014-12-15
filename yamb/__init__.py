"""
Created on Sep 22, 2014

@author: pupssman
"""
import yaml

from abc import ABCMeta, abstractmethod
from collections import MutableSequence


__all__ = ['YAMBObject', 'YAMBMeta', 'Literal', 'Nested', 'Collection']


class YambProperty(object):
    __metaclass__ = ABCMeta

    """
    Interface for all yaml facade objects
    """

    @abstractmethod
    def _load(self, value):
        """ this method is called to convert given YAML-value to Python facade"""

    @abstractmethod
    def _dump(self, value):
        """ this method is called to convert Python facade-like object to the YAML-value"""


class Literal(YambProperty):
    """
    Literal property -- will be passed to :py:mod:`yaml` as-is.

    Fits for primitive values -- strings, numbers, etc.

    :arg default: default value
    """

    def __init__(self, default=None):
        self.default = default

    def _load(self, value):
        if value is None:
            return self.default
        else:
            return value

    def _dump(self, value):
        return value


class Nested(YambProperty):
    """
    Nested :py:class:`YAMBObject` instance.
    """
    def __init__(self, clazz):
        self.clazz = clazz

    def _load(self, value):
        return self.clazz._load(value, top=False)

    def _dump(self, value):
        return value._dump(top=False)


class Collection(Nested):
    """
    A list of :py:class:`YAMBObject`s
    """

    def _load(self, value):
        one = super(Collection, self)

        class ListProxy(MutableSequence):
            def __init__(self, actual_list):
                self.list = actual_list

            def __getitem__(self, item):
                return one._load(self.list[item])

            def __setitem__(self, item, value):
                self.list[item] = one._dump(value)

            def __delitem__(self, item):
                del self.list[item]

            def __len__(self):
                return self.list.__len__()

            def insert(self, pos, value):
                return self.list.insert(pos, one._dump(value))

        return ListProxy(value)

    def _dump(self, value):
        return [super(Collection, self)._dump(x) for x in value]


class YAMBMeta(type):
    """
    A yaml-proxying metaclass -- a facade for the real data loaded from the document.

    Represents a YAML mapping as a Python object with attributes and real-like interactions.

    Apply to a class with some :py:class:`YambProperty` entries as in test example.
    """

    def __new__(self, name, bases, kw):
        things = {n: v for (n, v) in kw.items() if isinstance(v, YambProperty)}
        stuff = {n: v for (n, v) in kw.items() if n not in things}

        class YAMLYBase(object):
            def __init__(self, _data=None, **kw):
                if _data:
                    self._data = _data
                else:
                    # Here we do serve either as a top-level object or as a temporary facade
                    unknowns = filter(lambda k: k not in things, kw.keys())
                    if unknowns:
                        raise AttributeError('{0} was given unknown properties of {1}'.format(self, unknowns))

                    self._data = {k: things[k]._dump(v) for (k, v) in kw.items()}

            @classmethod
            def _load(cls, document, top=True):
                if top:
                    doc = yaml.load(document)
                    return cls._load(doc, top=False)
                return cls(_data=document)

            def _dump(self, top=True, **kw):
                if top:
                    doc = self._dump(top=False)
                    return yaml.dump(doc, **kw)
                else:
                    return self._data

            def __getattr__(self, attr):
                if attr in things:
                    return things[attr]._load(self._data.get(attr))
                raise AttributeError

            def __setattr__(self, attr, value):
                if attr in things:
                    self._data[attr] = things[attr]._dump(value)
                elif attr == '_data' or attr in stuff:  # so the internals and primitives work OK
                    self.__dict__[attr] = value
                else:
                    raise AttributeError

        return super(YAMBMeta, self).__new__(self, name, (YAMLYBase,) + bases, stuff)


class YAMBObject(object):
    """
    Convenience base class for YAML-mapped classes
    """
    __metaclass__ = YAMBMeta
