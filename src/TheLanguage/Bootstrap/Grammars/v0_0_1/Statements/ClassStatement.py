import itertools
import os

from enum import auto, Enum
from typing import Callable, cast, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import AttributePhraseItem
    from ..Common import ClassModifier
    from ..Common import ConstraintArgumentsPhraseItem
    from ..Common import ConstraintParametersPhraseItem
    from ..Common import TemplateArgumentsPhraseItem
    from ..Common import TemplateParametersPhraseItem
    from ..Common import StatementsPhraseItem

    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ..Common.Impl import ModifierImpl

    from ...Error import Error
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, CreateParserRegion, GetParserInfo

    from ....Parser.Statements.ClassStatementParserInfo import (
        ClassStatementDependencyParserInfo,
        ClassStatementParserInfo,
        ClassType,
    )

    # Convenience imports
    # <<unused-import> pylint: disable=W0611
    from ..Common.StatementsPhraseItem import (
        InvalidDocstringError,
        MultipleDocstringsError,
        MisplacedDocstringError,
        StatementsRequiredError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleBasesError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Classes can have only one base class; consider using interfaces, mixins, and traits instead.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DuplicateBaseTypeError(Error):
    Type: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The base type indicator '{Type}' may appear only once.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassStatementsRequiredError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Classes must have at least one statement.",
    )


