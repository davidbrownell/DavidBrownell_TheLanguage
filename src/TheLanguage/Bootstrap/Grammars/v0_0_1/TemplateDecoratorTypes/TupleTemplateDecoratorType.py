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
    from ..Common.Impl.TupleBase import TupleBase

    from ...GrammarInfo import AST, DynamicPhrasesType, ParserInfo

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Types.TupleTypeParserInfo import (
        TupleTypeParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class TupleTemplateDecoratorType(TupleBase):
    PHRASE_NAME                             = "Tuple TemplateDecoratorType"

    # ----------------------------------------------------------------------
    def __init__(self):
        # TODO: TypeModifier
        super(TupleTemplateDecoratorType, self).__init__(
            DynamicPhrasesType.TemplateDecoratorTypes,
            self.PHRASE_NAME,
            tuple_element_item=DynamicPhrasesType.Types,
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
