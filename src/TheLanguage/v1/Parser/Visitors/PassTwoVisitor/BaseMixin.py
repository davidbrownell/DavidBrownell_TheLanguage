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
from typing import Dict, List, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import Error, ErrorException

    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType
    from ...ParserInfos.AggregateParserInfo import AggregateParserInfo

    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo
    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import (
        NamedStatementTrait,
        ScopedStatementTrait,
        StatementParserInfo,
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

        self._configuration_info            = configuration_info

        self._errors: List[Error]           = []

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
                        namespace_stack = self._namespaces_stack[-1]
                        assert namespace_stack

                        assert isinstance(namespace_stack[-1], ParsedNamespaceInfo)

                        namespace_stack[-1].children[parser_info.name] = namespace_stack[-1].ordered_children[parser_info.name]

                    if isinstance(parser_info, ScopedStatementTrait):
                        if isinstance(parser_info, RootStatementParserInfo):
                            namespace = self._root_namespace
                        else:
                            namespace_stack = self._namespaces_stack[-1]
                            assert namespace_stack

                            namespace = namespace_stack[-1].children[parser_info.name]

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

                yield

                assert (
                    parser_info.parser_info_type__ != ParserInfoType.Configuration
                    and parser_info.parser_info_type__ != ParserInfoType.TypeCustomization
                ) or parser_info.is_validated__, (
                    "Internal Error",
                    parser_info.__class__.__name__,
                )

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnRootStatementParserInfo(*args, **kwargs):
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
