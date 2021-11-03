# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 11:17:37
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

from typing import Callable, cast, List, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import TypeModifier
    from ..Common.Impl.TupleBase import TupleBase

    from ...GrammarInfo import AST, DynamicPhrasesType, ParserInfo

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Types.TupleTypeParserInfo import (
        TupleTypeParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class TupleType(TupleBase):
    """
    A tuple of types.

    '(' <type> ',')+ ')'

    Examples:
        (Int, Char) Func():
            pass
    """

    PHRASE_NAME                             = "Tuple Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        # TODO: TypeModifier
        super(TupleType, self).__init__(DynamicPhrasesType.Types, self.PHRASE_NAME)

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
        # ----------------------------------------------------------------------
        def Impl():
            types: List[TypeParserInfo] = []

            for type_node in cast(List[AST.Node], cls._EnumNodes(node)):
                types.append(cast(TypeParserInfo, GetParserInfo(type_node)))

            type_modifier_node = None
            type_modifier_info = None

            return TupleTypeParserInfo(
                CreateParserRegions(node, type_modifier_node),  # type: ignore
                types,
                type_modifier_info,
            )

        # ----------------------------------------------------------------------

        return Impl
