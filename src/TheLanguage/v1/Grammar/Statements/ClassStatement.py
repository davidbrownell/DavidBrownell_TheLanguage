# ----------------------------------------------------------------------
# |
# |  ClassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 09:20:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassStatement object"""

import itertools
import os

from enum import auto, Enum
from typing import cast, Dict, List, Optional, Tuple, Type

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import StatementsFragment
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ..Common.Impl import ModifierImpl

    from ..Types.StandardType import StandardType

    from ...Common.Region import Region

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ...Parser.Error import CreateError, Error, ErrorException
    from ...Parser.Parser import CreateRegion, CreateRegions
    from ...Parser.Common.ClassModifier import ClassModifier

    from ...Parser.Statements import ClassStatement as ParserClassStatementModule

    from ...Parser.Statements.ClassCapabilities.ClassCapabilities import ClassCapabilities
    from ...Parser.Statements.ClassCapabilities.ConceptCapabilities import ConceptCapabilities
    from ...Parser.Statements.ClassCapabilities.InterfaceCapabilities import InterfaceCapabilities
    from ...Parser.Statements.ClassCapabilities.MixinCapabilities import MixinCapabilities
    from ...Parser.Statements.ClassCapabilities.StandardCapabilities import StandardCapabilities
    from ...Parser.Statements.ClassCapabilities.StructCapabilities import StructCapabilities


# ----------------------------------------------------------------------
DuplicateBaseTypeError                      = CreateError(
    "The base type indicator '{type}' may only appear once.",
    type=str,
    prev_region=Region,
)


# ----------------------------------------------------------------------
class ClassType(Enum):
    class_value                             = "class"
    concept_value                           = "concept"
    exception_value                         = "exception"
    interface_value                         = "interface"
    mixin_value                             = "mixin"
    struct_value                            = "struct"


# ----------------------------------------------------------------------
class DependencyType(Enum):
    extends                                 = auto()
    implements                              = auto()
    uses                                    = auto()


