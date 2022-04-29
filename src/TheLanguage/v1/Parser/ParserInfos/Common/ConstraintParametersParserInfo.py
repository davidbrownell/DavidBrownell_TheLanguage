# ----------------------------------------------------------------------
# |
# |  ConstraintParametersParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 09:58:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about constraint parameters"""

import itertools
import os

from typing import Dict, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import ParserInfo, ParserInfoType, Region, TypeParserInfo

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The constraint parameter '{name}' has already been defined",
    name=str,
    prev_region=Region,
)

InvalidConstraintExpressionError            = CreateError(
    "Constraint parameters must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintParameterParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    type: TypeParserInfo
    name: str
    default_value: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(ConstraintParameterParserInfo, self).__init__(
            ParserInfoType.CompileTimeType,
            *args,
            **kwargs,
            regionless_attributes=[
                "type",
                "default_value",
            ],
        )

        # Validate
        errors: List[Error] = []

        if (
            self.default_value is not None
            and self.default_value.parser_info_type__.value > ParserInfoType.MaxCompileValue.value  # type: ignore
        ):
            errors.append(
                InvalidConstraintExpressionError.Create(
                    region=self.default_value.regions__.self__,
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.default_value is not None:
            details.append(("default_value", self.default_value))

        return self._AcceptImpl(
            visitor,
            [
                ("type", self.type),
            ] + details,  # type: ignore
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintParametersParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List[ConstraintParameterParserInfo]]
    any: Optional[List[ConstraintParameterParserInfo]]
    keyword: Optional[List[ConstraintParameterParserInfo]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(ConstraintParametersParserInfo, self).__init__(ParserInfoType.CompileTimeType, *args, **kwargs)
        assert self.positional or self.any or self.keyword

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, ConstraintParameterParserInfo] = {}

        for parameter in itertools.chain(
            self.positional or [],
            self.any or [],
            self.keyword or [],
        ):
            # Check for duplicated names
            prev_parameter = name_lookup.get(parameter.name, None)
            if prev_parameter is not None:
                errors.append(
                    DuplicateNameError.Create(
                        region=parameter.regions__.name,
                        name=parameter.name,
                        prev_region=prev_parameter.regions__.name,
                    ),
                )
            else:
                name_lookup[parameter.name] = parameter

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.positional:
            details.append(("positional", self.positional))
        if self.any:
            details.append(("any", self.any))
        if self.keyword:
            details.append(("keyword", self.keyword))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=None,
        )
