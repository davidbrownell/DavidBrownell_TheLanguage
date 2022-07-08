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

from typing import Callable, List, Optional, Tuple, Union

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
def CreateRegexToken(
    name: str,
    tokens: Union[
        str,                                # single value
        List[str],                          # sequence
        Tuple[str, ...],                    # one of
    ],
    group_name: Optional[str]=None,
) -> RegexToken:
    if isinstance(tokens, str):
        expression = tokens
    elif isinstance(tokens, list):
        expression = "".join(tokens)
    elif isinstance(tokens, tuple):
        expression = "(?:{})".format("|".join(tokens))

    # Match whole word
    expression = r"{}(?![A-Za-z0-9_!\?])".format(expression)

    if group_name is not None:
        expression = r"(?P<{}>{})".format(group_name, expression)

    return RegexToken(name, re.compile(expression))


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
AttributeName                               = CreateRegexToken(
    "<attribute_name>",
    [
        r"[A-Z]",
        r"[A-Za-z0-9_]+",
    ],
    group_name="value",
)

AttributeName.Extract                       = _ExtractFuncFactory(False)  # type: ignore


# ----------------------------------------------------------------------
FuncOrTypeName                              = CreateRegexToken(
    "<func or type name>",
    [
        r"_*",
        r"[A-Z]",
        r"[A-Za-z0-9_]+",
        r"(?P<is_compile_time>!)?",
        r"(?P<is_exceptional>\?)?",
        "_*",
    ],
    group_name="value",
)

FuncOrTypeName.Extract                      = _ExtractFuncFactory(True)                             # type: ignore
FuncOrTypeName.IsCompileTime                = _IsFuncFactory(FuncOrTypeName, "is_compile_time")           # type: ignore
FuncOrTypeName.GetIsCompileTimeRegion       = _GetRegionFuncFactory(FuncOrTypeName, "is_compile_time")    # type: ignore
FuncOrTypeName.IsExceptional                = _IsFuncFactory(FuncOrTypeName, "is_exceptional")            # type: ignore
FuncOrTypeName.GetIsCompileTimeRegion       = _GetRegionFuncFactory(FuncOrTypeName, "is_exceptional")     # type: ignore

func_or_type_name_configuration_compile_time_regex      = re.compile(r"__[A-Z][A-Za-z0-9_]+!")

# ----------------------------------------------------------------------
ParameterName                               = CreateRegexToken(
    "<parameter name>",
    [
        r"[a-z]",
        r"[A-Za-z0-9_]+",
        r"(?P<is_compile_time>!)?",
    ],
    group_name="value",
)

ParameterName.Extract                       = _ExtractFuncFactory(True)                                 # type: ignore
ParameterName.IsCompileTime                 = _IsFuncFactory(ParameterName, "is_compile_time")          # type: ignore
ParameterName.GetIsCompileTimeRegion        = _GetRegionFuncFactory(ParameterName, "is_compile_time")   # type: ignore


# ----------------------------------------------------------------------
# TODO: I don't like the name "SpecialMethod"
SpecialMethodName                           = CreateRegexToken(
    "<class method name>",
    [
        r"__",
        r"[A-Z]",
        r"[A-Za-z0-9_]+",
        r"(?P<is_compile_time>!)?",
        r"(?P<is_exceptional>\?)?",
        r"__",
    ],
    group_name="value",
)

SpecialMethodName.Extract                   = _ExtractFuncFactory(True)                                     # type: ignore
SpecialMethodName.IsCompileTime             = _IsFuncFactory(SpecialMethodName, "is_compile_time")          # type: ignore
SpecialMethodName.GetIsCompileTimeRegion    = _GetRegionFuncFactory(SpecialMethodName, "is_compile_time")   # type: ignore
SpecialMethodName.IsExceptional             = _IsFuncFactory(SpecialMethodName, "is_exceptional")           # type: ignore
SpecialMethodName.GetIsExceptionalRegion    = _GetRegionFuncFactory(SpecialMethodName, "is_exceptional")    # type: ignore


# ----------------------------------------------------------------------
# TODO: Auto-detect template types by looking for a 'T' suffix?

TemplateTypeName                            = CreateRegexToken(
    "<template type name>",
    [
        r"[A-Z]",
        r"[A-Za-z0-9_]+",
        r"(?<=T)",
    ],
    group_name="value",
)

TemplateTypeName.Extract                    = _ExtractFuncFactory(False)  # type: ignore


# ----------------------------------------------------------------------
VariableName                                = CreateRegexToken(
    "<variable name>",
    [
        r"_*",
        r"[a-z]",
        r"[A-Za-z0-9_]*",
        r"(?P<is_compile_time>!)?",
        r"_*",
    ],
    group_name="value",
)

VariableName.Extract                        = _ExtractFuncFactory(True)  # type: ignore
VariableName.IsCompileTime                  = _IsFuncFactory(VariableName, "is_compile_time")  # type: ignore
VariableName.GetIsCompileTimeRegion         = _GetRegionFuncFactory(VariableName, "is_compile_time")  # type: ignore

variable_name_configuration_compile_time_regex          = re.compile(r"__[a-z][A-Za-z0-9_]*!")


# ----------------------------------------------------------------------
del _GetRegionFuncFactory
del _IsFuncFactory
del _ExtractFuncFactory
