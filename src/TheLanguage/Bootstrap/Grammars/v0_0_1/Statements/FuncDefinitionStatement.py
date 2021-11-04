import itertools
import os

from typing import Callable, cast, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassStatement import ClassStatement

    from ..Common import AttributePhraseItem
    from ..Common import CapturedVariablesPhraseItem
    from ..Common import ClassModifier
    from ..Common import MethodModifier
    from ..Common import FunctionParametersPhraseItem
    from ..Common import StatementsPhraseItem
    from ..Common import TemplateParametersPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...Error import Error
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        ExtractTokenSpan,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.FuncDefinitionStatementParserInfo import (
        FuncDefinitionStatementParserInfo,
        OperatorType,
        TypeParserInfo,
    )

    # Convenience imports
    # <<unused-import> pylint: disable=W0611
    from ..Common.Impl.ParametersPhraseItemImpl import (
        NewStyleParameterGroupDuplicateError,
        TraditionalDelimiterOrderError,
        TraditionalDelimiterDuplicatePositionalError,
        TraditionalDelimiterDuplicateKeywordError,
        TraditionalDelimiterPositionalError,
        TraditionalDelimiterKeywordError,
        RequiredParameterAfterDefaultError,
    )

    # <<unused-import> pylint: disable=W0611
    from ..Common.StatementsPhraseItem import (
        InvalidDocstringError,
        MultipleDocstringsError,
        MisplacedDocstringError,
        StatementsRequiredError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorNameError(Error):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Name}' is not a valid operator name.",
    )


