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
import types

from typing import Callable, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Lexer.Components import AST
    from ...Lexer.Components.Phrase import Phrase

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

    from ...Lexer.Phrases.DSL import ExtractToken, ExtractTokenRangeNoThrow


# ----------------------------------------------------------------------
Dedent                                      = DedentToken()
Indent                                      = IndentToken()
Newline                                     = NewlineToken()

PopIgnoreWhitespaceControl                  = PopIgnoreWhitespaceControlToken()
PushIgnoreWhitespaceControl                 = PushIgnoreWhitespaceControlToken()

PopPreserveWhitespaceControl                = PopPreserveWhitespaceControlToken()
PushPreserveWhitespaceControl               = PushPreserveWhitespaceControlToken()


# ----------------------------------------------------------------------
def _ExtractFuncFactory(
    has_nested_groups: bool,
) -> Callable[[AST.Leaf], str]:
    if has_nested_groups:
        return lambda leaf: ExtractToken(leaf, return_match_contents=True)

    return ExtractToken


# ----------------------------------------------------------------------
def _IsFuncFactory(
    regex_token: RegexToken,
    group_name: str,
) -> Callable[[str], bool]:
    # ----------------------------------------------------------------------
    def Impl(
        self,
        value: str,
    ) -> bool:
        match = self.regex.match(value)

        return match is not None and bool(match.group(group_name))

    # ----------------------------------------------------------------------

    return types.MethodType(Impl, regex_token)


# ----------------------------------------------------------------------
def _GetRegionFuncFactory(
    regex_token: RegexToken,
    group_name: str,
) -> Callable[[AST.Leaf], Optional[Phrase.NormalizedIteratorRange]]:
    # ----------------------------------------------------------------------
    def Impl(
        self,
        leaf: AST.Leaf,
    ) -> Optional[Phrase.NormalizedIteratorRange]:
        return ExtractTokenRangeNoThrow(leaf, group_name)

    # ----------------------------------------------------------------------

    return types.MethodType(Impl, regex_token)


# ----------------------------------------------------------------------
ReservedUpperNames                          = [
    # Fundamental Types
    "Bool",
    "Char",
    "Int",
    "None",
    "Num",
    "Str",

    # Fundamental Type Values
    "True",
    "False",
]

ReservedLowerNames                          = [
]


# ----------------------------------------------------------------------
AttributeName                               = RegexToken(
    "<attribute name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Upper                            )[A-Z](?#
            Alphanumeric                     )[A-Za-z0-9_]+(?#
            ))""",
        ),
    ),
    exclude_matches=ReservedLowerNames,
)

AttributeName.Extract                       = _ExtractFuncFactory(False)  # type: ignore


# ----------------------------------------------------------------------
FuncName                                    = RegexToken(
    "<func name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores [optional]  )_*(?#
            Upper                           )[A-Z](?#
            Alphanumeric                    )[A-Za-z0-9_]+(?#
            Is compile time [optional]      )(?P<is_compile_time>!)?(?#
            Is exceptional [optional]       )(?P<is_exceptional>\?)?(?#
            Trailing Underscores [optional] )_*(?#
            Whole match only                )(?![A-Za-z0-9_!\?])(?#
            ))""",
        ),
    ),
    exclude_matches=ReservedUpperNames,
)

FuncName.Extract                            = _ExtractFuncFactory(True)                             # type: ignore
FuncName.IsCompileTime                      = _IsFuncFactory(FuncName, "is_compile_time")           # type: ignore
FuncName.GetIsCompileTimeRegion             = _GetRegionFuncFactory(FuncName, "is_compile_time")    # type: ignore
FuncName.IsExceptional                      = _IsFuncFactory(FuncName, "is_exceptional")            # type: ignore
FuncName.GetIsCompileTimeRegion             = _GetRegionFuncFactory(FuncName, "is_exceptional")     # type: ignore


