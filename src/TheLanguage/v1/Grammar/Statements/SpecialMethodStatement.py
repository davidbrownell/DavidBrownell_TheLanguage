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
        ErrorException,
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

    FUNCTION_MAP                            = {
        "__EvalTemplates!__": SpecialMethodType.EvalTemplates,
        "__EvalConstraints!__": SpecialMethodType.CompileTimeEvalConstraints,
        "__EvalConvertible!__": SpecialMethodType.CompileTimeConvert,
        "__Validate?__": SpecialMethodType.Validate,
        "__ValidateFinal?__": SpecialMethodType.ValidateFinal,
        "__Destroy__": SpecialMethodType.Destroy,
        "__DestroyFinal__": SpecialMethodType.DestroyFinal,
        "__PrepareFinalize?__": SpecialMethodType.PrepareFinalize,
        "__Finalize__": SpecialMethodType.Finalize,
    }

    assert len(FUNCTION_MAP) == len(SpecialMethodType)

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
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
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

            name_info = cls.FUNCTION_MAP.get(name_info, None)
            if name_info is None:
                errors.append(
                    InvalidMethodNameError.Create(
                        region=CreateRegion(name_leaf),
                        name=name_info,
                    ),
                )

            # <statements>
            statements_node = cast(AST.Node, nodes[5])
            statements_info = StatementsFragment.Extract(statements_node)[0]

            if errors:
                raise ErrorException(*errors)

            return SpecialMethodStatementParserInfo.Create(
                CreateRegions(node, name_leaf, statements_node),
                statements_info,
                ClassStatement.GetParentClassCapabilities(node),
                cast(SpecialMethodType, name_info),
            )

        # ----------------------------------------------------------------------

        return Callback
