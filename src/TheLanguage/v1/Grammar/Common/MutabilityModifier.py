# ----------------------------------------------------------------------
# |
# |  MutabilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 12:25:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality associated with mutability modifiers"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl import ModifierImpl
    from ...Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier


# ----------------------------------------------------------------------
CreatePhraseItem                            = ModifierImpl.StandardCreatePhraseItemFuncFactory(MutabilityModifier)
Extract                                     = ModifierImpl.StandardExtractFuncFactory(MutabilityModifier)
