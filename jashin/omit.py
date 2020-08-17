from __future__ import annotations

import enum
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    if sys.version_info >= (3, 8):
        from typing import Final
    else:
        from typing_extensions import Final


__all__ = ["Omit", "OMIT"]


class Omit(enum.Enum):
    """Default value for keyword argument to represent ommition.

    Usage::
        from jashin.omit import OMIT

        def func(arg=OMIT):
            if arg is OMIT:
                print("arg is ommitted")


    Or, for type annotations::

        from jashin.omit import Omit, OMIT
        def func2(arg:Union[int, None, Omit]=OMIT)
            if arg is OMIT:
                print("arg is ommitted")

        func2(1)
        func2(None)
        func2()
    """

    omit = True


OMIT: Final = Omit.omit