# ----------------------------------------------------------------------
class ClassStatement(GrammarPhrase):
    PHRASE_NAME                             = "Class Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        self._standard_type                 = StandardType()

        dependency_element = PhraseItem(
            name="Class Dependency Element",
            item=[
                # <visibility>?
                OptionalPhraseItem(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                # <standard_type>
                self._standard_type.phrase,
            ],
        )

        dependency_elements = PhraseItem(
            name="Class Dependency Elements",
            item=[
                # <dependency_element>
                dependency_element,

                # (',' <dependency_element>)*
                ZeroOrMorePhraseItem(
                    name="Comma and Element",
                    item=[
                        ",",
                        dependency_element,
                    ],
                ),

                # ','?
                OptionalPhraseItem(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        )

        super(ClassStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # TODO: <attributes>?

                    # <visibility>?
                    OptionalPhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <class_modifier>?
                    OptionalPhraseItem(
                        name="Class Modifier",
                        item=CreateClassModifierPhraseItem(),
                    ),

                    # <class_type>
                    CreateClassTypePhraseItem(),

                    # <type_name>
                    CommonTokens.RuntimeTypeName,

                    # Template Parameters, Constraints, Dependencies
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # TODO: <template_parameters>?

                    # TODO: <constraints>?

                    # <dependencies>?
                    ZeroOrMorePhraseItem(
                        name="Dependencies",
                        item=[
                            # <dependency_type>
                            CreateDependencyTypePhraseItem(),

                            # Items
                            (
                                # '(' <dependency_elements> ')'
                                PhraseItem(
                                    name="Grouped",
                                    item=[
                                        "(",
                                        CommonTokens.PushIgnoreWhitespaceControl,

                                        dependency_elements,

                                        CommonTokens.PopIgnoreWhitespaceControl,
                                        ")",
                                    ],
                                ),

                                # <dependency_elements>
                                dependency_elements,
                            ),
                        ],
                    ),

                    CommonTokens.PopIgnoreWhitespaceControl,

                    # <statements>
                    StatementsFragment.Create(),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def GetParentClassCapabilities(
        cls,
        node: AST.Node,
        function_defintion_statement: Type[GrammarPhrase],
    ) -> Optional[ClassCapabilities]:

        walking_node = node.parent

        while walking_node is not None:
            if walking_node.type is not None:
                if walking_node.type.name == cls.PHRASE_NAME:
                    return getattr(walking_node, cls._CLASS_CAPABILITIES_ATTRIBUTE_NAME)

                # Do not attempt to get class info if it means walking beyond a function
                if isinstance(node.type, function_defintion_statement):
                    break

            walking_node = walking_node.parent

        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractParserPhrase(
        self,
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserPhraseReturnType:

        # Construct the ParserPhrase in 2 passes. The first will contain information that contained
        # statements need to create their parser phrases. The second will collect that information
        # and create the class statement parser phrase.
        nodes = ExtractSequence(node)
        assert len(nodes) == 8 # TODO: 11

        errors: List[Error] = []

        # Detect early errors and get information necessary for child statements; the rest will be
        # done later.

        # <class_type>
        class_type_node = cast(AST.Node, nodes[2])
        class_type_info = ExtractClassType(class_type_node)

        if class_type_info ==  ClassType.class_value:
            class_capabilities = StandardCapabilities
        elif class_type_info == ClassType.concept_value:
            class_capabilities = ConceptCapabilities
        # TODO: elif class_type_info == ClassType.exception_value:
        # TODO:     class_capabilities = ExceptionCapabilities
        elif class_type_info == ClassType.interface_value:
            class_capabilities = InterfaceCapabilities
        elif class_type_info == ClassType.mixin_value:
            class_capabilities = MixinCapabilities
        elif class_type_info == ClassType.struct_value:
            class_capabilities = StructCapabilities
        else:
            assert False, class_type_info  # pragma: no cover

        # <dependencies>?
        all_dependency_nodes: Dict[DependencyType, Tuple[AST.Node, AST.Node]] = {}

        all_dependencies_node = cast(AST.Node, nodes[5])

        for dependency_node in cast(List[AST.Node], ExtractRepeat(all_dependencies_node)):
            dependency_nodes = ExtractSequence(dependency_node)
            assert len(dependency_nodes) == 2

            dependency_type_node = cast(AST.Node, dependency_nodes[0])
            dependencies_node = cast(AST.Node, dependency_nodes[1])

            dependency_type_info = ExtractDependencyType(dependency_type_node)

            prev_dependencies_node = all_dependency_nodes.get(dependency_type_info, None)
            if prev_dependencies_node is not None:
                errors.append(
                    DuplicateBaseTypeError.Create(
                        region=CreateRegion(dependency_type_node),
                        type=dependency_type_info.value,
                        prev_region=CreateRegion(prev_dependencies_node[0]),
                    ),
                )

            all_dependency_nodes[dependency_type_info] = (dependency_type_node, dependencies_node)

        # This information will be used when children call `GetParentClassCapabilities`
        object.__setattr__(node, self.__class__._CLASS_CAPABILITIES_ATTRIBUTE_NAME, class_capabilities)

        if errors:
            return errors

        # ----------------------------------------------------------------------
        def Callback():
            # TODO: <attributes>?

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <class_modifier>?
            class_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[1])))
            if class_modifier_node is None:
                class_modifier_info = None
            else:
                class_modifier_info = ExtractClassModifier(class_modifier_node)

            # <type_name>
            type_name_node = cast(AST.Leaf, nodes[3])
            type_name_info = ExtractToken(type_name_node)

            # TODO: <template_parameters>?
            # TODO: <constraints>?

            # <dependencies>?
            all_dependencies_info: Dict[DependencyType, Tuple[AST.Node, List[ParserClassStatementModule.ClassStatementDependency]]] = {}

            for dependency_type, (_, these_dependencies_node) in all_dependency_nodes.items():
                these_dependency_nodes = cast(AST.Node, ExtractOr(these_dependencies_node))

                assert these_dependency_nodes.type is not None
                if these_dependency_nodes.type.name == "Grouped":
                    grouped_nodes = ExtractSequence(these_dependency_nodes)
                    assert len(grouped_nodes) == 3

                    these_dependency_nodes = cast(AST.Node, grouped_nodes[2])

                these_dependency_nodes = ExtractSequence(these_dependency_nodes)
                assert len(these_dependency_nodes) == 3

                these_dependencies: List[ParserClassStatementModule.ClassStatementDependency] = []

                for this_dependency_node in itertools.chain(
                    [these_dependency_nodes[0]],
                    (
                        ExtractSequence(delimited_node)[1]
                        for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(Optional[AST.Node], these_dependency_nodes[1])))
                    ),
                ):
                    this_dependency_nodes = ExtractSequence(cast(AST.Node, this_dependency_node))
                    assert len(this_dependency_nodes) == 2

                    # <visibility>?
                    this_visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, this_dependency_nodes[0])))
                    if this_visibility_node is None:
                        this_visibility_info = None
                    else:
                        this_visibility_info = VisibilityModifier.Extract(this_visibility_node)

                    # <standard_type>
                    standard_type_node = cast(AST.Node, this_dependency_nodes[1])
                    standard_type_info = self._standard_type.ExtractParserPhrase(standard_type_node)

                    # Add it
                    these_dependencies.append(
                        ParserClassStatementModule.ClassStatementDependency.Create(
                            CreateRegions(this_dependency_node, this_visibility_node, standard_type_node),
                            this_visibility_info,
                            standard_type_info,
                        ),
                    )

                all_dependencies_info[dependency_type] = (dependencies_node, these_dependencies)

            # <statements>
            statements_node = cast(AST.Node, nodes[7])

            statements_info, docstring_info = StatementsFragment.Extract(statements_node)

            # Commit
            return ParserClassStatementModule.ClassStatement.Create(
                CreateRegions(
                    node,
                    visibility_node,
                    class_modifier_node,
                    type_name_node,
                    docstring_info[0] if docstring_info else None,
                    all_dependencies_info.get(DependencyType.extends, [None])[0],
                    all_dependencies_info.get(DependencyType.implements, [None])[0],
                    all_dependencies_info.get(DependencyType.uses, [None])[0],
                    statements_node,
                ),
                class_capabilities,
                visibility_info,
                class_modifier_info,
                type_name_info,
                docstring_info[1] if docstring_info else None,
                all_dependencies_info.get(DependencyType.extends, [None, None])[1],
                all_dependencies_info.get(DependencyType.implements, [None, None])[1],
                all_dependencies_info.get(DependencyType.uses, [None, None])[1],
                statements_info,
            )

        # ----------------------------------------------------------------------

        return Callback  # type: ignore

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _CLASS_CAPABILITIES_ATTRIBUTE_NAME      = "_class_capabilities"


# ----------------------------------------------------------------------
CreateClassModifierPhraseItem               = ModifierImpl.StandardCreatePhraseItemFuncFactory(ClassModifier)
ExtractClassModifier                        = ModifierImpl.StandardExtractFuncFactory(ClassModifier)

CreateClassTypePhraseItem                   = ModifierImpl.ByValueCreatePhraseItemFuncFactory(ClassType)
ExtractClassType                            = ModifierImpl.ByValueExtractFuncFactory(ClassType)

CreateDependencyTypePhraseItem              = ModifierImpl.StandardCreatePhraseItemFuncFactory(DependencyType)
ExtractDependencyType                       = ModifierImpl.StandardExtractFuncFactory(DependencyType)
