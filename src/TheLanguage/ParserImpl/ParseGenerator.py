# ----------------------------------------------------------------------
# |
# |  ParseGenerator.py
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
"""Contains utilities that support Parsing"""

from collections import OrderedDict
import itertools
import os

from concurrent.futures import Future
from enum import auto, Enum
from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

from Error import Error                                 # <Unable to import> pylint: disable=E0401
from NormalizedIterator import NormalizedIterator
from Statement import Statement
from Token import Token                                 # <No name in module> pylint: disable=E0611

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _SyntaxError(Error):
    """Base class for all exceptions thrown by this module"""

    PotentialStatements: Dict[Statement, Statement.ParseResult]             = field(init=False)
    statements: InitVar[List[Statement]]

    # ----------------------------------------------------------------------
    def __post_init__(self, statements):
        potentials = OrderedDict()

        for statement, result in statements:
            if result.Results:
                potentials[statement] = result

        object.__setattr__(self, "PotentialStatements", potentials)


# ----------------------------------------------------------------------
class SyntaxInvalidError(_SyntaxError):
    """Exception thrown when there are no statement matches"""

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")


# ----------------------------------------------------------------------
class SyntaxAmbiguousError(_SyntaxError):
    """Exception thrown when there are multiple potential matches (we should rarely see this exception in practices, as it is a single of problematic grammar design)"""

    MessageTemplate                         = Interface.DerivedProperty("The syntax is ambiguous")


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
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    class OnStatementCompleteFlag(Enum):
        Continue                            = auto()
        Yield                               = auto()
        Terminate                           = auto()

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
    @classmethod
    def Enqueue(
        cls,
        func_or_funcs: Union[Callable[[], None], List[Callable[[], None]]],
    ) -> Union[Future, List[Future]]:
        if isinstance(func_or_funcs, list):
            return cls._Enqueue(func_or_funcs)

        results = cls._Enqueue([func_or_funcs])
        assert len(results) == 1

        return results[0]

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStatementComplete(
        statement: Statement,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator
    ) -> Union[
        "OnStatementCompleteFlag",
        List[Statement],                    # New statements to add to the current scope (implies continue)
    ]:
        """Called on the completion of each statement"""
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _Enqueue(
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        """Enqueues a list of functions to be executed; the Generator will yield immediately after this call"""
        raise Exception("Abstract method")


# ----------------------------------------------------------------------
def Parse(
    normalized_iter: NormalizedIterator,
    initial_statements: List[Statement],
    observer: Observer,
) -> Generator[
    bool,                                   # True to yield and continue, False to terminate
    None,
    Optional[RootNode],                     # Parsing result or None if terminated
]:
    """Parses the provided content based on the provided statements"""

    assert normalized_iter.Offset == 0, normalized_iter.Offset

    statement_observer = _StatementObserver([initial_statements], observer)

    root = RootNode()

    while not normalized_iter.AtEnd():
        these_statements = []
        these_parse_funcs = []

        for statement in itertools.chain(*statement_observer.statements):
            these_statements.append(statement)
            these_parse_funcs.append(lambda statement=statement: statement.Parse(normalized_iter.Clone(), statement_observer))

        these_futures = observer.Enqueue(these_parse_funcs)
        yield True

        successes = []
        failures = []

        for statement, future in zip(these_statements, these_futures):
            result = future.result()

            if result.Success:
                successes.append((statement, result))
            else:
                failures.append((statement, result))

        if not successes:
            raise SyntaxInvalidError(normalized_iter.Line, normalized_iter.Column, failures)

        if len(successes) > 1:
            raise SyntaxAmbiguousError(normalized_iter.Line, normalized_iter.Column, successes)

        assert len(successes) == 1
        statement, result = successes[0]

        prev_iter = normalized_iter
        normalized_iter = result.Iter

        result = observer.OnStatementComplete(
            statement,
            _CreateNode(root, statement, result.Results),
            prev_iter,
            normalized_iter,
        )

        if isinstance(result, list):
            statement_observer.statements[-1].extend(result)

        elif result == Observer.OnStatementCompleteFlag.Continue:
            continue

        elif result == Observer.OnStatementCompleteFlag.Yield:
            yield True

        elif result == Observer.OnStatementCompleteFlag.Terminate:
            yield False
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
    statements: List[List[Statement]]
    observer: Observer

    # ----------------------------------------------------------------------
    @Interface.override
    def OnIndent(self):
        self.statements.append([])

        self.observer.OnIndent()

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(self):
        assert self.statements
        self.statements.pop()

        assert len(self.statements) >= 1, self.statements

        self.observer.OnDedent()


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
            _CreateNode(node, result.StatementItem, result.Results)
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
