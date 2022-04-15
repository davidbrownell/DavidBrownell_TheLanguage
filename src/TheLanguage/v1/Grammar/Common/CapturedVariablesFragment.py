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

from typing import cast, List, Union, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl import ArgumentsFragmentImpl

    from ..GrammarPhrase import AST

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        PhraseItem,
    )

    from ...Parser.Parser import GetPhrase, Phrase
    from ...Parser.Phrases.Common.CapturedVariablesPhrase import CapturedVariablesPhrase

    from ...Parser.Phrases.Error import Error


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    variable_element = PhraseItem(
        name="Variable",
        item=DynamicPhrasesType.Expressions,
    )

    return ArgumentsFragmentImpl.Create(
        "Captured Variables",
        "|", "|",
        variable_element,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    CapturedVariablesPhrase,
]:
    result = ArgumentsFragmentImpl.Extract(
        CapturedVariablesPhrase,
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
) -> Tuple[Phrase, bool]:
    return GetPhrase(cast(AST.Node, ExtractDynamic(node))), False
