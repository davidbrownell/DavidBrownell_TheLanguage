import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.StandardTypeImpl import StandardTypeImpl

    from ...GrammarInfo import DynamicPhrasesType


# ----------------------------------------------------------------------
class StandardType(StandardTypeImpl):
    """\
    Type declaration.

    <type_name> <modifier>?

    Examples:
        Int
        Int var
    """

    PHRASE_NAME                             = "Standard Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardType, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.Types,
        )
