# ----------------------------------------------------------------------
# |
# |  CommonStatements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-06 14:53:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements used by other statements"""

import os
import re
import textwrap

from collections import OrderedDict
from enum import auto, Enum
from typing import Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...ParserImpl.Normalize import Normalize
    from ...ParserImpl.NormalizedIterator import NormalizedIterator
    from ...ParserImpl.Statement import Statement
    from ...ParserImpl.Token import RegexToken


# ----------------------------------------------------------------------
def _CreateRegexStatement(
    statement_name: str,
    regex: str,
) -> Statement:
    assert statement_name
    assert regex and regex[0] != "_", regex

    return Statement(
        statement_name,
        [
            # _<name>_
            RegexToken("Protected", re.compile(r"(?P<value>_{}_)(?<!__)\b".format(regex))),

            # _<name>
            RegexToken("Private", re.compile(r"(?P<value>_{})(?<!_)\b".format(regex))),

            # <name>
            RegexToken("Public", re.compile(r"(?P<value>{})(?<!_)\b".format(regex))),
        ],
    )


# ----------------------------------------------------------------------
ModuleNameStatement                         = _CreateRegexStatement(
    "<module_name>",
    textwrap.dedent(
        r"""(?#
            Leading Upper                   )[A-Z](?#
            Alpha-Numeric w/under [+]       )[A-Za-z0-9_]+(?#
        )""",
    ),
)


ClassNameStatement                          = _CreateRegexStatement(
    "<class_name>",
    textwrap.dedent(
        r"""(?#
            Leading Upper                   )[A-Z](?#
            Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
        )""",
    ),
)


ClassMemberNameStatement                    = _CreateRegexStatement(
    "<class_member>",
    textwrap.dedent(
        r"""(?#
            Leading Lower                   )[a-z](?#
            Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
        )""",
    ),
)


FunctionNameStatement                       = _CreateRegexStatement(
    "<function_name>",
    textwrap.dedent(
        r"""(?#
            Leading Upper                   )[A-Z](?#
            Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
            Trailing '?' [optional]         )\??(?#
        )""",
    ),
)


FunctionParameterNameStatement              = _CreateRegexStatement(
    "<parameter_name>",
    textwrap.dedent(
        r"""(?#
            Leading Lower                   )[a-z](?#
            Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
        )""",
    ),
)


VariableNameStatement                       = RegexToken(
    "<name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Leading Lower               )[a-z](?#
                Alpha-Numeric w/under [*]   )[A-Za-z0-9_]*(?#
                No trailing underscore      )(?<!_)(?#
                End Word Boundary           )\b(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
del _CreateRegexStatement


# ----------------------------------------------------------------------
class MatchRegexStatementResult(Enum):
    NoMatch                                 = auto()
    Private                                 = auto()
    Protected                               = auto()
    Public                                  = auto()


def MatchRegexStatement(
    content: str,
    *statements: Union[Statement, RegexToken],
) -> MatchRegexStatementResult:
    """Convenience function that attempts to match a string to one of the statements defined above"""

    normalized_iter = NormalizedIterator(Normalize(content))

    for statement in statements:
        tokens = OrderedDict()

        if isinstance(statement, RegexToken):
            tokens[MatchRegexStatementResult.Public] = statement

        elif isinstance(statement, Statement):
            assert len(statement.Items) == 1

            for token in statement.Items[0]:
                tokens[MatchRegexStatementResult[token.Name]] = token

        else:
            assert False  # pragma: no cover

        for result, token in tokens.items():
            if token.Match(normalized_iter):
                return result

    return MatchRegexStatementResult.NoMatch
