# ----------------------------------------------------------------------
# |
# |  TranslationUnitsParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-02 11:23:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality to parse multiple translation units simultaneously"""

import asyncio
import os
import textwrap
import threading
import traceback

from concurrent.futures import Future
from typing import Any, Awaitable, Callable, cast, Dict, List, Optional, Tuple, Union

import nest_asyncio

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

    from .StatementEx import (
        Statement,
        TokenClass as Token,
        TokenStatement,
    )

    from .TranslationUnitParser import (
        DynamicStatementInfo,
        Observer as TranslationUnitObserver,
        ParseAsync as TranslationUnitParseAsync,
    )


# ----------------------------------------------------------------------
nest_asyncio.apply()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UnknownSourceError(Error):
    SourceName: str

    MessageTemplate                         = Interface.DerivedProperty("'{SourceName}' could not be found")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ParseResultBase(Interface.Interface):
    """Base class for parsed AST entities"""

    Type: Union[None, Statement, Token]

    Parent: Optional[Statement]             = field(
        default_factory=lambda: None,
        init=False,
    )

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.ToString()

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def ToString(
        self,
        verbose=False,
    ) -> str:
        if self.Type is None:
            return "<Root>" if isinstance(self, RootNode) else "<None>"

        return self.Type.Name


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _Node(_ParseResultBase):
    Children: List[Union["_Node", "Leaf"]]  = field(
        default_factory=list,
        init=False,
    )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        verbose=False,
    ) -> str:
        children = [
            child.ToString(
                verbose=verbose,
            ).rstrip()
            for child in self.Children
        ]

        if not children:
            children.append("<No Children>")

        return textwrap.dedent(
            """\
            {heading}
                {children}
            """,
        ).format(
            heading=super(_Node, self).ToString(
                verbose=verbose,
            ),
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
            node = node.Children[0]

        return cast(Leaf, node).IterBefore

    @property
    def IterAfter(self):
        node = self

        while isinstance(node, _Node):
            node = node.Children[-1]

        return cast(Leaf, node).IterAfter


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RootNode(_Node):
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Node(_Node):
    """AST results of a Statement"""
    pass


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
    @Interface.override
    def ToString(
        self,
        verbose=False,
    ) -> str:
        return "{typ} <<{value}>> ws:{ws}{ignored} [{line_before}, {column_before} -> {line_after}, {column_after}]".format(
            typ=super(Leaf, self).ToString(
                verbose=verbose,
            ),
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
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ImportInfo(object):
        SourceName: str
        FullyQualifiedName: Optional[str]   # None if the SourceName cannot be resolved

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def LoadContent(
        fully_qualified_name: str,
    ) -> str:
        """Returns the content associated with the fully qualified name"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        """Enqueues the funcs for execution on a thread pool"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractDynamicStatements(
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
        data: Statement.TokenParseResultData,
    ) -> Optional[DynamicStatementInfo]:
        """Event generated on the creation of a new scope"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDedent(
        fully_qualified_name: str,
        data: Statement.TokenParseResultData,
    ) -> None:
        """Event generated on the end of a scope"""
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
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement
        "Observer.ImportInfo",              # Import information generated by the statement
    ]:
        """Called on the completion of each statement"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    fully_qualified_names: List[str],
    initial_statement_info: DynamicStatementInfo,
    observer: Observer,
    single_threaded=False,
) -> Union[
    None,
    Dict[str, RootNode],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    class SourceInfo(object):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            node: Optional[RootNode],
            statement_info: DynamicStatementInfo,
        ):
            self.Node                       = node
            self.StatementInfo              = statement_info

    # ----------------------------------------------------------------------
    class ThreadInfo(object):
        def __init__(self):
            self.pending_ctr                                                = 0

            self.source_lookup: Dict[str, Optional[SourceInfo]]             = {}
            self.source_pending: Dict[str, List[threading.Event]]           = {}

            self.errors: List[Exception]                                    = []

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo()
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    async def ExecuteAsync(
        fully_qualified_name,
        increment_pending_ctr=True,
    ) -> DynamicStatementInfo:
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
                if fully_qualified_name not in thread_info.source_lookup:
                    should_execute = True
                    wait_event = None

                    thread_info.source_lookup[fully_qualified_name] = None

                    if increment_pending_ctr:
                        thread_info.pending_ctr += 1

                else:
                    source_info = thread_info.source_lookup[fully_qualified_name]
                    if source_info is not None:
                        return source_info.StatementInfo

                    should_execute = False
                    wait_event = threading.Event()

                    thread_info.source_pending.setdefault(fully_qualified_name, []).append(wait_event)

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
                        statement_observer = _StatementsObserver(fully_qualified_name, observer, ExecuteAsync)

                        content = observer.LoadContent(fully_qualified_name)

                        results = await TranslationUnitParseAsync(
                            initial_statement_info,
                            NormalizedIterator(Normalize(content)),
                            statement_observer,
                            single_threaded=single_threaded,
                        )

                        # BugBug: What happens when results is None?

                        # The noes have already been created, but we need to finalize
                        # the relationships.
                        root = RootNode(None)

                        for result in results:
                            statement_observer.CreateNode(result.Statement, result.Data, root)

                        # Get the Dynamic Statements
                        dynamic_statements = observer.ExtractDynamicStatements(fully_qualified_name, root)

                        # Commit the results
                        with thread_info_lock:
                            assert thread_info.source_lookup[fully_qualified_name] is None
                            thread_info.source_lookup[fully_qualified_name] = SourceInfo(root, dynamic_statements)

                    except Exception as ex:
                        assert not hasattr(ex, "Traceback")
                        object.__setattr__(ex, "Traceback", traceback.format_exc())

                        assert not hasattr(ex, "FullyQualifiedName")
                        object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

                        with thread_info_lock:
                            thread_info.errors.append(ex)

            elif wait_event:
                wait_event.wait()

        assert final_result
        return final_result.StatementInfo

    # ----------------------------------------------------------------------
    def PrepLoopAndExecute(
        fully_qualified_name,
        increment_pending_ctr=True,
    ):
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)

        try:
            return thread_loop.run_until_complete(
                ExecuteAsync(
                    fully_qualified_name,
                    increment_pending_ctr=increment_pending_ctr,
                ),
            )
        finally:
            thread_loop.close()

    # ----------------------------------------------------------------------

    if single_threaded:
        for fqn in fully_qualified_names:
            await ExecuteAsync(fqn)

    else:
        with thread_info_lock:
            # Prepopulate the pending ctr so that we can make sure that we don't
            # prematurely terminate as threads are spinning up.
            thread_info.pending_ctr = len(fully_qualified_names)

        observer.Enqueue(
            [
                cast(Callable[[], None], lambda fqn=fqn: PrepLoopAndExecute(fqn, increment_pending_ctr=False))
                for fqn in fully_qualified_names
            ],
        )

    is_complete.wait()

    assert not thread_info.source_pending, thread_info.source_pending

    if thread_info.errors:
        return thread_info.errors

    return {
        fqn: cast(RootNode, cast(SourceInfo, si).Node)
        for fqn, si in thread_info.source_lookup.items()
    }


