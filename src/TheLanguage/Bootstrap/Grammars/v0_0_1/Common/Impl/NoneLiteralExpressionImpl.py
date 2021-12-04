import os
import re

from typing import Callable, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.Tokens import RegexToken

    from ....GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from .....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
    )

    from .....Parser.Parser import CreateParserRegions

    from .....Parser.Literals.NoneLiteralParserInfo import NoneLiteralParserInfo


# ----------------------------------------------------------------------
class NoneLiteralExpressionImpl(GrammarPhrase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        dynamic_phrases_type: DynamicPhrasesType,
    ):
        super(NoneLiteralExpressionImpl, self).__init__(
            dynamic_phrases_type,
            CreatePhrase(
                name=phrase_name,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken.Create("'None'", re.compile(r"None\b")),
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
        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        return NoneLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
        )
