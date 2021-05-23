# ----------------------------------------------------------------------
# |
# |  MultifileParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-11 10:50:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that parses multiple files"""

import os
import threading
import traceback

from concurrent.futures import Future
from typing import cast, Callable, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error
    from .Normalize import Normalize
    from .NormalizedIterator import NormalizedIterator
    from .Statement import Statement

    from .StatementsParser import (
        DynamicStatementInfo,
        Observer as StatementsObserver,
        Parse as StatementsParse,
    )

    from .Token import Token

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UnknownSourceError(Error):
    SourceName: str

    MessageTemplate                         = Interface.DerivedProperty("'{SourceName}' could not be found")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ParseResultBase(object):
    """Base class for parsed AST entities"""

    Type: Union[Optional[Statement], Token]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        object.__setattr__(self, "Parent", None)


# ----------------------------------------------------------------------
class _Node(_ParseResultBase):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(_Node, self).__init__(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(_Node, self).__post_init__()
        object.__setattr__(self, "Children", [])


# ----------------------------------------------------------------------
class RootNode(_Node):
    # ----------------------------------------------------------------------
    def __init__(self):
        super(RootNode, self).__init__(None)


# ----------------------------------------------------------------------
class Node(_Node):
    """AST results of a Statement"""

    # ----------------------------------------------------------------------
    # <Useless super delegation> pylint: disable=W0235
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
    @dataclass(frozen=True)
    class ImportInfo(object):
        SourceName: str
        FullyQualifiedName: Optional[str]   # None if the SourceName cannot be resolved

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def LoadContent(
        fully_qualified_name: str
    ) -> str:
        """Returns the content associated with the fully qualified name"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractDynamicStatementInfo(
        fully_qualified_name: str,
        node: RootNode,
    ) -> DynamicStatementInfo:
        """Extracts statements from parsed content"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        """Enqueues the funcs for execution"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIndent(
        fully_qualified_name: str,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDedent(
        fully_qualified_name: str,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStatementComplete(
        fully_qualified_name: str,
        result: Statement.StatementParseResultItem,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement (if necessary)
        "Observer.ImportInfo",              # Import information generated by the statement
    ]:
        """Called on the completion of each statement"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def Parse(
    fully_qualified_names: List[str],
    initial_statement_info: DynamicStatementInfo,
    observer: Observer,
) -> Union[
    Dict[str, RootNode],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    @dataclass
    class SourceInfo(object):
        Node: RootNode
        SourceInfo: DynamicStatementInfo

    # ----------------------------------------------------------------------
    @dataclass
    class ThreadInfo(object):
        pending_ctr: int                                                    = 0

        source_lookup: Dict[str, Optional[SourceInfo]]                      = field(default_factory=dict)
        source_pending: Dict[str, List[threading.Event]]                    = field(default_factory=dict)

        errors: List[Exception]                                             = field(default_factory=list)

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo()
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    # TODO: Check for import cycles
    def Execute(fully_qualified_name) -> DynamicStatementInfo:
        with thread_info_lock:
            if fully_qualified_name not in thread_info.source_lookup:       # <Value doesn't support membership test> pylint: disable=E1135
                should_execute = True
                wait_event = None

                thread_info.source_lookup[fully_qualified_name] = None      # <Value doesn't support item assignment> pylint: disable=E1137
                thread_info.pending_ctr += 1

            else:
                source_info = thread_info.source_lookup[fully_qualified_name]                       # <Value is unscriptable> pylint: disable=E1136
                if source_info is not None:
                    return source_info.SourceInfo

                should_execute = False
                wait_event = threading.Event()

                thread_info.source_pending.setdefault(fully_qualified_name, []).append(wait_event)  # <Has no member> pylint: disable=E1101

        if should_execute:
            # ----------------------------------------------------------------------
            def OnExit():
                with thread_info_lock:
                    assert thread_info.pending_ctr
                    thread_info.pending_ctr -= 1

                    if thread_info.pending_ctr == 0:
                        is_complete.set()

            # ----------------------------------------------------------------------

            with CallOnExit(OnExit):
                try:
                    results = StatementsParse(
                        initial_statement_info,
                        NormalizedIterator(Normalize(observer.LoadContent(fully_qualified_name))),
                        _StatementsObserver(
                            fully_qualified_name,
                            observer,
                            Execute,
                        ),
                    )

                    # Convert to Node
                    root = RootNode()

                    for result in results:
                        _CreateNode(root, cast(Statement, result.Statement), result.Results)

                    # Get the source info
                    source_info = observer.ExtractDynamicStatementInfo(fully_qualified_name, root)

                    # Commit the results
                    with thread_info_lock:
                        assert thread_info.source_lookup[fully_qualified_name] is None                      # <Value is unscriptable> pylint: disable=E1136
                        thread_info.source_lookup[fully_qualified_name] = SourceInfo(root, source_info)     # <Does not support item assignment> pylint: disable=E1137

                        for event in thread_info.source_pending.pop(fully_qualified_name, []):      # <Has no member> pylint: disable=E1101
                            event.set()

                except Exception as ex:
                    assert not hasattr(ex, "Traceback")
                    object.__setattr__(ex, "Traceback", traceback.format_exc())

                    assert not hasattr(ex, "FullyQualifiedName")
                    object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

                    with thread_info_lock:
                        thread_info.errors.append(ex)   # <Has no member> pylint: disable=E1101

        elif wait_event:
            wait_event.wait()

        with thread_info_lock:
            return thread_info.source_lookup[fully_qualified_name].SourceInfo  # <Value is unscriptable> pylint: disable=E1136

    # ----------------------------------------------------------------------

    observer.Enqueue(
        [
            cast(Callable[[], None], lambda fqn=fqn: Execute(fqn))
            for fqn in fully_qualified_names
        ],
    )

    is_complete.wait()

    assert not thread_info.source_pending, thread_info.source_pending

    if thread_info.errors:
        return thread_info.errors

    return {fqn: si.Node for fqn, si in thread_info.source_lookup.items()}  # <Has no member> pylint: disable=E1101


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _StatementsObserver(StatementsObserver):
    _fully_qualified_name: str
    _observer: Observer
    _enqueue_content_func: Callable[[str], DynamicStatementInfo]

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        return self._observer.Enqueue(funcs)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnIndent(
        self,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        return self._observer.OnIndent(self._fully_qualified_name, statement, results)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(
        self,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ):
        return self._observer.OnDedent(self._fully_qualified_name, statement, results)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnStatementComplete(
        self,
        result: Statement.StatementParseResultItem,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement (if necessary)
    ]:
        this_result = self._observer.OnStatementComplete(
            self._fully_qualified_name,
            result,
            iter_before,
            iter_after,
        )

        if isinstance(this_result, Observer.ImportInfo):
            if not this_result.FullyQualifiedName:
                raise UnknownSourceError(
                    iter_before.Line,
                    iter_before.Column,
                    this_result.SourceName,
                )

            return self._enqueue_content_func(this_result.FullyQualifiedName)

        return this_result


# ----------------------------------------------------------------------
def _CreateNode(
    parent: Union[RootNode, Node],
    statement: Statement,
    parse_results: Statement.ParseResultItemsType,
) -> Node:
    """Converts a parse result into a node"""

    node = Node(statement)

    object.__setattr__(node, "Parent", parent)
    parent.Children.append(node)  # type: ignore

    for result in parse_results:
        if isinstance(result, Statement.TokenParseResultItem):
            _CreateLeaf(node, result)
        elif isinstance(result, Statement.StatementParseResultItem):
            _CreateNode(node, cast(Statement, result.Statement), result.Results)
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
    parent.Children.append(leaf)  # type: ignore

    return leaf
