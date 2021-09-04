# ----------------------------------------------------------------------
# |
# |  TranslationUnitParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-09 16:29:57
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
import sys
import textwrap
import threading

from collections import OrderedDict
from typing import Any, Awaitable, cast, Dict, Generator, List, Optional, Tuple, Union

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
    from .Components import AST
    from .Components.Error import Error
    from .Components.Phrase import Phrase

    from .Phrases.DSL import DynamicPhrasesType, Leaf
    from .Phrases.DynamicPhrase import DynamicPhrase
    from .Phrases.LeftRecursiveSequencePhraseWrapper import LeftRecursiveSequencePhraseWrapper
    from .Phrases.TokenPhrase import TokenPhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDynamicTraversalError(Error):
    """Exception thrown when dynamic phrases that prohibit parent traversal are applied over other dynamic phrases"""

    ExistingDynamicPhrases: Phrase.NormalizedIterator

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dynamic phrases the first ones applied in this lexical scope.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidError(Error):
    """Exception thrown when no matching phrases were found"""

    iter_begin: InitVar[Phrase.NormalizedIterator]

    Root: AST.RootNode
    LastMatch: AST.Node                     = field(init=False)

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")  # type: ignore

    # TODO: Add functionality that discusses naming conventions if the wrong type of name is used

    # ----------------------------------------------------------------------
    def __post_init__(self, iter_begin):
        last_matches: List[
            Tuple[
                Union[AST.Leaf, AST.Node, AST.RootNode],
                int,
            ]
        ] = []

        compare_begin_iters = iter_begin.Line != self.Line or iter_begin.Column != self.Column

        for node in self.Root.Enum():
            if isinstance(node, AST.Leaf):
                continue

            # Get the begin value
            node_iter_begin = node.IterBegin
            if node_iter_begin is None:
                continue

            # Get the end value
            iter_end = node.IterEnd
            if iter_end is None:
                continue

            if (
                iter_end.Line == self.Line
                and iter_end.Column == self.Column
                and (
                    not compare_begin_iters
                    or (
                        node_iter_begin.Line == iter_begin.Line
                        and node_iter_begin.Column == iter_begin.Column
                    )
                )
            ):
                # Calculate the depth of this node
                depth = 0

                parent = node
                while parent is not None:
                    depth += 1
                    parent = parent.Parent  # type: ignore

                last_matches.append((node, depth))

        assert last_matches

        # Select the node with the lowest depth (as this is likely to include the other nodes)
        last_matches.sort(
            key=lambda value: value[-1] if value[-1] != 1 else sys.maxsize
        )

        last_match = last_matches[0][0]

        object.__setattr__(self, "LastMatch", last_match)

        # If necessary, adjust the column to account for whitespace
        potential_whitespace = TokenPhrase.ExtractWhitespace(last_match.IterEnd.Clone())  # type: ignore
        if potential_whitespace is not None:
            object.__setattr__(self, "Column", self.Column + potential_whitespace[1] - potential_whitespace[0])

    # ----------------------------------------------------------------------
    def ToDebugString(
        self,
        verbose=False,
    ) -> str:
        return textwrap.dedent(
            """\
            {message} [{line}, {column}]


            {content}


            {last_match_content}
            """,
        ).format(
            message=str(self),
            line=self.Line,
            column=self.Column,
            content=self.Root.ToYamlString().rstrip(),
            # pylint: disable=no-member
            last_match_content=self.LastMatch.ToYamlString().rstrip(),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DynamicPhrasesInfo(YamlRepr.ObjectReprImplBase):
    """Phrases that should be dynamically added to the active scope"""

    # ----------------------------------------------------------------------
    # |  Public Data
    Expressions: List[Phrase]
    Names: List[Phrase]
    Statements: List[Phrase]
    Types: List[Phrase]

    AllowParentTraversal: bool              = field(default=True)
    Name: Optional[str]                     = field(default=None)

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        phrase_display_func = lambda phrases: ", ".join([phrase.Name for phrase in phrases])

        YamlRepr.ObjectReprImplBase.__init__(
            self,
            Expressions=phrase_display_func,
            Names=phrase_display_func,
            Statements=phrase_display_func,
            Types=phrase_display_func,
        )

    # ----------------------------------------------------------------------
    def __bool__(self):
        return (
            bool(self.Expressions)
            or bool(self.Names)
            or bool(self.Statements)
            or bool(self.Types)
        )

    # ----------------------------------------------------------------------
    def Clone(
        self,
        updated_expressions=None,
        updated_names=None,
        updated_statements=None,
        updated_types=None,
        updated_allow_parent_traversal=None,
        updated_name=None,
    ):
        # pylint: disable=too-many-function-args
        return self.__class__(
            updated_expressions if updated_expressions is not None else self.Expressions,
            updated_names if updated_names is not None else self.Names,
            updated_statements if updated_statements is not None else self.Statements,
            updated_types if updated_types is not None else self.Types,
            updated_allow_parent_traversal if updated_allow_parent_traversal is not None else self.AllowParentTraversal,
            updated_name if updated_name is not None else self.Name,
        )


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
    async def OnIndentAsync(
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnDedentAsync(
        data_stack: List[Phrase.StandardParseResultData],
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
        bool,                               # True to continue processing, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phases (if any) resulting from the parsed phrase
    ]:
        """Used when an internal phrase is successfully parsed"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    initial_phrase_info: DynamicPhrasesInfo,
    normalized_iter: Phrase.NormalizedIterator,
    observer: Observer,
    single_threaded=False,
    name: str=None,
):
    """Repeatedly matches the statements for the contents of the iterator"""

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

    root = AST.RootNode(None)

    # ----------------------------------------------------------------------
    def FinalInit():
        for node in root.Enum(children_first=True):
            if isinstance(node, Leaf):
                continue

            node.FinalInit()

    # ----------------------------------------------------------------------

    while not normalized_iter.AtEnd():
        phrase_observer.ClearNodeCache()

        result = await phrase.ParseAsync(
            ("root", ),
            normalized_iter,
            phrase_observer,
            ignore_whitespace=False,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        assert result.Data

        phrase_observer.CreateNode(
            result.Data.Phrase,
            result.Data.Data,
            result.Data.UniqueId,
            root,
        )

        if not result.Success:
            FinalInit()

            raise SyntaxInvalidError(
                result.IterEnd.Line,
                result.IterEnd.Column,
                result.IterBegin,  # type: ignore
                root,
            )

        normalized_iter = result.IterEnd.Clone()

        # TODO: Eat trailing comments (here or in SequencePhrase.py?)
        # TODO: What happens to file that starts with newlines?
        # TODO: Handle empty file

    FinalInit()

    assert normalized_iter.AtEnd()
    return root


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _ScopeTracker(object):
    """Manages access to scope impacted by phrase modifications via DynamicPhraseInfo objects"""

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
            _ScopeTracker._TrackerNode
        ] = OrderedDict()

        tracker_nodes[self._DefaultScopeTrackerTagInstance] = _ScopeTracker._TrackerNode("")

        tracker_nodes[self._DefaultScopeTrackerTagInstance].ScopeItems.append(
            _ScopeTracker._ScopeItem(
                0,
                normalized_iter.Clone(),
                initial_phrase_info,
            ),
        )

        # Create the cache info
        cache: Dict[
            Tuple[
                Tuple[str, ...],            # unique_id
                DynamicPhrasesType,
            ],
            Tuple[Optional[str], List[Phrase]]
        ] = {}

        # Commit the information
        self._tracker_nodes                 = tracker_nodes
        self._cache                         = cache

    # ----------------------------------------------------------------------
    def AddNode(
        self,
        unique_id: Tuple[str, ...],
    ) -> None:
        d = self._tracker_nodes

        for id_part in unique_id:
            node = d.get(id_part, None)
            if node is None:
                node = _ScopeTracker._TrackerNode(id_part)
                d[id_part] = node

            d = node.Children

        self._cache.clear()

    # ----------------------------------------------------------------------
    def RemoveNode(
        self,
        unique_id: Tuple[str, ...],
        was_successful: bool,
    ) -> None:
        # Get the tracker node
        d = self._tracker_nodes
        tracker_node = None

        for id_part in unique_id:
            tracker_node = d.get(id_part, None)
            assert tracker_node is not None

            d = tracker_node.Children

        assert tracker_node is not None

        # Collect all of the dynamic phrase info associated with the descendants and add them here
        if was_successful:
            if not tracker_node.ScopeItems:
                for descendant_node in self._EnumDescendants(tracker_node.Children):
                    tracker_node.ScopeItems += descendant_node.ScopeItems
        else:
            tracker_node.ScopeItems = []

        tracker_node.Children = {}

        self._cache.clear()

    # ----------------------------------------------------------------------
    def AddScopeItem(
        self,
        unique_id: Tuple[str, ...],
        indentation_level: int,
        iter_after: Phrase.NormalizedIterator,
        phrases_info: DynamicPhrasesInfo,
    ) -> None:
        if not phrases_info:
            return

        this_tracker_node = None
        last_scope_item = None

        # The tracker node associated with this event will be the last one that we encounter when enumerating
        # through the previous tracker nodes. In addition to the current tracker node, get the last dynamic
        # info associated with all of the scope_trackers to determine if adding this dynamic info will be a problem.
        for tracker_node in self._EnumPrevious(unique_id):
            this_tracker_node = tracker_node

            if tracker_node.ScopeItems:
                last_scope_item = tracker_node.ScopeItems[-1]

        assert this_tracker_node is not None
        assert this_tracker_node.UniqueIdPart == unique_id[-1], (this_tracker_node.UniqueIdPart, unique_id[-1])

        if (
            not phrases_info.AllowParentTraversal
            and last_scope_item is not None
            and last_scope_item.IndentLevel == indentation_level
        ):
            raise InvalidDynamicTraversalError(
                iter_after.Line,
                iter_after.Column,
                last_scope_item.IterEnd,
            )

        this_tracker_node.ScopeItems.append(
            _ScopeTracker._ScopeItem(
                indentation_level,
                iter_after.Clone(),
                phrases_info,
            ),
        )

        self._cache.clear()

    # ----------------------------------------------------------------------
    def RemoveScopeItems(
        self,
        unique_id: Tuple[str, ...],
        indentation_level: int,
    ) -> None:
        for tracker_node in self._EnumPrevious(unique_id):
            if not tracker_node.ScopeItems:
                continue

            item_index = 0
            while item_index < len(tracker_node.ScopeItems):
                scope_item = tracker_node.ScopeItems[item_index]

                if scope_item.IndentLevel == indentation_level:
                    del tracker_node.ScopeItems[item_index]
                else:
                    item_index += 1

        self._cache.clear()

    # ----------------------------------------------------------------------
    def GetDynamicPhrases(
        self,
        unique_id: Tuple[str, ...],
        dynamic_phrases_type: DynamicPhrasesType,
    ) -> Tuple[Optional[str], List[Phrase]]:

        # TODO: cache results

        if dynamic_phrases_type == DynamicPhrasesType.Expressions:
            attribute_name = "Expressions"
        elif dynamic_phrases_type == DynamicPhrasesType.Names:
            attribute_name = "Names"
        elif dynamic_phrases_type == DynamicPhrasesType.Statements:
            attribute_name = "Statements"
        elif dynamic_phrases_type == DynamicPhrasesType.Types:
            attribute_name = "Types"
        else:
            assert False, dynamic_phrases_type  # pragma: no cover

        all_phrases = []
        all_names = []

        processed_dynamic_infos = set()
        processed_phrases = set()

        should_continue = True

        # Process the phrases from most recently added to those added long ago (this is the reason
        # for the use of 'reversed' in the code that follows)
        previous_tracker_nodes = list(self._EnumPrevious(unique_id))

        for tracker_node in reversed(previous_tracker_nodes):
            these_phrases = []
            these_names = []

            for scope_item in tracker_node.ScopeItems:
                dynamic_info = scope_item.Info

                # Have we seen this info before?
                dynamic_info_key = id(dynamic_info)

                if dynamic_info_key in processed_dynamic_infos:
                    continue

                processed_dynamic_infos.add(dynamic_info_key)

                # Get the phrases
                phrases = getattr(dynamic_info, attribute_name)
                if not phrases:
                    continue

                len_these_phrases = len(these_phrases)

                for phrase in phrases:
                    # Have we seen this phrase before
                    phrase_key = id(phrase)

                    if phrase_key in processed_phrases:
                        continue

                    processed_phrases.add(phrase_key)

                    these_phrases.append(phrase)

                if len(these_phrases) == len_these_phrases:
                    # No new phrases to process
                    continue

                these_names.append(
                    dynamic_info.Name or "({})".format(
                        ", ".join([phrase.Name for phrase in these_phrases[len_these_phrases:]]),
                    ),
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

        # Combine the phrases into 2 groups, those that are left-recursive and those that are not
        standard_phrases = []
        left_recursive_phrases = []

        for phrase in all_phrases:
            if LeftRecursiveSequencePhraseWrapper.IsLeftRecursivePhrase(
                phrase,
                dynamic_phrases_type,
            ):
                left_recursive_phrases.append(phrase)
            else:
                standard_phrases.append(phrase)

        if left_recursive_phrases:
            standard_phrases.append(
                LeftRecursiveSequencePhraseWrapper(
                    dynamic_phrases_type,
                    list(standard_phrases),
                    left_recursive_phrases,
                    prefix_name="Left Recursive Wrapper",
                ),
            )

        result = " / ".join(all_names), standard_phrases

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
        IndentLevel: int
        IterEnd: Phrase.NormalizedIterator
        Info: DynamicPhrasesInfo

    # ----------------------------------------------------------------------
    @dataclass
    class _TrackerNode(object):
        UniqueIdPart: str
        Children: Dict[Union[str, "_ScopeTracker._DefaultScopeTrackerTag"], "_ScopeTracker._TrackerNode"]   = field(default_factory=OrderedDict)
        ScopeItems: List["_ScopeTracker._ScopeItem"]                                                        = field(default_factory=list)

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
        for v in tracker_nodes.values():
            yield v
            yield from cls._EnumDescendants(v.Children)

    # ----------------------------------------------------------------------
    def _EnumPrevious(
        self,
        unique_id: Tuple[str, ...],
    ) -> Generator["_ScopeTracker._TrackerNode", None, None]:
        yield self._tracker_nodes[self._DefaultScopeTrackerTagInstance]

        d = self._tracker_nodes

        for id_part in unique_id:
            for k, v in d.items():
                if k == self._DefaultScopeTrackerTagInstance:
                    continue

                yield v

                if k == id_part:
                    d = v.Children
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

        self._indent_level                  = 0

        self._node_cache: Dict[Any, Union[AST.Leaf, AST.Node]]              = {}

    # ----------------------------------------------------------------------
    def ClearNodeCache(self):
        self._node_cache.clear()

    # ----------------------------------------------------------------------
    def CreateNode(
        self,
        phrase: Phrase,
        data: Optional[Phrase.ParseResultData],
        unique_id: Optional[Tuple[str, ...]],
        parent: Optional[Union[AST.RootNode, AST.Node]],
    ) -> Union[AST.Leaf, AST.Node]:

        node: Optional[Union[AST.Leaf, AST.Node]] = None

        # Look for the cached value
        cache_key = unique_id
        was_cached = False

        potential_node = self._node_cache.get(cache_key, None)
        if potential_node is not None:
            node = potential_node
            was_cached = True

        # Create the node (if necessary)
        if node is None:
            if isinstance(phrase, TokenPhrase) and data:
                node = self._CreateLeaf(cast(Phrase.TokenParseResultData, data), parent)
            else:
                node = AST.Node(phrase)

        assert node

        # Assign the parent (if necessary)
        if parent != node.Parent:
            assert parent

            object.__setattr__(node, "Parent", parent)
            parent.Children.append(node)

        # Populate the children (if necessary)
        if not was_cached:
            if isinstance(node, AST.Node) and data is not None:
                for data_item in data.Enum():
                    if isinstance(data_item, Phrase.TokenParseResultData):
                        self._CreateLeaf(data_item, node)
                    elif isinstance(data_item, Phrase.StandardParseResultData):
                        self.CreateNode(data_item.Phrase, data_item.Data, data_item.UniqueId, node)
                    else:
                        assert False, data_item  # pragma: no cover

            if cache_key is not None:
                self._node_cache[cache_key] = node

        return node

    # ----------------------------------------------------------------------
    @Interface.override
    def GetDynamicPhrases(
        self,
        unique_id: Tuple[str, ...],
        phrases_type: DynamicPhrasesType,
    ) -> Tuple[Optional[str], List[Phrase]]:
        with self._scope_tracker_lock:
            return self._scope_tracker.GetDynamicPhrases(unique_id, phrases_type)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        func_infos: List[Phrase.EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        return self._observer.Enqueue(func_infos)

    # ----------------------------------------------------------------------
    @Interface.override
    def StartPhrase(
        self,
        unique_id: Tuple[str, ...],
        phrase_stack: List[Phrase],
    ):
        with self._scope_tracker_lock:
            self._scope_tracker.AddNode(unique_id)

    # ----------------------------------------------------------------------
    @Interface.override
    def EndPhrase(
        self,
        unique_id: Tuple[str, ...],
        phrase_info_stack: List[Tuple[Phrase, Optional[bool]]],
    ):
        was_successful = bool(phrase_info_stack[0][1])

        with self._scope_tracker_lock:
            self._scope_tracker.RemoveNode(unique_id, was_successful)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ):
        self._indent_level += 1

        this_result = await self._observer.OnIndentAsync(data_stack, iter_before, iter_after)
        if isinstance(this_result, DynamicPhrasesInfo):
            assert data_stack[0].UniqueId is not None
            unique_id = data_stack[0].UniqueId

            with self._scope_tracker_lock:
                self._scope_tracker.AddScopeItem(unique_id, self._indent_level, iter_after, this_result)

        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(
        self,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ):
        assert data_stack[0].UniqueId is not None
        unique_id = data_stack[0].UniqueId

        with self._scope_tracker_lock:
            self._scope_tracker.RemoveScopeItems(unique_id, self._indent_level)

        assert self._indent_level
        self._indent_level -= 1

        await self._observer.OnDedentAsync(data_stack, iter_before, iter_after)

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnInternalPhraseAsync(
        self,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> bool:
        assert data_stack[0].Data

        this_result = await self._observer.OnPhraseCompleteAsync(
            data_stack[0].Phrase,
            cast(
                AST.Node,
                self.CreateNode(
                    data_stack[0].Phrase,
                    data_stack[0].Data,
                    data_stack[0].UniqueId,
                    None,
                ),
            ),
            iter_before,
            iter_after,
        )

        if isinstance(this_result, DynamicPhrasesInfo):
            assert data_stack[0].UniqueId is not None

            with self._scope_tracker_lock:
                self._scope_tracker.AddScopeItem(
                    data_stack[0].UniqueId,
                    self._indent_level,
                    iter_after,
                    this_result,
                )

            return True

        return this_result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateLeaf(
        data: Phrase.TokenParseResultData,
        parent: Optional[Union[AST.RootNode, AST.Node]],
    ) -> AST.Leaf:
        # pylint: disable=too-many-function-args
        leaf = AST.Leaf(
            data.Token,
            data.Whitespace,
            data.Value,
            data.IterBegin,
            data.IterEnd,
            data.IsIgnored,
        )

        if parent:
            object.__setattr__(leaf, "Parent", parent)
            parent.Children.append(leaf)

        return leaf
