# ----------------------------------------------------------------------
# |
# |  TranslationUnitParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-01 15:36:23
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

import asyncio
import os
import textwrap

from typing import cast, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error
    from .NormalizedIterator import NormalizedIterator
    from .StatementEx import DynamicStatements, Statement, StatementEx

    from .StatementImpl.DynamicStatement import DynamicStatement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DynamicStatementInfo(object):
    """Contains Statements that have been dynamically added to the active scope"""

    Statements: List[Statement]
    Expressions: List[Statement]
    AllowParentTraversal: bool              = True      # If False, prevent content from including values from higher-level scope
    Name: Optional[str]                     = None

    # ----------------------------------------------------------------------
    def Clone(
        self,
        updated_statements=None,
        updated_expressions=None,
        updated_allow_parent_traversal=None,
        updated_name=None,
    ):
        return self.__class__(
            updated_statements if updated_statements is not None else list(self.Statements),
            updated_expressions if updated_expressions is not None else list(self.Expressions),
            updated_allow_parent_traversal if updated_allow_parent_traversal is not None else self.AllowParentTraversal,
            updated_name if updated_name is not None else self.Name,
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

    DataItems: List[Statement.ParseResultData]

    MessageTemplate                         = Interface.DerivedProperty("The syntax is not recognized")

    # ----------------------------------------------------------------------
    def ToString(
        self,
        verbose=False,
    ):
        return textwrap.dedent(
            """\
            {message} [{line}, {column}]

            {content}
            """,
        ).format(
            message=str(self),
            line=self.Line,
            column=self.Column,
            content="".join(
                [
                    data_item.ToString(
                        verbose=verbose,
                    )
                    for data_item in self.DataItems
                ],
            ).rstrip(),
        )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnIndentAsync(
        data: Statement.TokenParseResultData,
    ) -> Optional[DynamicStatementInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnDedentAsync(
        data: Statement.TokenParseResultData,
    ):
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnStatementCompleteAsync(
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement
    ]:
        """Invoked when an internal statement is successfully matched"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    initial_statement_info: DynamicStatementInfo,
    normalized_iter: NormalizedIterator,
    observer: Observer,
    single_threaded=False,
) -> Optional[List[Statement.ParseResultData]]:
    """Repeatedly matches statements for all of the iterator"""

    assert normalized_iter.Offset == 0, normalized_iter

    location_and_data_items: List[_LocationAndData] = []

    # ----------------------------------------------------------------------
    def ToDataResults() -> List[Statement.ParseResultData]:
        return [item.Data for item in location_and_data_items]

    # ----------------------------------------------------------------------

    statement_observer = _StatementObserver(
        initial_statement_info,
        observer,
        location_and_data_items,
    )

    statement = DynamicStatement(
        lambda observer: cast(StatementEx.Observer, observer).GetDynamicStatements(DynamicStatements.Statements),
    )

    while not normalized_iter.AtEnd():
        result = await statement.ParseAsync(
            normalized_iter,
            statement_observer,
            ignore_whitespace=False,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        assert result.Data
        location_and_data_items.append(
            _LocationAndData(
                result.Iter,
                result.Data,
            ),
        )

        if not result.Success:
            raise SyntaxInvalidError(
                result.Iter.Line,
                result.Iter.Column,
                ToDataResults(),
            )

        normalized_iter = result.Iter.Clone()

    assert normalized_iter.AtEnd()

    return ToDataResults()


# ----------------------------------------------------------------------
def Parse(*args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(ParseAsync(*args, **kwargs))


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _LocationAndData(object):
    Location: NormalizedIterator
    Data: Statement.ParseResultData

# ----------------------------------------------------------------------
class _StatementObserver(StatementEx.Observer):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        init_statement_info: DynamicStatementInfo,
        observer: Observer,
        location_and_data_items: List[_LocationAndData],
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
        self._location_and_data_items       = location_and_data_items

        self._all_statement_infos           = all_statement_infos

        self._cached_statements: Tuple[str, List[Statement]] = []
        self._cached_expressions: Tuple[str, List[Statement]] = []

        self._UpdateCache()

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

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(
        self,
        data: Statement.TokenParseResultData,
    ):
        self._all_statement_infos.append([])

        this_result = await self._observer.OnIndentAsync(data)
        if isinstance(this_result, DynamicStatementInfo):
            assert self._location_and_data_items
            self.AddDynamicStatementInfo(self._location_and_data_items[-1].Location, this_result)

        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(
        self,
        data: Statement.TokenParseResultData,
    ):
        assert self._all_statement_infos
        self._all_statement_infos.pop()
        assert len(self._all_statement_infos) >= 1, self._all_statement_infos

        self._UpdateCache()

        await self._observer.OnDedentAsync()

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnInternalStatementAsync(
        self,
        statement: Statement,
        data: Optional[Statement.ParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> bool:
        this_result = await self._observer.OnStatementCompleteAsync(statement, data, iter_before, iter_after)

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
        if not info.Statements and not info.Expressions:
            return

        if not info.AllowParentTraversal and self._all_statement_infos[-1]:
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
        for statement_info_attribute_name, cached_attribute_name in [
            ("Statements", "_cached_statements"),
            ("Expressions", "_cached_expressions"),
        ]:
            cached_statements = []
            names = []
            id_lookup = set()

            for statement_infos in reversed(self._all_statement_infos):
                for _, statement_info in reversed(statement_infos):
                    statements = getattr(statement_info, statement_info_attribute_name)
                    added_statement = False

                    for statement in statements:
                        this_id = id(statement)

                        if this_id in id_lookup:
                            continue

                        id_lookup.add(this_id)

                        cached_statements.append(statement)
                        added_statement = True

                    if added_statement:
                        names.append(
                            statement_info.Name or "[{}]".format(", ".join([statement.Name for statement in statements])),
                        )

                if statement_infos and not statement_infos[0][1].AllowParentTraversal:
                    break

            # In the code above, we reversed the list so that statements added later (or nearer)
            # to the code would be matched before statements defined further away. However when
            # displaying the content names, we want the names to be the order in which they were
            # defined.
            names = " / ".join(reversed(names))

            setattr(self, cached_attribute_name, (names, cached_statements))
