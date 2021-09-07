# ----------------------------------------------------------------------
# |
# |  TryExceptStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 05:38:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TryExceptStatement object"""

import os

from typing import List, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import StatementsPhraseItem
    from ...GrammarPhrase import GrammarPhrase

    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class TryExceptStatement(GrammarPhrase):
    """\
    Try/except blocks.

    'try' ':'
        <statement>+
    (
        'except' <type> <name> ':'
            <statement>+
    )*
    (
        'except' ':'
            <statement>+
    )?

    Examples:
        try:
            Func1()
        except Exception ex:
            Func2()
        except (Exception1 | Exception2) ex:
            Func3()
        except:
            Func4()
    """

    PHRASE_NAME                             = "Try Except Statement"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(GrammarPhrase.NodeInfo):
        TryStatements: List[Union[Leaf, Node]]
        ExceptVarStatements: List[
            Tuple[
                Tuple[Node, Leaf],          # Exception Type, name
                List[Union[Leaf, Node]],    # Statements
            ]
        ]
        ExceptStatements: List[Union[Leaf, Node]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            # <Parameters differ> pylint: disable=W0221
            super(TryExceptStatement.NodeInfo, self).__post_init__(
                TryStatements=lambda statements: [statement.Type.Name for statement in statements],
                ExceptVarStatements=lambda items: ["{}, {}, {}".format(ex_type, ex_name, ", ".join([statement.Type.Name for statement in statements])) for (ex_type, ex_name), statements in items],
                ExceptStatements=lambda statements: [statement.Type.Name for statement in statements],
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        statements_item = StatementsPhraseItem.Create()

        super(TryExceptStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'try' ':'
                    #     <statement>+
                    "try",
                    statements_item,

                    # (
                    #     'except' <type> <name> ':'
                    #         <statement>+
                    # )*
                    PhraseItem(
                        name="Except Var",
                        item=[
                            "except",
                            DynamicPhrasesType.Types,
                            DynamicPhrasesType.Names,
                            statements_item,
                        ],
                        arity="*",
                    ),

                    # (
                    #     'except' ':'
                    #         <statement>+
                    # )?
                    PhraseItem(
                        name="Except",
                        item=[
                            "except",
                            statements_item,
                        ],
                        arity="?",
                    ),
                ],
            ),
        )
