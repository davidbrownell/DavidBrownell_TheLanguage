# ----------------------------------------------------------------------
# |
# |  ClassDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-28 15:41:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassDeclarationStatement object"""

import os
import textwrap

from typing import cast, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.GrammarAST import (
        ExtractDynamicExpressionNode,
        ExtractLeafValue,
        ExtractOptionalNode,
        ExtractOrNode,
        ExtractRepeatedNodes,
        Leaf,
        Node,
    )

    from .Common import GrammarDSL
    from .Common import NamingConventions
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class ClassDeclarationStatement(GrammarStatement):
    """\
    Class definition.

    'public'|'protected'|'private'?
        'class'|'interface'|'mixin' <name>
            ('public'|'protected'|'private' <name>)?
            ('implements' <name>)*
            ('uses' <name>)*
    ':'
        <docstring>?
        <statement>+
    """

    NODE_NAME                               = "Class Declaration"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class Info(object):
        Visibility: Optional[str]           # TODO: This should be an enum
        Type: str                           # TODO: This should be an enum
        Name: str
        Base: Optional[Tuple[str, str]]
        Interfaces: List[str]
        Mixins: List[str]
        Docstring: Optional[str]
        Statements: List[Node]

        # ----------------------------------------------------------------------
        def __str__(self):
            return self.ToString()

        # ----------------------------------------------------------------------
        def ToString(
            self,
            verbose=False,
        ) -> str:
            return textwrap.dedent(
                """\
                {name} {the_type}
                    Visibility: {visibility}
                    Statements: {num_statements}
                    Base: {base}
                    Interfaces:{interfaces}
                    Mixins:{mixins}
                    Docstring:
                        {docstring}
                """,
            ).format(
                name=self.Name,
                the_type=self.Type,
                visibility=self.Visibility,
                num_statements=len(self.Statements),
                base="<None>" if not self.Base else "{} {}".format(*self.Base),
                interfaces=" <None>" if not self.Interfaces else "\n    {}".format(
                    StringHelpers.LeftJustify("\n".join(self.Interfaces), 8).rstrip(),
                ),
                mixins=" <None>" if not self.Mixins else "\n    {}".format(
                    StringHelpers.LeftJustify("\n".join(self.Mixins), 8).rstrip(),
                ),
                docstring=StringHelpers.LeftJustify(
                    (self.Docstring or "<No Data>").rstrip(),
                    8,
                ),
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    # 'public'|'protected'|'private'?
                    GrammarDSL.StatementItem(
                        name="Visibility",
                        item=tuple(CommonTokens.AllAccessModifiers),
                        arity="?",
                    ),

                    # 'class'|'interface'|'mixin'
                    (
                        CommonTokens.Class,
                        CommonTokens.Interface,
                        CommonTokens.Mixin,
                    ),

                    # <name>
                    CommonTokens.Name,

                    # Bases
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # Base Class
                    GrammarDSL.StatementItem(
                        name="Base",
                        item=[
                            # 'public'|'protected'|'private'
                            tuple(CommonTokens.AllAccessModifiers),
                            CommonTokens.Name
                        ],
                        arity="?",
                    ),

                    # Interfaces
                    GrammarDSL.StatementItem(
                        name="Interfaces",
                        item=[
                            CommonTokens.Implements,
                            CommonTokens.Name,
                        ],
                        arity="*",
                    ),

                    # Mixins
                    GrammarDSL.StatementItem(
                        name="Mixins",
                        item=[
                            CommonTokens.Uses,
                            CommonTokens.Name,
                        ],
                        arity="*",
                    ),

                    CommonTokens.PopIgnoreWhitespaceControl,

                    # ':', <newline>, <indent>
                    CommonTokens.Colon,
                    CommonTokens.Newline,
                    CommonTokens.Indent,

                    # <docstring>?
                    GrammarDSL.StatementItem(
                        name="Docstring",
                        item=[
                            CommonTokens.DocString,
                            CommonTokens.Newline,
                        ],
                        arity="?",
                    ),

                    # <statement>+
                    GrammarDSL.StatementItem(
                        GrammarDSL.DynamicStatements.Statements,
                        arity="+",
                    ),

                    CommonTokens.Dedent,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        child_index = 0

        # 'public'|'protected'|'private'?
        assert len(node.Children) >= child_index + 1

        potential_visibility_node = ExtractOptionalNode(node, child_index, "Visibility")
        if potential_visibility_node is not None:
            child_index += 1

            visibility = ExtractLeafValue(
                cast(Leaf, potential_visibility_node),
                group_value_name=None,
            )
        else:
            visibility = None

        # 'class'|'interface'|'mixin'
        assert len(node.Children) >= child_index + 1
        the_type = ExtractLeafValue(
            cast(Leaf, node.Children[child_index]),
            group_value_name=None,
        )
        child_index += 1

        # <name>
        assert len(node.Children) >= child_index + 1
        name = ExtractLeafValue(cast(Leaf, node.Children[child_index]))

        if not NamingConventions.Type.Regex.match(name):
            raise NamingConventions.InvalidTypeNameError.FromNode(node.Children[child_index], name)

        child_index += 1

        # Base Class
        potential_base_node = ExtractOptionalNode(node, child_index, "Base")
        if potential_base_node is not None:
            child_index += 1

            potential_base_node = cast(Node, potential_base_node)
            assert len(potential_base_node.Children) == 2

            base_info = (
                ExtractLeafValue(
                    cast(Leaf, ExtractOrNode(cast(Node, potential_base_node.Children[0]))),
                ),
                ExtractLeafValue(cast(Leaf, potential_base_node.Children[1])),
            )
        else:
            base_info = None

        # Interfaces
        interfaces = []

        potential_interface_nodes = ExtractRepeatedNodes(node, child_index, "Interfaces")
        if potential_interface_nodes is not None:
            child_index += 1

            for interface_node in potential_interface_nodes:
                interface_node = cast(Node, interface_node)

                assert len(interface_node.Children) == 2
                interfaces.append(ExtractLeafValue(cast(Leaf, interface_node.Children[1])))

        # Mixins
        mixins = []

        potential_mixin_nodes = ExtractRepeatedNodes(node, child_index, "Mixins")
        if potential_mixin_nodes is not None:
            child_index += 1

            for mixin_node in potential_mixin_nodes:
                mixin_node = cast(Node, mixin_node)

                assert len(mixin_node.Children) == 2
                mixins.append(ExtractLeafValue(cast(Leaf, mixin_node.Children[1])))

        # ':', <newline>, <indent>
        assert len(node.Children) >= child_index + 3
        child_index += 3

        # <docstring>?
        docstring_node = ExtractOptionalNode(node, child_index, "Docstring")
        if docstring_node is not None:
            child_index += 1

            docstring_node = cast(Node, docstring_node)
            assert len(docstring_node.Children) == 2
            docstring_node = cast(Leaf, docstring_node.Children[0])

            docstring = ExtractLeafValue(docstring_node)
        else:
            docstring = None

        # <statement>+
        assert len(node.Children) >= child_index + 1
        statements = [
            ExtractDynamicExpressionNode(cast(Node, child))
            for child in cast(Node, node.Children[child_index]).Children
        ]
        child_index += 1

        # <dedent>
        child_index += 1

        assert len(node.Children) == child_index

        # Persist the info
        object.__setattr__(
            node,
            "Info",
            cls.Info(
                visibility,
                name,
                the_type,
                base_info,
                interfaces,
                mixins,
                docstring,
                statements,
            ),
        )
