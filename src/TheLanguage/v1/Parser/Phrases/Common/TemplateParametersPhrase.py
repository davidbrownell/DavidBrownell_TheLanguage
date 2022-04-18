# ----------------------------------------------------------------------
# |
# |  TemplateParametersPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 17:41:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about template parameters"""

import itertools
import os

from typing import Dict, List, Optional, Union

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Error import CreateError, Error, ErrorException

    from ..CompileExpressions.CompileExpressionPhrase import CompileExpressionPhrase
    from ..CompileTypes.CompileTypePhrase import CompileTypePhrase
    from ..Types.TypePhrase import Phrase, Region, TypePhrase


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The template parameter '{name}' has already been defined",
    name=str,
    prev_region=Region,
)

DuplicateVariadicError                      = CreateError(
    "A variadic template parameter has already been defined",
    prev_region=Region,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeParameterPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    name: str
    is_variadic: Optional[bool]
    default_type: Optional[TypePhrase]

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
        super(TemplateTypeParameterPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorParameterPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    type: CompileTypePhrase
    name: str
    default_value: Optional[CompileExpressionPhrase]

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
        super(TemplateDecoratorParameterPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateParametersPhrase(Phrase):
    # ----------------------------------------------------------------------
    # |  Public Types
    ParameterType                           = Union[
        TemplateTypeParameterPhrase,
        TemplateDecoratorParameterPhrase,
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List["TemplateParametersPhrase.ParameterType"]]
    any: Optional[List["TemplateParametersPhrase.ParameterType"]]
    keyword: Optional[List["TemplateParametersPhrase.ParameterType"]]

    # ----------------------------------------------------------------------
    # |  Public Methods
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TemplateParametersPhrase, self).__init__(regions)
        assert self.positional or self.any or self.keyword

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, TemplateParametersPhrase.ParameterType] = {}
        prev_variadic_parameter: Optional[TemplateParametersPhrase.ParameterType] = None

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
            if getattr(parameter, "is_variadic", False):
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
