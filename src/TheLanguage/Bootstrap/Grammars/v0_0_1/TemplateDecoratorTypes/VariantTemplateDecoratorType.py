# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 11:31:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.VariantTypeImpl import VariantTypeImpl
    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class VariantTemplateDecoratorType(VariantTypeImpl):
    """\
    A type that can be any one of a collection of types.

    '(' <type> '|' (<type> '|')* <type> ')'

    Examples:
        (Int | Float)
        (Int val | Bool | Char view)
    """

    PHRASE_NAME                             = "Variant TemplateDecoratorType"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantTemplateDecoratorType, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.TemplateDecoratorTypes,
        )
