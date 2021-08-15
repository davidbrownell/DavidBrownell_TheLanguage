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
import textwrap

from collections import OrderedDict
from typing import Any, Awaitable, cast, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Components import AST
    from .Components.Error import Error
    from .Components.Phrase import Phrase

    from .Phrases.DSL import DynamicPhrasesType
    from .Phrases.DynamicPhrase import DynamicPhrase
    from .Phrases.TokenPhrase import TokenPhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDynamicTraversalError(Error):
    """Exception thrown when dynamic phrases that prohibit parent traversal are applied over other dynamic phrases"""

    ExistingDynamicPhrases: Phrase.NormalizedIterator

    MessageTemplate                         = Interface.DerivedProperty("Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dynamic phrases the first ones applied in this lexical scope.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidError(Error):
    """Exception thrown when no matching phrases were found"""

    Root: AST.RootNode

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")

    # ----------------------------------------------------------------------
    def ToDebugString(
        self,
        verbose=False,
    ) -> str:
        return textwrap.dedent(
            """\
            {message} [{line}, {column}]

            {content}
            """,
        ).format(
            message=str(self),
            line=self.Line,
            column=self.Column,
            content=self.Root.ToString().rstrip(),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DynamicPhrasesInfo(CommonEnvironment.ObjectReprImplBase):
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

        CommonEnvironment.ObjectReprImplBase.__init__(
            self,
            Expressions=phrase_display_func,
            Names=phrase_display_func,
            Statements=phrase_display_func,
            Types=phrase_display_func,
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
    ) -> None:
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

    scope_trackers: Dict[Any, _ScopeTracker] = {
        _DefaultScopeTrackerTag : _ScopeTracker(
            "",
            OrderedDict(),
            [_ScopeItem(0, normalized_iter.Clone(), initial_phrase_info)],
        ),
    }

    phrase_observer = _PhraseObserver(observer, scope_trackers)

    phrase = DynamicPhrase(
        lambda unique_id, observer: cast(
                _PhraseObserver,
                observer,
            ).GetDynamicPhrases(unique_id, DynamicPhrasesType.Statements),
        name=name,
    )

    root = AST.RootNode(None)

    while not normalized_iter.AtEnd():
        phrase_observer.ClearNodeCache()

        result = await phrase.ParseAsync(
            ["root"],
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
            raise SyntaxInvalidError(
                result.Iter.Line,
                result.Iter.Column,
                root,
            )

        normalized_iter = result.Iter.Clone()

        # TODO: Eat trailing comments (here or in SequencePhrase.py?)
        # TODO: What happens to file that starts with newlines?

    assert normalized_iter.AtEnd()
    return root


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _DefaultScopeTrackerTag(object):
    """\
    Unique type to use as a key in `_ScopeTracker` dictionaries; this is used rather
    than a normal value (for example, `None`) to allow for any key types.
    """
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ScopeItem(object):
    IndentLevel: int
    IterAfter: Phrase.NormalizedIterator
    Info: DynamicPhrasesInfo


# ----------------------------------------------------------------------
@dataclass()
class _ScopeTracker(object):
    UniqueIdPart: str
    Children: Dict[Any, "_ScopeTracker"]    = field(default_factory=OrderedDict)
    DynamicItems: List[_ScopeItem]          = field(default_factory=list)


# ----------------------------------------------------------------------
class _PhraseObserver(Phrase.Observer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: Observer,
        scope_trackers: Dict[Any, _ScopeTracker],
    ):
        self._observer                      = observer
        self._scope_trackers                = scope_trackers

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
        unique_id: Optional[List[str]],
        parent: Optional[Union[AST.RootNode, AST.Node]],
    ) -> Union[AST.Leaf, AST.Node]:

        # Look for the cached value
        if unique_id is not None:
            key = tuple(unique_id)
        else:
            key = None

        node: Optional[Union[AST.Leaf, AST.Node]] = None
        was_cached = False

        potential_node = self._node_cache.get(key, None)
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

            if key is not None:
                self._node_cache[key] = node

        return node

    # ----------------------------------------------------------------------
    def GetDynamicPhrases(
        self,
        unique_id: List[str],
        dynamic_phrases_type: DynamicPhrasesType,
    ) -> Tuple[List[Phrase], str]:
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

        processed_infos = set()
        processed_phrases = set()

        should_continue = True

        # Process from the phrases most recently added to those added long ago
        previous_scope_trackers = list(self._EnumPreviousScopeTrackers(unique_id))

        for tracker in reversed(previous_scope_trackers):
            these_phrases = []
            these_names = []

            for dynamic_item in tracker.DynamicItems:
                info = dynamic_item.Info

                # Have we seen this info before
                info_key = id(info)

                if info_key in processed_infos:
                    continue

                processed_infos.add(info_key)

                # Get the phrases
                phrases = getattr(info, attribute_name)
                if not phrases:
                    continue

                len_these_phrases = len(these_phrases)

                for phrase in phrases:
                    # Have we seen this phrase before?
                    phrase_key = id(phrase)

                    if phrase_key in processed_phrases:
                        continue

                    processed_phrases.add(phrase_key)

                    these_phrases.append(phrase)

                if len(these_phrases) == len_these_phrases:
                    # No new phrases to process
                    continue

                these_names.append(
                    info.Name or "({})".format(
                        ", ".join([phrase.Name for phrase in these_phrases[len_these_phrases:]]),
                    ),
                )

                if not info.AllowParentTraversal:
                    should_continue = False
                    break

            if these_phrases:
                all_phrases = these_phrases + all_phrases
            if these_names:
                all_names = these_names + all_names

            if not should_continue:
                break

        return all_phrases, " / ".join(all_names)

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
        unique_id: List[str],
        phrase_stack: List[Phrase],
    ):
        d = self._scope_trackers

        for id_part in unique_id:
            value = d.get(id_part, None)
            if value is None:
                value = _ScopeTracker(id_part)
                d[id_part] = value

            d = value.Children

    # ----------------------------------------------------------------------
    @Interface.override
    def EndPhrase(
        self,
        unique_id: List[str],
        phrase_info_stack: List[Tuple[Phrase, Optional[bool]]],
    ):
        was_successful = bool(phrase_info_stack[0][1])

        # Get the tracker
        d = self._scope_trackers
        tracker = None

        for id_part in unique_id:
            tracker = d.get(id_part, None)
            assert tracker is not None

            d = tracker.Children

        assert tracker

        # Collect all the infos associated with the descendances of this tracker and add them here
        if was_successful:
            if not tracker.DynamicItems:
                for descendant in self._EnumDescendantScopeTrackers(tracker.Children):
                    tracker.DynamicItems += descendant.DynamicItems
        else:
            tracker.DynamicItems = []

        tracker.Children = {}

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

            self._AddScopeItem(unique_id, iter_after, this_result)

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

        for tracker in self._EnumPreviousScopeTrackers(unique_id):
            if not tracker.DynamicItems:
                continue

            item_index = 0
            while item_index < len(tracker.DynamicItems):
                info = tracker.DynamicItems[item_index]

                if info.IndentLevel == self._indent_level:
                    del tracker.DynamicItems[item_index]
                else:
                    item_index += 1

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

            self._AddScopeItem(data_stack[0].UniqueId, iter_after, this_result)
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
            data.IterBefore,
            data.IterAfter,
            data.IsIgnored,
        )

        if parent:
            object.__setattr__(leaf, "Parent", parent)
            parent.Children.append(leaf)

        return leaf

    # ----------------------------------------------------------------------
    def _AddScopeItem(
        self,
        unique_id: List[str],
        iter_after: Phrase.NormalizedIterator,
        info: DynamicPhrasesInfo,
    ):
        if not info.Expressions and not info.Names and not info.Statements and not info.Types:
            return

        this_tracker = None
        last_item = None

        # The tracker associated with this event will be the last one that we encounter when enumerating
        # through the previous scope_trackers. In addition to the current tracker, get the last dynamic info associated
        # with all of the scope_trackers to determine if adding this dynamic info will be a problem.
        for tracker in self._EnumPreviousScopeTrackers(unique_id):
            this_tracker = tracker

            if tracker.DynamicItems:
                last_item = tracker.DynamicItems[-1]

        assert this_tracker
        assert this_tracker.UniqueIdPart == unique_id[-1], (this_tracker.UniqueIdPart, unique_id[-1])

        if (
            not info.AllowParentTraversal
            and last_item is not None
            and last_item.IndentLevel == self._indent_level
        ):
            raise InvalidDynamicTraversalError(
                iter_after.Line,
                iter_after.Column,
                last_item.IterAfter,
            )

        this_tracker.DynamicItems.append(
            _ScopeItem(
                self._indent_level,
                iter_after.Clone(),
                info,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def _EnumDescendantScopeTrackers(
        cls,
        scope_trackers: Dict[Any, _ScopeTracker],
    ) -> Generator[_ScopeTracker, None, None]:
        for v in scope_trackers.values():
            yield v
            yield from cls._EnumDescendantScopeTrackers(v.Children)

    # ----------------------------------------------------------------------
    def _EnumPreviousScopeTrackers(
        self,
        unique_id: List[str],
    ) -> Generator[_ScopeTracker, None, None]:
        yield self._scope_trackers[_DefaultScopeTrackerTag]

        d = self._scope_trackers

        for id_part in unique_id:
            for k, v in d.items():
                if k == _DefaultScopeTrackerTag:
                    continue

                yield v

                if k == id_part:
                    d = v.Children
                    break
