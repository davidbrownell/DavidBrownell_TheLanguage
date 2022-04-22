# ----------------------------------------------------------------------
# |
# |  SpecialMethodStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-18 14:01:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SpecialMethodStatement object"""

import os

from typing import cast, List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassStatement import ClassStatement
    from .FuncDefinitionStatement import FuncDefinitionStatement

    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import StatementsFragment
    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractSequence,
    )

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
    )

    from ...Parser.ParserInfos.Statements.SpecialMethodStatementParserInfo import (
        SpecialMethodType,
        SpecialMethodStatementParserInfo,
    )


# ----------------------------------------------------------------------
InvalidMethodNameError                      = CreateError(
    "The method name '{name}' is not a valid special method name",
    name=str,
)


# ----------------------------------------------------------------------
class SpecialMethodStatement(GrammarPhrase):
    """Statements unique to a class - no return value, no parameters, no modifer, etc."""

    PHRASE_NAME                             = "Class Func Definition Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(SpecialMethodStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # <method_name>
                CommonTokens.SpecialMethodName,

                # '('
                "(",
                CommonTokens.PushIgnoreWhitespaceControl,

                # ')'
                CommonTokens.PopIgnoreWhitespaceControl,
                ")",

                # <statements>
                StatementsFragment.Create(),
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 6

            errors: List[Error] = []

            # <method_name>
            name_leaf = cast(AST.Leaf, nodes[0])
            name_info = CommonTokens.SpecialMethodName.Extract(name_leaf)  # type: ignore

            if name_info == "__EvalTemplates!__":
                name_info = SpecialMethodType.CompileTimeEvalTemplates
            elif name_info == "__EvalConstraints!__":
                name_info = SpecialMethodType.CompileTimeEvalConstraints
            elif name_info == "__EvalConvertible!__":
                name_info = SpecialMethodType.CompileTimeConvert
            elif name_info == "__Construct?__":
                name_info = SpecialMethodType.Construct
            elif name_info == "__ConstructFinal?__":
                name_info = SpecialMethodType.ConstructFinal
            elif name_info == "__Destroy__":
                name_info = SpecialMethodType.Destroy
            elif name_info == "__DestroyFinal__":
                name_info = SpecialMethodType.DestroyFinal
            elif name_info == "__PrepareFinalize?__":
                name_info = SpecialMethodType.PrepareFinalize
            elif name_info == "__Finalize__":
                name_info = SpecialMethodType.Finalize
            else:
                errors.append(
                    InvalidMethodNameError.Create(
                        region=CreateRegion(name_leaf),
                        name=name_info,
                    ),
                )

            # <statements>
            statements_info = None
            statements_node = cast(AST.Node, nodes[5])

            result = StatementsFragment.Extract(statements_node)

            if isinstance(result, list):
                errors += result
            else:
                statements_info = result[0]

            if errors:
                return errors

            return SpecialMethodStatementParserInfo.Create(
                CreateRegions(node, name_leaf, statements_node),
                ClassStatement.GetParentClassCapabilities(node, FuncDefinitionStatement),
                name_info,
                statements_info,
            )

        # ----------------------------------------------------------------------

        return Callback
