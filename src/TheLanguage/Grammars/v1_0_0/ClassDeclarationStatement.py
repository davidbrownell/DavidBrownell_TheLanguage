# ----------------------------------------------------------------------
# |
# |  ClassDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-17 08:13:51
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens
    from .Common import Statements as CommonStatements
    from .Common import NamingConventions

    from .Impl import CustomStatements

    from .CommentStatement import CommentStatement
    from .VerticalWhitespaceStatement import VerticalWhitespaceStatement

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Leaf,
        Node,
        Statement,
        ValidationError,
    )


# ----------------------------------------------------------------------
class ClassDeclarationStatement(GrammarStatement):
    """\
    Class definition.

    'export'? 'class' <class_name> (
            'public'|'protected'|'private' <base_class_name>
        |   'implements' <interface_name>
        |   'uses' <mixin_name>
    )* ':'
        <statements>
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        class_statements = [
            CustomStatements.DynamicContentStatement,
            # BugBug: Attributes
            # BugBug: Methods
            CommentStatement().Statement,
            VerticalWhitespaceStatement().Statement,
        ] # BugBug

        suffix_statement = [
            Statement(
                "Inheritance",
                [
                    CommonTokens.Public,
                    CommonTokens.Protected,
                    CommonTokens.Private,
                ],
                CommonTokens.Name,
            ),
            Statement(
                "Implements",
                CommonTokens.Implements,
                CommonTokens.Name,
            ),
            Statement(
                "Uses",
                CommonTokens.Uses,
                CommonTokens.Name,
            ),
        ]

        suffix_statements = Statement(
            "Suffixes",
            suffix_statement,
            (
                Statement(
                    "Comma and Suffix",
                    CommonTokens.Comma,
                    suffix_statement,
                ),
                0,
                None,
            ),
            (CommonTokens.Comma, 0, 1),
        )

        super(ClassDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement(
                "Class Declaration",
                (CommonTokens.Export, 0, 1),
                CommonTokens.Class,
                CommonTokens.Name,
                (
                    [
                        # '(' <suffix_statements> ')'
                        Statement(
                            "Grouped",
                            CommonTokens.LParen,
                            CommonTokens.PushIgnoreWhitespaceControl,
                            suffix_statements,
                            CommonTokens.PopIgnoreWhitespaceControl,
                            CommonTokens.RParen,
                        ),

                        # <suffix_statements>
                        suffix_statements,
                    ],
                    0,
                    1,
                ),
                CommonTokens.Colon,
                CommonTokens.NewlineToken(),
                CommonTokens.Indent,
                (CommonTokens.DocString, 0, 1),
                (class_statements, 1, None),
                CommonTokens.Dedent,
            ),
        )

# BugBug: Ensure only 1 inherit
