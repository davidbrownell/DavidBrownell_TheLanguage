# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-23 16:40:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains tokens used by multiple statements"""

import os
import re
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...ParserImpl.Token import RegexToken


# ----------------------------------------------------------------------
ModuleNameToken                             = RegexToken(
    "<module_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Uppercase Letter                        )[A-Z](?#
                Alpha Numeric and underscore            )[a-zA-Z0-9_]+(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
ClassNameToken                              = RegexToken(
    "<class_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Leading Underscore [optional]           )_?(?#
                Uppercase Letter                        )[A-Z](?#
                Alpha Numeric and underscore            )[a-zA-Z0-9_]+(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
FunctionNameToken                           = RegexToken(
    "<funciton_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Leading Underscore [optional]           )_?(?#
                Uppercase Letter                        )[A-Z](?#
                Alpha Numeric and underscore            )[a-zA-Z0-9_]+(?#
                Question Mark [optional]                )\??(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
VariableNameToken                           = RegexToken(
    "<variable_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Leading Underscore [optional]           )_?(?#
                Lowercase Letter                        )[a-z](?#
                Alpha Numeric and underscore            )[a-zA-Z0-9_]*(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
ParameterNameToken                          = RegexToken(
    "<parameter_name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Lowercase Letter                        )[a-z](?#
                Alpha Numeric and underscore            )[a-zA-Z0-9_]*(?#
                Tick [optional]                         )'?(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
CommentToken                                = RegexToken(
    "Comment",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Prefix                      )\#(?#
                Content                     )[^\n]*(?#
            ))""",
        ),
    ),
)


# ----------------------------------------------------------------------
CommaToken                                  = RegexToken("','", re.compile(","))
LParenToken                                 = RegexToken("'('", re.compile(r"\("))
RParenToken                                 = RegexToken("')'", re.compile(r"\)"))
