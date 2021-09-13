# ----------------------------------------------------------------------
# |
# |  TypeModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 22:32:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality associated with type modifiers"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl import ModifierImpl
    from ....Lexer.Common.TypeModifier import TypeModifier as Enum


# ----------------------------------------------------------------------
CreatePhraseItem                            = ModifierImpl.CreateStandardCreatePhraseItemFunc(Enum)
Extract                                     = ModifierImpl.CreateStandardExtractFunc(Enum)
