# ----------------------------------------------------------------------
# |
# |  ConstraintExpressionPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 10:04:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConstraintExpressionPhrase object"""

import os

from typing import Any, Callable, Dict, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Phrase import Phrase, Region
    from ...CompileTimeTypes.CompileTimeType import CompileTimeType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintExpressionPhrase(Phrase, Interface.Interface):
    """Abstract base class for all constraint expressions"""

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        super(ConstraintExpressionPhrase, self).__init__(
            regions,
            regionless_attributes,
            validate,
            expression_type=None,  # type: ignore
            **custom_display_funcs,
        )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class EvalResult(object):
        value: Any
        type: CompileTimeType
        name: Optional[str]                 # None if the value is a temporary

    @staticmethod
    @Interface.abstractmethod
    def Eval(
        args: Dict[str, Any],
        type_overloads: Dict[str, CompileTimeType],
    ) -> "ConstraintExpressionPhrase.EvalResult":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ToString(
        args: Dict[str, Any],
    ) -> str:
        raise Exception("Abstract method")  # pragma: no cover
