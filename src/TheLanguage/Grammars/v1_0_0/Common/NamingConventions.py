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


# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
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
