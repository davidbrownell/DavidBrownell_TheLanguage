# ----------------------------------------------------------------------
# |
# |  DynamicMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 21:25:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DynamicMethods object"""

import os

from typing import Any, cast, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MethodDefinitionStatement import MethodDefinitionStatement


# ----------------------------------------------------------------------
class DynamicMethods(object):
    """\
    TODO: Describe
    """

    # TODO: Index operator
    # TODO: Tuple assignment unpacking

    # ----------------------------------------------------------------------
    def __init__(
        self,
        getAttributeMethod: Optional[MethodDefinitionStatement]=None,
        callMethods: Optional[List[MethodDefinitionStatement]]=None,
        castMethods: Optional[List[MethodDefinitionStatement]]=None,
    ):
        # BugBug: Validate params
        self._getAttributeMethod            = getAttributeMethod
        self._callMethods                   = callMethods
        self._castMethods                   = castMethods

    # ----------------------------------------------------------------------
    def Init(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement

        class_stmt = cast(ClassStatement, class_stmt)

        self.GetAttribueMethod = self._getAttributeMethod; del self._getAttributeMethod
        self.CallMethods = self._callMethods; del self._callMethods
        self.CastMethods = self._castMethods; del self._castMethods
