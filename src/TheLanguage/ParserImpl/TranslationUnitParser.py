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
    from . import AST
    from .Error import Error
    from .StatementDSL import DynamicStatements

    from .Statements.DynamicStatement import DynamicStatement
    from .Statements.Statement import Statement
    from .Statements.TokenStatement import TokenStatement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDynamicTraversalError(Error):
    """Exception thrown when dynamic statements that prohibit parent traversal are applied over other dynamic statements"""

    ExistingDynamicStatements: Statement.NormalizedIterator

    MessageTemplate                         = Interface.DerivedProperty("Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidError(Error):
    """Exception thrown when no matching statements were found"""

    Root: AST.RootNode

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
            content=self.Root.ToString(
                verbose=verbose,
            ).rstrip(),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicStatementInfo(object):
    """Contains Statements that have been dynamically added to the active scope"""

    Statements: Tuple[Statement, ...]
    Expressions: Tuple[Statement, ...]
    Types: Tuple[Statement, ...]
    AllowParentTraversal: bool              = True      # If False, prevent content from including values from higher-level scope
    Name: Optional[str]                     = None

    # ----------------------------------------------------------------------
    def __post_init__(self):
        for attribute_name in [
            "Statements",
            "Expressions",
            "Types",
        ]:
            if not isinstance(getattr(self, attribute_name), tuple):
                raise Exception("'{}' must be a tuple".format(attribute_name))

    # ----------------------------------------------------------------------
    def Clone(
        self,
        updated_statements=None,
        updated_expressions=None,
        updated_types=None,
        updated_allow_parent_traversal=None,
        updated_name=None,
    ):
        return self.__class__(
            updated_statements if updated_statements is not None else tuple(self.Statements),
            updated_expressions if updated_expressions is not None else tuple(self.Expressions),
            updated_types if updated_types is not None else tuple(self.Types),
            updated_allow_parent_traversal if updated_allow_parent_traversal is not None else self.AllowParentTraversal,
            updated_name if updated_name is not None else self.Name,
        )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnIndentAsync(
        data_stack: List[Statement.StandardParseResultData],
        iter_before: Statement.NormalizedIterator,
        iter_after: Statement.NormalizedIterator,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnDedentAsync(
        data_stack: List[Statement.StandardParseResultData],
        iter_before: Statement.NormalizedIterator,
        iter_after: Statement.NormalizedIterator,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnStatementCompleteAsync(
        statement: Statement,
        node: AST.Node,
        iter_before: Statement.NormalizedIterator,
        iter_after: Statement.NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement
    ]:
        """Invoked when an internal statement is successfully matched"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    initial_statement_info: DynamicStatementInfo,
    normalized_iter: Statement.NormalizedIterator,
    observer: Observer,
    single_threaded=False,
    name: str = None,
) -> Optional[AST.RootNode]:
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

    statement_observer = _StatementObserver(observer, all_statement_infos)

    statement = DynamicStatement(
        lambda unique_id, observer: cast(_StatementObserver, observer).GetDynamicStatements(unique_id, DynamicStatements.Statements),
        name=name,
    )

    root = AST.RootNode(None)

    while not normalized_iter.AtEnd():
        statement_observer.ClearNodeCache()

        result = await statement.ParseAsync(
            ["root"],
            normalized_iter,
            statement_observer,
            ignore_whitespace=False,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        assert result.Data

        statement_observer.CreateNode(
            result.Data.Statement,
            result.Data.Data,
            result.Data.UniqueId,
            root,
        )

        if not result.Success:
            raise SyntaxInvalidError(
                result.Iter.Line,
                result.Iter.Column,
                root,
            )

        normalized_iter = result.Iter.Clone()

        # TODO: Eat trailing comments (here or in SequenceStatement.py?)

    assert normalized_iter.AtEnd()
    return root


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
    IterAfter: Statement.NormalizedIterator
    Info: DynamicStatementInfo


 # ----------------------------------------------------------------------
@dataclass()
class _StatementInfoNode(object):
    UniqueIdPart: Any
    Children: Dict[Any, "_StatementInfoNode"]           = field(default_factory=OrderedDict)
    Infos: List[_InternalDynamicStatementInfo]          = field(default_factory=list)


# ----------------------------------------------------------------------
class _StatementObserver(Statement.Observer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: Observer,
        all_statement_infos: Dict[Any, _StatementInfoNode],
    ):
        self._observer                      = observer
        self._all_statement_infos           = all_statement_infos

        self._indent_level                  = 0

        self._node_cache: Dict[Any, Union[AST.Node, AST.Leaf]]              = {}

    # ----------------------------------------------------------------------
    def ClearNodeCache(self):
        self._node_cache.clear()

    # ----------------------------------------------------------------------
    def CreateNode(
        self,
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        unique_id: Optional[List[str]],
        parent: Optional[Union[AST.RootNode, AST.Node]],
    ) -> Union[AST.Node, AST.Leaf]:

        # Look for the cached value
        if unique_id is not None:
            key = tuple(unique_id)
        else:
            key = None

        node: Optional[Union[AST.Node, AST.Leaf]] = None
        was_cached = False

        potential_node = self._node_cache.get(key, None)
        if potential_node is not None:
            node = potential_node
            was_cached = True

        # Create the node if necessary
        if node is None:
            if isinstance(statement, TokenStatement) and data:
                node = self._CreateLeaf(cast(Statement.TokenParseResultData, data), parent)
            else:
                node = AST.Node(statement)

        assert node

        # Assign the parent if necessary
        if parent != node.Parent:
            assert parent

            object.__setattr__(node, "Parent", parent)
            parent.Children.append(node)

        # Populate the children
        if not was_cached:
            if isinstance(node, AST.Node):
                for child_statement, child_data, child_unique_id in (data.Enum() if data else []):
                    if child_statement is None:
                        assert child_data
                        self._CreateLeaf(cast(Statement.TokenParseResultData, child_data), node)
                    else:
                        self.CreateNode(child_statement, child_data, child_unique_id, node)

            if key is not None:
                self._node_cache[key] = node

        return node

    # ----------------------------------------------------------------------
    def GetDynamicStatements(
        self,
        unique_id: List[str],
        dynamic_statement_type: DynamicStatements,
    ) -> Union[
        Tuple[str, List[Statement]],
        List[Statement],
    ]:
        if dynamic_statement_type == DynamicStatements.Statements:
            attribute_name = "Statements"
        elif dynamic_statement_type == DynamicStatements.Expressions:
            attribute_name = "Expressions"
        else:
            assert False, dynamic_statement_type  # pragma: no cover

        all_statements = []
        all_names = []

        processed_infos = set()
        processed_statements = set()

        should_continue = True

        # Process the most recently added statements to the original ones
        previous_nodes = list(self._EnumPreviousNodes(unique_id))

        for node in reversed(previous_nodes):
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
                    info.Name or "{{{}}}".format(
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
        unique_id: List[str],
        statement_stack: List[Statement],
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
        unique_id: List[str],
        statement_info_stack: List[
            Tuple[
                Statement,
                Optional[bool],
            ],
        ],
    ):
        was_successful = statement_info_stack[0][1]

        # Get this node
        d = self._all_statement_infos
        node = None

        for id_part in unique_id:
            node = d.get(id_part, None)
            assert node is not None

            d = node.Children

        assert node

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
        data_stack: List[Statement.StandardParseResultData],
        iter_before: Statement.NormalizedIterator,
        iter_after: Statement.NormalizedIterator,
    ):
        self._indent_level += 1

        this_result = await self._observer.OnIndentAsync(
            data_stack,
            iter_before,
            iter_after,
        )
        if isinstance(this_result, DynamicStatementInfo):
            assert data_stack[0].UniqueId is not None
            unique_id = data_stack[0].UniqueId

            self._AddDynamicStatementInfo(unique_id, iter_after, this_result)

        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(
        self,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: Statement.NormalizedIterator,
        iter_after: Statement.NormalizedIterator,
    ):
        assert data_stack[0].UniqueId is not None
        unique_id = data_stack[0].UniqueId

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
            data_stack,
            iter_before,
            iter_after,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnInternalStatementAsync(
        self,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: Statement.NormalizedIterator,
        iter_after: Statement.NormalizedIterator,
    ) -> bool:
        assert data_stack[0].Data

        this_result = await self._observer.OnStatementCompleteAsync(
            data_stack[0].Statement,
            cast(
                AST.Node,
                self.CreateNode(
                    data_stack[0].Statement,
                    data_stack[0].Data,
                    data_stack[0].UniqueId,
                    None,
                ),
            ),
            iter_before,
            iter_after,
        )

        if isinstance(this_result, DynamicStatementInfo):
            assert data_stack[0].UniqueId is not None
            unique_id = data_stack[0].UniqueId

            self._AddDynamicStatementInfo(unique_id, iter_after, this_result)
            return True

        return this_result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateLeaf(
        data: Statement.TokenParseResultData,
        parent: Optional[Union[AST.RootNode, AST.Node]],
    ) -> AST.Leaf:
        leaf = AST.Leaf(
            data.Token,
            data.Whitespace,
            data.Value,
            data.IterBefore,
            data.IterAfter,
            data.IsIgnored,
        )

        if parent:
            object.__setattr__(leaf, "Parent", parent)
            parent.Children.append(leaf)

        return leaf

    # ----------------------------------------------------------------------
    def _AddDynamicStatementInfo(
        self,
        unique_id: List[str],
        iter_after: Statement.NormalizedIterator,
        info: DynamicStatementInfo,
    ):
        if not info.Statements and not info.Expressions:
            return

        this_node = None
        last_info = None

        # The node associated with this event will be the last one that
        # we encounter in this generator. In addition to the current node,
        # get the last dynamic info associated with all of the nodes to determine
        # if adding this dynamic info will be a problem.
        for node in self._EnumPreviousNodes(unique_id):
            this_node = node

            if node.Infos:
                last_info = node.Infos[-1]

        assert this_node
        assert this_node.UniqueIdPart == unique_id[-1], (this_node.UniqueIdPart, unique_id[-1])

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
        unique_id: List[str],
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
