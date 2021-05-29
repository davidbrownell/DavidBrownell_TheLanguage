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
from typing import cast, Callable, Dict, List, Optional, Tuple, Union

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
    from .StatementEx import StatementEx

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

    Type: Union[Optional[StatementEx], Token]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        object.__setattr__(self, "Parent", None)

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        if self.Type is None:
            return "<None>"

        return StatementEx.ItemTypeToString(self.Type)


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
    def __str__(self) -> str:
        children = [str(child) for child in getattr(self, "Children", [])]
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
            ).rstrip(),
        )


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
        statement: StatementEx,
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
    def __str__(self):
        return "{} <<{}>> [{}, {}]".format(
            super(Leaf, self).__str__(),
            str(self.Value),
            self.Iter.Line,
            self.Iter.Column,
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
        statement: StatementEx,
        results: StatementEx.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDedent(
        fully_qualified_name: str,
        statement: StatementEx,
        results: StatementEx.ParseResultItemsType,
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
    single_threaded = True # BugBug

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
                        _StatementsObserver(fully_qualified_name, observer, Execute),
                        single_threaded=single_threaded,
                    )

                    # The nodes have already been created, but we need to finalize the parent/child
                    # relationships.
                    root = RootNode()

                    UpdateRelationships(root, results)

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
    def UpdateRelationships(
        parent: Union[RootNode, Node],
        results: StatementEx.ParseResultItemsType,
    ):
        for result in results:
            if not isinstance(result, StatementEx.StatementParseResultItem):
                continue

            # The node attribute was set when the statement was completed
            node = getattr(result, "_node", None)
            if node is None:
                continue

            assert node is not None

            if node.Parent:
                assert node.Parent == parent
            else:
                object.__setattr__(node, "Parent", parent)
                parent.Children.append(node)

            children_results = getattr(result, "Results", None)
            if children_results:
                UpdateRelationships(node, children_results)

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
        statement: StatementEx,
        results: StatementEx.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        return self._observer.OnIndent(self._fully_qualified_name, statement, results)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(
        self,
        statement: StatementEx,
        results: StatementEx.ParseResultItemsType,
    ):
        return self._observer.OnDedent(self._fully_qualified_name, statement, results)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnStatementComplete(
        self,
        result: StatementEx.StatementParseResultItem,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement (if necessary)
    ]:
        node = _CreateNode(
            cast(StatementEx, result.Statement),
            result.Results,
            parent=None,
        )

        # Associate the node with the result so that we can retrieve it later
        object.__setattr__(result, "_node", node)

        this_result = self._observer.OnStatementComplete(
            self._fully_qualified_name,
            node,
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
    statement: StatementEx,
    parse_results: StatementEx.ParseResultItemsType,
    parent: Optional[Union[RootNode, Node]],
) -> Node:
    """Converts a parse result into a node"""

    node = Node(statement)

    if parent is not None:
        object.__setattr__(node, "Parent", parent)
        parent.Children.append(node)  # type: ignore

    for result in parse_results:
        if isinstance(result, StatementEx.TokenParseResultItem):
            _CreateLeaf(result, node)
        elif isinstance(result, StatementEx.StatementParseResultItem):
            _CreateNode(cast(StatementEx, result.Statement), result.Results, node)
        else:
            assert False, result

    return node


# ----------------------------------------------------------------------
def _CreateLeaf(
    result: StatementEx.TokenParseResultItem,
    parent: Node,
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
