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
import textwrap
import threading
import traceback

from concurrent.futures import Future
from typing import Any, cast, Callable, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

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
    def __str__(self) -> str:
        if self.Type is None:
            return "<Root>" if isinstance(self, RootNode) else "<None>"

        return Statement.ItemTypeToString(self.Type)


# ----------------------------------------------------------------------
class _Node(_ParseResultBase):
    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(_Node, self).__post_init__()
        object.__setattr__(self, "Children", [])

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        children = [str(child).rstrip() for child in getattr(self, "Children", [])]
        if not children:
            children.append("<No children>")

        return textwrap.dedent(
            """\
            {name}
                {children}
            """,
        ).format(
            name=super(_Node, self).__str__(),
            children=StringHelpers.LeftJustify(
                "\n".join(children),
                4,
            ),
        )

    # ----------------------------------------------------------------------
    @property
    def IterBefore(self):
        node = self

        while isinstance(node, _Node):
            node = node.Children[0]         # <Has no member> pylint: disable=E1101

        return cast(Leaf, node).IterBefore

    @property
    def IterAfter(self):
        node = self

        while isinstance(node, _Node):
            node = node.Children[-1]        # <Has no member> pylint: disable=E1101

        return cast(Leaf, node).IterAfter


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
    IterBefore: NormalizedIterator          # NormalizedIterator before the token
    IterAfter: NormalizedIterator           # NormalizedIterator after the token has been consumed
    IsIgnored: bool                         # True if the result is whitespace while whitespace is being ignored

    # ----------------------------------------------------------------------
    def __str__(self):
        return "{typ} <<{value}>> ws:{ws}{ignored} [{line_before}, {column_before} -> {line_after}, {column_after}]".format(
            typ=super(Leaf, self).__str__(),
            value=str(self.Value),
            ws="None" if self.Whitespace is None else "({}, {})".format(*self.Whitespace),
            ignored=" !Ignored!" if self.IsIgnored else "",
            line_before=self.IterBefore.Line,
            column_before=self.IterBefore.Column,
            line_after=self.IterAfter.Line,
            column_after=self.IterAfter.Column,
        )


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
    def Enqueue(
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        """Enqueues the funcs for execution"""
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
        node: Node,
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

    # True to execute all statements within a single thread
    single_threaded=False,
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
        final_result = None

        # ----------------------------------------------------------------------
        def OnExit():
            nonlocal final_result

            with thread_info_lock:
                final_result = thread_info.source_lookup.get(fully_qualified_name, None)
                if final_result is None:
                    del thread_info.source_lookup[fully_qualified_name]

                    final_result = SourceInfo(None, DynamicStatementInfo([], []))

                for event in thread_info.source_pending.pop(fully_qualified_name, []):
                    event.set()

        # ----------------------------------------------------------------------

        with CallOnExit(OnExit):
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
                def OnExecuteExit():
                    with thread_info_lock:
                        assert thread_info.pending_ctr
                        thread_info.pending_ctr -= 1

                        if thread_info.pending_ctr == 0:
                            is_complete.set()

                # ----------------------------------------------------------------------

                with CallOnExit(OnExecuteExit):
                    try:
                        statement_observer = _StatementsObserver(fully_qualified_name, observer, Execute)

                        content = observer.LoadContent(fully_qualified_name)

                        results = StatementsParse(
                            initial_statement_info,
                            NormalizedIterator(Normalize(content)),
                            statement_observer,
                            single_threaded=single_threaded,
                        )

                        # The nodes have already been created, but we need to finalize the parent/child
                        # relationships.
                        root = RootNode()

                        for result in results:
                            statement_observer.CreateNode(result.Statement, result.Results, root)

                        # Get the source info
                        source_info = observer.ExtractDynamicStatementInfo(fully_qualified_name, root)

                        # Commit the results
                        with thread_info_lock:
                            assert thread_info.source_lookup[fully_qualified_name] is None                      # <Value is unscriptable> pylint: disable=E1136
                            thread_info.source_lookup[fully_qualified_name] = SourceInfo(root, source_info)     # <Does not support item assignment> pylint: disable=E1137

                    except Exception as ex:
                        assert not hasattr(ex, "Traceback")
                        object.__setattr__(ex, "Traceback", traceback.format_exc())

                        assert not hasattr(ex, "FullyQualifiedName")
                        object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

                        with thread_info_lock:
                            thread_info.errors.append(ex)   # <Has no member> pylint: disable=E1101

            elif wait_event:
                wait_event.wait()

        return final_result.SourceInfo

    # ----------------------------------------------------------------------

    if single_threaded:
        for fqn in fully_qualified_names:
            Execute(fqn)

    else:
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
class _StatementsObserver(StatementsObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        fully_qualified_name: str,
        observer: Observer,
        enqueue_content_func: Callable[[str], DynamicStatementInfo],
    ):
        self._fully_qualified_name          = fully_qualified_name
        self._observer                      = observer
        self._enqueue_content_func          = enqueue_content_func

        # Preserve cached nodes so that we don't have to continually recreate them.
        # This is also beneficial, as some statements will add context data to the
        # node when processing it.
        self.node_cache: Dict[Any, Node]    = {}
        self._node_cache_lock               = threading.Lock()

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
            self.CreateNode(
                cast(Statement, result.Statement),
                result.Results,
                parent=None,
            ),
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
    def CreateNode(
        self,
        statement: Statement,
        parse_results: Statement.ParseResultItemsType,
        parent: Optional[Union[RootNode, Node]],
    ) -> Node:
        """Converts a parse result into a node"""

        node = None
        was_cached = False

        # Look for the cached value
        key = tuple([id(statement)] + [id(result) for result in parse_results])
        if key:
            with self._node_cache_lock:
                potential_node = self.node_cache.get(key, None)             # <Has no member> pylint: disable=E1101
                if potential_node is not None:
                    node = potential_node
                    was_cached = True

        if node is None:
            node = Node(statement)

        if parent is not None:
            object.__setattr__(node, "Parent", parent)
            parent.Children.append(node)  # type: ignore

        if not was_cached:
            for result in parse_results:
                if isinstance(result, Statement.TokenParseResultItem):
                    self._CreateLeaf(result, node)
                elif isinstance(result, Statement.StatementParseResultItem):
                    self.CreateNode(cast(Statement, result.Statement), result.Results, node)
                else:
                    assert False, result  # pragma: no cover

            # Cache the node
            if key:
                with self._node_cache_lock:
                    self.node_cache[key] = node         # <Does not support item assignment> pylint: disable=E1137

        return node

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateLeaf(
        result: Statement.TokenParseResultItem,
        parent: Node,
    ) -> Leaf:
        """Converts a parse result item into a leaf"""

        leaf = Leaf(
            result.Token,
            result.Whitespace,
            result.Value,
            result.IterBefore,
            result.IterAfter,
            result.IsIgnored,
        )

        object.__setattr__(leaf, "Parent", parent)
        parent.Children.append(leaf)  # type: ignore

        return leaf
