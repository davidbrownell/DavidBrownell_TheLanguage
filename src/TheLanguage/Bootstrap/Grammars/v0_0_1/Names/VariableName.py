# ----------------------------------------------------------------------
# |
# |  VariableName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 12:57:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableName object"""

import os

from typing import Callable, cast, Tuple, Union

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
        ExtractSequence,
        ExtractToken,
    )

    from ....Parser.Parser import CreateParserRegions
    from ....Parser.Names.VariableNameParserInfo import VariableNameParserInfo


# ----------------------------------------------------------------------
class VariableName(GrammarPhrase):
    """\
    A variable name.

    <name>

    Examples:
        foo
        bar
    """

    PHRASE_NAME                             = "Variable Name"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableName, self).__init__(
            DynamicPhrasesType.Names,
            CreatePhrase(
                name=self.PHRASE_NAME,

                # Note that this needs to be a sequence rather than just the name as this is the only
                # way to ensure that the extraction below is invoked. If just the name, there would
                # be nothing to tie the token to this phrase.
                item=[CommonTokens.GenericLowerName],
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

        # <generic_name>
        name_leaf = cast(AST.Leaf, nodes[0])
        name_info = cast(str, ExtractToken(name_leaf))

        if not CommonTokens.VariableNameRegex.match(name_info):
            raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "variable")

        return VariableNameParserInfo(
            CreateParserRegions(name_leaf),  # type: ignore
            name_info,
        )
