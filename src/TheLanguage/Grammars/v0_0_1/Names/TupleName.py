# ----------------------------------------------------------------------
# |
# |  TupleName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 10:57:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleName object"""

import os

from typing import Callable, cast, List, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.TupleBase import TupleBase

    from ...GrammarInfo import AST, DynamicPhrasesType, ParserInfo

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Names.TupleNameParserInfo import (
        NameParserInfo,
        TupleNameParserInfo,
    )


# ----------------------------------------------------------------------
class TupleName(TupleBase):
    """\
    A tuple of names.

    '(' (<name> ',')+ ')'

    Examples:
        (a, b, (c, d)) = value
    """

    PHRASE_NAME                             = "Tuple Name"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleName, self).__init__(DynamicPhrasesType.Names, self.PHRASE_NAME)

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
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            names: List[NameParserInfo] = []

            for name_node in cast(List[AST.Node], cls._EnumNodes(node)):
                names.append(cast(NameParserInfo, GetParserInfo(name_node)))

            return TupleNameParserInfo(
                CreateParserRegions(node),  # type: ignore
                names,
            )

        # ----------------------------------------------------------------------

        return Impl
