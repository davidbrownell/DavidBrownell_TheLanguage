"""Contains the PassStatement object"""

import os

from typing import Callable, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import CreatePhrase

    from ....Parser.Parser import CreateParserRegions
    from ....Parser.Statements.NoopStatementParserInfo import NoopStatementParserInfo


# ----------------------------------------------------------------------
class PassStatement(GrammarPhrase):
    """\
    Noop (No-Operation) statement.

    'pass'

    Example:
        Int var Func():
            pass
    """

    PHRASE_NAME                             = "Pass Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PassStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "pass",
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        return NoopStatementParserInfo(
            CreateParserRegions(node),  # type: ignore
        )
