# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:59:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains utilities used by multiple statements and expressions"""

import os

from typing import cast, Match

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...ParserImpl.Token import Token

    from ..GrammarStatement import (
        Leaf,
        Statement,
    )

# TODO:
#   docstrings in function decl
#   Function type
#   Variant/Union
#       String Func():
#           return "Hi"
#       var variant = (String | None)(Func())
#       var variant = (String | None)Func()
#       var variant = Func() as (String | None)
#       var string = Func()
#
#   scoped ref syntax (can be similar to with statements?)


#   Classes / Interfaces / Mixins
#   Exceptions
#   Async/Await (Possibly "FuncName..." suffix?)
#   Generators
#       for / in
#       all
#       any
#   Loops
#   Conditional
#   Pattern Matching / Super case statements
#   Templates
#   Docstrings
#   Lambdas / Capture scope
#   "with" statements (context generators)
#   dunder methods
#   type aliases
#   Enumerations
#   None

#   Class library
#       String
#       List
#       Dict
#       Int: Increases in size
#       ____Int: Checks for overflow
#       FixedInt: fixed size
#       Int<Min, Max>: Same as regular Int?
#       Floating points similar to ints


# ----------------------------------------------------------------------
def GetRegexMatch(
    leaf: Leaf,
) -> Match:
    return cast(
        Token.RegexMatch,
        leaf.Value,
    ).Match
