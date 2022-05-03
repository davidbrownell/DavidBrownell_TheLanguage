# ----------------------------------------------------------------------
# |
# |  CapturedVariablesFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 08:37:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when working with captured variables"""

import os

from typing import cast, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl import ArgumentsFragmentImpl

    from ..GrammarPhrase import AST
    from ..Expressions.VariableExpression import VariableExpression

    from ...Lexer.Phrases.DSL import (
        ExtractDynamic,
        PhraseItem,
    )

    from ...Parser.Parser import (
        GetParserInfo,
        ParserInfo,
    )

    from ...Parser.ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    return ArgumentsFragmentImpl.Create(
        "Captured Variables",
        "|", "|",
        VariableExpression().phrase,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> CapturedVariablesParserInfo:
    result = ArgumentsFragmentImpl.Extract(
        CapturedVariablesParserInfo,
        _ExtractElement,
        node,
        allow_empty=False,
    )

    assert not isinstance(result, bool)
    return result


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractElement(
    node: AST.Node,
) -> Tuple[ParserInfo, bool]:
    return GetParserInfo(cast(AST.Node, ExtractDynamic(node))), False
