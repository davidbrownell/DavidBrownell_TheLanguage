# ----------------------------------------------------------------------
# |
# |  VariableNameExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 17:12:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for VariableNameExpression.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import PatchAndExecute, PatchAndExecuteFlag
    from ..CommentStatement import *


# ----------------------------------------------------------------------
def Execute(content: str) -> str:
    result = PatchAndExecute(
        {
            "filename" : content,
        },
        ["filename"],
        [],
        flag=PatchAndExecuteFlag.Validate,
        # max_num_threads=1,
    )

    return str(result["filename"])


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            Func(variable_name1, variable_name2)
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Function Invocation
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 4), match='Func'>>> ws:None [1, 1 -> 1, 5]
                    '(' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:None [1, 5 -> 1, 6]
                    Repeat: (Arguments, 0, 1)
                        Arguments
                            Or: [Keyword, DynamicStatements.Expressions]
                                DynamicStatements.Expressions
                                    1.0.0 Grammar
                                        Variable Name
                                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 19), match='variable_name1'>>> ws:None [1, 6 -> 1, 20]
                            Repeat: (Comma and Argument, 0, None)
                                Comma and Argument
                                    ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [1, 20 -> 1, 21]
                                    Or: [Keyword, DynamicStatements.Expressions]
                                        DynamicStatements.Expressions
                                            1.0.0 Grammar
                                                Variable Name
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(21, 35), match='variable_name2'>>> ws:(20, 21) [1, 22 -> 1, 36]
                    ')' <<Regex: <_sre.SRE_Match object; span=(35, 36), match=')'>>> ws:None [1, 36 -> 1, 37]
        """,
    )
