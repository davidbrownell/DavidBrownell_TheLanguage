# ----------------------------------------------------------------------
# |
# |  AsExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-18 14:07:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AsExpression object"""

import os

from typing import List, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import GrammarDSL
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.Statements.OrStatement import OrStatement
    from ...ParserImpl.Statements.Statement import Statement


# ----------------------------------------------------------------------
class AsExpression(GrammarStatement):
    """<expr> 'as' <type>"""

    NODE_NAME                               = "As"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(AsExpression, self).__init__(
            GrammarStatement.Type.Expression,
            _AsStatement(
                self.NODE_NAME,
                GrammarDSL.CreateStatement(
                    name=self.NODE_NAME,
                    item=[
                        GrammarDSL.DynamicStatements.Expressions,
                        CommonTokens.As,
                        GrammarDSL.DynamicStatements.Types,
                    ],
                ),
            ),
        )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _AsStatement(Statement):
    """\
    This statement is an expression that leverages an expression. Detect
    cycles to prevent infinite recursion.
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        statement: Statement,
    ):
        assert statement

        super(_AsStatement, self).__init__(name)

        self._statement                     = statement

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        unique_id: List[str],
        normalized_iter: Statement.NormalizedIterator,
        observer: Statement.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Statement.ParseResult,
        None,
    ]:
        # Don't allow recursion
        if unique_id[-1] in unique_id[:-1]:
            return Statement.ParseResult(False, normalized_iter.Clone(), None)

        return await self._statement.ParseAsync(
            unique_id,
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_statement: "Statement",
    ):
        return self._statement.PopulateRecursiveImpl(new_statement)
