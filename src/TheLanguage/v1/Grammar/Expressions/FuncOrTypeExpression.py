# ----------------------------------------------------------------------
# |
# |  FuncOrTypeExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 08:05:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncOrTypeExpression object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import ConstraintArgumentsFragment
    from ..Common import MutabilityModifier
    from ..Common import TemplateArgumentsFragment
    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegions

    from ...Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import (
        BooleanType,
        CharacterType,
        CustomType,
        FuncOrTypeExpressionParserInfo,
        IntegerType,
        NoneType,
        NumberType,
        ParserInfoType,
        StringType,
    )


# ----------------------------------------------------------------------
class FuncOrTypeExpression(GrammarPhrase):
    PHRASE_NAME                             = "Func or Type Expression"

    MINILANGUAGE_TYPE_MAP                   = {
        "Bool" : BooleanType(),
        "Char" : CharacterType(),
        "Int" : IntegerType(),
        "None" : NoneType(),
        "Num" : NumberType(),
        "Str" : StringType(),
    }

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncOrTypeExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # <name>
                CommonTokens.FuncOrTypeName,

                # <template_arguments>?
                OptionalPhraseItem(TemplateArgumentsFragment.Create()),

                # <constraint_arguments>?
                OptionalPhraseItem(ConstraintArgumentsFragment.Create()),

                # <mutability_modifier>?
                OptionalPhraseItem(
                    name="Mutability Modifier",
                    item=MutabilityModifier.CreatePhraseItem(),
                ),
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
            assert len(nodes) == 4

            # <name>
            name_leaf = cast(AST.Leaf, nodes[0])
            name_info = CommonTokens.FuncOrTypeName.Extract(name_leaf)  # type: ignore

            if CommonTokens.FuncOrTypeName.IsCompileTime(name_info):  # type: ignore
                # If here, the function could be invoked during Configuration or TypeCustomization.
                # Pick the smallest of the two.
                assert ParserInfoType.Configuration.value < ParserInfoType.TypeCustomization.value
                parser_info_type = ParserInfoType.Configuration

                name_info = CustomType(name_info)

            else:
                potential_mini_language_type = cls.MINILANGUAGE_TYPE_MAP.get(name_info, None)
                if potential_mini_language_type is not None:
                    name_info = potential_mini_language_type
                    parser_info_type = ParserInfoType.Configuration

                else:
                    name_info = CustomType(name_info)
                    parser_info_type = ParserInfoType.Unknown

            # <template_arguments>?
            template_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if template_arguments_node is None:
                template_arguments_info = None
            else:
                template_arguments_info = TemplateArgumentsFragment.Extract(template_arguments_node)

            # <constraint_arguments>?
            constraint_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
            if constraint_arguments_node is None:
                constraint_arguments_info = None
            else:
                constraint_arguments_info = ConstraintArgumentsFragment.Extract(constraint_arguments_node)

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[3])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            return FuncOrTypeExpressionParserInfo.Create(
                parser_info_type,
                CreateRegions(node, name_leaf, mutability_modifier_node),
                name_info,
                template_arguments_info,
                constraint_arguments_info,
                mutability_modifier_info,
            )

        # ----------------------------------------------------------------------

        return Callback
