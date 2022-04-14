# ----------------------------------------------------------------------
# |
# |  FuncParametersPhrase.py
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
    from ..Error import CreateError, Error, ErrorException

    from ..Expressions.ExpressionPhrase import ExpressionPhrase
    from ..Types.TypePhrase import Phrase, Region, TypePhrase


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
class FuncParameterPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    type: TypePhrase
    is_variadic: Optional[bool]
    name: str
    default_value: Optional[ExpressionPhrase]

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
        super(FuncParameterPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParametersPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List[FuncParameterPhrase]]
    any: Optional[List[FuncParameterPhrase]]
    keyword: Optional[List[FuncParameterPhrase]]

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
        super(FuncParametersPhrase, self).__init__(regions)
        assert self.positional or self.any or self.keyword

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, FuncParameterPhrase] = {}
        prev_variadic_parameter: Optional[FuncParameterPhrase] = None

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
