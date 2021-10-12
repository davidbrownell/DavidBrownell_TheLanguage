# ----------------------------------------------------------------------
# |
# |  FuncNameExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 12:58:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncNameExpression object"""

import os

from typing import Callable, cast, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions
    from ....Parser.Expressions.FuncNameExpressionParserInfo import FuncNameExpressionParserInfo


# ----------------------------------------------------------------------
class FuncNameExpression(GrammarPhrase):
    """\
    The name of a function.
    """

    PHRASE_NAME                             = "Func Name Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncNameExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    CommonTokens.FuncName,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        # <func_name>
        func_name_leaf = cast(AST.Leaf, nodes[0])
        func_name_info = cast(str, ExtractToken(func_name_leaf, group_dict_name="value"))

        return FuncNameExpressionParserInfo(
            CreateParserRegions(node, func_name_leaf),  # type: ignore
            func_name_info,
        )
