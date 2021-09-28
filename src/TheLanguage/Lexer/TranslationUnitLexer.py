# ----------------------------------------------------------------------
# |
# |  TranslationUnitLexer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 14:45:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used to lex a single translation unit"""

import os
import sys
import textwrap
import threading

from collections import OrderedDict
from typing import Any, Awaitable, cast, Dict, Generator, List, Optional, Set, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error

    from .Components import AST
    from .Components.Phrase import Phrase

    from .Phrases.DSL import DynamicPhrasesType
    from .Phrases.DynamicPhrase import DynamicPhrase
    from .Phrases.OrPhrase import OrPhrase
    from .Phrases.RepeatPhrase import RepeatPhrase
    from .Phrases.SequencePhrase import SequencePhrase
    from .Phrases.TokenPhrase import RegexToken, TokenPhrase


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDynamicTraversalError(Error):
    """Exception raised when dynamic phrases that prohibit parent traversal are applied over existing dynamic phrases"""

    ExistingDynamicPhrases: Phrase.NormalizedIterator

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dynamic phrases the first ones applied in this lexical scope.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidError(Error):
    """Exception raises when no matching phrases could be found"""

    iter_begin: InitVar[Phrase.NormalizedIterator]
    iter_end: InitVar[Phrase.NormalizedIterator]

    Root: AST.Node

    ErrorContext: str                       = field(init=False)
    ErrorNode: AST.Node                     = field(init=False)

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        textwrap.dedent(
            """\
            The syntax is not recognized. [{Line}, {Column}]

            {ErrorContext}
            """,
        ),
    )

    # ----------------------------------------------------------------------
    def __post_init__(self, iter_begin, iter_end):
        # When this exception is created, we are only provided with the root node.
        # This algorithm attempts to drill down into the exact error to provided better
        # contextual information.

        compare_begin_iters = iter_begin.Line != self.Line or iter_begin.Column != self.Column

        node_matches: List[
            Tuple[
                int, # depth
                Union[AST.Leaf, AST.Node],
            ]
        ] = []

        for node in self.Root.Enum():
            if isinstance(node, AST.Leaf):
                continue

            # Get the begin value
            node_iter_begin = node.IterBegin
            if node_iter_begin is None:
                continue

            # Get the end value
            node_iter_end = node.IterEnd
            if node_iter_end is None:
                continue

            if (
                node_iter_end == iter_end
                and (not compare_begin_iters or node_iter_begin == iter_begin)
            ):
                # Calculate the depth of this node
                depth = 0

                parent = node
                while parent is not None:
                    depth += 1
                    parent = parent.Parent

                node_matches.append((depth, node))

        # Attempt to provide more helpful information
        error_context = None

        if not node_matches:
            assert self.Root.IterEnd is None

            error_node = self.Root

        else:
            # Select the node with the lowest depth (or closest to the root), as it will include the
            # other nodes.
            node_matches.sort(
                key=lambda value: value[:-1],
            )

            error_node = node_matches[-1][-1]

            # Attempt to provide more helpful information
            while True:
                assert error_node.Type is not None

                if isinstance(error_node, AST.Leaf):
                    if isinstance(error_node.Type, RegexToken):
                        phrase_name = error_node.Type.Name
                    else:
                        # If here, the last valid token was an indent, dedent, or newline. Most of the time,
                        # we will see this happen when the scope has changed due to a dedent. However, we
                        # need to display the expected phrase as it will be after this token is consumed
                        # rather than what it was when it was consumed.

                        # Walk up the hierarchy to find the parent of both this node and the actual error
                        # node.
                        while error_node.Parent is not None:
                            error_node_parent = cast(AST.Node, error_node.Parent)

                            if len(error_node_parent.Children) > 1 and error_node_parent.Children[-2] == error_node:
                                error_node = error_node_parent.Children[-1]
                                break

                            error_node = cast(AST.Node, error_node.Parent)

                        # Now walk down the hierarchy until we find a node that we can key off of
                        assert isinstance(error_node, AST.Node)
                        assert error_node.Type is not None

                        if isinstance(error_node.Type, DynamicPhrase):
                            assert len(error_node.Children) == 1
                            error_node = error_node.Children[0]

                        assert error_node.Type is not None
                        phrase_name = error_node.Type.Name

                    error_context = "'{}' was expected.".format(phrase_name)
                    break

                assert isinstance(error_node, AST.Node)
                assert error_node.Children

                if isinstance(error_node.Type, SequencePhrase):
                    if error_node.Children[-1].IterEnd is None:
                        # Sometimes, the problem isn't due to the phrase that failed, but rather the
                        # phrase right before it.
                        if len(error_node.Children) > 1:
                            potential_error_node = getattr(error_node.Children[-2], _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME, None)
                            if potential_error_node is not None and potential_error_node.IterEnd is not None:
                                error_node = potential_error_node
                                continue

                        expected_phrase = error_node.Type.Phrases[len(error_node.Children) - 1]
                        error_context = "'{}' was expected in '{}'.".format(
                            expected_phrase.Name,
                            error_node.Type.Name,
                        )

                        break

                    if error_node.Children[-1].IterEnd is not None:
                        error_node = error_node.Children[-1]
                        continue

                elif isinstance(error_node.Type, RepeatPhrase):
                    if error_node.Children[-1].IterEnd is None:
                        # If here, no content matched in the repeat
                        num_valid_children = len(error_node.Children) - 1
                        num_expected = error_node.Type.MinMatches

                        assert num_valid_children < num_expected, (num_valid_children, num_expected)

                        error_context = "'{}' was expected.".format(error_node.Type.Name)
                        break

                    if error_node.Children[-1].IterEnd is not None:
                        error_node = error_node.Children[-1]
                        continue

                elif isinstance(error_node.Type, OrPhrase):
                    assert error_node.IterEnd is not None

                    child_error_node = None

                    for child_node in error_node.Children:
                        if child_node.IterEnd == error_node.IterEnd:
                            child_error_node = child_node
                            break

                    assert child_error_node is not None
                    error_node = child_error_node

                    continue

                break

            if error_node.IterEnd is not None:
                # Adjust the column to account for whitespace
                column = error_node.IterEnd.Column

                potential_whitespace = TokenPhrase.ExtractPotentialWhitespace(error_node.IterEnd.Clone())
                if potential_whitespace is not None:
                    column += (potential_whitespace[1] - potential_whitespace[0])

                object.__setattr__(self, "Column", column)
                object.__setattr__(self, "Line", error_node.IterEnd.Line)

        if error_context is None:
            error_context = error_node.ToYamlString().rstrip()

        object.__setattr__(self, "ErrorNode", error_node)
        object.__setattr__(self, "ErrorContext", error_context)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DynamicPhrasesInfo(YamlRepr.ObjectReprImplBase):
    """Phrases that should be dynamically added to the active scope"""

    Phrases: Dict[DynamicPhrasesType, List[Phrase]]
    AllowParentTraversal: bool              = field(default=True)
    Name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert all(phrases for phrases in self.Phrases.values())

        YamlRepr.ObjectReprImplBase.__init__(
            self,
            Phrases=lambda phrases: "\n".join(
                [
                    "- {}: [{}]".format(
                        key,
                        ", ".join(["'{}'".format(phrase.Name) for phrase in value]),
                    )
                    for key, value in phrases.items()
                ],
            ),
        )

    # ----------------------------------------------------------------------
    def __bool__(self):
        return bool(self.Phrases)


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        func_infos: List[Phrase.EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnPushScopeAsync(
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnPopScopeAsync(
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnPhraseCompleteAsync(
        phrase: Phrase,
        node: AST.Node,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phrases to add to the active scope as a result of completing this phrase
    ]:
        """Invoked when an internal phrase has been successfully parsed"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
async def LexAsync(
    comment_token: RegexToken,
    initial_phrase_info: DynamicPhrasesInfo,
    normalized_iter: Phrase.NormalizedIterator,
    observer: Observer,
    single_threaded=False,
    name: Optional[str]=None,
) -> Optional[AST.Node]:
    """Repeatedly matches the statements for everything within the iterator"""

    assert normalized_iter.Offset == 0, normalized_iter

    phrase_observer = _PhraseObserver(
        observer,
        normalized_iter,
        initial_phrase_info,
    )

    phrase = DynamicPhrase(
        DynamicPhrasesType.Statements,
        lambda unique_id, phrases_type, observer: observer.GetDynamicPhrases(unique_id, phrases_type),
        name=name,
    )

    root = AST.Node(
        None,
        IsIgnored=False,
    )

    # ----------------------------------------------------------------------
    def FinalInit(
        *,
        is_error: bool,
    ):
        if is_error:
            # ----------------------------------------------------------------------
            def InitPotentialErrorNode(node, potential_error_node):
                for node in potential_error_node.Enum(
                    nodes_only=True,
                    children_first=True,
                ):
                    node.FinalInit()

            # ----------------------------------------------------------------------

            process_potential_error_node_func = InitPotentialErrorNode

        else:
            # ----------------------------------------------------------------------
            def RemovePotentialErrorNode(node, potential_error_node):
                object.__delattr__(node, _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME)

            # ----------------------------------------------------------------------

            process_potential_error_node_func = RemovePotentialErrorNode

        for node in root.Enum(children_first=True):
            if isinstance(node, AST.Leaf):
                continue

            node.FinalInit()

            potential_error_node = getattr(node, _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME, None)
            if potential_error_node is not None:
                process_potential_error_node_func(node, potential_error_node)

    # ----------------------------------------------------------------------

    while not normalized_iter.AtEnd():
        phrase_observer.ClearNodeCache()

        # Get leading comments or whitespace
        result = TokenPhrase.ExtractPotentialCommentsOrWhitespace(
            comment_token,
            normalized_iter,
            0,
            ignore_whitespace=False,
            next_phrase_is_indent=False,
            next_phrase_is_dedent=False,
        )

        if result is not None:
            data_items, normalized_iter, _ = result

            for data in data_items:
                phrase_observer.__class__.CreateLeaf(data, root)

            if normalized_iter.AtEnd():
                continue

        # Process the content
        result = await phrase.LexAsync(
            ("root", ),
            normalized_iter,
            phrase_observer,
            ignore_whitespace=False,
            single_threaded=single_threaded,
        )

        if result is None or result.Data is None:
            return None

        phrase_observer.CreateNode(result.Data, root)

        if not result.Success:
            FinalInit(
                is_error=True,
            )

            raise SyntaxInvalidError(
                result.IterEnd.Line,
                result.IterEnd.Column,
                result.IterBegin,  # type: ignore
                result.IterEnd,  # type: ignore
                root,
            )

        normalized_iter = result.IterEnd.Clone()

    FinalInit(
        is_error=False,
    )

    assert normalized_iter.AtEnd()
    return root


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
        normalized_iter: Phrase.NormalizedIterator,
        initial_phrase_info: DynamicPhrasesInfo,
    ):
        # Initialize the tracker nodes
        tracker_nodes: Dict[
            Union[str, _ScopeTracker._DefaultScopeTrackerTag],
            _ScopeTracker._TrackerNode,
        ] = OrderedDict()

        tracker_nodes[self._DefaultScopeTrackerTagInstance] = _ScopeTracker._TrackerNode("")
        tracker_nodes[self._DefaultScopeTrackerTagInstance].scope_items.append(
            _ScopeTracker._ScopeItem(
                0,
                normalized_iter.Clone(),
                initial_phrase_info,
            ),
        )

        # Create the cache info
        cache: Dict[
            DynamicPhrasesType,
            Dict[
                Tuple[str, ...],            # unique_id
                Tuple[List[Phrase], Optional[str]]
            ]
        ] = {}

        # Commit the info
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
        d = self._tracker_nodes
        tracker_node: Optional[_ScopeTracker._TrackerNode] = None

        for id_part in unique_id:
            tracker_node = d.get(id_part, None)
            assert tracker_node is not None

            d = tracker_node.children

        assert tracker_node is not None

        clear_cache_types: Set[DynamicPhrasesType] = set()

        # ----------------------------------------------------------------------
        def ProcessScopeItems(scope_items):
            for scope_item in scope_items:
                for dynamic_phrase_info in scope_item.Info.Phrases.keys():
                    clear_cache_types.add(dynamic_phrase_info)

        # ----------------------------------------------------------------------

        if not tracker_node.scope_items:
            if was_successful:
                # Move all scope items found in the descendants to this node

                # ----------------------------------------------------------------------
                def OnDescendantTrackerNode(descendant_tracker_node):
                    tracker_node.scope_items += descendant_tracker_node.scope_items  # type: ignore

                # ----------------------------------------------------------------------

                on_descendant_tracker_node_func = OnDescendantTrackerNode

            else:
                on_descendant_tracker_node_func = lambda *args, **kwargs: None

            for descendant_tracker_node in self.__class__._EnumDescendants(tracker_node.children):
                on_descendant_tracker_node_func(descendant_tracker_node)
                ProcessScopeItems(descendant_tracker_node.scope_items)

        elif not was_successful:
            ProcessScopeItems(tracker_node.scope_items)
            tracker_node.scope_items = []

        tracker_node.children = {}

        if self._cache:
            for dynamic_phrases_type in clear_cache_types:
                self._cache.pop(dynamic_phrases_type)

    # ----------------------------------------------------------------------
    def AddScopeItem(
        self,
        unique_id: Tuple[str, ...],
        indentation_level: int,
        iter_after: Phrase.NormalizedIterator,
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
            not dynamic_phrases_info.AllowParentTraversal
            and last_scope_item is not None
            and last_scope_item.IndentationLevel == indentation_level
        ):
            raise InvalidDynamicTraversalError(
                iter_after.Line,
                iter_after.Column,
                last_scope_item.IterEnd,
            )

        this_tracker_node.scope_items.append(
            _ScopeTracker._ScopeItem(
                indentation_level,
                iter_after.Clone(),
                dynamic_phrases_info,
            ),
        )

        if self._cache:
            for dynamic_phrases_type in dynamic_phrases_info.Phrases.keys():
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

                if scope_item.IndentationLevel == indentation_level:
                    for dynamic_phrases_type in scope_item.Info.Phrases.keys():
                        clear_cache_types.add(dynamic_phrases_type)

                    del tracker_node.scope_items[item_index]

                else:
                    item_index += 1

        if self._cache:
            for dynamic_phrases_type in clear_cache_types:
                self._cache.pop(dynamic_phrases_type)

    # ----------------------------------------------------------------------
    def GetDynamicPhrases(
        self,
        unique_id: Tuple[str, ...],
        dynamic_phrases_type: DynamicPhrasesType,
    ) -> Tuple[List[Phrase], Optional[str]]:
        cache = self._cache.setdefault(dynamic_phrases_type, {})
        cache_key = unique_id

        cache_value = cache.get(cache_key, None)
        if cache_value is not None:
            return cache_value

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
                dynamic_info = scope_item.Info

                # Have we seen this info before?
                dynamic_info_key = id(dynamic_info)

                if dynamic_info_key in processed_dynamic_infos:
                    continue

                processed_dynamic_infos.add(dynamic_info_key)

                # Get the phrases
                phrases = scope_item.Info.Phrases.get(dynamic_phrases_type, None)
                if phrases is None:
                    continue

                len_these_phrases = len(these_phrases)

                for phrase in phrases:
                    # Have we seen this phrase before?
                    phrase_key = id(phrase)

                    if phrase_key in processed_phrases:
                        continue

                    processed_phrases.add(phrase_key)

                    these_phrases.append(phrase)

                # No need to continue this iteration if we didn't see any new phrases
                if len(these_phrases) == len_these_phrases:
                    continue

                these_names.append(
                    dynamic_info.Name or "({})".format(" | ".join([phrase.Name for phrase in these_phrases[len_these_phrases:]])),
                )

                if not dynamic_info.AllowParentTraversal:
                    should_continue = False
                    break

            if these_phrases:
                all_phrases = these_phrases + all_phrases
            if these_names:
                all_names = these_names + all_names

            if not should_continue:
                break

        result = (all_phrases, " / ".join(all_names))

        cache[cache_key] = result
        return result

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    class _DefaultScopeTrackerTag(object):
        """\
        Unique type to use as a key in `_ScopeTracker` dictionaries; this is used rather
        than a normal value (for example, `None`) to allow for any key types.
        """
        pass

    _DefaultScopeTrackerTagInstance         = _DefaultScopeTrackerTag()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _ScopeItem(object):
        IndentationLevel: int
        IterEnd: Phrase.NormalizedIterator
        Info: DynamicPhrasesInfo

    # ----------------------------------------------------------------------
    @dataclass
    class _TrackerNode(object):
        unique_id_part: str
        children: Dict[Union[str, "_ScopeTracker._DefaultScopeTrackerTag"], "_ScopeTracker._TrackerNode"]   = field(default_factory=OrderedDict)
        scope_items: List["_ScopeTracker._ScopeItem"]                                                       = field(default_factory=list)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _EnumDescendants(
        cls,
        tracker_nodes: Dict[Any, "_ScopeTracker._TrackerNode"],
    ) -> Generator["_ScopeTracker._TrackerNode", None, None]:
        for tracker_node in tracker_nodes.values():
            yield tracker_node
            yield from cls._EnumDescendants(tracker_node.children)

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
        normalized_iter: Phrase.NormalizedIterator,
        initial_phrase_info: DynamicPhrasesInfo,
    ):
        self._observer                      = observer

        self._scope_tracker                 = _ScopeTracker(normalized_iter, initial_phrase_info)
        self._scope_tracker_lock            = threading.Lock()

        self._scope_level                   = 0

        self._node_cache: Dict[Any, Union[AST.Leaf, AST.Node]]              = {}

    # ----------------------------------------------------------------------
    def ClearNodeCache(self):
        self._node_cache.clear()

    # ----------------------------------------------------------------------
    def CreateNode(
        self,
        data: Phrase.StandardLexResultData,
        parent: Optional[AST.Node],
    ) -> Union[AST.Leaf, AST.Node]:

        node: Optional[Union[AST.Leaf, AST.Node]] = None

        # Look for the cached value
        cache_key = data.UniqueId

        node = self._node_cache.get(cache_key, None)
        if node is not None:
            was_cached = True
        else:
            was_cached = False

            if isinstance(data.Phrase, TokenPhrase) and data.Data is not None:
                node = self.__class__.CreateLeaf(cast(Phrase.TokenLexResultData, data.Data), parent)
            else:
                node = AST.Node(
                    data.Phrase,
                    IsIgnored=False,
                )

        assert node is not None

        # Assign the parent (if necessary(
        if parent != node.Parent:
            assert parent is not None

            object.__setattr__(node, "Parent", parent)
            parent.Children.append(node)

        # Populate the children (if necessary)
        if not was_cached:
            if isinstance(node, AST.Node) and data.Data is not None:
                for data_item in data.Data.Enum():
                    if isinstance(data_item, Phrase.TokenLexResultData):
                        self.__class__.CreateLeaf(data_item, node)
                    elif isinstance(data_item, Phrase.StandardLexResultData):
                        self.CreateNode(data_item, node)
                    else:
                        assert False, data_item  # pragma: no cover

            if cache_key is not None:
                self._node_cache[cache_key] = node

        if data.PotentialErrorContext is not None:
            potential_error_node = self.CreateNode(data.PotentialErrorContext, None)
            object.__setattr__(node, _POTENTIAL_ERROR_NODE_ATTRIBUTE_NAME, potential_error_node)

        return node

    # ----------------------------------------------------------------------
    @staticmethod
    def CreateLeaf(
        data: Phrase.TokenLexResultData,
        parent: Optional[AST.Node],
    ) -> AST.Leaf:
        leaf = AST.Leaf(
            data.Token,
            data.IsIgnored,
            data.Whitespace,
            data.Value,
            data.IterBegin,
            data.IterEnd,
        )

        if parent:
            object.__setattr__(leaf, "Parent", parent)
            parent.Children.append(leaf)

        return leaf

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        func_infos: List[Phrase.EnqueueAsyncItemType],
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
    async def OnPushScopeAsync(
        self,
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        self._scope_level += 1

        result = await self._observer.OnPushScopeAsync(data, iter_before, iter_after)
        if isinstance(result, DynamicPhrasesInfo):
            assert data.UniqueId is not None
            unique_id = data.UniqueId

            with self._scope_tracker_lock:
                self._scope_tracker.AddScopeItem(
                    unique_id,
                    self._scope_level,
                    iter_after,
                    result,
                )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPopScopeAsync(
        self,
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        assert data.UniqueId is not None
        unique_id = data.UniqueId

        with self._scope_tracker_lock:
            self._scope_tracker.RemoveScopeItems(unique_id, self._scope_level)

        assert self._scope_level
        self._scope_level -= 1

        await self._observer.OnPopScopeAsync(data, iter_before, iter_after)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnInternalPhraseAsync(
        self,
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> bool:
        assert data.Data is not None
        assert data.UniqueId is not None

        result = await self._observer.OnPhraseCompleteAsync(
            data.Phrase,
            cast(AST.Node, self.CreateNode(data, None)),
            iter_before,
            iter_after,
        )

        if isinstance(result, DynamicPhrasesInfo):
            if result:
                with self._scope_tracker_lock:
                    self._scope_tracker.AddScopeItem(
                        data.UniqueId,
                        self._scope_level,
                        iter_after,
                        result,
                    )

            return True

        return result
