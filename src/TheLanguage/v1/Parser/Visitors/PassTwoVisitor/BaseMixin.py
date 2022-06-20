# ----------------------------------------------------------------------
# |
# |  BaseMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BaseMixin object"""

import os
import types

from contextlib import contextmanager, ExitStack
from typing import Dict, List, Optional, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, Error, ErrorException

    from ...MiniLanguage.Types.ExternalType import ExternalType as MiniLanguageExternalType

    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType, VisitResult
    from ...ParserInfos.AggregateParserInfo import AggregateParserInfo

    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo

    from ...ParserInfos.Statements.Traits.NamedStatementTrait import NamedStatementTrait
    from ...ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{name}' is not a recognized type",
    name=str,
)


# ----------------------------------------------------------------------
class BaseMixin(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        fundamental_types_namespace: Optional[NamespaceInfo],
        this_namespace: ParsedNamespaceInfo,
    ):
        namespace_stack: List[NamespaceInfo] = []

        if fundamental_types_namespace is not None:
            namespace_stack.append(fundamental_types_namespace)

        self._namespaces_stack              = [namespace_stack, ]
        self._root_namespace                = this_namespace

        self._compile_time_stack            = [configuration_info, ]

        self._errors: List[Error]           = []

        self._template_ctr                  = 0

        self._namespace_to_names_map: Dict[int, Tuple[str, str]]            = {}

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        index = name.find("ParserInfo__")
        if index != -1 and index + len("ParserInfo__") + 1 < len(name):
            return types.MethodType(self.__class__._DefaultDetailMethod, self)  # pylint: disable=protected-access

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPhrase(
        self,
        parser_info: ParserInfo,
    ):
        try:
            with ExitStack() as exit_stack:
                if isinstance(parser_info, NamedStatementTrait):
                    assert self._namespaces_stack

                    if parser_info.name_is_ordered__:
                        # Add the item
                        assert self._namespaces_stack
                        namespace_stack = self._namespaces_stack[-1]

                        assert namespace_stack
                        namespace = namespace_stack[-1]

                        assert isinstance(namespace, ParsedNamespaceInfo)

                        namespace.children[parser_info.name] = namespace.ordered_children[parser_info.name]

                    if isinstance(parser_info, ScopedStatementTrait):
                        if isinstance(parser_info, RootStatementParserInfo):
                            namespace = self._root_namespace
                        else:
                            assert self._namespaces_stack
                            namespace_stack = self._namespaces_stack[-1]

                            assert namespace_stack
                            namespace = namespace_stack[-1]

                            namespace = namespace.children[parser_info.name]

                            if isinstance(namespace, list):
                                for potential_namespace in namespace:
                                    if potential_namespace.parser_info == parser_info:
                                        namespace = potential_namespace
                                        break

                        assert isinstance(namespace, NamespaceInfo)

                        assert self._namespaces_stack
                        namespace_stack = self._namespaces_stack[-1]

                        namespace_stack.append(namespace)
                        exit_stack.callback(namespace_stack.pop)

                if isinstance(parser_info, TemplatedStatementTrait) and parser_info.templates:
                    yield VisitResult.SkipAll
                    return

                if isinstance(parser_info, ExpressionParserInfo):
                    if not parser_info.IsType():
                        yield VisitResult.SkipAll
                        return

                    type_result = MiniLanguageHelpers.EvalType(
                        parser_info,
                        self._compile_time_stack,
                    )

                    if isinstance(type_result, MiniLanguageExternalType):
                        resolved_type = self._GetResolvedType(type_result.name, parser_info)

                        print("BugBug (1)", parser_info.parser_info_type__)
                    else:
                        print("BugBug (2)", parser_info.parser_info_type__)

                        if not ParserInfoType.IsCompileTimeStrict(parser_info.parser_info_type__):
                            BugBug = 10

                yield

                # BugBug assert (
                # BugBug     ParserInfoType.IsCompileTimeStrict(parser_info.parser_info_type__)
                # BugBug     or not isinstance(parser_info, ExpressionParserInfo)
                # BugBug     or isinstance(parser_info, VariableExpressionParserInfo)
                # BugBug     or parser_info.in_template__
                # BugBug     or parser_info.has_resolved_type__
                # BugBug ), (
                # BugBug     "Internal Error",
                # BugBug     parser_info.__class__.__name__,
                # BugBug )

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnRootStatementParserInfo(*args, **kwargs):  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnAggregateParserInfo(
        self,
        parser_info: AggregateParserInfo,
    ):
        for agg_parser_info in parser_info.parser_infos:
            agg_parser_info.Accept(self)

        yield

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _GetResolvedType(
        self,
        type_name: str,
        parser_info: ParserInfo,
    ) -> ExpressionParserInfo.ResolvedType:
        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        for namespace in reversed(namespace_stack):
            potential_namespace = namespace.children.get(type_name, None)
            if potential_namespace is None:
                continue

            assert isinstance(potential_namespace, ParsedNamespaceInfo), potential_namespace
            namespace = potential_namespace.parent

            # Get the names for the namespace
            key = id(namespace)

            namespace_names = self._namespace_to_names_map.get(key, None)
            if namespace_names is None:
                names: List[str] = []

                while namespace is not None:
                    if namespace.name is not None:
                        names.append(namespace.name)

                    namespace = namespace.parent

                assert len(names) >= 2, names

                workspace_name = names.pop()
                relative_name = ".".join(reversed(names))

                namespace_names = (workspace_name, relative_name)

                self._namespace_to_names_map[key] = namespace_names

            assert namespace_names is not None

            return ExpressionParserInfo.ResolvedType.Create(
                potential_namespace.parser_info,
                namespace_names[0],
                namespace_names[1],
            )

        raise ErrorException(
            InvalidTypeError.Create(
                region=parser_info.regions__.self__,
                name=type_name,
            ),
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        parser_info_or_infos: Union[ParserInfo, List[ParserInfo]],
        *,
        include_disabled: bool,
    ):
        if isinstance(parser_info_or_infos, list):
            for parser_info in parser_info_or_infos:
                parser_info.Accept(
                    self,
                    include_disabled=include_disabled,
                )
        else:
            parser_info_or_infos.Accept(
                self,
                include_disabled=include_disabled,
            )
