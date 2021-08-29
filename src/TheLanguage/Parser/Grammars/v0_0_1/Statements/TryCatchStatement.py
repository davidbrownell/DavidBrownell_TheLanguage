# ----------------------------------------------------------------------
# |
# |  TryCatchStatement.py
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
"""Contains the TryCatchStatement object"""

import os

from typing import cast, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import GrammarPhrase

    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractRepeat,
        ExtractSequence,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class TryCatchStatement(GrammarPhrase):
    """\
    Try/catch blocks.

    'try' ':'
        <statement>+
    (
        'catch' <type> <name> ':'
            <statement>+
    )*
    (
        'catch' ':'
            <statement>+
    )?

    Examples:
        try:
            Func1()
        catch Exception ex:
            Func2()
        catch (Exception1 | Exception2) ex:
            Func3()
        catch:
            Func4()
    """

    PHRASE_NAME                             = "Try Catch Statement"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(GrammarPhrase.NodeInfo):
        TryStatements: List[Union[Leaf, Node]]
        CatchVarStatements: List[
            Tuple[
                Tuple[Node, Leaf],          # Exception Type, name
                List[Union[Leaf, Node]],    # Statements
            ]
        ]
        CatchStatements: List[Union[Leaf, Node]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(TryCatchStatement.NodeInfo, self).__post_init__(
                TryStatements=lambda statements: [statement.Type.Name for statement in statements],
                CatchVarStatements=lambda items: ["{}, {}, {}".format(ex_type, ex_name, ", ".join([statement.Type.Name for statement in statements])) for (ex_type, ex_name), statements in items],
                CatchStatements=lambda statements: [statement.Type.Name for statement in statements],
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        # TODO: Single line statement
        statements_item = PhraseItem(
            name="Statements",
            item=DynamicPhrasesType.Statements,
            arity="+",
        )

        super(TryCatchStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'try' ':'
                    #     <statement>+
                    "try",
                    ":",
                    CommonTokens.Newline,
                    CommonTokens.Indent,
                    statements_item,
                    CommonTokens.Dedent,

                    # (
                    #     'catch' <type> <name> ':'
                    #         <statement>+
                    # )*
                    PhraseItem(
                        name="Catch Var",
                        item=[
                            "catch",
                            DynamicPhrasesType.Types,
                            DynamicPhrasesType.Names,
                            ":",
                            CommonTokens.Newline,
                            CommonTokens.Indent,
                            statements_item,
                            CommonTokens.Dedent,
                        ],
                        arity="*",
                    ),

                    # (
                    #     'catch' ':'
                    #         <statement>+
                    # )?
                    PhraseItem(
                        name="Catch",
                        item=[
                            "catch",
                            ":",
                            CommonTokens.Newline,
                            CommonTokens.Indent,
                            statements_item,
                            CommonTokens.Dedent,
                        ],
                        arity="?",
                    ),
                ],
            ),
        )
