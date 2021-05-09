# ----------------------------------------------------------------------
# |
# |  ParseCoroutine.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-20 07:35:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that supports the dynamic addition of statements at various scopes"""

import os

from collections import OrderedDict
from typing import Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Coroutine
    from .Error import Error
    from .NormalizedIterator import NormalizedIterator
    from .Statement import DynamicStatements, Statement
    from .Token import Token


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _SyntaxError(Error):
    """Base class for all exceptions thrown by this module"""

    PotentialStatements: Dict[Statement, Statement.ParseResultsType]        = field(init=False)
    parse_result_items: InitVar[List[Statement.StatementParseResultItem]]

    # ----------------------------------------------------------------------
    def __post_init__(self, parse_result_items):
        potentials = OrderedDict()

        for parse_result_item in parse_result_items:
            potentials[parse_result_item.Statement] = parse_result_item.Results

        object.__setattr__(self, "PotentialStatements", potentials)


# ----------------------------------------------------------------------
class SyntaxInvalidError(_SyntaxError):
    """Exception thrown when there are no statement matches"""

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")


# ----------------------------------------------------------------------
class InvalidDynamicTraversalError(Error):
    """Exception thrown when dynamic statements that prohibit parent traversal are applied over other dynamic statements"""

    ExistingDynamicStatements: List[NormalizedIterator]

    MessageTemplate                         = Interface.DerivedProperty("Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ParseResultBase(object):
    """Base class for parsed AST entities"""

    Type: Union[Statement, Token]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        object.__setattr__(self, "Parent", None)        # This value will be set when _Create- functions are invoked


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _Node(_ParseResultBase):

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(_Node, self).__post_init__()
        object.__setattr__(self, "Children", [])        # This value will be populated when _Create- functions are invoked


# ----------------------------------------------------------------------
class RootNode(_Node):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(RootNode, self).__init__(None)


# ----------------------------------------------------------------------
class Node(_Node):
    """AST results of a Statement"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Statement,
    ):
        super(Node, self).__init__(statement)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Leaf(_ParseResultBase):
    """AST results of a Token"""

    Whitespace: Optional[Tuple[int, int]]   # Whitespace immediately before the token
    Value: Token.MatchType                  # Result of the call to Token.Match
    Iter: NormalizedIterator                # NormalizedIterator after the token has been consumed
    IsIgnored: bool                         # True if the result is whitespace while whitespace is being ignored


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicStatementInfo(object):
    statements: List[Statement]
    expressions: List[Statement]
    allow_parent_traversal: bool                        = True      # If False, prevent content from including values from higher-level scope

    # ----------------------------------------------------------------------
    def Clone(self):
        return self.__class__(
            list(self.statements),
            list(self.expressions),
            self.allow_parent_traversal,
        )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIndent():
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDedent():
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStatementComplete(
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator
    ) -> Union[
        Coroutine.Status,
        DynamicStatementInfo,
    ]:
        """Called on the completion of each statement"""
        raise Exception("Abstract method")


# ----------------------------------------------------------------------
def ParseCoroutine(
    normalized_iter: NormalizedIterator,
    initial_statement_info: DynamicStatementInfo,
    observer: Observer,
) -> Generator[
    Coroutine.Status,
    Optional[DynamicStatementInfo],         # The dynamic statement info is required only when the coroutine generates 'yield'
    Optional[RootNode],
]:
    """Manages complexities associated with statement/expression generation"""

    assert normalized_iter.Offset == 0, normalized_iter.Offset

    statement_observer = _StatementObserver(initial_statement_info, observer)

    root = RootNode()

    while not normalized_iter.AtEnd():
        try:
            iterator = Statement.ParseMultipleCoroutine(
                statement_observer.GetDynamicStatements(DynamicStatements.Statements),
                normalized_iter,
                statement_observer,
            )

            while True:
                result = next(iterator)
                if result is not None:
                    BugBug = 10

        except StopIteration as ex:
            result = ex.value

        if not result.Success:              # <Has no member> pylint: disable=E1101
            raise SyntaxInvalidError(
                normalized_iter.Line,
                normalized_iter.Column,
                result.Results,             # <Has no member> pylint: disable=E1101
            )

        prev_iter = normalized_iter
        normalized_iter = result.Iter       # <Has no member> pylint: disable=E1101

        assert len(result.Results) == 1, result.Results                     # <Has no member> pylint: disable=E1101
        result = result.Results[0]                                          # <Has no member> pylint: disable=E1101

        result = observer.OnStatementComplete(
            _CreateNode(root, result.Statement, result.Results),
            prev_iter,
            normalized_iter,
        )

        if isinstance(result, DynamicStatementInfo):
            statement_observer.AddDynamicStatementInfo(prev_iter, result)

        elif result == Coroutine.Status.Continue:
            continue

        elif result == Coroutine.Status.Yield:
            dynamic_info = yield Coroutine.Status.Yield
            assert dynamic_info is not None

            statement_observer.AddDynamicStatementInfo(prev_iter, dynamic_info)
            yield Coroutine.Status.Continue

        elif result == Coroutine.Status.Terminate:
            return None

        else:
            assert False, result

    assert normalized_iter.AtEnd()

    return root


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass
class _StatementObserver(Statement.Observer):
    init_statement_info: InitVar[DynamicStatementInfo]

    _observer: Observer

    # ----------------------------------------------------------------------
    def __post_init__(self, init_statement_info):
        # <Attribute defined outside __init__> pylint: disable=W0201
        self._all_statement_infos: List[
            List[
                Tuple[
                    NormalizedIterator,
                    DynamicStatementInfo,
                ]
            ]
        ] = [
            [ (None, init_statement_info.Clone()) ],
        ]

        self._cached_statements: List[Statement]        = []
        self._cached_expressions: List[Statement]       = []

        self._UpdateCache()

    # ----------------------------------------------------------------------
    @Interface.override
    def OnIndent(self):
        self._all_statement_infos.append([])

        self._observer.OnIndent()

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(self):
        assert self._all_statement_infos
        self._all_statement_infos.pop()
        assert len(self._all_statement_infos) >= 1, self._all_statement_infos

        self._UpdateCache()

        self._observer.OnDedent()

    # ----------------------------------------------------------------------
    def AddDynamicStatementInfo(
        self,
        normalized_iter: NormalizedIterator,
        info: DynamicStatementInfo,
    ):
        if not info.statements and not info.expressions:
            return

        if not info.allow_parent_traversal and self._all_statement_infos[-1]:
            raise InvalidDynamicTraversalError(
                normalized_iter.Line,
                normalized_iter.Column,
                [location for location, _ in self._all_statement_infos[-1]],
            )

        self._all_statement_infos[-1].append((normalized_iter, info))

        self._UpdateCache()

    # ----------------------------------------------------------------------
    @Interface.override
    def GetDynamicStatements(
        self,
        value: DynamicStatements,
    ) -> List["Statement"]:
        if value == DynamicStatements.Statements:
            return self._cached_statements
        elif value == DynamicStatements.Expressions:
            return self._cached_expressions

        assert False
        return None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _UpdateCache(self):
        statements = []
        expressions = []

        for statement_infos in reversed(self._all_statement_infos):
            for _, statement_info in reversed(statement_infos):
                statements += statement_info.statements
                expressions += statement_info.expressions

            if statement_infos and not statement_infos[0][1].allow_parent_traversal:
                break

        self._cached_statements = statements            # <Attribute defined outside __init__> pylint: disable=W0201
        self._cached_expressions = expressions          # <Attribute defined outside __init__> pylint: disable=W0201


# ----------------------------------------------------------------------
def _CreateNode(
    parent: Union[RootNode, Node],
    statement: Statement,
    parse_results: Statement.ParseResultsType,
) -> Node:
    """Converts a parse result into a node"""

    node = Node(statement)

    object.__setattr__(node, "Parent", parent)
    parent.Children.append(node)

    for result in parse_results:
        if isinstance(result, Statement.TokenParseResultItem):
            _CreateLeaf(node, result)
        elif isinstance(result, Statement.StatementParseResultItem):
            _CreateNode(node, result.Statement, result.Results)
        else:
            assert False, result

    return node


# ----------------------------------------------------------------------
def _CreateLeaf(
    parent: Node,
    result: Statement.TokenParseResultItem,
) -> Leaf:
    """Converts a parse result item into a leaf"""

    leaf = Leaf(
        result.Token,
        result.Whitespace,
        result.Value,
        result.Iter,
        result.IsIgnored,
    )

    object.__setattr__(leaf, "Parent", parent)
    parent.Children.append(leaf)

    return leaf
