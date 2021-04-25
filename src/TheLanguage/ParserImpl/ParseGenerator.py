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

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Optional, Tuple, Union

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
class _SyntaxException(Error):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        statements,
        line,
        column,
    ):
        super(_SyntaxException, self).__init__(line, column)

        potentials = OrderedDict()

        for statement, result in statements:
            if result.results:
                potentials[statement] = result

        self.Potentials                     = potentials


# ----------------------------------------------------------------------
class SyntaxErrorException(_SyntaxException):
    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")


# ----------------------------------------------------------------------
class SyntaxAmbiguousException(_SyntaxException):
    MessageTemplate                         = Interface.DerivedProperty("The syntax is ambiguous")


# ----------------------------------------------------------------------
class _ParseResultBase(object):
    """Base class for entities returned when parsed"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        result_type: Union[Statement, Token],
    ):
        self.Type                                       = result_type
        self.Parent: Optional[_ParseResultBase]         = None


# ----------------------------------------------------------------------
class _Node(_ParseResultBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Optional[Statement],
    ):
        super(_Node, self).__init__(statement)

        self.Children                       = []


# ----------------------------------------------------------------------
class RootNode(_Node):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(RootNode, self).__init__(None)


# ----------------------------------------------------------------------
class Node(_Node):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Statement,
    ):
        super(Node, self).__init__(statement)


# ----------------------------------------------------------------------
class Leaf(_ParseResultBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        token: Token,
        whitespace: Optional[Tuple[int, int]],          # Whitespace immediately before the token
        value: Token.MatchType,                         # Result of the call to Token.Match
        normalized_iter: NormalizedIterator,            # NormalizedIterator after the token has been consumed
        is_ignored: bool,                               # True if the result is whitespace while whitespace is being ignored
    ):
        super(Leaf, self).__init__(token)

        self.Whitespace                     = whitespace
        self.Value                          = value
        self.Iter                           = normalized_iter
        self.IsIgnored                      = is_ignored


# ----------------------------------------------------------------------
def Parse(
    normalized_iter: NormalizedIterator,
    statements: List[Statement],
    on_statement_complete: Callable[
        [
            Statement,                      # Matching statement
            Node,                           # Result node
            int,                            # Line number
        ],
        Optional[
            Union[
                Callable[[], None],
                List[Statement],
            ]
        ]
    ],
    executor: ThreadPoolExecutor,
) -> Node:
    """Parses the provided content based on the provided statements"""

    assert normalized_iter.Offset == 0, normalized_iter.Offset

    statements = [statements]

    # ----------------------------------------------------------------------
    @Interface.staticderived
    class Observer(Statement.Observer):
        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnIndent():
            statements.append([])

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnDedent():
            assert statements
            statements.pop()
            assert len(statements) >= 1, statements

    # ----------------------------------------------------------------------

    root = RootNode()

    while not normalized_iter.AtEnd():
        futures = [
            (
                statement,
                executor.submit(
                    statement.Parse,
                    normalized_iter.Clone(),
                    Observer,
                ),
            )
            for statement in itertools.chain(*statements)
        ]

        successes = []
        failures = []

        for statement, future in futures:
            result = future.result()

            if result.success:
                successes.append((statement, result))
            else:
                failures.append((statement, result))

        if not successes:
            raise SyntaxErrorException(failures, normalized_iter.Line, normalized_iter.Column)

        if len(successes) > 1:
            raise SyntaxAmbiguousException(successes, normalized_iter.Line, normalized_iter.Column)

        assert len(successes) == 1
        statement, result = successes[0]

        normalized_iter = result.iter

        result = on_statement_complete(
            statement,
            _CreateNode(root, statement, result.results),
            result.iter.Line,
        )

        if result is None:
            continue

        if callable(result):
            yield result
        elif isinstance(result, list):
            statements[-1].extend(result)
        else:
            assert False, result

    assert normalized_iter.AtEnd()

    yield root


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CreateNode(
    parent: Union[RootNode, Node],
    statement: Statement,
    parse_results: Statement.ParseResultsType,
) -> Node:
    """Converts a parse result into a node"""

    node = Node(statement)

    node.Parent = parent
    parent.Children.append(node)

    for result in parse_results:
        if isinstance(result, Statement.TokenParseResultItem):
            _CreateLeaf(node, result)
        elif isinstance(result, Statement.StatementParseResultItem):
            _CreateNode(node, result.statement, result.results)
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
        result.token,
        result.whitespace,
        result.value,
        result.iter,
        result.is_ignored,
    )

    leaf.Parent = parent
    parent.Children.append(leaf)

    return leaf
