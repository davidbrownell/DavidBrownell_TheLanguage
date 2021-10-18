# ----------------------------------------------------------------------
# |
# |  TryStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 11:16:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TryStatement object"""

import os

from typing import Callable, cast, List, Optional, Tuple, Union

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

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.TryStatementParserInfo import (
        TryStatementClauseParserInfo,
        TryStatementParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class TryStatement(GrammarPhrase):
    """\
    Try/except blocks.

    'try' ':'
        <statement>+
    (
        'except' <type> <name>? ':'
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
        except Exception4:
            Func4()
        except:
            Func5()
    """

    PHRASE_NAME                             = "Try Except Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        statements_phrase_item = StatementsPhraseItem.Create()

        super(TryStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'try' ':'
                    #     <statement>+
                    "try",
                    statements_phrase_item,

                    # (
                    #     'except' <type> <name>? ':'
                    #         <statement>+
                    # )*
                    ZeroOrMorePhraseItem.Create(
                        name="Typed Except Clause",
                        item=[
                            "except",
                            DynamicPhrasesType.Types,
                            OptionalPhraseItem.Create(CommonTokens.VariableName),
                            statements_phrase_item,
                        ],
                    ),

                    # (
                    #     'except' ':'
                    #         <statement>+
                    # )?
                    OptionalPhraseItem.Create(
                        name="Except Clause",
                        item=[
                            "except",
                            statements_phrase_item,
                        ],
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 4

            # 'try'...
            try_statements_node = cast(AST.Node, nodes[1])
            try_statements_info = StatementsPhraseItem.ExtractParserInfo(try_statements_node)

            # 'except' <type>...
            except_clauses_node = cast(Optional[AST.Node], nodes[2])
            if except_clauses_node is None:
                except_clauses_info = None  # type: ignore
            else:
                except_clauses_info: List[TryStatementClauseParserInfo] = []

                for except_clause_node in cast(List[AST.Node], ExtractRepeat(except_clauses_node)):
                    except_clause_nodes = ExtractSequence(except_clause_node)
                    assert len(except_clause_nodes) == 4

                    # <type>
                    type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, except_clause_nodes[1])))
                    type_info = cast(TypeParserInfo, GetParserInfo(type_node))

                    # <name>?
                    name_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], except_clause_nodes[2])))
                    if name_node is None:
                        name_info = None
                    else:
                        name_info = cast(str, ExtractToken(cast(AST.Leaf, name_node)))

                    # <statement>+
                    statements_node = cast(AST.Node, except_clause_nodes[3])
                    statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

                    except_clauses_info.append(
                        # pylint: disable=too-many-function-args
                        TryStatementClauseParserInfo(
                            CreateParserRegions(except_clause_node, type_node, name_node, statements_node),  # type: ignore
                            type_info,
                            name_info,
                            statements_info,
                        ),
                    )

                assert except_clauses_info

            # 'except'...
            except_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[3])))
            if except_node is None:
                except_info = None
            else:
                except_nodes = ExtractSequence(except_node)
                assert len(except_nodes) == 2

                except_info = StatementsPhraseItem.ExtractParserInfo(cast(AST.Node, except_nodes[1]))

            return TryStatementParserInfo(
                CreateParserRegions(node, try_statements_node, except_clauses_node, except_node),  # type: ignore
                try_statements_info,
                except_clauses_info,
                except_info,
            )

        # ----------------------------------------------------------------------

        return Impl
