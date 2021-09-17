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

from typing import cast, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens

    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Statements.TryExceptStatementLexerInfo import (
        StatementLexerInfo,
        TryExceptStatementClauseLexerInfo,
        TryExceptStatementLexerInfo,
        TypeLexerInfo,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
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
                            CommonTokens.GenericName,
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

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractLexerInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 4

            # 'try'...
            try_statements_node = cast(Node, nodes[1])
            try_statements_info = StatementsPhraseItem.ExtractLexerInfo(try_statements_node)

            # 'except' <type>...
            except_type_nodes = cast(Node, nodes[2])
            except_infos: List[TryExceptStatementClauseLexerInfo] = []

            for except_type_node in cast(List[Node], ExtractRepeat(except_type_nodes)):
                these_type_expect_nodes = ExtractSequence(except_type_node)
                assert len(these_type_expect_nodes) == 4

                # <type>
                type_node = cast(Node, ExtractDynamic(cast(Node, these_type_expect_nodes[1])))
                type_info = cast(TypeLexerInfo, GetLexerInfo(type_node))

                # <name>
                name_leaf = cast(Leaf, these_type_expect_nodes[2])
                name_info = cast(str, ExtractToken(name_leaf))

                # <statements>
                statements_node = cast(Node, these_type_expect_nodes[3])
                statements_info = StatementsPhraseItem.ExtractLexerInfo(statements_node)

                except_infos.append(
                    # pylint: disable=too-many-function-args
                    TryExceptStatementClauseLexerInfo(
                        CreateLexerRegions(except_type_node, type_node, name_leaf, statements_node),  # type: ignore
                        type_info,
                        name_info,
                        statements_info,
                    ),
                )

            # 'except'...
            except_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[3])))
            if except_node is not None:
                except_nodes = ExtractSequence(except_node)
                assert len(except_nodes) == 2

                except_info = StatementsPhraseItem.ExtractLexerInfo(cast(Node, except_nodes[1]))
            else:
                except_info = None

            SetLexerInfo(
                node,
                TryExceptStatementLexerInfo(
                    CreateLexerRegions(
                        node,
                        try_statements_node,
                        except_type_nodes if except_infos else None,
                        except_node,
                    ),  # type: ignore
                    try_statements_info,
                    except_infos or None,
                    except_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
