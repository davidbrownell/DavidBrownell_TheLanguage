# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:27:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

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
    from ....Lexer.Types.TupleTypeLexerInfo import (
        TupleTypeLexerInfo,
        TypeLexerInfo,
    )

    from ....Parser.Phrases.DSL import Node


# ----------------------------------------------------------------------
class TupleType(TupleBase):
    """\
    Creates a tuple type that can be used where types are used.

    '(' <type> ',' ')'
    '(' <type> (',' <type>)+ ','? ')'

    Example:
        (Int, Char) Func():
            <statement>+
    """

    PHRASE_NAME                             = "Tuple Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleType, self).__init__(GrammarPhrase.Type.Type, self.PHRASE_NAME)

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
                TupleTypeLexerInfo(
                    CreateLexerRegions(node, node),  # type: ignore
                    [cast(TypeLexerInfo, GetLexerInfo(child)) for child in cls.EnumNodeValues(node)],
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
