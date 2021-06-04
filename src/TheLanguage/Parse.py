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

import importlib
import os
import sys

from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Dict, List, Optional, Union

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
    from .Grammars.GrammarStatement import GrammarStatement, ImportGrammarStatement

    from .ParserImpl.MultifileParser import (
        Observer as MultifileObserver,
        Node,
        Parse as MultifileParse,
        RootNode,
    )

    from .ParserImpl.NormalizedIterator import NormalizedIterator
    from .ParserImpl.Statement import Statement
    from .ParserImpl.StatementsParser import DynamicStatementInfo

    from .ParserImpl.Syntax import (
        Observer as SyntaxObserver
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
Grammars: Dict[SemVer, DynamicStatementInfo]            = OrderedDict()
StatementLookup: Dict[Statement, GrammarStatement]      = OrderedDict()


# ----------------------------------------------------------------------
def _LoadDyanmicStatementsFromFile(
    filename: str,
    attribute_name: Optional[str]="Statements",
) -> DynamicStatementInfo:
    assert os.path.isfile(filename), filename

    dirname, basename = os.path.split(filename)
    basename = os.path.splitext(basename)[0]

    sys.path.insert(0, dirname)
    with CallOnExit(lambda: sys.path.pop(0)):
        mod = importlib.import_module(basename)

        grammar_statements = getattr(mod, attribute_name, None)
        assert grammar_statements is not None, filename

        statements = []
        expressions = []

        for grammar_statement in grammar_statements:
            if grammar_statement.TypeValue == GrammarStatement.Type.Statement:
                statements.append(grammar_statement.Statement)
            elif grammar_statement.TypeValue == GrammarStatement.Type.Expression:
                expressions.append(grammar_statement.Statement)
            else:
                assert False, grammar_statement.TypeValue  # pragma: no cover

            assert grammar_statement.Statement not in StatementLookup, grammar_statement.Statement
            StatementLookup[grammar_statement.Statement] = grammar_statement

        del sys.modules[basename]

        return DynamicStatementInfo(
            statements,
            expressions,
            allow_parent_traversal=False,
        )


# ----------------------------------------------------------------------
Grammars[SemVer("1.0.0")]                   = _LoadDyanmicStatementsFromFile(os.path.join(_script_dir, "Grammars", "v1_0_0", "AllStatements.py"))


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
):
    syntax_observer = SyntaxObserver(
        _Observer(
            source_roots,
            max_num_threads=max_num_threads,
        ),
        Grammars,
    )

    return MultifileParse(
        fully_qualified_names,
        syntax_observer.Syntaxes[syntax_observer.DefaultVersion],
        syntax_observer,
        single_threaded=max_num_threads == 1,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Observer(MultifileObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_roots: List[str],
        max_num_threads: Optional[int] = None,
    ):
        assert all(os.path.isdir(source_root) for source_root in source_roots)
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
    def ExtractDynamicStatementInfo(
        self,
        fully_qualified_name: str,
        node: RootNode,
    ) -> DynamicStatementInfo:
        # TODO
        return DynamicStatementInfo([], [])

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
    def OnIndent(
        self,
        fully_qualified_name: str,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(
        self,
        fully_qualified_name: str,
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ):
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def OnStatementComplete(
        self,
        fully_qualified_name: str,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,
        DynamicStatementInfo,
        MultifileObserver.ImportInfo,
    ]:
        try:
            grammar_statement = StatementLookup.get(node.Type, None)
        except TypeError:
            grammar_statement = None

        if isinstance(grammar_statement, ImportGrammarStatement):
            return grammar_statement.ProcessImportStatement(
                self._source_roots,
                fully_qualified_name,
                node,
            )

        return not self._is_cancelled