# ----------------------------------------------------------------------
class FuncDefinitionStatement(GrammarPhrase):
    """\
    Defines a function (or method when used within a class statement)
    """

    PHRASE_NAME                             = "Func Definition Statement"

    # TODO: Add Captures
    # TODO: Add Templates

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    # TODO: Decorate these values with 'Async', '...', and '?'
    OperatorNameMap                         = {
        # Compile-Time
        OperatorType.EvalTemplates: "__EvalTemplates!__",
        OperatorType.EvalConstraints: "__EvalConstraints!__",
        OperatorType.IsConvertibleTo: "__IsConvertibleTo!__",

        # Foundational
        OperatorType.ToBool: "__ToBool__",
        OperatorType.ToString: "__ToString?__",
        OperatorType.Repr: "__Repr?__",
        OperatorType.Clone: "__Clone?__",
        OperatorType.Serialize: "__Serialize?__",
        OperatorType.Deserialize: "__Deserialize?__",

        # Instance Instantiation
        OperatorType.Init: "__Init__",
        OperatorType.PostInit: "__PostInit__",

        # Dynamic
        OperatorType.GetAttribute: "__GetAttribute__",
        OperatorType.Call: "__Call__",
        OperatorType.Cast: "__Cast__",
        OperatorType.Index: "__Index__",

        # Container
        OperatorType.Contains: "__Contains__",
        OperatorType.Length: "__Length__",
        OperatorType.Iter: "__Iter__",
        OperatorType.AtEnd: "__AtEnd__",

        # Comparison
        OperatorType.Compare: "__Compare__",
        OperatorType.Equal: "__Equal__",
        OperatorType.NotEqual: "__NotEqual__",
        OperatorType.Less: "__Less__",
        OperatorType.LessOrEqual: "__LessOrEqual__",
        OperatorType.Greater: "__Greater__",
        OperatorType.GreaterOrEqual: "__GreaterOrEqual__",

        # Logical
        OperatorType.And: "__And__",
        OperatorType.Or: "__Or__",
        OperatorType.Not: "__Not__",

        # Mathematical
        OperatorType.Add: "__Add?__",
        OperatorType.Subtract: "__Subtract__",
        OperatorType.Multiply: "__Multiply__",
        OperatorType.Power: "__Power__",
        OperatorType.Divide: "__Divide__",
        OperatorType.DivideFloor: "__DivideFloor__",
        OperatorType.Modulo: "__Modulo__",
        OperatorType.Positive: "__Positive__",
        OperatorType.Negative: "__Negative__",

        OperatorType.AddInplace: "__AddInplace?__",
        OperatorType.SubtractInplace: "__SubtractInplace__",
        OperatorType.MultiplyInplace: "__MultiplyInplace__",
        OperatorType.PowerInplace: "__PowerInplace__",
        OperatorType.DivideInplace: "__DivideInplace__",
        OperatorType.DivideFloorInplace: "__DivideFloorInplace__",
        OperatorType.ModuloInplace: "__ModuloInplace__",

        # Bit Manipulation
        OperatorType.BitShiftLeft: "__BitShiftLeft__",
        OperatorType.BitShiftRight: "__BitShiftRight__",
        OperatorType.BitAnd: "__BitAnd__",
        OperatorType.BitOr: "__BitOr__",
        OperatorType.BitXor: "__BitXor__",
        OperatorType.BitFlip: "__BitFlip__",

        OperatorType.BitShiftLeftInplace: "__BitShiftLeftInplace__",
        OperatorType.BitShiftRightInplace: "__BitShiftRightInplace__",
        OperatorType.BitAndInplace: "__BitAndInplace__",
        OperatorType.BitOrInplace: "__BitOrInplace__",
        OperatorType.BitXorInplace: "__BitXorInplace__",
    }

    NameOperatorMap                         = {
        v: k for k, v in OperatorNameMap.items()
    }

    assert len(OperatorNameMap) == len(OperatorType)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncDefinitionStatement, self).__init__(
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

                    # <method_type_modifier>?
                    OptionalPhraseItem.Create(
                        name="Method Type",
                        item=MethodModifier.CreatePhraseItem(),
                    ),

                    # <class_modifier>?
                    OptionalPhraseItem.Create(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <generic_name>
                    CommonTokens.GenericUpperName,

                    # Begin: Template Parameters, Captures
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <template_parameters>?
                    OptionalPhraseItem.Create(
                        name="Template Parameters",
                        item=TemplateParametersPhraseItem.Create(),
                    ),

                    # <captured_arguments>?
                    OptionalPhraseItem.Create(
                        name="Captured Variables",
                        item=CapturedVariablesPhraseItem.Create(),
                    ),

                    # End: Template Parameters, Captures
                    CommonTokens.PopIgnoreWhitespaceControl,

                    # <parameters>
                    FunctionParametersPhraseItem.Create(),

                    # Statements or None
                    (
                        StatementsPhraseItem.Create(),

                        # Newline (no content)
                        CommonTokens.Newline,
                    ),
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
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 12

            # <attribute>*
            attributes_node = cast(Optional[AST.Node], nodes[0])

            attribute_data: List[List[AttributePhraseItem.AttributeData]] = []

            for attribute_node in cast(List[AST.Node], ExtractRepeat(attributes_node)):
                attribute_data.append(AttributePhraseItem.ExtractLexerData(cast(AST.Node, attribute_node)))

            # Leverage attribute data
            is_deferred_node = None
            is_deferred_info = None

            is_generator_node = None
            is_generator_info = None

            is_reentrant_node = None
            is_reentrant_info = None

            is_scoped_node = None
            is_scoped_info = None

            is_async_node = None
            is_async_info = None

            for attribute in itertools.chain(*attribute_data):
                if attribute.Name == "Deferred":
                    is_deferred_node = attribute.NameLeaf
                    is_deferred_info = True

                elif attribute.Name == "Generator":
                    is_generator_node = attribute.NameLeaf
                    is_generator_info = True

                elif attribute.Name == "Reentrant":
                    is_reentrant_node = attribute.NameLeaf
                    is_reentrant_info = True

                elif attribute.Name == "Scoped":
                    is_scoped_node = attribute.NameLeaf
                    is_scoped_info = True

                elif attribute.Name == "Async":
                    is_async_node = attribute.NameLeaf
                    is_async_info = True

                else:
                    raise Exception("BugBug: {} is not a valid attribute".format(attribute.Name))

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))

            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <method_type_modifier>?
            method_type_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))

            if method_type_modifier_node is None:
                method_type_modifier_info = None
            else:
                method_type_modifier_info = MethodModifier.Extract(method_type_modifier_node)

            # <class_modifier>?
            class_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[3])))

            if class_modifier_node is None:
                class_modifier_info = None
            else:
                class_modifier_info = ClassModifier.Extract(class_modifier_node)

            # <type>
            return_type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[4])))
            return_type_info = cast(TypeParserInfo, GetParserInfo(return_type_node))

            # <generic_name>
            func_name_leaf = cast(AST.Leaf, nodes[5])
            func_name_info = cast(str, ExtractToken(func_name_leaf, group_dict_name="value"))

            func_name_match = CommonTokens.FuncNameRegex.match(func_name_info)
            if not func_name_match:
                raise CommonTokens.InvalidTokenError.FromNode(func_name_leaf, func_name_info, "function")

            is_exceptional_region = ExtractTokenSpan(func_name_leaf, "exceptional_suffix", func_name_match)
            is_exceptional_info = None if is_exceptional_region is None else True

            is_compile_time_region = ExtractTokenSpan(func_name_leaf, "compile_time_suffix", func_name_match)
            is_compile_time_info = None if is_compile_time_region is None else True

            if is_exceptional_info and is_compile_time_info:
                raise Exception("BugBug - invalid function name (1)")

            if func_name_info.startswith("__") or func_name_info.endswith("__"):
                operator_name = cls.NameOperatorMap.get(func_name_info, None)
                if operator_name is None:
                    raise InvalidOperatorNameError.FromNode(func_name_leaf, func_name_info)

                func_name_info = operator_name
            elif is_compile_time_info:
                raise Exception("BugBug - invalid function name (2)")

            # <template_parameters>?
            template_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))
            if template_parameters_node is None:
                template_parameters_info = None
            else:
                template_parameters_info = TemplateParametersPhraseItem.ExtractParserInfo(template_parameters_node)

            # <captured_arguments>?
            captured_variables_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[8])))
            if captured_variables_node is None:
                captured_variables_info = None
            else:
                captured_variables_info = CapturedVariablesPhraseItem.ExtractParserInfo(captured_variables_node)

            # <parameters>
            parameters_node = cast(AST.Node, nodes[10])
            parameters_info = FunctionParametersPhraseItem.ExtractParserInfo(parameters_node)

            # Statements Or None
            statements_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[11])))

            if isinstance(statements_node, AST.Leaf):
                statements_node = None
                statements_info = None

                docstring_leaf = None
                docstring_info = None
            else:
                statements_info, docstring_info = StatementsPhraseItem.ExtractParserInfoWithDocstrings(statements_node)

                if docstring_info is None:
                    docstring_leaf = None
                else:
                    docstring_info, docstring_leaf = docstring_info

                    if not statements_info:
                        statements_info = None
                        statements_node = None

            return FuncDefinitionStatementParserInfo(
                CreateParserRegions(
                    node,
                    visibility_node,
                    method_type_modifier_node,
                    class_modifier_node,
                    return_type_node,
                    func_name_leaf,
                    template_parameters_node,
                    captured_variables_node,
                    parameters_node,
                    statements_node,
                    docstring_leaf,
                    is_deferred_node,
                    is_generator_node,
                    is_reentrant_node,
                    is_exceptional_region,
                    is_scoped_node,
                    is_async_node,
                ), # type: ignore
                ClassStatement.GetContainingClassParserInfo(node, cls.PHRASE_NAME),  # type: ignore
                visibility_info,  # type: ignore
                method_type_modifier_info,  # type: ignore
                class_modifier_info,  # type: ignore
                return_type_info,
                func_name_info,
                template_parameters_info,
                captured_variables_info,
                parameters_info,
                statements_info,
                docstring_info,
                is_deferred_info,
                is_generator_info,
                is_reentrant_info,
                is_exceptional_info,
                is_scoped_info,
                is_async_info,
            )

        # ----------------------------------------------------------------------

        return Impl
