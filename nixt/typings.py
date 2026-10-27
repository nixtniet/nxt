# This file is placed in the Public Domain.


"default types"


from collections.abc import Callable, Iterator
from types           import FunctionType, MethodType, ModuleType
from types           import MappingProxyType
from typing          import Any, ClassVar, Dict, List, Set, TextIO
from typing          import Tuple, Union, Generator


Anys      = Dict[str, Any]
Callables = Dict[str, Callable]
Exec      = Union[FunctionType, MethodType]
Execs     = Dict[str, Exec]
Hash      = Dict[str, str]


__all__ = (
    'Any',
    'Anys',
    'Callable',
    'Callables',
    'ClassVar',
    'Dict',
    'Exec',
    'Execs',
    'FunctionType',
    'Generator',
    'Hash',
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
