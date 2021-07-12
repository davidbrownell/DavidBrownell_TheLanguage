# ----------------------------------------------------------------------
# |
# |  TranslationUnitParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-01 15:36:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used to parse a single translation unit"""

import os
import textwrap

from collections import OrderedDict
from typing import Any, cast, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error
    from .NormalizedIterator import NormalizedIterator
    from .StatementEx import DynamicStatements, Statement, StatementEx

    from .StatementImpl.DynamicStatement import DynamicStatement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDynamicTraversalError(Error):
    """Exception thrown when dynamic statements that prohibit parent traversal are applied over other dynamic statements"""

    ExistingDynamicStatements: NormalizedIterator

    MessageTemplate                         = Interface.DerivedProperty("Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidError(Error):
    """Exception thrown when no matching statements were found"""

    DataItems: List[Statement.ParseResultData]

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")

    # ----------------------------------------------------------------------
    def ToDebugString(
        self,
        verbose=False,
    ):
        return textwrap.dedent(
            """\
            {message} [{line}, {column}]

            {content}
            """,
        ).format(
            message=str(self),
            line=self.Line,
            column=self.Column,
            content="".join(
                [
                    data_item.ToString(
                        verbose=verbose,
                    )
                    for data_item in self.DataItems
                ],
            ).rstrip(),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicStatementInfo(object):
    """Contains Statements that have been dynamically added to the active scope"""

    Statements: List[Statement]
    Expressions: List[Statement]
    AllowParentTraversal: bool              = True      # If False, prevent content from including values from higher-level scope
    Name: Optional[str]                     = None

    # ----------------------------------------------------------------------
    def Clone(
        self,
        updated_statements=None,
        updated_expressions=None,
        updated_allow_parent_traversal=None,
        updated_name=None,
    ):
        return self.__class__(
            updated_statements if updated_statements is not None else list(self.Statements),
            updated_expressions if updated_expressions is not None else list(self.Expressions),
            updated_allow_parent_traversal if updated_allow_parent_traversal is not None else self.AllowParentTraversal,
            updated_name if updated_name is not None else self.Name,
        )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnIndentAsync(
        statement: StatementEx,
        data_items: List[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Optional[DynamicStatementInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnDedentAsync(
        statement: Statement,
        data_items: List[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnStatementCompleteAsync(
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement
    ]:
        """Invoked when an internal statement is successfully matched"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    initial_statement_info: DynamicStatementInfo,
    normalized_iter: NormalizedIterator,
    observer: Observer,
    single_threaded=False,
    name: str = None,
) -> Optional[List[Statement.ParseResultData]]:
    """Repeatedly matches statements for all of the iterator"""

    assert normalized_iter.Offset == 0, normalized_iter

    all_statement_infos: Dict[Any, _StatementInfoNode] = {
        _DefaultStatementInfoTag : _StatementInfoNode(
            [],
            OrderedDict(),
            [
                _InternalDynamicStatementInfo(
                    0,
                    normalized_iter.Clone(),
                    initial_statement_info,
                ),
            ],
        ),
    }

    statement = DynamicStatement(
        lambda unique_id, observer: cast(StatementEx.Observer, observer).GetDynamicStatements(unique_id, DynamicStatements.Statements),
        name=name,
    )

    statement_ex_observer = _StatementExObserver(all_statement_infos, observer)

    data_items: List[Statement.ParseResultData] = []

    while not normalized_iter.AtEnd():
        result = await statement.ParseAsync(
            normalized_iter,
            statement_ex_observer,
            ignore_whitespace=False,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        assert result.Data
        data_items.append(result.Data)

        if not result.Success:
            raise SyntaxInvalidError(
                result.Iter.Line,
                result.Iter.Column,
                data_items,
            )

        normalized_iter = result.Iter.Clone()

    assert normalized_iter.AtEnd()

    return data_items


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _DefaultStatementInfoTag(object):
    """\
    Unique type to use as a key in `_StatementInfoNode` dictionaries; this is used rather
    than a normal value (for example, `None`) to allow for any key types.
    """
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _InternalDynamicStatementInfo(object):
    IndentLevel: int
    IterAfter: NormalizedIterator
    Info: DynamicStatementInfo


 # ----------------------------------------------------------------------
@dataclass()
class _StatementInfoNode(object):
    UniqueIdPart: Any
    Children: Dict[Any, "_StatementInfoNode"]           = field(default_factory=OrderedDict)
    Infos: List[_InternalDynamicStatementInfo]          = field(default_factory=list)


# ----------------------------------------------------------------------
class _StatementExObserver(StatementEx.Observer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        all_statement_infos: Dict[Any, _StatementInfoNode],
        observer: Observer,
    ):
        self._all_statement_infos           = all_statement_infos
        self._observer                      = observer
        self._indent_level                  = 0

    # ----------------------------------------------------------------------
    @Interface.override
    def GetDynamicStatements(
        self,
        unique_id: List[Any],
        value: DynamicStatements,
    ) -> Union[
        Tuple[str, List[Statement]],
        List[Statement],
    ]:
        if value == DynamicStatements.Statements:
            attribute_name = "Statements"
        elif value == DynamicStatements.Expressions:
            attribute_name = "Expressions"
        else:
            assert False, value  # pragma: no cover

        all_statements = []
        all_names = []

        processed_infos = set()
        processed_statements = set()

        should_continue = True

        # Process the most recently added statements to the original ones
        for node in self._EnumInfoNodes(unique_id):
            these_statements = []
            these_names = []

            for info in node.Infos:
                info = info.Info

                # Have we seen this DynamicStatementInfo before?
                info_key = id(info)

                if info_key in processed_infos:
                    continue

                processed_infos.add(info_key)

                # Get the statements
                statements = getattr(info, attribute_name)
                if not statements:
                    continue

                len_these_statements = len(these_statements)

                for statement in statements:
                    # Have we already seen this statement
                    statement_key = id(statement)

                    if statement_key in processed_statements:
                        continue

                    processed_statements.add(statement_key)

                    these_statements.append(statement)

                if len(these_statements) == len_these_statements:
                    continue

                these_names.append(
                    info.Name or "[{}]".format(
                        ", ".join([statement.ToString() for statement in these_statements[len_these_statements:]]),
                    ),
                )

                if not info.AllowParentTraversal:
                    should_continue = False
                    break

            if these_statements:
                all_statements = these_statements + all_statements
            if these_names:
                all_names = these_names + all_names

            if not should_continue:
                break

        return " / ".join(all_names), all_statements

    # ----------------------------------------------------------------------
    @Interface.override
    def StartStatement(
        self,
        unique_id: List[Any],
    ):
        d = self._all_statement_infos

        for id_part in unique_id:
            value = d.get(id_part, None)
            if value is None:
                value = _StatementInfoNode(id_part)
                d[id_part] = value

            d = value.Children

    # ----------------------------------------------------------------------
    @Interface.override
    def EndStatement(
        self,
        unique_id: List[Any],
        was_successful: bool,
    ):
        node = self._GetNode(unique_id)

        # Collect all the infos of the descendants and add them here
        if was_successful:
            if not node.Infos:
                for descendant in self._EnumDescendantNodes(node.Children):
                    node.Infos += descendant.Infos
        else:
            node.Infos = []

        node.Children = {}

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        statement: StatementEx,
        data_items: List[Statement.ParseResultData],
        unique_id: List[Any],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ):
        self._indent_level += 1

        this_result = await self._observer.OnIndentAsync(
            statement,
            data_items,
            iter_before,
            iter_after,
        )
        if isinstance(this_result, DynamicStatementInfo):
            self._AddDynamicStatementInfo(unique_id, iter_after, this_result)

        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(
        self,
        statement: Statement,
        data_items: List[Statement.ParseResultData],
        unique_id: List[Any],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ):
        for node in self._EnumPreviousNodes(unique_id):
            if not node.Infos:
                continue

            info_index = 0
            while info_index < len(node.Infos):
                info = node.Infos[info_index]

                if info.IndentLevel == self._indent_level:
                    del node.Infos[info_index]
                else:
                    info_index += 1

        assert self._indent_level
        self._indent_level -= 1

        await self._observer.OnDedentAsync(
            statement,
            data_items,
            iter_before,
            iter_after,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnInternalStatementAsync(
        self,
        unique_id: List[Any],
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> bool:

        this_result = await self._observer.OnStatementCompleteAsync(
            statement,
            data,
            iter_before,
            iter_after,
        )

        if isinstance(this_result, DynamicStatementInfo):
            self._AddDynamicStatementInfo(unique_id, iter_after, this_result)
            return True

        return this_result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _GetNode(
        self,
        unique_id: List[Any],
    ) -> _StatementInfoNode:
        d = self._all_statement_infos
        node = None

        for id_part in unique_id:
            node = d.get(id_part, None)
            assert node is not None

            d = node.Children

        assert node
        return node

    # ----------------------------------------------------------------------
    def _AddDynamicStatementInfo(
        self,
        unique_id: List[Any],
        iter_after: NormalizedIterator,
        info: DynamicStatementInfo,
    ):
        this_node = None
        last_info = None

        for node in self._EnumInfoNodes(unique_id):
            if this_node is None:
                this_node = node

            if node.Infos:
                last_info = node.Infos[-1]
                break

        assert this_node.UniqueIdPart == unique_id[-1], (node.UniqueIdPart, unique_id[-1])

        if (
            not info.AllowParentTraversal
            and last_info is not None
            and last_info.IndentLevel == self._indent_level
        ):
            raise InvalidDynamicTraversalError(
                iter_after.Line,
                iter_after.Column,
                last_info.IterAfter,
            )

        assert this_node is not None, unique_id
        this_node.Infos.append(
            _InternalDynamicStatementInfo(
                self._indent_level,
                iter_after.Clone(),
                info,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def _EnumDescendantNodes(
        cls,
        node_children: Dict[Any, _StatementInfoNode],
    ) -> Generator[_StatementInfoNode, None, None]:
        for v in node_children.values():
            yield v
            yield from cls._EnumDescendantNodes(v.Children)

    # ----------------------------------------------------------------------
    def _EnumPreviousNodes(
        self,
        unique_id: List[Any],
    ) -> Generator[_StatementInfoNode, None, None]:
        yield self._all_statement_infos[_DefaultStatementInfoTag]

        d = self._all_statement_infos

        for id_part in unique_id:
            for k, v in d.items():
                if k == _DefaultStatementInfoTag:
                    continue

                yield v

                if k == id_part:
                    d = v.Children
                    break

    # ----------------------------------------------------------------------
    def _EnumInfoNodes(
        self,
        unique_id: List[Any],
    ) -> Generator[_StatementInfoNode, None, None]:
        nodes = list(self._EnumPreviousNodes(unique_id))

        # Process the most recently added statements to the original ones
        yield from reversed(nodes)
