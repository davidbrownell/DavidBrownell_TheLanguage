# ----------------------------------------------------------------------
# |
# |  FuncDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-13 12:21:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDeclarationStatement object"""

import os
import textwrap

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
    from .Common import Tokens as CommonTokens
    from .Common import Statements as CommonStatements
    from .Common import NamingConventions

    from .Impl import FuncParameters

    from .Impl.FuncParameters import (
        # This is here as a convenience for files that import this one; please do not remove
        DuplicateParameterNameError,
        PositionalParameterAfterDefaultValueParameterError,
        NewStyleParameterGroupOrderingError,
        TraditionalDelimiterOrderError,
        TraditionalDuplicateKeywordDelimiterError,
        TraditionalDuplicatePositionalDelimiterError,
        TraditionalKeywordDelimiterError,
        TraditionalPositionalDelimiterError,
    )

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Node,
        StatementEx,
        ValidationError,
    )

    from ...ParserImpl.StatementImpl.RepeatStatement import RepeatStatement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FunctionNameError(ValidationError):
    FunctionName: str

    MessageTemplate                         = Interface.DerivedProperty(
        textwrap.dedent(
            """\
            '{{FunctionName}}' is not a valid function name.

            Function names must:
                {}
            """,
        ).format(
            StringHelpers.LeftJustify("\n".join(NamingConventions.Function.Constraints).rstrip(), 4),
        ),
    )


# ----------------------------------------------------------------------
class FuncDeclarationStatement(GrammarStatement):
    """\
    Declares a function.

    <type> <name> '(' <args> ')' ':'
        <dynamic_statements>
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        statement_items = [
            (CommonTokens.Export, 0, 1),
            CommonStatements.Type,
            CommonTokens.Name,
        ]

        statement_items += FuncParameters.ParameterItems

        statement_items += [
            CommonTokens.Colon,
            CommonTokens.NewlineToken(),

            CommonTokens.Indent,
            (CommonTokens.DocString, 0, 1),
            (DynamicStatements.Statements, 1, None),
            CommonTokens.Dedent,
        ]

        super(FuncDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            StatementEx(
                "Function Declaration",
                *statement_items,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        # The export keyword may or may not appear, which will impact the parameter index
        if (
            isinstance(node.Children[0].Type, RepeatStatement)
            and node.Children[0].Type.Statement.Name == CommonTokens.Export.Name
        ):
            parameter_offset = 1
        else:
            parameter_offset = 0

        # Validate the function name
        assert len(node.Children) > (2 + parameter_offset)

        name_node = node.Children[1 + parameter_offset]
        function_name = name_node.Value.Match.group("value")

        if not NamingConventions.Function.Regex.match(function_name):
            raise FunctionNameError.FromNode(name_node, function_name)

        # Validate the parameters
        assert len(node.Children) > (4 + parameter_offset)
        parameters = FuncParameters.GetParameters(node.Children[3 + parameter_offset])

        # Commit the values for later
        object.__setattr__(node, "function_name", function_name)
        object.__setattr__(node, "parameters", parameters)
