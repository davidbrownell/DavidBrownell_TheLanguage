# ----------------------------------------------------------------------
# |
# |  RepeatStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-25 16:17:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RepeatStatement object"""

import os
import textwrap

from typing import cast, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement as StatementType


# ----------------------------------------------------------------------
class RepeatStatement(StatementType):
    """Matches content that repeats the provided statement N times"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class RepeatParseResultData(StatementType.ParseResultData):
        """Result return for both matching and non-matching statements"""

        Statement: StatementType
        DataItems: List[Optional[StatementType.ParseResultData]]

        # ----------------------------------------------------------------------
        @Interface.override
        def __str__(self) -> str:
            results = []

            for data_item_index, data_item in enumerate(self.DataItems):
                prefix = "{}) ".format(data_item_index)

                results.append(
                    "{}{}".format(
                        prefix,
                        StringHelpers.LeftJustify(str(data_item).rstrip(), len(prefix)),
                    ),
                )

            if not results:
                results.append("<No Results>")

            return textwrap.dedent(
                """\
                {name}
                    {results}
                """,
            ).format(
                name=self.Statement.Name,
                results=StringHelpers.LeftJustify("\n".join(results), 4),
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def EnumTokens(self) -> Generator[StatementType.TokenParseResultData, None, None]:
            for data in self.DataItems:
                if data is None:
                    continue

                yield from data.EnumTokens()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: StatementType,
        min_matches: int,
        max_matches: Optional[int],
        name: str=None,
    ):
        assert min_matches >= 0, min_matches
        assert max_matches is None or max_matches >= min_matches, (min_matches, max_matches)

        name = name or "Repeat: ({}, {}, {})".format(statement.Name, min_matches, max_matches)

        super(RepeatStatement, self).__init__(name)

        self.Statement                      = statement
        self.MinMatches                     = min_matches
        self.MaxMatches                     = max_matches

    # ----------------------------------------------------------------------
    @Interface.override
    def Parse(
        self,
        normalized_iter: StatementType.NormalizedIterator,
        observer: StatementType.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        StatementType.ParseResult,
        None,
    ]:
        queue_command_observer                                              = StatementType.QueueCommandObserver(observer)
        results: List[StatementType.ParseResult]                            = []
        error_result: Optional[StatementType.ParseResult]                   = None

        while not normalized_iter.AtEnd():
            this_queue_command_observer = StatementType.QueueCommandObserver(queue_command_observer)

            result = self.Statement.Parse(
                normalized_iter.Clone(),
                this_queue_command_observer,
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            if not result.Success:
                error_result = result
                break

            replay_result = this_queue_command_observer.Replay()
            assert replay_result

            on_internal_statement_results = queue_command_observer.OnInternalStatement(
                self.Statement,
                result.Data,
                normalized_iter,
                result.Iter,
            )
            assert on_internal_statement_results

            results.append(result)
            normalized_iter = result.Iter.Clone()

            if self.MaxMatches is not None and len(results) == self.MaxMatches:
                break

        results = cast(List[StatementType.ParseResult], results)

        success = (
            len(results) >= self.MinMatches
            and (
                self.MaxMatches is None
                or self.MaxMatches >= len(results)
            )
        )

        if not success:
            assert error_result

            return StatementType.ParseResult(
                False,
                error_result.Iter,
                RepeatStatement.RepeatParseResultData(
                    self.Statement,
                    [result.Data for result in results] + [error_result.Data],
                ),
            )

        if not queue_command_observer.Replay():
            return None

        return StatementType.ParseResult(
            True,
            normalized_iter,
            RepeatStatement.RepeatParseResultData(
                self.Statement,
                [result.Data for result in results],
            ),
        )
