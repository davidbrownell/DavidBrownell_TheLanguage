# ----------------------------------------------------------------------
# |
# |  TemplateParametersParserInfo.py
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
    "The template parameter '{name}' has already been defined",
    name=str,
    prev_region=Region,
)

DuplicateVariadicError                      = CreateError(
    "A variadic template parameter has already been defined",
    prev_region=Region,
)

InvalidTemplateExpressionError              = CreateError(
    "Template decorator parameters must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeParameterParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    name: str
    is_variadic: Optional[bool]
    default_type: Optional[TypeParserInfo]

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
        super(TemplateTypeParameterParserInfo, self).__init__(
            ParserInfoType.CompileTime,
            *args,
            **kwargs,
            regionless_attributes=["default_type", ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.default_type is not None:
            details.append(("default_type", self.default_type))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorParameterParserInfo(ParserInfo):
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
        super(TemplateDecoratorParameterParserInfo, self).__init__(
            ParserInfoType.CompileTime,
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
            and self.default_value.parser_info_type__.value > ParserInfoType.CompileTime.value  # type: ignore
        ):
            errors.append(
                InvalidTemplateExpressionError.Create(
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
            details=[
                ("type", self.type),
            ] + details,  # type: ignore
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateParametersParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    # |  Public Types
    ParameterType                           = Union[
        TemplateTypeParameterParserInfo,
        TemplateDecoratorParameterParserInfo,
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List["TemplateParametersParserInfo.ParameterType"]]
    any: Optional[List["TemplateParametersParserInfo.ParameterType"]]
    keyword: Optional[List["TemplateParametersParserInfo.ParameterType"]]

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
    def __post_init__(self, *args, **kwargs):
        super(TemplateParametersParserInfo, self).__init__(ParserInfoType.CompileTime, *args, **kwargs)
        assert self.positional or self.any or self.keyword

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, TemplateParametersParserInfo.ParameterType] = {}
        prev_variadic_parameter: Optional[TemplateParametersParserInfo.ParameterType] = None

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

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.positional is not None:
            details.append(("positional", self.positional))
        if self.any is not None:
            details.append(("any", self.any))
        if self.keyword is not None:
            details.append(("keyword", self.keyword))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=None,
        )
