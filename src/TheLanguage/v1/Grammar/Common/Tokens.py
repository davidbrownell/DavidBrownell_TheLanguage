# ----------------------------------------------------------------------
# |
# |  Tokens.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 10:19:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Tokens used across multiple phrases"""

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
    from ...Lexer.Components.Tokens import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PopPreserveWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        PushPreserveWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
Dedent                                      = DedentToken()
Indent                                      = IndentToken()
Newline                                     = NewlineToken()

PopIgnoreWhitespaceControl                  = PopIgnoreWhitespaceControlToken()
PushIgnoreWhitespaceControl                 = PushIgnoreWhitespaceControlToken()

PopPreserveWhitespaceControl                = PopPreserveWhitespaceControlToken()
PushPreserveWhitespaceControl               = PushPreserveWhitespaceControlToken()


# ----------------------------------------------------------------------
CompileParameterName                        = RegexToken(
    "<compile parameter name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Lower                           )[a-z](?#
            Alphanumeric [optional]         )[A-Za-z0-9_]*(?#
            Bang                            )!(?#
            ))""",
        ),
    ),
)

# TODO: Auto-detect template types by looking for a 'T' suffix?
CompileTemplateTypeName                     = RegexToken(
    "<template type name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Upper                           )[A-Z](?#
            Alphanumeric [optional]         )[A-Za-z0-9_]*(?#
            Ends with a 'T'                 )(?<=T)(?#
            ))""",
        ),
    ),
)

CompileTypeName                             = RegexToken(
    "<compile type name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                                            )Bool|(?#
                                            )Char|(?#
                                            )Int|(?#
                                            )None|(?#
                                            )Num|(?#
                                            )Str(?#
            ))""",
        ),
    ),
)

# ----------------------------------------------------------------------
RuntimeAttributeName                        = RegexToken(
    "<attribute name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Upper                            )[A-Z](?#
            Alphanumeric                     )[A-Za-z0-9_]+(?#
            ))""",
        ),
    ),
)

RuntimeFuncName                             = RegexToken(
    "<func name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores [optional]  )_*(?#
            Upper                           )[A-Z](?#
            Alphanumeric                    )[A-Za-z0-9_]+(?#
            Is Exceptional [optional]       )(?P<is_exceptional>\?)?(?#
            Trailing Underscores [optional] )_*(?#
            ))""",
        ),
    ),
)

RuntimeParameterName                        = RegexToken(
    "<parameter name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Lower                           )[a-z](?#
            Alphanumeric [optional]         )[A-Za-z0-9_]*(?#
            ))""",
        ),
    ),
)

RuntimeSpecialMethodName                    = RegexToken(
    "<class method name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores             )__(?#
            Upper                           )[A-Z](?#
            Alphanumeric                    )[A-Za-z0-9_]+(?#
            Bang or Question                )(?:!|\?)?(?#
            Trailing Underscores            )__(?#
            ))""",
        ),
    ),
)

RuntimeTypeName                             = RegexToken(
    "<type name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores [optional]  )_*(?#
            Upper                           )[A-Z](?#
            Alphanumeric                    )[A-Za-z0-9_]+(?#
            Trailing Underscores [optional] )_*(?#
            ))""",
        ),
    ),
)

RuntimeVariableName                         = RegexToken(
    "<variable name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores [optional]  )_*(?#
            Lower                           )[a-z](?#
            Alphanumeric [optional]         )[A-Za-z0-9_]*(?#
            Trailing Underscores [optional] )_*(?#
            ))""",
        ),
    ),
)
