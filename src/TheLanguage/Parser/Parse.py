# ----------------------------------------------------------------------
# |
# |  Parse.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-23 09:55:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps with parsing"""

import asyncio
import importlib
import os
import sys

from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from typing import cast, Callable, Dict, List, Optional, Tuple, Union

from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Syntax import (
        Observer as SyntaxObserver
    )

    from .TranslationUnitsParser import (
        DynamicStatementInfo,
        Leaf,
        Node,
        Observer as TranslationUnitsParserObserver,
        ParseAsync as TranslationUnitsParseAsync,
        RootNode,
        Statement,
    )

    from .Grammars.GrammarStatement import GrammarStatement, ImportGrammarStatement

    from .Components.NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
Grammars: Dict[SemVer, DynamicStatementInfo]            = OrderedDict()
StatementLookup: Dict[Statement, GrammarStatement]      = OrderedDict()


# ----------------------------------------------------------------------
def _LoadDyanmicStatementsFromFile(
    filename: str,
    attribute_name: Optional[str]=None,
) -> DynamicStatementInfo:
    assert os.path.isfile(filename), filename

    attribute_name = attribute_name or "Statements"

    dirname, basename = os.path.split(filename)
    basename = os.path.splitext(basename)[0]

    sys.path.insert(0, dirname)
    with CallOnExit(lambda: sys.path.pop(0)):
        mod = importlib.import_module(basename)

        grammar_statements = getattr(mod, attribute_name, None)
        assert grammar_statements is not None, filename

        statements = []
        expressions = []
        types = []

        for grammar_statement in grammar_statements:
            if grammar_statement.TypeValue == GrammarStatement.Type.Statement:
                statements.append(grammar_statement.Statement)
            elif grammar_statement.TypeValue == GrammarStatement.Type.Expression:
                expressions.append(grammar_statement.Statement)
            elif grammar_statement.TypeValue == GrammarStatement.Type.Type:
                types.append(grammar_statement.Statement)
            else:
                assert False, grammar_statement.TypeValue  # pragma: no cover

            assert grammar_statement.Statement not in StatementLookup, grammar_statement.Statement
            StatementLookup[grammar_statement.Statement] = grammar_statement

        del sys.modules[basename]

        return DynamicStatementInfo(
            tuple(statements),
            tuple(expressions),
            tuple(types),
            AllowParentTraversal=False,
        )


# ----------------------------------------------------------------------
Grammars[SemVer("1.0.0")]                   = _LoadDyanmicStatementsFromFile(os.path.join(_script_dir, "Grammars", "v1_0_0", "All.py"))


# ----------------------------------------------------------------------
assert StatementLookup
del _LoadDyanmicStatementsFromFile


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def Parse(
    fully_qualified_names: List[str],
    source_roots: List[str],
    max_num_threads: Optional[int]=None,
) -> Union[
    None,
    Dict[str, RootNode],
    List[Exception],
]:
    """\
    Return AST(s) for the given names.

    This information can be used to completely regenerate the original source. This is valuable for
    writing things like source formatting tools, but contains extraneous data that can make parsing
    more difficult (for example, comments and vertical whitespace).

    The `Prune` function should be used before invoking additional functionality.
    """

    syntax_observer = SyntaxObserver(
        _Observer(
            source_roots,
            max_num_threads=max_num_threads,
        ),
        Grammars,
    )

    return asyncio.get_event_loop().run_until_complete(
        TranslationUnitsParseAsync(
            fully_qualified_names,
            syntax_observer.Syntaxes[syntax_observer.DefaultVersion],
            syntax_observer,
            single_threaded=max_num_threads == 1,
        ),
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, RootNode],
    max_num_threads: Optional[int]=None,
):
    """Removes Leaf nodes that have been explicitly ignored for easier parsing"""

    _Execute(
        lambda fqn, node: _Prune(node),
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
def Validate(
    roots: Dict[str, RootNode],
    max_num_threads: Optional[int]=None,
):
    """Invokes functionality to validate a node and its children in isolation"""

    _Execute(
        _ValidateRoot,
        roots,
        max_num_threads=max_num_threads,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Observer(TranslationUnitsParserObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_roots: List[str],
        max_num_threads: Optional[int] = None,
    ):
        for source_root in source_roots:
            assert os.path.isdir(source_root), source_root

        assert max_num_threads is None or max_num_threads > 0, max_num_threads

        self._is_cancelled                  = False
        self._source_roots                  = source_roots
        self._executor                      = ThreadPoolExecutor(
            max_workers=max_num_threads,
        )

    # ----------------------------------------------------------------------
    def Cancel(self):
        self._is_cancelled = True

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        # TODO: Handle scenario where there are too many enqueued items
        return [self._executor.submit(func) for func in funcs]

    # ----------------------------------------------------------------------
    @Interface.override
    def LoadContent(
        self,
        fully_qualified_name: str,
    ) -> str:
        assert os.path.isfile(fully_qualified_name), fully_qualified_name

        with open(fully_qualified_name) as f:
            content = f.read()

        return content

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicStatements(
        self,
        fully_qualified_name: str,
        node: RootNode,
    ) -> DynamicStatementInfo:
        # TODO
        return DynamicStatementInfo((), (), ())

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        fully_qualified_name: str,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Optional[DynamicStatementInfo]:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(
        self,
        fully_qualified_name: str,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> None:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnStatementCompleteAsync(
        self,
        fully_qualified_name: str,
        statement: Statement,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,
        DynamicStatementInfo,
        TranslationUnitsParserObserver.ImportInfo,
    ]:
        try:
            grammar_statement = StatementLookup.get(statement, None)
        except TypeError:
            grammar_statement = None

        if grammar_statement is not None:
            if isinstance(grammar_statement, ImportGrammarStatement):
                return grammar_statement.ProcessImportStatement(
                    self._source_roots,
                    fully_qualified_name,
                    node,
                )

        return not self._is_cancelled


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    func: Callable[[str, RootNode], None],
    roots: Dict[str, RootNode],
    max_num_threads: Optional[int]=None,
):
    use_futures = max_num_threads != 1 and len(roots) != 1

    if use_futures:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(lambda k=k, v=v: func(k, v))
                for k, v in roots.items()
            ]

            [future.result() for future in futures]
            return

    for k, v in roots.items():
        func(k, v)


# ----------------------------------------------------------------------
def _Prune(
    node: Union[RootNode, Node],
):
    child_index = 0

    while child_index < len(node.Children):
        child = node.Children[child_index]

        should_delete = False

        if isinstance(child, Node):
            _Prune(child)

            if not child.Children:
                should_delete = True

        elif isinstance(child, Leaf):
            if child.IsIgnored:
                should_delete = True

        else:
            assert False, child  # pragma: no cover

        if not should_delete:
            child_index += 1
            continue

        del node.Children[child_index]


# ----------------------------------------------------------------------
def _ValidateRoot(
    fully_qualified_name: str,
    root: RootNode,
):
    try:
        for child in root.Children:
            _ValidateNode(child)

    except Exception as ex:
        if not hasattr(ex, "FullyQualifiedName"):
            object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

        raise


# ----------------------------------------------------------------------
def _ValidateNode(
    node: Union[Node, Leaf],
):
    if isinstance(node.Type, Statement):
        grammar_statement = StatementLookup.get(cast(Statement, node.Type), None)
        if grammar_statement:
            result = grammar_statement.ValidateNodeSyntax(cast(Node, node))
            if isinstance(result, bool) and not result:
                return

    for child in getattr(node, "Children", []):
        _ValidateNode(child)
