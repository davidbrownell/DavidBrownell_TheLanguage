# ----------------------------------------------------------------------
# |
# |  StatementsMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 09:11:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementsMixin object"""

import os
import textwrap

from contextlib import contextmanager
from typing import cast, List

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ....Parser.ParserInfos.ParserInfo import ParserInfo

    from ....Parser.ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ....Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ....Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ....Parser.ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ....Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo, IfStatementElseClauseParserInfo
    from ....Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo
    from ....Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
    from ....Parser.ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ....Parser.ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


# ----------------------------------------------------------------------
# pylint: disable=protected-access


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):
    """Implements functionality for ParserInfos/Statements"""

    # ----------------------------------------------------------------------
    # |  ClassAttributeStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassAttributeStatementParserInfo(
        self,
        parser_info: ClassAttributeStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo")

        class_capabilities = "{}Capabilities".format(parser_info.class_capabilities.name)

        self._imports.add(
            "from v1.Parser.ParserInfos.Statements.ClassCapabilities.{class_capabilities} import {class_capabilities}".format(
                class_capabilities=class_capabilities,
            ),
        )

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ClassAttributeStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {name_region}, {documentation_region}, {keyword_initialization_region}, {no_initialization_region}, {no_serialize_region}, {no_compare_region}, {is_override_region}],
                    class_capabilities={class_capabilities},
                    visibility_param={visibility},
                    type={type},
                    name={name},
                    documentation={documentation},
                    initialized_value={initialized_value},
                    keyword_initialization={keyword_initialization},
                    no_initialization={no_initialization},
                    no_serialize={no_serialize},
                    no_compare={no_compare},
                    is_override={is_override},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                name_region=self._ToString(parser_info.regions__.name),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                keyword_initialization_region=self._ToString(parser_info.regions__.keyword_initialization),
                no_initialization_region=self._ToString(parser_info.regions__.no_initialization),
                no_serialize_region=self._ToString(parser_info.regions__.no_serialize),
                no_compare_region=self._ToString(parser_info.regions__.no_compare),
                is_override_region=self._ToString(parser_info.regions__.is_override),
                class_capabilities=class_capabilities,
                visibility=self._ToString(parser_info.visibility),
                type=self._ToString(parser_info.type),
                name=self._ToString(parser_info.name),
                documentation=self._ToString(parser_info.documentation),
                initialized_value=self._ToString(parser_info.initialized_value),
                keyword_initialization=self._ToString(parser_info.keyword_initialization),
                no_initialization=self._ToString(parser_info.no_initialization),
                no_serialize=self._ToString(parser_info.no_serialize),
                no_compare=self._ToString(parser_info.no_compare),
                is_override=self._ToString(parser_info.is_override),
            ),
        )

    # ----------------------------------------------------------------------
    # |  ClassStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo")

        class_capabilities = "{}Capabilities".format(parser_info.class_capabilities.name)

        self._imports.add(
            "from v1.Parser.ParserInfos.Statements.ClassCapabilities.{class_capabilities} import {class_capabilities}".format(
                class_capabilities=class_capabilities,
            ),
        )

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ClassStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {class_modifier_region}, {name_region}, {documentation_region}, {extends_region}, {implements_region}, {uses_region}, {statements_region}, {constructor_visibility_region}, {is_abstract_region}, {is_final_region}],
                    class_capabilities={class_capabilities},
                    visibility_param={visibility},
                    class_modifier_param={class_modifier},
                    name={name},
                    documentation={documentation},
                    templates={templates},
                    constraints={constraints},
                    extends={extends},
                    implements={implements},
                    uses={uses},
                    statements={statements},
                    constructor_visibility_param={constructor_visibility},
                    is_abstract={is_abstract},
                    is_final={is_final},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                class_modifier_region=self._ToString(parser_info.regions__.class_modifier),
                name_region=self._ToString(parser_info.regions__.name),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                extends_region=self._ToString(parser_info.regions__.extends),
                implements_region=self._ToString(parser_info.regions__.implements),
                uses_region=self._ToString(parser_info.regions__.uses),
                statements_region=self._ToString(parser_info.regions__.statements),
                constructor_visibility_region=self._ToString(parser_info.regions__.constructor_visibility),
                is_abstract_region=self._ToString(parser_info.regions__.is_abstract),
                is_final_region=self._ToString(parser_info.regions__.is_final),
                class_capabilities=class_capabilities,
                visibility=self._ToString(parser_info.visibility),
                class_modifier=self._ToString(parser_info.class_modifier),
                name=self._ToString(parser_info.name),
                documentation=self._ToString(parser_info.documentation),
                templates=self._ToString(parser_info.templates),
                constraints=self._ToString(parser_info.constraints),
                extends=self._ToString(parser_info.extends),                # type: ignore
                implements=self._ToString(parser_info.implements),          # type: ignore
                uses=self._ToString(parser_info.uses),                      # type: ignore
                statements=self._ToString(parser_info.statements),          # type: ignore
                constructor_visibility=self._ToString(parser_info.constructor_visibility),
                is_abstract=self._ToString(parser_info.is_abstract),
                is_final=self._ToString(parser_info.is_final),
            ),
        )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementDependencyParserInfo(
        self,
        parser_info: ClassStatementDependencyParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementDependencyParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ClassStatementDependencyParserInfo.Create(
                    regions=[{self_region}, {visibility_region}],
                    visibility={visibility},
                    type={type},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                visibility=self._ToString(parser_info.visibility),
                type=self._ToString(parser_info.type),
            ),
        )

    # ----------------------------------------------------------------------
    # |  FuncDefinitionStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncDefinitionStatementParserInfo(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo, OperatorType as FuncDefinitionStatementParserInfoOperatorType")

        if parser_info.parent_class_capabilities is None:
            parent_class_capabilities = None
        else:
            parent_class_capabilities = "{}Capabilities".format(parser_info.parent_class_capabilities.name)

            self._imports.add(
                "from v1.Parser.ParserInfos.Statements.ClassCapabilities.{parent_class_capabilities} import {parent_class_capabilities}".format(
                    parent_class_capabilities=parent_class_capabilities,
                ),
            )

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncDefinitionStatementParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {parameters_region}, {visibility_region}, {mutability_region}, {method_modifier_region}, {name_region}, {documentation_region}, {captured_variables_region}, {statements_region}, {is_deferred_region}, {is_exceptional_region}, {is_generator_region}, {is_reentrant_region}, {is_scoped_region}, {is_static_region}],
                    parent_class_capabilities={parent_class_capabilities},
                    parameters={parameters},
                    visibility_param={visibility},
                    mutability_param={mutability},
                    method_modifier_param={method_modifier},
                    return_type={return_type},
                    name={name},
                    documentation={documentation},
                    templates={templates},
                    captured_variables={captured_variables},
                    statements={statements},
                    is_deferred={is_deferred},
                    is_exceptional={is_exceptional},
                    is_generator={is_generator},
                    is_reentrant={is_reentrant},
                    is_scoped={is_scoped},
                    is_static={is_static},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                parser_info_type=str(parser_info.parser_info_type__),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                mutability_region=self._ToString(parser_info.regions__.mutability),
                method_modifier_region=self._ToString(parser_info.regions__.method_modifier),
                name_region=self._ToString(parser_info.regions__.name),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                captured_variables_region=self._ToString(parser_info.regions__.captured_variables),
                parameters_region=self._ToString(parser_info.regions__.parameters),
                statements_region=self._ToString(parser_info.regions__.statements),
                is_deferred_region=self._ToString(parser_info.regions__.is_deferred),
                is_exceptional_region=self._ToString(parser_info.regions__.is_exceptional),
                is_generator_region=self._ToString(parser_info.regions__.is_generator),
                is_reentrant_region=self._ToString(parser_info.regions__.is_reentrant),
                is_scoped_region=self._ToString(parser_info.regions__.is_scoped),
                is_static_region=self._ToString(parser_info.regions__.is_static),
                parent_class_capabilities=parent_class_capabilities,
                visibility=self._ToString(parser_info.visibility),
                mutability=self._ToString(parser_info.mutability),
                method_modifier=self._ToString(parser_info.method_modifier),
                return_type=self._ToString(parser_info.return_type),
                name=self._ToString(parser_info.name) if isinstance(parser_info.name, str) else "FuncDefinitionStatementParserInfoOperatorType.{}".format(parser_info.name.name),
                documentation=self._ToString(parser_info.documentation),
                templates=self._ToString(parser_info.templates),
                captured_variables=self._ToString(parser_info.captured_variables),    # type: ignore
                parameters=self._ToString(parser_info.parameters),
                statements=self._ToString(parser_info.statements),                    # type: ignore
                is_deferred=self._ToString(parser_info.is_deferred),
                is_exceptional=self._ToString(parser_info.is_exceptional),
                is_generator=self._ToString(parser_info.is_generator),
                is_reentrant=self._ToString(parser_info.is_reentrant),
                is_scoped=self._ToString(parser_info.is_scoped),
                is_static=self._ToString(parser_info.is_static),
            ),
        )

    # ----------------------------------------------------------------------
    # |  FuncInvocationStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncInvocationStatementParserInfo(
        self,
        parser_info: FuncInvocationStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncInvocationStatementParserInfo.Create(
                    regions=[{self_region}],
                    expression={expression},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                expression=self._ToString(parser_info.expression),
            ),
        )

    # ----------------------------------------------------------------------
    # |  IfStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = IfStatementParserInfo.Create(
                    regions=[{self_region}],
                    clauses={clauses},
                    else_clause={else_clause},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                clauses=self._ToString(parser_info.clauses),  # type: ignore
                else_clause=self._ToString(parser_info.else_clause),
            ),
        )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementClauseParserInfo(
        self,
        parser_info: IfStatementClauseParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementClauseParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = IfStatementClauseParserInfo.Create(
                    regions=[{self_region}, {statements_region}, {documentation_region}],
                    expression={expression},
                    statements={statements},
                    documentation={documentation},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                statements_region=self._ToString(parser_info.regions__.statements),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                expression=self._ToString(parser_info.expression),
                statements=self._ToString(parser_info.statements),  # type: ignore
                documentation=self._ToString(parser_info.documentation),
            ),
        )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementElseClauseParserInfo(
        self,
        parser_info: IfStatementElseClauseParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementElseClauseParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = IfStatementElseClauseParserInfo.Create(
                    regions=[{self_region}, {statements_region}, {documentation_region}],
                    statements={statements},
                    documentation={documentation},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                statements_region=self._ToString(parser_info.regions__.statements),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                statements=self._ToString(parser_info.statements),  # type: ignore
                documentation=self._ToString(parser_info.documentation),
            ),
        )

    # ----------------------------------------------------------------------
    # |  ImportStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnImportStatementParserInfo(
        self,
        parser_info: ImportStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportType as ImportStatementParserInfoImportType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ImportStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {source_filename_region}],
                    visibility_param={visibility},
                    source_filename={source_filename},
                    import_items={import_items},
                    import_type={import_type},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                source_filename_region=self._ToString(parser_info.regions__.source_filename),
                visibility=self._ToString(parser_info.visibility),
                source_filename=self._ToString(parser_info.source_filename),
                import_items=self._ToString(parser_info.import_items),  # type: ignore
                import_type="ImportStatementParserInfoImportType.{}".format(parser_info.import_type.name),
            ),
        )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnImportStatementItemParserInfo(
        self,
        parser_info: ImportStatementItemParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementItemParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ImportStatementItemParserInfo.Create(
                    regions=[{self_region}, {name_region}, {alias_region}],
                    name={name},
                    alias={alias},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                alias_region=self._ToString(parser_info.regions__.alias),
                name=self._ToString(parser_info.name),
                alias=self._ToString(parser_info.alias),
            ),
        )

    # ----------------------------------------------------------------------
    # |  PassStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnPassStatementParserInfo(
        self,
        parser_info: PassStatementParserInfo,  # pylint: disable=unused-argument
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = PassStatementParserInfo.Create([{self_region}])
                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
            ),
        )

    # ----------------------------------------------------------------------
    # |  SpecialMethodStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType")

        parent_class_capabilities = "{}Capabilities".format(parser_info.parent_class_capabilities.name)

        self._imports.add(
            "from v1.Parser.ParserInfos.Statements.ClassCapabilities.{parent_class_capabilities} import {parent_class_capabilities}".format(
                parent_class_capabilities=parent_class_capabilities,
            ),
        )

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = SpecialMethodStatementParserInfo.Create(
                    regions=[{self_region}, {name_region}, {statements_region}],
                    parent_class_capabilities={parent_class_capabilities},
                    name={name},
                    statements={statements},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                statements_region=self._ToString(parser_info.regions__.statements),
                parent_class_capabilities=parent_class_capabilities,
                name="SpecialMethodType.{}".format(parser_info.name.name),
                statements=self._ToString(cast(List[ParserInfo], parser_info.statements)),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TypeAliasStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeAliasStatementParserInfo(
        self,
        parser_info: TypeAliasStatementParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo")

        if parser_info.parent_class_capabilities is None:
            parent_class_capabilities = None
        else:
            parent_class_capabilities = "{}Capabilities".format(parser_info.parent_class_capabilities.name)

            self._imports.add(
                "from v1.Parser.ParserInfos.Statements.ClassCapabilities.{parent_class_capabilities} import {parent_class_capabilities}".format(
                    parent_class_capabilities=parent_class_capabilities,
                ),
            )

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TypeAliasStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {name_region}],
                    parent_class_capabilities={parent_class_capabilities},
                    visibility_param={visibility},
                    name={name},
                    type={type},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                name_region=self._ToString(parser_info.regions__.name),
                visibility=self._ToString(parser_info.visibility),
                parent_class_capabilities=parent_class_capabilities,
                name=self._ToString(parser_info.name),
                type=self._ToString(parser_info.type),
            ),
        )
