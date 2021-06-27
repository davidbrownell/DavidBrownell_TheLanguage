# ----------------------------------------------------------------------
# |
# |  StatementsParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-11 05:50:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that parses multiple statements"""

import os
import textwrap

from collections import OrderedDict
from concurrent.futures import Future
from typing import Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error
    from .NormalizedIterator import NormalizedIterator
    from .Statement import DynamicStatements, Statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicStatementInfo(object):
    """Contains statements that have dynamically been added to the active scope"""

    statements: List[Statement]
    expressions: List[Statement]
    allow_parent_traversal: bool            = True      # If False, prevent content from including values from higher-level scope
    name: Optional[str]                     = None

    # ----------------------------------------------------------------------
    def Clone(
        self,
        updated_statements=None,
        updated_expressions=None,
        updated_allow_parent_traversal=None,
        updated_name=None,
    ):
        return self.__class__(
            updated_statements if updated_statements is not None else list(self.statements),
            updated_expressions if updated_expressions is not None else list(self.expressions),
            updated_allow_parent_traversal if updated_allow_parent_traversal is not None else self.allow_parent_traversal,
            name=updated_name if updated_name is not None else self.name,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDynamicTraversalError(Error):
    """Exception thrown when dynamic statements that prohibit parent traversal are applied over other dynamic statements"""

    ExistingDynamicStatements: List[NormalizedIterator]

    MessageTemplate                         = Interface.DerivedProperty("Dynamic statements that prohibit parent traversal should never be applied over other dynamic statements within the same lexical scope. You should make these dynamic statements the first ones applied in this lexical scope.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SyntaxInvalidError(Error):
    """Exception thrown when no matching statements were found"""

    PotentialStatements: Dict[Statement, Statement.ParseResultItemsType]    = field(init=False)
    parse_result_items: InitVar[Statement.ParseResultItemsType]

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")

    # ----------------------------------------------------------------------
    def __post_init__(self, parse_result_items):
        potentials = OrderedDict()

        for parse_result_item in parse_result_items:
            key = parse_result_item.Statement

            if isinstance(key, Statement.NamedItem):
                key = key.Item

            if isinstance(key, list):
                key = tuple(key)

            potentials[key] = parse_result_item.Results

        object.__setattr__(self, "PotentialStatements", potentials)

    # ----------------------------------------------------------------------
    def DebugString(self):
        content = []

        for parse_results in self.PotentialStatements.values():
            for parse_result in parse_results:
                if not parse_result.HasResults():
                    continue

                content.append(str(parse_result))

        return textwrap.dedent(
            """\
            {msg} [{line}, {column}]

            Partial Matches:
                {partial}

            """,
        ).format(
            msg=str(self),
            line=self.Line,
            column=self.Column,
            partial="<None>" if not content else StringHelpers.LeftJustify("\n".join(content).rstrip(), 4),
        )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
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
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ) -> Optional[DynamicStatementInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDedent(
        statement: Statement,
        results: Statement.ParseResultItemsType,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStatementComplete(
        result: Statement.StatementParseResultItem,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement (if necessary)
    ]:
        """Called on the completion of each statement"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def Parse(
    initial_statement_info: DynamicStatementInfo,
    normalized_iter: NormalizedIterator,
    observer: Observer,

    # True to execute all statements within a single thread
    single_threaded=False,
) -> Optional[List[Statement.StatementParseResultItem]]:
    """Repeatedly matches statements for all of the iterator"""

    assert normalized_iter.Offset == 0, normalized_iter.Offset

    statement_observer = _StatementObserver(initial_statement_info, observer)
    results = []

    while not normalized_iter.AtEnd():
        result = Statement.ParseMultiple(
            statement_observer.GetDynamicStatements(DynamicStatements.Statements),
            normalized_iter,
            statement_observer,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        if not result.Success:
            raise SyntaxInvalidError(
                result.Iter.Line,
                result.Iter.Column,
                result.Results,
            )

        normalized_iter = result.Iter

        assert len(result.Results) == 1, result.Results
        result = result.Results[0]

        results.append(result)

    assert normalized_iter.AtEnd()

    return results


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _StatementObserver(Statement.Observer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        init_statement_info: InitVar[DynamicStatementInfo],
        observer: Observer,
    ):
        all_statement_infos: List[
            List[
                Tuple[
                    Optional[NormalizedIterator],
                    DynamicStatementInfo,
                ]
            ]
        ] = [
            [ (None, init_statement_info.Clone()) ],
        ]

        self._observer                      = observer
        self._all_statement_infos           = all_statement_infos

        self._cached_statements: Union[Statement.NamedItem, List[Statement]]    = []
        self._cached_expressions: Union[Statement.NamedItem, List[Statement]]   = []

        self._UpdateCache()

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        return self._observer.Enqueue(funcs)

    # ----------------------------------------------------------------------
    @Interface.override
    def GetDynamicStatements(
        self,
        value: DynamicStatements,
    ) -> List[Statement]:
        if value == DynamicStatements.Statements:
            return self._cached_statements
        elif value == DynamicStatements.Expressions:
            return self._cached_expressions
        else:
            assert False, value  # pragma: no cover

        # Make the linter happy
        return []  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.override
    def OnIndent(self, statement, results):
        self._all_statement_infos.append([])

        this_result = self._observer.OnIndent(statement, results)
        if isinstance(this_result, DynamicStatementInfo):
            self.AddDynamicStatementInfo(results[-1].IterAfter, this_result)

        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def OnDedent(self, statement, results):
        assert self._all_statement_infos
        self._all_statement_infos.pop()
        assert len(self._all_statement_infos) >= 1, self._all_statement_infos

        self._UpdateCache()

        self._observer.OnDedent(statement, results)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnInternalStatement(
        self,
        result: Statement.StatementParseResultItem,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> bool:
        this_result = self._observer.OnStatementComplete(result, iter_before, iter_after)

        if isinstance(this_result, DynamicStatementInfo):
            self.AddDynamicStatementInfo(iter_before, this_result)
            return True

        return this_result

    # ----------------------------------------------------------------------
    def AddDynamicStatementInfo(
        self,
        normalized_iter: NormalizedIterator,
        info: DynamicStatementInfo,
    ):
        if not info.statements and not info.expressions:
            return

        if not info.allow_parent_traversal and self._all_statement_infos[-1]:
            raise InvalidDynamicTraversalError(
                normalized_iter.Line,
                normalized_iter.Column,
                [location for location, _ in self._all_statement_infos[-1] if location is not None],
            )

        self._all_statement_infos[-1].append((normalized_iter, info))

        self._UpdateCache()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _UpdateCache(self):
        statements = []
        statement_names = []

        expressions = []
        expression_names = []

        for statement_infos in reversed(self._all_statement_infos):
            for _, statement_info in reversed(statement_infos):
                if statement_info.statements:
                    statements += statement_info.statements
                    statement_names.append(
                        statement_info.name or Statement.ItemTypeToString(statement_info.statements),
                    )

                if statement_info.expressions:
                    expressions += statement_info.expressions
                    expression_names.append(
                        statement_info.name or Statement.ItemTypeToString(statement_info.expressions),
                    )

            if statement_infos and not statement_infos[0][1].allow_parent_traversal:
                break

        # In the code above, we reversed the list so that statements added later (or nearer)
        # to the code would be matched before statements defined further away. However when
        # displaying the content names, we want the names to be the order in which they were
        # defined.
        if statement_names:
            statement_names = " / ".join(reversed(statement_names))
            statements = Statement.NamedItem(statement_names, statements)

        if expression_names:
            expression_names = " / ".join(reversed(expression_names))
            expressions = Statement.NamedItem(expression_names, expressions)

        self._cached_statements = statements
        self._cached_expressions = expressions
