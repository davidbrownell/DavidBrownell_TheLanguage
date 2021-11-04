import os
import re

from typing import Callable, cast, Tuple, Union

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
        ExtractToken,
    )

    from .....Parser.Parser import CreateParserRegions

    from .....Parser.Literals.BoolLiteralParserInfo import BoolLiteralParserInfo


# ----------------------------------------------------------------------
class BoolLiteralExpressionImpl(GrammarPhrase):

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        dynamic_phrases_type: DynamicPhrasesType,
    ):
        super(BoolLiteralExpressionImpl, self).__init__(
            dynamic_phrases_type,
            CreatePhrase(
                name=phrase_name,
                item=[
                    # Note that this must be a sequence so that ExtractParserInfo will be called.
                    RegexToken(
                        "<bool>",
                        re.compile(r"(?P<value>True|False)\b"),
                    ),
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

        # <bool>
        bool_leaf = cast(AST.Leaf, nodes[0])
        bool_value = cast(str, ExtractToken(bool_leaf))

        if bool_value == "True":
            bool_info = True
        elif bool_value == "False":
            bool_info = False
        else:
            assert False, bool_value  # pragma: no cover

        return BoolLiteralParserInfo(
            CreateParserRegions(node),  # type: ignore
            bool_info,
        )
