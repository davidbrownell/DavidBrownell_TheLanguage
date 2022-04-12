# ----------------------------------------------------------------------
# |
# |  VisibilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 10:11:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality associated with visibility modifiers"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl import ModifierImpl
    from ...Parser.Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
CreatePhraseItem                            = ModifierImpl.StandardCreatePhraseItemFuncFactory(VisibilityModifier)
Extract                                     = ModifierImpl.StandardExtractFuncFactory(VisibilityModifier)