# ----------------------------------------------------------------------
def Parse(*args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(ParseAsync(*args, **kwargs))


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _StatementsObserver(TranslationUnitObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        fully_qualified_name: str,
        observer: Observer,
        async_parse_func: Callable[[str], Awaitable[DynamicStatementInfo]],
    ):
        self._fully_qualified_name          = fully_qualified_name
        self._observer                      = observer
        self._async_parse_func              = async_parse_func

        # Preserve cached nodes so that we don't have to continually recreate them.
        # This is also beneficial, as some statements will add context data to the
        # node when processing it.
        self._node_cache: Dict[Any, Node]   = {}
        self._node_cache_lock               = threading.Lock()

    # ----------------------------------------------------------------------
    @Interface.override
    def OnIndent(
        self,
        data: Statement.TokenParseResultData,
    ):
        return self._observer.OnIndent(self._fully_qualified_name, data)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(
        self,
        data: Statement.TokenParseResultData,
    ):
        return self._observer.OnDedent(self._fully_qualified_name, data)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnStatementComplete(
        self,
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,
        DynamicStatementInfo,
    ]:
        this_result = self._observer.OnStatementComplete(
            self._fully_qualified_name,
            self.CreateNode(
                statement,
                data,
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

            return asyncio.get_event_loop().run_until_complete(self._async_parse_func(this_result.FullyQualifiedName))

        return this_result

    # ----------------------------------------------------------------------
    def CreateNode(
        self,
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        parent: Optional[Union[RootNode, Node]],
    ) -> Node:
        node: Optional[Node] = None
        was_cached = False

        # Look for the cached value
        key = tuple([id(statement)] + ([id(child_data) for _, child_data in data.Enum()]) if data else [])
        if key:
            with self._node_cache_lock:
                potential_node = self._node_cache.get(key, None)
                if potential_node is not None:
                    node = potential_node
                    was_cached = True

        if node is None:
            node = Node(statement)

        if parent is not None:
            object.__setattr__(node, "Parent", parent)
            parent.Children.append(node)

        if not was_cached:
            for child_statement, child_data in data.Enum() if data else []:
                if isinstance(child_statement, TokenStatement):
                    this_child_statement, this_child_data = next(child_data.Enum())
                    assert this_child_statement is None

                    self._CreateLeaf(
                        cast(Statement.TokenParseResultData, this_child_data),
                        node,
                    )

                else:
                    self.CreateNode(child_statement, child_data, node)

            if key:
                with self._node_cache_lock:
                    self._node_cache[key] = node

        return node

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateLeaf(
        data: Statement.TokenParseResultData,
        parent: Node,
    ) -> Leaf:
        leaf = Leaf(
            data.Token,
            data.Whitespace,
            data.Value,
            data.IterBefore,
            data.IterAfter,
            data.IsIgnored,
        )

        object.__setattr__(leaf, "Parent", parent)
        parent.Children.append(leaf)

        return leaf
