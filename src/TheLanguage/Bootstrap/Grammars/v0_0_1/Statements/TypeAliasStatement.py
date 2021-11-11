# ----------------------------------------------------------------------
# |
# |  TypeAliasStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 13:22:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasStatement object"""

import os

from typing import Callable, cast, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import ConstraintParametersPhraseItem
    from ..Common import TemplateParametersPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.TypeAliasStatementParserInfo import (
        TypeAliasStatementParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class TypeAliasStatement(GrammarPhrase):
    """\
    Create a new type name.

    'using' <name> '=' <type>

    Examples:
        using PositiveInt = Int<min_value=0>
    """

    PHRASE_NAME                             = "Type Alias Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TypeAliasStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <visibility>?
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # 'using'
                    "using",

                    # <generic_name>
                    CommonTokens.GenericUpperName,

                    # Begin: Template parameters, Constraint parameters
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <template_parameters>?
                    OptionalPhraseItem.Create(
                        name="Template Parameters",
                        item=TemplateParametersPhraseItem.Create(),
                    ),

                    # <constraint_parameters>?
                    OptionalPhraseItem.Create(
                        name="Constraint Parameters",
                        item=ConstraintParametersPhraseItem.Create(),
                    ),

                    # End: Template parameters, Constraint parameters
                    CommonTokens.PopIgnoreWhitespaceControl,

                    # '='
                    "=",

                    # <type>
                    DynamicPhrasesType.Types,

                    CommonTokens.Newline,
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
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 10

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <generic_name>
            name_leaf = cast(AST.Leaf, nodes[2])
            name_info = cast(str, ExtractToken(name_leaf))

            if not CommonTokens.TypeNameRegex.match(name_info):
                raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "type")

            # <template_parameters>?
            template_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[4])))
            if template_parameters_node is None:
                template_parameters_info = None
            else:
                template_parameters_info = TemplateParametersPhraseItem.ExtractParserInfo(template_parameters_node)

            # <constraint_parameters>?
            constraint_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[5])))
            if constraint_parameters_node is None:
                constraint_parameters_info = None
            else:
                constraint_parameters_info = ConstraintParametersPhraseItem.ExtractParserInfo(constraint_parameters_node)

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[8])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            return TypeAliasStatementParserInfo(
                CreateParserRegions(
                    node,
                    visibility_node,
                    name_leaf,
                    template_parameters_node,
                    constraint_parameters_node,
                    type_node,
                ),  # type: ignore
                visibility_info,  # type: ignore
                name_info,
                template_parameters_info,
                constraint_parameters_info,
                type_info,
            )

        # ----------------------------------------------------------------------

        return Impl