# ----------------------------------------------------------------------
ParameterName                               = RegexToken(
    "<parameter name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Lower                           )[a-z](?#
            Alphanumeric [optional]         )[A-Za-z0-9_]*(?#
            Bang [optional]                 )(?P<is_compile_time>!)?(?#
            ))""",
        ),
    ),
    exclude_matches=ReservedLowerNames,
)

ParameterName.Extract                       = _ExtractFuncFactory(True)                                 # type: ignore
ParameterName.IsCompileTime                 = _IsFuncFactory(ParameterName, "is_compile_time")          # type: ignore
ParameterName.GetIsCompileTimeRegion        = _GetRegionFuncFactory(ParameterName, "is_compile_time")   # type: ignore


# ----------------------------------------------------------------------
# TODO: I don't like the name "SpecialMethod"
SpecialMethodName                           = RegexToken(
    "<class method name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores             )__(?#
            Upper                           )[A-Z](?#
            Alphanumeric                    )[A-Za-z0-9_]+(?#
            Bang [optional]                 )(?P<is_compile_time>!)?(?#
            Question mark [optional]        )(?P<is_exceptional>\?)?(?#
            Trailing Underscores            )__(?#
            Whole match only                )(?![A-Za-z0-9_!\?])(?#
            ))""",
        ),
    ),
)

SpecialMethodName.Extract                   = _ExtractFuncFactory(True)                                     # type: ignore
SpecialMethodName.IsCompileTime             = _IsFuncFactory(SpecialMethodName, "is_compile_time")          # type: ignore
SpecialMethodName.GetIsCompileTimeRegion    = _GetRegionFuncFactory(SpecialMethodName, "is_compile_time")   # type: ignore
SpecialMethodName.IsExceptional             = _IsFuncFactory(SpecialMethodName, "is_exceptional")           # type: ignore
SpecialMethodName.GetIsExceptionalRegion    = _GetRegionFuncFactory(SpecialMethodName, "is_exceptional")    # type: ignore


# ----------------------------------------------------------------------
# TODO: Auto-detect template types by looking for a 'T' suffix?
TemplateTypeName                            = RegexToken(
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
    exclude_matches=ReservedUpperNames,
)

TemplateTypeName.Extract                    = _ExtractFuncFactory(False)  # type: ignore


# ----------------------------------------------------------------------
TypeName                                    = RegexToken(
    "<type name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores [optional]  )_*(?#
            Upper                           )[A-Z](?#
            Alphanumeric                    )[A-Za-z0-9_]+(?#
            Trailing Underscores [optional] )_*(?#
            Whole match only                )(?![A-Za-z0-9_])(?#
            ))""",
        ),
    ),
)


TypeName.Extract                            = _ExtractFuncFactory(False)  # type: ignore


# ----------------------------------------------------------------------
# TODO: Probably looking at 2 types here, those that allow leading underscores (class attributes)
#       and everything else.
VariableName                                = RegexToken(
    "<variable name>",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
            Initial Underscores [optional]  )_*(?#
            Lower                           )[a-z](?#
            Alphanumeric [optional]         )[A-Za-z0-9_]*(?#
            Bang [optional]                 )(?P<is_compile_time>!)?(?#
            Trailing Underscores [optional] )_*(?#
            Whole match only                )(?![A-Za-z0-9_!])(?#
            ))""",
        ),
    ),
    exclude_matches=ReservedLowerNames,
)

VariableName.Extract                        = _ExtractFuncFactory(True)  # type: ignore
VariableName.IsCompileTime                  = _IsFuncFactory(VariableName, "is_compile_time")  # type: ignore
VariableName.GetIsCompileTimeRegion         = _GetRegionFuncFactory(VariableName, "is_compile_time")  # type: ignore


# ----------------------------------------------------------------------
del _GetRegionFuncFactory
del _IsFuncFactory
del _ExtractFuncFactory
