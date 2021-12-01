import os
import re

from typing import Callable, cast, List, Optional, Tuple, Union

from dataclasses import dataclass

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

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        ExtractTokenSpan,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.PythonHackStatementParserInfo import PythonHackStatementParserInfo


# ----------------------------------------------------------------------
class PythonHackStatement(GrammarPhrase):
    PHRASE_NAME                             = "Python Hack Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PythonHackStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    CommonTokens.RegexToken("PythonHack", re.compile(r"python_hack: (?P<value>[^\n]*)")),
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        # <data>
        data_node = cast(AST.Leaf, nodes[0])
        data_info = cast(str, ExtractToken(data_node))

        return PythonHackStatementParserInfo(
            CreateParserRegions(node, data_node),  # type: ignore
            data_info,
        )
