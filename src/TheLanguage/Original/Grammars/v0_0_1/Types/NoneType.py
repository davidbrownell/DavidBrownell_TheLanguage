# ----------------------------------------------------------------------
# |
# |  NoneType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-27 15:12:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneType object"""

import os
import re

from typing import Callable, cast, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Tokens import RegexToken
    from ..Common import TypeModifier

    from ...Error import Error

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegion, CreateParserRegions
    from ....Parser.Types.NoneTypeParserInfo import NoneTypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneWithModifierError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Modifiers should never be applied to 'None' types.",
    )


# ----------------------------------------------------------------------
class NoneType(GrammarPhrase):
    """\
    No type.

    'None'

    Examples:
        None
    """

    PHRASE_NAME                             = "None Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(NoneType, self).__init__(
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    RegexToken("'None'", re.compile(r"None\b")),

                    # <modifier>?
                    OptionalPhraseItem.Create(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
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
        assert len(nodes) == 2

        # <modifier>?
        modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
        if modifier_node is not None:
            # Here, we check for a modifier and then throw an exception if one is found. This seems
            # strange, but allows for more helpful error messages. Without this code, a type modifier
            # will appear to be a valid variable name, and the error will be associated with code later
            # within the phrase (which isn't helpful).
            raise NoneWithModifierError(CreateParserRegion(modifier_node))

        return NoneTypeParserInfo(
            CreateParserRegions(node),  # type: ignore
        )