# ----------------------------------------------------------------------
class ClassStatement(GrammarPhrase):
    PHRASE_NAME                             = "Class Statement"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class DependencyIndicator(Enum):
        based                               = auto()
        extends                             = auto()
        implements                          = auto()
        uses                                = auto()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        dependency_item = PhraseItem.Create(
            name="Dependency Item",
            item=[
                # <visibility>?
                OptionalPhraseItem.Create(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                # <generic_name>
                CommonTokens.GenericUpperName,

                # <template_arguments>?
                OptionalPhraseItem.Create(
                    name="Template Arguments",
                    item=TemplateArgumentsPhraseItem.Create(),
                ),

                # <constraint_arguments>?
                OptionalPhraseItem.Create(
                    name="Constraint Arguments",
                    item=ConstraintArgumentsPhraseItem.Create(),
                ),
            ],
        )

        # <dependency_item> (',' <dependency_item>)* ','?
        dependency_items = PhraseItem.Create(
            name="Dependency Items",
            item=[
                # <dependency_item>
                dependency_item,

                # (',' <dependency_item>)*
                ZeroOrMorePhraseItem.Create(
                    name="Comma and Dependency",
                    item=[
                        ",",
                        dependency_item,
                    ],
                ),

                # ','?
                OptionalPhraseItem.Create(
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
                    # <attribute>*
                    ZeroOrMorePhraseItem.Create(
                        name="Attributes",
                        item=AttributePhraseItem.Create(),
                    ),

                    # <visibility>?
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <class_modifier>?
                    OptionalPhraseItem.Create(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                    ),

                    # <class_type>
                    PhraseItem.Create(
                        name="Class Type",
                        item=self.__class__._CreateClassTypePhraseItem(),
                    ),

                    # <name>
                    CommonTokens.GenericUpperName,

                    # Begin: Template Parameters, Constraint Parameters, Dependencies
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

                    # <dependencies>*
                    ZeroOrMorePhraseItem.Create(
                        name="Dependencies",
                        item=[
                            # ('based', 'extends', 'implements', 'uses')
                            self.__class__.DependencyIndicator.CreatePhraseItem(),  # type: ignore

                            # Items
                            PhraseItem.Create(
                                item=(
                                    # '(' <dependency_items> ')'
                                    PhraseItem.Create(
                                        name="Grouped",
                                        item=[
                                            "(",
                                            CommonTokens.PushIgnoreWhitespaceControl,

                                            dependency_items,

                                            CommonTokens.PopIgnoreWhitespaceControl,
                                            ")",
                                        ],
                                    ),

                                    # <dependency_items>
                                    dependency_items,
                                ),

                                # Use the order to disambiguate between group clauses and tuples
                                ambiguities_resolved_by_order=True,
                            ),
                        ],
                    ),

                    # End: Template Parameters, Constraint Parameters, Dependencies
                    CommonTokens.PopIgnoreWhitespaceControl,

                    # <statement>+
                    StatementsPhraseItem.Create(),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # Construct the class parser info in 2 phases. The first will contain information that
        # contained statements need to create their parser info. The second will collect the parser
        # info generated by those contained statements.

        nodes = ExtractSequence(node)
        assert len(nodes) == 11

        # <attribute>*
        attributes_node = cast(Optional[AST.Node], nodes[0])

        attribute_data: List[List[AttributePhraseItem.AttributeData]] = []

        for attribute_node in cast(List[AST.Node], ExtractRepeat(attributes_node)):
            attribute_data.append(AttributePhraseItem.ExtractLexerData(cast(AST.Node, attribute_node)))

        # TODO: Leverage attribute data

        # <visibility>?
        visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[1])))
        if visibility_node is None:
            visibility_info = None
        else:
            visibility_info = VisibilityModifier.Extract(visibility_node)

        # <class_modifier>?
        class_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[2])))
        if class_modifier_node is None:
            class_modifier_info = None
        else:
            class_modifier_info = ClassModifier.Extract(class_modifier_node)

        # <class_type>
        class_type_node = cast(AST.Node, nodes[3])
        class_type_info = cls._ExtractClassType(class_type_node)

        # <name>
        name_leaf = cast(AST.Leaf, nodes[4])
        name_info = cast(str, ExtractToken(name_leaf))

        if not CommonTokens.TypeNameRegex.match(name_info):
            raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "type")

        # <template_parameters>?
        template_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[6])))
        if template_parameters_node is None:
            template_parameters_info = None
        else:
            template_parameters_info = TemplateParametersPhraseItem.ExtractParserInfo(template_parameters_node)

        # <constraint_parameters>?
        constraint_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))
        if constraint_parameters_node is None:
            constraint_parameters_info = None
        else:
            constraint_parameters_info = ConstraintParametersPhraseItem.ExtractParserInfo(constraint_parameters_node)

        # <dependencies>*
        dependencies_parser_infos: Dict[
            cls.DependencyIndicator,
            Tuple[AST.Node, List[ClassStatementDependencyParserInfo]]
        ] = {}

        dependencies_node = cast(AST.Node, nodes[8])

        for dependency_node in cast(List[AST.Node], ExtractRepeat(dependencies_node)):
            dependency_nodes = ExtractSequence(dependency_node)
            assert len(dependency_nodes) == 2

            # <dependency_indicator>
            dependency_indicator_node = cast(AST.Node, dependency_nodes[0])
            dependency_indicator = cls.DependencyIndicator.Extract(dependency_indicator_node)  # type: ignore

            if dependency_indicator in dependencies_parser_infos:
                DuplicateBaseTypeError.FromNode(dependency_indicator_node, dependency_indicator.name)

            # Items
            items_node = cast(AST.Node, ExtractOr(cast(AST.Node, dependency_nodes[1])))

            assert items_node.Type is not None
            if items_node.Type.Name == "Grouped":
                items_nodes = ExtractSequence(items_node)
                assert len(items_nodes) == 5

                items_node = cast(AST.Node, items_nodes[2])

            items_nodes = ExtractSequence(items_node)
            assert len(items_nodes) == 3

            dependency_parser_infos: List[ClassStatementDependencyParserInfo] = []

            for item_node in itertools.chain(
                [items_nodes[0]],
                (
                    ExtractSequence(delimited_node)[1]
                    for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, items_nodes[1])))
                ),
            ):
                item_nodes = ExtractSequence(cast(AST.Node, item_node))
                assert len(item_nodes) == 4

                # <visibility>?
                item_visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, item_nodes[0])))
                if item_visibility_node is None:
                    item_visibility_info = None
                else:
                    item_visibility_info = VisibilityModifier.Extract(item_visibility_node)

                # <generic_name>
                item_name_leaf = cast(AST.Leaf, item_nodes[1])
                item_name_info = cast(str, ExtractToken(item_name_leaf))

                if not CommonTokens.TypeNameRegex.match(item_name_info):
                    raise CommonTokens.InvalidTokenError.FromNode(item_name_leaf, item_name_info, "type")

                # <template_arguments>?
                item_template_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, item_nodes[2])))
                if item_template_arguments_node is None:
                    item_template_arguments_info = None
                else:
                    item_template_arguments_info = TemplateArgumentsPhraseItem.ExtractParserInfo(item_template_arguments_node)

                # <constraint_arguments>?
                item_constraints_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, item_nodes[3])))
                if item_constraints_arguments_node is None:
                    item_constraints_arguments_info = None
                else:
                    item_constraints_arguments_info = ConstraintArgumentsPhraseItem.ExtractParserInfo(item_constraints_arguments_node)

                dependency_parser_infos.append(
                    ClassStatementDependencyParserInfo(
                        CreateParserRegions(
                            item_node,
                            item_visibility_node,
                            item_name_leaf,
                            item_template_arguments_node,
                            item_constraints_arguments_node,
                        ),  # type: ignore
                        item_visibility_info,  # type: ignore
                        item_name_info,
                        item_template_arguments_info,
                        item_constraints_arguments_info,
                    )
                )

            assert dependencies_parser_infos
            dependencies_parser_infos[dependency_indicator] = (dependency_node, dependency_parser_infos)

        # <statement>+
        statements_node = cast(AST.Node, nodes[10])

        # Create Phase 1 Info
        parser_info = ClassStatementParserInfo(
            CreateParserRegions(
                node,
                visibility_node,
                class_modifier_node,
                class_type_node,
                name_leaf,
                template_parameters_node,
                constraint_parameters_node,
                dependencies_parser_infos.get(cls.DependencyIndicator.based, (None,))[0],
                dependencies_parser_infos.get(cls.DependencyIndicator.extends, (None,))[0],
                dependencies_parser_infos.get(cls.DependencyIndicator.implements, (None,))[0],
                dependencies_parser_infos.get(cls.DependencyIndicator.uses, (None,))[0],
                statements_node,
                None, # Documentation
            ),  # type: ignore
            visibility_info,  # type: ignore
            class_modifier_info,  # type: ignore
            class_type_info,
            name_info,
            template_parameters_info,
            constraint_parameters_info,
            dependencies_parser_infos.get(cls.DependencyIndicator.based, (None, None))[1],  # type: ignore
            dependencies_parser_infos.get(cls.DependencyIndicator.extends, (None, None))[1],
            dependencies_parser_infos.get(cls.DependencyIndicator.implements, (None, None))[1],
            dependencies_parser_infos.get(cls.DependencyIndicator.uses, (None, None))[1],
        )

        # ----------------------------------------------------------------------
        def Phase2Construct():
            # <statement>+
            (
                statement_info,
                docstring_info,
            ) = StatementsPhraseItem.ExtractParserInfoWithDocstrings(statements_node)

            if docstring_info is not None:
                if not statement_info:
                    raise ClassStatementsRequiredError.FromNode(statements_node)

                docstring_info = (
                    docstring_info[0],
                    CreateParserRegion(docstring_info[1]),
                )

            parser_info.FinalConstruct(statement_info, docstring_info)

            return parser_info

        # ----------------------------------------------------------------------

        return (parser_info, Phase2Construct)

    # ----------------------------------------------------------------------
    @classmethod
    def GetContainingClassParserInfo(
        cls,
        child_node: AST.Node,
        # Taking this as a parameter to avoid circular dependencies, as
        # FuncDefinitionStatement.py imports this file.
        func_definition_statement_phrase_name: str,
    ) -> Optional[ClassStatementParserInfo]:
        """Returns the ClassStatementParserInfo for the class that contains the given node (if any)"""

        node = child_node.Parent

        while node is not None:
            if node.Type is not None:
                if node.Type.Name == cls.PHRASE_NAME:
                    return cast(ClassStatementParserInfo, GetParserInfo(node))

                if node.Type.Name == func_definition_statement_phrase_name:
                    break

            node = node.Parent

        return None

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    _CreateClassTypePhraseItem              = staticmethod(ModifierImpl.ByValueCreatePhraseItemFuncFactory(ClassType))
    _ExtractClassType                       = staticmethod(ModifierImpl.ByValueExtractFuncFactory(ClassType))


# ----------------------------------------------------------------------
ClassStatement.DependencyIndicator.CreatePhraseItem     = staticmethod(ModifierImpl.StandardCreatePhraseItemFuncFactory(ClassStatement.DependencyIndicator))  # type: ignore
ClassStatement.DependencyIndicator.Extract              = staticmethod(ModifierImpl.StandardExtractFuncFactory(ClassStatement.DependencyIndicator))  # type: ignore
