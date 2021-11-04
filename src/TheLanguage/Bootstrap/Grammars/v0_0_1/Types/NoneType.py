# ----------------------------------------------------------------------
# |
# |  NoneType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-27 15:12:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneType object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.NoneTypeImpl import NoneTypeImpl
    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class NoneType(NoneTypeImpl):
    """\
    No type.

    'None'

    Examples:
        None
    """

    PHRASE_NAME                             = "None Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(NoneType, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.Types,
        )
