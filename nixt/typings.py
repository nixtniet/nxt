# This file is placed in the Public Domain.


"defines types"


from collections.abc import Callable, Iterator
from types           import FunctionType, MethodType, ModuleType
from types           import MappingProxyType
from typing          import Any, ClassVar, Dict, List, Set, TextIO
from typing          import Tuple, Union, Generator


__all__ = (
    'Any',
    'Callable',
    'ClassVar',
    'Dict',
    'FunctionType',
    'Generator',
    'Iterator',
    'List',
    'MappingProxyType',
    'MethodType',
    'ModuleType',
    'Set',
    'TextIO',
    'Tuple',
    'Union'
)


def __dir__():
    return __all__
