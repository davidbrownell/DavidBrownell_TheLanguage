# ----------------------------------------------------------------------
# |
# |  CommonStatements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-06 14:53:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements used by other statements"""

import os
import re
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...ParserImpl.Normalize import Normalize
    from ...ParserImpl.NormalizedIterator import NormalizedIterator
    from ...ParserImpl.Statement import Statement
    from ...ParserImpl.Token import RegexToken


# ----------------------------------------------------------------------
# TODO: Not sure this is necessary

# # ----------------------------------------------------------------------
# ModuleNameStatement                         = _CreateRegexStatement(
#     "<module_name>",
#     textwrap.dedent(
#         r"""(?#
#             Leading Upper                   )[A-Z](?#
#             Alpha-Numeric w/under [+]       )[A-Za-z0-9_]+(?#
#         )""",
#     ),
# )
#
#
# ClassNameStatement                          = _CreateRegexStatement(
#     "<class_name>",
#     textwrap.dedent(
#         r"""(?#
#             Leading Upper                   )[A-Z](?#
#             Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
#         )""",
#     ),
# )
#
#
# ClassMemberNameStatement                    = _CreateRegexStatement(
#     "<class_member>",
#     textwrap.dedent(
#         r"""(?#
#             Leading Lower                   )[a-z](?#
#             Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
#         )""",
#     ),
# )
#
#
# FunctionNameStatement                       = _CreateRegexStatement(
#     "<function_name>",
#     textwrap.dedent(
#         r"""(?#
#             Leading Upper                   )[A-Z](?#
#             Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
#             Trailing '?' [optional]         )\??(?#
#         )""",
#     ),
# )
#
#
# FunctionParameterNameStatement              = _CreateRegexStatement(
#     "<parameter_name>",
#     textwrap.dedent(
#         r"""(?#
#             Leading Lower                   )[a-z](?#
#             Alpha-Numeric w/under [*]       )[A-Za-z0-9_]*(?#
#         )""",
#     ),
# )
#
#
# VariableNameStatement                       = RegexToken(
#     "<name>",
#     re.compile(
#         textwrap.dedent(
#             r"""(?P<value>(?#
#                 Leading Lower               )[a-z](?#
#                 Alpha-Numeric w/under [*]   )[A-Za-z0-9_]*(?#
#                 No trailing underscore      )(?<!_)(?#
#                 End Word Boundary           )\b(?#
#             ))""",
#         ),
#     ),
# )
