# ----------------------------------------------------------------------
# |
# |  FuncParametersParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:43:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about function parameters"""

import itertools
import os

from typing import Dict, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ..Types.TypeParserInfo import (
        MutabilityModifierRequiredError,
        ParserInfo,
        Region,
        TypeParserInfo,
    )

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The parameter name '{name}' has already been defined",
    name=str,
    prev_region=Region,
)

DuplicateVariadicError                      = CreateError(
    "A variadic parameter has already been defined",
    prev_region=Region,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParameterParserInfo(ParserInfo):
    regions: InitVar[List[Optional[Region]]]

    type: TypeParserInfo
    is_variadic: Optional[bool]
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
    def __post_init__(self, regions):
        super(FuncParameterParserInfo, self).__init__(regions)

        # Validate
        errors: List[Error] = []

        if self.type.mutability_modifier is None:
            errors.append(
                MutabilityModifierRequiredError.Create(
                    region=self.type.regions__.self__,
                ),
            )

        if errors:
            raise ErrorException(*errors)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParametersParserInfo(ParserInfo):
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List[FuncParameterParserInfo]]
    any: Optional[List[FuncParameterParserInfo]]
    keyword: Optional[List[FuncParameterParserInfo]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(FuncParametersParserInfo, self).__init__(regions)
        assert self.positional or self.any or self.keyword

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, FuncParameterParserInfo] = {}
        prev_variadic_parameter: Optional[FuncParameterParserInfo] = None

        # Check for duplicate names and multiple variadic parameters
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

            # Check for multiple variadic parameters
            if parameter.is_variadic:
                if prev_variadic_parameter is not None:
                    errors.append(
                        DuplicateVariadicError.Create(
                            region=parameter.regions__.is_variadic,
                            prev_region=prev_variadic_parameter.regions__.is_variadic,
                        ),
                    )
                else:
                    prev_variadic_parameter = parameter

        if errors:
            raise ErrorException(*errors)
