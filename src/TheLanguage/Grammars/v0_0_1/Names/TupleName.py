# ----------------------------------------------------------------------
# |
# |  TupleName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:06:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleHeader object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.TupleBase import TupleBase
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Names.TupleNameLexerInfo import NameLexerInfo, TupleNameLexerInfo

    from ....Parser.Phrases.DSL import Node


# ----------------------------------------------------------------------
class TupleName(TupleBase):
    """\
    Creates a tuple that can be used as a name.

    '(' <name> ',' ')'
    '(' <name> (',' <name>)+ ','? ')'

    Example:
        (a, b, (c, d)) = value
    """

    PHRASE_NAME                             = "Tuple Name"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleName, self).__init__(GrammarPhrase.Type.Name, self.PHRASE_NAME)

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                TupleNameLexerInfo(
                    CreateLexerRegions(node, node),  # type: ignore
                    [cast(NameLexerInfo, GetLexerInfo(child)) for child in cls.EnumNodeValues(node)],
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
