# ----------------------------------------------------------------------
# |
# |  TranslationUnitLexer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 09:46:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that can lex a single translation unit"""

import os
import threading

from collections import OrderedDict
from typing import Any, Awaitable, cast, Callable, Dict, Generator, List, Optional, Set, Tuple, Union

from dataclasses import dataclass, field
import inflect as inflect_mod

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import CreateError, Location

    from .Components import AST
    from .Components.Phrase import EnqueueAsyncItemType, NormalizedIterator, Phrase
    from .Components.Tokens import RegexToken

    from .Phrases.DSL import CreatePhrase, DynamicPhrasesType
    from .Phrases.DynamicPhrase import DynamicPhrase
    from .Phrases.OrPhrase import OrPhrase
    from .Phrases.RepeatPhrase import RepeatPhrase
    from .Phrases.SequencePhrase import SequencePhrase
    from .Phrases.TokenPhrase import TokenPhrase


# ----------------------------------------------------------------------
inflect                                     = inflect_mod.engine()


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
InvalidDynamicTraversalError                = CreateError(
    "Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dynamic phrases the first ones applied in this lexical scope.",
    existing_dynamic_phrases=Location,
)


SyntaxInvalidError                          = CreateError(
    "The syntax is not recognized [Ln {line}, Col {column}]: {error_context}",
    line=int,
    column=int,
    error_context=str,
    error_node=AST.Node,
)

# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DynamicPhrasesInfo(ObjectReprImplBase):
    phrases: Dict[DynamicPhrasesType, List[Phrase]]
    allow_parent_traversal: bool            = field(default=True)
    name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert all(phrases for phrases in self.phrases.values())

        ObjectReprImplBase.__init__(
            self,
            phrases=lambda value: "\n".join(
                [
                    "- {}: [{}]".format(
                        key,
                        ", ".join("'{}'".format(phrase.name) for phrase in value),
                    )
                    for key, value in value.items()
                ],
            ),
        )

    # ----------------------------------------------------------------------
    def __bool__(self):
        return bool(self.phrases)

    # ----------------------------------------------------------------------
    def Clone(
        self,
        new_phrases: Optional[Dict[DynamicPhrasesType, List[Phrase]]]=None,
        new_allow_parent_traversal: Optional[bool]=None,
        new_name: Optional[str]=None,
    ) -> "DynamicPhrasesInfo":
        return DynamicPhrasesInfo.Create(
            self.phrases if new_phrases is None else new_phrases,
            self.allow_parent_traversal if new_allow_parent_traversal is None else new_allow_parent_traversal,
            self.name if new_name is None else new_name,
        )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def GetParentStatementNode(
        node: AST.Node,
    ) -> Optional[AST.Node]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        func_infos: List[EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPushScope(
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPopScope(
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPhraseComplete(
        phrase: Phrase,
        iter_range: Phrase.NormalizedIteratorRange,
        node: AST.Node,
    ) -> Union[
        bool,                               # True to continue, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phrases to add to the active scope as a result of completing this phrase
    ]:
        """Invoked when an internal phrase is successfully matched"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Lex(
    comment_token: RegexToken,
    initial_phrase_info: DynamicPhrasesInfo,
    normalized_iter: NormalizedIterator,
    observer: Observer,
    single_threaded=False,
    name: Optional[str]=None,
) -> Optional[AST.Node]:
    """Repeatedly matches the statements for everything within the iterator"""

    assert normalized_iter.offset == 0, normalized_iter

    phrase_observer = _PhraseObserver(
        observer,
        normalized_iter,
        initial_phrase_info,
    )

    root_phrase = CreatePhrase(
        DynamicPhrasesType.Statements,
        name=name,
        comment_token=comment_token,
    )

    root_node = AST.Node(None)

    while not normalized_iter.AtEnd():
        phrase_observer.ClearNodeCache()

        result = root_phrase.Lex(
            ("root", ),
            normalized_iter,
            phrase_observer,
            single_threaded=single_threaded,
            ignore_whitespace=False,
        )

        if result is None or result.data is None:
            return None

        phrase_observer.CreateNode(result.data, root_node)

        if not result.success:
            root_node.FinalInit()

            # Initialize all of the potential error nodes now that we know that there is an actual error
            for node in root_node.Enum(
                nodes_only=True,
            ):
                potential_error_node = getattr(node, _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME, None)
                if potential_error_node is not None:
                    potential_error_node.FinalInit()

            raise _CreateSyntaxInvalidError(
                root_node,
                result.iter_range.end,
                observer.GetParentStatementNode,
            )

        normalized_iter = result.iter_range.end.Clone()

    root_node.FinalInit()

    assert normalized_iter.AtEnd()
    return root_node


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
_POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME        = "_error_context_node"


# ----------------------------------------------------------------------
class _ScopeTracker(object):
    """Manages access to scopes impacted by phrase modifications via DynamicPhraseInfo objects"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        normalized_iter: NormalizedIterator,
        initial_phrase_info: DynamicPhrasesInfo,
    ):
        # Initialize the tracker nodes
        tracker_nodes: Dict[
            Union[str, _ScopeTracker._DefaultScopeTrackerTag],
            _ScopeTracker._TrackerNode
        ] = OrderedDict()

        tracker_nodes[self._DefaultScopeTrackerTagInstance] = _ScopeTracker._TrackerNode(
            unique_id_part="",
            scope_items=[
                _ScopeTracker._ScopeItem(
                    0,
                    normalized_iter.Clone(),
                    initial_phrase_info,
                ),
            ],
        )

        # Create the cache info
        cache: Dict[
            DynamicPhrasesType,
            Dict[
                Tuple[str, ...],            # unique_id
                Tuple[List[Phrase], Optional[str]]
            ]
        ] = {}

        # Commit
        self._tracker_nodes                 = tracker_nodes
        self._cache                         = cache

    # ----------------------------------------------------------------------
    def AddNode(
        self,
        unique_id: Tuple[str, ...],
    ) -> None:
        d = self._tracker_nodes

        for id_part in unique_id:
            tracker_node = d.get(id_part, None)
            if tracker_node is None:
                tracker_node = _ScopeTracker._TrackerNode(id_part)
                d[id_part] = tracker_node

            d = tracker_node.children

    # ----------------------------------------------------------------------
    def RemoveNode(
        self,
        unique_id: Tuple[str, ...],
        was_successful: bool,
    ) -> None:
        # Get the tracker node
        tracker_node: Optional[_ScopeTracker._TrackerNode] = None

        d = self._tracker_nodes

        for id_part in unique_id:
            tracker_node = d.get(id_part, None)
            assert tracker_node is not None

            d = tracker_node.children

        assert tracker_node is not None

        clear_cache_types: Set[DynamicPhrasesType] = set()

        # ----------------------------------------------------------------------
        def ProcessScopeItems(
            scope_items: List[_ScopeTracker._ScopeItem],
        ) -> None:
            for scope_item in scope_items:
                for dynamic_phrase_info in scope_item.info.phrases.keys():
                    clear_cache_types.add(dynamic_phrase_info)

        # ----------------------------------------------------------------------

        if not tracker_node.scope_items:
            if was_successful:
                # Move all the items found int the descendants to this node

                # ----------------------------------------------------------------------
                def OnDescendantTrackerNode(
                    descendant_tracker_node: _ScopeTracker._TrackerNode,
                ) -> None:
                    tracker_node.scope_items += descendant_tracker_node.scope_items  # type: ignore

                # ----------------------------------------------------------------------

                on_descendant_tracker_node_func = OnDescendantTrackerNode

            else:
                on_descendant_tracker_node_func = lambda *args, **kwargs: None

            for descendant_tracker_node in tracker_node.EnumChildren():
                on_descendant_tracker_node_func(descendant_tracker_node)
                ProcessScopeItems(descendant_tracker_node.scope_items)

        elif not was_successful:
            ProcessScopeItems(tracker_node.scope_items)
            tracker_node.scope_items = []  # type: ignore

        tracker_node.children = {}  # type: ignore

        if self._cache:
            for dynamic_phrases_type in clear_cache_types:
                self._cache.pop(dynamic_phrases_type)

    # ----------------------------------------------------------------------
    def AddScopeItem(
        self,
        unique_id: Tuple[str, ...],
        indentation_level: int,
        iter_range: Phrase.NormalizedIteratorRange,
        dynamic_phrases_info: DynamicPhrasesInfo,
    ) -> None:
        if not dynamic_phrases_info:
            return

        this_tracker_node: Optional[_ScopeTracker._TrackerNode] = None
        last_scope_item: Optional[_ScopeTracker._ScopeItem] = None

        # The tracker node associated with this event will be the last one that we encounter when enumerating
        # through the previous tracker nodes. In addition to the current tracker node, get the last dynamic
        # info associated with all of the scope_trackers to determine if adding this dynamic info will be a problem.
        for tracker_node in self._EnumPrevious(unique_id):
            this_tracker_node = tracker_node

            if tracker_node.scope_items:
                last_scope_item = tracker_node.scope_items[-1]

        assert this_tracker_node is not None
        assert this_tracker_node.unique_id_part == unique_id[-1], (this_tracker_node.unique_id_part, unique_id[-1])

        if (
            not dynamic_phrases_info.allow_parent_traversal
            and last_scope_item is not None
            and last_scope_item.indentation_level == indentation_level
        ):
            raise InvalidDynamicTraversalError.Create(
                location=iter_range.end.ToLocation(),
                existing_dynamic_phrases=last_scope_item.iter_end.ToLocation(),
            )

        this_tracker_node.scope_items.append(
            _ScopeTracker._ScopeItem(
                indentation_level,
                iter_range.end.Clone(),
                dynamic_phrases_info,
            ),
        )

        if self._cache:
            for dynamic_phrases_type in dynamic_phrases_info.phrases.keys():
                self._cache.pop(dynamic_phrases_type, None)

    # ----------------------------------------------------------------------
    def RemoveScopeItems(
        self,
        unique_id: Tuple[str, ...],
        indentation_level: int,
    ) -> None:
        clear_cache_types: Set[DynamicPhrasesType] = set()

        for tracker_node in self._EnumPrevious(unique_id):
            if not tracker_node.scope_items:
                continue

            item_index = 0
            while item_index < len(tracker_node.scope_items):
                scope_item = tracker_node.scope_items[item_index]

                if scope_item.indentation_level == indentation_level:
                    for dynamic_phrases_type in scope_item.info.phrases.keys():
                        clear_cache_types.add(dynamic_phrases_type)

                    del tracker_node.scope_items[item_index]
                else:
                    item_index += 1

        if self._cache:
            for dynamic_phrases_type in clear_cache_types:
                self._cache.pop(dynamic_phrases_type, None)

    # ----------------------------------------------------------------------
    def GetDynamicPhrases(
        self,
        unique_id: Tuple[str, ...],
        dynamic_phrases_type: DynamicPhrasesType,
    ) -> Tuple[List[Phrase], Optional[str]]:
        # Find a cached value (if any)
        cache = self._cache.setdefault(dynamic_phrases_type, {})

        cache_value = cache.get(unique_id, None)
        if cache_value is not None:
            return cache_value

        # Calculate the result
        all_phrases: List[Phrase] = []
        all_names: List[str] = []

        processed_dynamic_infos: Set[int] = set()
        processed_phrases: Set[int] = set()

        should_continue = True

        # Process the phrases from the most recently added to those added long ago (this is the
        # reason why 'reversed' is in the code that follows).
        previous_tracker_nodes = list(self._EnumPrevious(unique_id))

        for tracker_node in reversed(previous_tracker_nodes):
            these_phrases: List[Phrase] = []
            these_names: List[str] = []

            for scope_item in tracker_node.scope_items:
                dynamic_info = scope_item.info

                # Have we seen this before?
                dynamic_info_key = id(dynamic_info)

                if dynamic_info_key in processed_dynamic_infos:
                    continue

                processed_dynamic_infos.add(dynamic_info_key)

                # Get the phrases
                phrases = scope_item.info.phrases.get(dynamic_phrases_type, None)
                if phrases is None:
                    continue

                prev_these_phrases_length = len(these_phrases)

                for phrase in phrases:
                    # Have we seen this phrase before?
                    phrase_key = id(phrase)

                    if phrase_key in processed_phrases:
                        continue

                    processed_phrases.add(phrase_key)

                    these_phrases.append(phrase)

                # No need to continue this iteration if we didn't see any new phrases
                if len(these_phrases) == prev_these_phrases_length:
                    continue

                these_names.append(dynamic_info.name or "({})".format(" | ".join(phrase.name for phrase in these_phrases[prev_these_phrases_length:])))

                if not dynamic_info.allow_parent_traversal:
                    should_continue = False
                    break

            if these_phrases:
                all_phrases = these_phrases + all_phrases
            if these_names:
                all_names = these_names + all_names

            if not should_continue:
                break

        result = (all_phrases, " / ".join(all_names))

        # Update the cache
        cache[unique_id] = result

        return result

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    class _DefaultScopeTrackerTag(object):
        """\
        Unique type used as a key in `_ScopeTracker` directionaries; this is used rather
        than a normal value (for example, `None`) to allow for any key types.
        """
        pass

    _DefaultScopeTrackerTagInstance         = _DefaultScopeTrackerTag()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _ScopeItem(object):
        indentation_level: int
        iter_end: NormalizedIterator
        info: DynamicPhrasesInfo

    # ----------------------------------------------------------------------
    @dataclass
    class _TrackerNode(object):
        unique_id_part: str

        children: Dict[
            Union[str, "_ScopeTracker._DefaultScopeTrackerTag"],
            "_ScopeTracker._TrackerNode"
        ] = field(default_factory=OrderedDict)

        scope_items: List["_ScopeTracker._ScopeItem"]   = field(default_factory=list)

        # ----------------------------------------------------------------------
        def EnumChildren(self) -> Generator["_ScopeTracker._TrackerNode", None, None]:
            for child in self.children.values():  # type: ignore  # pylint: disable=no-member
                yield child
                yield from child.EnumChildren()

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _EnumPrevious(
        self,
        unique_id: Tuple[str, ...],
    ) -> Generator["_ScopeTracker._TrackerNode", None, None]:
        yield self._tracker_nodes[self._DefaultScopeTrackerTagInstance]

        d = self._tracker_nodes

        for id_part in unique_id:
            for k, tracker_node in d.items():
                if k == self._DefaultScopeTrackerTagInstance:
                    continue

                yield tracker_node

                if k == id_part:
                    d = tracker_node.children
                    break


# ----------------------------------------------------------------------
class _PhraseObserver(Phrase.Observer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: Observer,
        normalized_iter: NormalizedIterator,
        initial_phrase_info: DynamicPhrasesInfo,
    ):
        self._observer                      = observer

        self._scope_tracker                 = _ScopeTracker(normalized_iter, initial_phrase_info)
        self._scope_tracker_lock            = threading.Lock()

        self._scope_level                   = 0

        self._node_cache: Dict[Tuple[str, ...], Union[AST.Leaf, AST.Node]]  = {}

    # ----------------------------------------------------------------------
    def ClearNodeCache(self):
        self._node_cache.clear()

    # ----------------------------------------------------------------------
    def CreateNode(
        self,
        data: Phrase.LexResultData,
        parent: Optional[AST.Node],
    ) -> Union[AST.Leaf, AST.Node]:
        node: Optional[Union[AST.Leaf, AST.Node]] = None

        # Look for the cached value
        cache_key = data.unique_id

        if cache_key is not None:
            node = self._node_cache.get(cache_key, None)

        if node is not None:
            was_cached = True
        else:
            was_cached = False

            if isinstance(data.phrase, TokenPhrase) and data.data is not None:
                node = self.__class__.CreateLeaf(cast(Phrase.TokenLexResultData, data.data), parent)
            else:
                node = AST.Node(data.phrase)

        assert node is not None

        # Assign the parent (if necessary)
        if parent != node.parent:
            assert parent is not None

            object.__setattr__(node, "parent", parent)
            parent.children.append(node)

        # Populate the children (if necessary)
        if not was_cached:
            if isinstance(node, AST.Node) and data.data is not None:
                if isinstance(data.data, Phrase.LexResultData):
                    data_items = [data.data]
                elif isinstance(data.data, list):
                    data_items = data.data
                else:
                    assert False, data.data  # pragma: no cover

                for data_item in data_items:
                    if isinstance(data_item, Phrase.LexResultData):
                        self.CreateNode(data_item, node)
                    elif isinstance(data_item, Phrase.TokenLexResultData):
                        self.__class__.CreateLeaf(data_item, node)
                    else:
                        assert False, data_item  # pragma: no cover

            if cache_key is not None:
                self._node_cache[cache_key] = node

        if data.potential_error_context is not None:
            potential_error_node = self.CreateNode(data.potential_error_context, None)
            object.__setattr__(node, _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME, potential_error_node)

        return node

    # ----------------------------------------------------------------------
    @staticmethod
    def CreateLeaf(
        data: Phrase.TokenLexResultData,
        parent: Optional[AST.Node],
    ) -> AST.Leaf:
        leaf = AST.Leaf(
            data.token,
            data.value,
            data.iter_range,
            data.is_ignored,
        )

        if parent:
            object.__setattr__(leaf, "parent", parent)
            parent.children.append(leaf)

        return leaf

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        func_infos: List[EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        return self._observer.Enqueue(func_infos)

    # ----------------------------------------------------------------------
    @Interface.override
    def GetDynamicPhrases(
        self,
        unique_id: Tuple[str, ...],
        phrases_type: DynamicPhrasesType,
    ) -> Tuple[List[Phrase], Optional[str]]:
        with self._scope_tracker_lock:
            return self._scope_tracker.GetDynamicPhrases(unique_id, phrases_type)

    # ----------------------------------------------------------------------
    @Interface.override
    def StartPhrase(
        self,
        unique_id: Tuple[str, ...],
        phrase: Phrase,
    ) -> None:
        with self._scope_tracker_lock:
            self._scope_tracker.AddNode(unique_id)

    # ----------------------------------------------------------------------
    @Interface.override
    def EndPhrase(
        self,
        unique_id: Tuple[str, ...],
        phrase: Phrase,
        was_successful: bool,
    ) -> None:
        with self._scope_tracker_lock:
            self._scope_tracker.RemoveNode(unique_id, was_successful)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPushScope(
        self,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> None:
        self._scope_level += 1

        result = self._observer.OnPushScope(iter_range, data)
        if isinstance(result, DynamicPhrasesInfo):
            assert data.unique_id is not None

            with self._scope_tracker_lock:
                self._scope_tracker.AddScopeItem(
                    data.unique_id,
                    self._scope_level,
                    iter_range,
                    result,
                )

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPopScope(
        self,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> None:
        assert data.unique_id is not None

        with self._scope_tracker_lock:
            self._scope_tracker.RemoveScopeItems(data.unique_id, self._scope_level)

        assert self._scope_level
        self._scope_level -= 1

        self._observer.OnPopScope(iter_range, data)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnInternalPhrase(
        self,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> bool:
        assert data.data is not None
        assert data.unique_id is not None

        result = self._observer.OnPhraseComplete(
            data.phrase,
            iter_range,
            cast(AST.Node, self.CreateNode(data, None)),
        )

        if isinstance(result, DynamicPhrasesInfo):
            with self._scope_tracker_lock:
                self._scope_tracker.AddScopeItem(
                    data.unique_id,
                    self._scope_level,
                    iter_range,
                    result,
                )

            return True

        return result


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _CreateSyntaxInvalidError(
    root_node: AST.Node,
    normalized_iter: NormalizedIterator,
    get_parent_statement_node_func: Callable[[AST.Node], Optional[AST.Node]],
) -> SyntaxInvalidError:
    # ----------------------------------------------------------------------
    def CalcDepth(
        node: Union[AST.Leaf, AST.Node],
    ) -> int:
        depth = 0

        working_node = node

        while working_node is not None:
            depth += 1
            working_node = working_node.parent

        return depth

    # ----------------------------------------------------------------------

    # Find the nodes that represents the furthest valid thing that was lexed
    best_nodes: List[
        Tuple[
            int,                            # depth
            Union[AST.Leaf, AST.Node],      # node
            Union[AST.Leaf, AST.Node],      # reference_node
        ]
    ] = []

    nodes_to_query: List[
        Tuple[
            Union[AST.Leaf, AST.Node],      # node
            Union[AST.Leaf, AST.Node],      # reference_node
        ]
    ] = [(root_node, root_node)]

    while nodes_to_query:
        node_to_query, reference_node = nodes_to_query.pop()

        for node in node_to_query.Enum():
            # Add potential error nodes to the list of nodes to query (if such a value exists)
            potential_error_node = getattr(node, _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME, None)
            if potential_error_node is not None:
                nodes_to_query.append((potential_error_node, node))

            if node.iter_range is None:
                continue

            assert not best_nodes or best_nodes[-1][1].iter_range is not None

            if best_nodes and node.iter_range.end == best_nodes[-1][1].iter_range.end:  # type: ignore
                best_nodes.append((CalcDepth(node), node, reference_node))
            elif not best_nodes or node.iter_range.end > best_nodes[-1][1].iter_range.end:  # type: ignore
                best_nodes = [(CalcDepth(node), node, reference_node)]

    # the best error node is the one that has the greatest depth
    error_node: Optional[Union[AST.Leaf, AST.Node]] = None
    error_reference_node: Optional[Union[AST.Leaf, AST.Node]] = None

    if not best_nodes:
        error_node = root_node
        error_reference_node = root_node

        is_error_ambiguous = False

        assert error_node.iter_range is not None
        location = error_node.iter_range.end.ToLocation()

    else:
        # Sort by depth to get the node that is deepest in the tree
        best_nodes.sort(
            key=lambda value: value[0],
        )

        # Resolve ties by taking the first node at this depth
        best_depth = best_nodes[-1][0]

        for depth, error_node, error_reference_node in reversed(best_nodes):
            if depth != best_depth:
                break

        assert error_node is not None

        is_error_ambiguous = (
            len(best_nodes) > 2
            and best_nodes[-1][0] == best_nodes[-2][0]
            and error_node.iter_range is not None
            and error_node.iter_range.begin != error_node.iter_range.end
        )

        # Adjust the column to account for whitespace so that the error information is more
        # accurate.
        error_iter = error_node.iter_range.end if error_node.iter_range is not None else normalized_iter

        potential_whitespace = error_iter.GetNextWhitespaceRange()
        if potential_whitespace is not None and error_iter.offset == potential_whitespace.begin:
            error_iter.Advance(potential_whitespace.end - potential_whitespace.begin)

        location = error_iter.ToLocation()

    # Generate contextual information about the error

    # Ideally, we would use inflect here to better handle plural/singular detection and conversion.
    # Unfortunately, inflect gets confused by strings such as "(One | Two | Three)" and we
    # therefore have to take matters into our own hands.

    # ----------------------------------------------------------------------
    def MakeSingular(
        phrase_name: str,
    ) -> str:
        if phrase_name.endswith("s"):
            return phrase_name[:-1]

        return phrase_name

    # ----------------------------------------------------------------------
    def GeneratePrefix(
        phrase_name: str,
        *,
        make_singular: bool=False,
    ) -> str:
        is_plural = phrase_name.endswith("s")

        if make_singular and is_plural:
            phrase_name = phrase_name[:-1]
            is_plural = False

        return "'{}' {}".format(phrase_name, "were" if is_plural else "was")

    # ----------------------------------------------------------------------

    error_context: Optional[str] = None

    if is_error_ambiguous:
        error_context = "No statements matched this content"

    else:
        # Navigate up the tree until we have a node that can provide good contextual information
        while True:
            if isinstance(error_node, AST.Node) and error_node.type is not None:
                if isinstance(error_node.type, SequencePhrase):
                    meaningful_children: List[Union[AST.Leaf, AST.Node]] = []

                    for child in error_node.children:
                        if isinstance(child, AST.Leaf):
                            if child.is_ignored:
                                continue
                        elif child.iter_range is None:
                            continue

                        meaningful_children.append(child)

                    # Sometimes, the problem isn't due to the phrase that failed but rather the
                    # phrase that came right before it. See if there is error information associated
                    # with the second-to-last phrase.
                    if len(meaningful_children) > 1:
                        potential_error_node = getattr(
                            meaningful_children[-2],
                            _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME,
                            None,
                        )

                        if potential_error_node is not None and potential_error_node.iter_range is None:
                            error_context = "{} evaluated but not matched; therefore ".format(
                                GeneratePrefix(potential_error_node.type.name),
                            )

                    phrase_index = len(meaningful_children)

                    if (
                        phrase_index == len(error_node.type.phrases) - 1
                        and DynamicPhrase.IsRightRecursivePhrase(error_node.type)
                    ):
                        expected_phrase_name = cast(DynamicPhrase, error_node.type.phrases[-1]).DisplayName
                    else:
                        assert phrase_index < len(error_node.type.phrases)

                        if (
                            isinstance(error_node.type.phrases[phrase_index], TokenPhrase)
                            and error_node.type.phrases[phrase_index].token.is_control_token  # type: ignore
                            and phrase_index + 1 < len(error_node.type.phrases)
                        ):
                            phrase_index += 1

                        expected_phrase_name = error_node.type.phrases[phrase_index].name

                    error_context = "{}{} expected in '{}'".format(
                        error_context or "",
                        GeneratePrefix(
                            expected_phrase_name,
                            make_singular=True,
                        ),
                        error_node.type.name,
                    )

                    break

                elif isinstance(error_node.type, RepeatPhrase):
                    if error_node.children[-1].iter_range is None:
                        error_context = "{} expected".format(
                            GeneratePrefix(
                                error_node.type.name,
                                make_singular=True,
                            ),
                        )

                        break

                elif isinstance(error_node.type, (DynamicPhrase, OrPhrase)):
                    # Keep walking
                    pass

                else:
                    assert False, error_node.type  # pragma: no cover

            assert error_node is not None

            if error_node.parent is None:
                assert isinstance(error_node, AST.Node)
                assert error_node.children
                assert error_node.children[-1].type is not None

                if isinstance(error_node.children[-1].type, DynamicPhrase):
                    expected_phrase_name = error_node.children[-1].type.DisplayName
                else:
                    expected_phrase_name = error_node.children[-1].type.name

                error_context = "{} expected".format(
                    GeneratePrefix(
                        expected_phrase_name,
                        make_singular=True,
                    ),
                )

                break

            error_node = error_node.parent  # type: ignore

    if error_context is None:
        error_context = error_node.ToYamlString().rstrip()
    else:
        assert isinstance(error_node, AST.Node), error_node

        error_statement = get_parent_statement_node_func(error_node)
        if error_statement is None:
            assert isinstance(error_reference_node, AST.Node), error_reference_node
            error_statement = get_parent_statement_node_func(error_reference_node)

        if (
            error_statement is not None
            and error_statement != error_node
            and error_statement.type is not None
        ):
            error_context += " for '{}'".format(MakeSingular(error_statement.type.name))

        error_context += "."

    return SyntaxInvalidError.Create(
        location=location,
        line=location.line,
        column=location.column,
        error_node=error_node,
        error_context=error_context,
    )
