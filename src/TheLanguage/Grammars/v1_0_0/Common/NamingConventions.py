# ----------------------------------------------------------------------
# |
# |  NamingConventions.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:48:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Various naming conventions requiring environment"""

import os
import re
import textwrap

from dataclasses import dataclass
from typing import List, Pattern

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarStatement import ValidationError


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NamingConvention(object):
    Regex: Pattern
    Constraints: List[str]


# ----------------------------------------------------------------------
Variable                                    = NamingConvention(
    re.compile(
        textwrap.dedent(
            r"""(?#
                Start of Content            )^(?#
                [Optional] Underscore       )_?(?#
                Lowercase                   )[a-z](?#
                Alpha-numeric and under     )[a-zA-Z0-9_]*(?#
                Not end with double under   )(?<!__)(?#
                End of Content              )$(?#
            )""",
        ),
    ),
    [
        "Begin with a lowercase letter",
        "Contain at least 1 upper-, lower-, numeric-, or underscore-characters",
        "Not end with double underscores",
    ],
)


Type                                        = NamingConvention(
    re.compile(
        textwrap.dedent(
            r"""(?#
                Start of Content            )^(?#
                Uppercase                   )[A-Z](?#
                Alpha-numeric and under     )[A-Za-z0-9_]+(?#
                Not end with double under   )(?<!__)(?#
                End of Content              )$(?#
            )""",
        ),
    ),
    [
        "Begin with an uppercase letter",
        "Contain at least 2 upper-, lower-, numeric-, or underscore-characters",
        "Not end with double underscores",
    ],
)


Function                                    = NamingConvention(
    re.compile(
        textwrap.dedent(
            r"""(?#
                Start of Content                        )^(?:(?#
                Dunder                                  )(?:(?#
                    Double Under                        )__(?#
                    Uppercase                           )[A-Z](?#
                    Alpha-numeric and under             )[A-Za-z0-9_]+(?#
                    Double Under                        )__(?#
                End                                     ))(?#
                -or-                                    )|(?#
                Standard                                )(?:(?#
                    Uppercase                           )[A-Z](?#
                    Alpha-numeric and under             )[A-Za-z0-9_]+(?#
                    Not end with double under           )(?<!__)(?#
                End                                     ))(?#
                [Optional] Trailing ?                   )\??(?#
                End of Content                          ))$(?#
            )""",
        ),
    ),
    [
        "Begin with an uppercase letter",
        "Contain at least 2 upper-, lower-, numeric-, or underscore-characters",
        "Not end with double underscores (unless starting with double underscores)",
    ],
)


Parameter                                   = Variable


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidVariableNameError(ValidationError):
    VariableName: str

    MessageTemplate                         = Interface.DerivedProperty(
        textwrap.dedent(
            """\
            '{{VariableName}}' is not a valid variable name.

            Variable names must:
                {}
            """,
        ).format(
            StringHelpers.LeftJustify("\n".join(Variable.Constraints).rstrip(), 4),
        ),
    )


@dataclass(frozen=True)
class InvalidTypeNameError(ValidationError):
    TypeName: str

    MessageTemplate                         = Interface.DerivedProperty(
        textwrap.dedent(
            """\
            '{{TypeName}}' is not a valid type name.

            Type names must:
                {}
            """,
        ).format(
            StringHelpers.LeftJustify("\n".join(Type.Constraints).rstrip(), 4),
        ),
    )


@dataclass(frozen=True)
class InvalidFunctionNameError(ValidationError):
    FunctionName: str

    MessageTemplate                         = Interface.DerivedProperty(
        textwrap.dedent(
            """\
            '{{FunctionName}}' is not a valid function name.

            Function names must:
                {}
            """,
        ).format(
            StringHelpers.LeftJustify("\n".join(Function.Constraints).rstrip(), 4),
        ),
    )


@dataclass(frozen=True)
class InvalidParameterNameError(ValidationError):
    ParameterName: str

    MessageTemplate                         = Interface.DerivedProperty(
        textwrap.dedent(
            """\
            '{{ParameterName}}' is not a valid parameter name.

            Parameter names must:
                {}
            """,
        ).format(
            StringHelpers.LeftJustify("\n".join(Parameter.Constraints).rstrip(), 4),
        ),
    )
