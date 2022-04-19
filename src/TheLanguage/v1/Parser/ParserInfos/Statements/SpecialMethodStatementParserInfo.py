# ----------------------------------------------------------------------
# |
# |  SpecialMethodStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-18 15:28:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SpecialMethodStatementParserInfo object"""

import os

from enum import auto, Enum
from typing import cast, List

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, StatementParserInfo
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities


# ----------------------------------------------------------------------
class SpecialMethodType(Enum):
    #                                                       Description                                         Default Behavior                Is Exceptional  Signature
    #                                                       --------------------------------------------        --------------------------      --------------  ---------------------------------
    CompileTimeEvalTemplates    = auto()                    # Custom functionality invoked at compile time      Noop                            N/A             __EvalTemplates!__()  # Uses `Enforce!`
                                                            # to ensure that the template arguments are
                                                            # valid.

    CompileTimeEvalConstraints  = auto()                    # Custom functionality invoked at compile time      Noop                            N/A             __EvalConstraints!__()  # Uses `Enforce!`
                                                            # to ensure that the constraint arguments are
                                                            # valid.

    CompileTimeConvert          = auto()                    # Custom functionality invoked at compile time      No seamless conversions         N/A             __EvalConvertible!__()  # Uses `Enforce!`; `other` is name of other type
                                                            # to determine if a type with one set of            are allowed.
                                                            # constraints can be converted seamlessly to
                                                            # a different set of constraints.

    Construct                   = auto()                    # Validates an instance of an object                Noop                            Yes             __Construct?__()
                                                            # (invoked before bases are validated).

    ConstructFinal              = auto()                    # Validates an instance of an object                Noop                            Yes             __ConstructFinal?__()
                                                            # (invoked after bases are validated).

    Destroy                     = auto()                    # Called when an instance is being destroyed        Noop                            No              __Destroy__()
                                                            # (invoked before bases are destroyed).

    DestroyFinal                = auto()                    # Called when an instance is being destroyed        Noop                            No              __DestroyFinal__()
                                                            # (invoked after bases are destroyed).

    PrepareFinalize             = auto()                    # Called when an instance is being finalized        Impl based on attr flags        Yes             __PrepareFinalize?__()
    Finalize                    = auto()                    # Called when an instance is being finalized        Impl based on attr flags        No              __Finalize__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class SpecialMethodStatementParserInfo(StatementParserInfo):

    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    class_capabilities: InitVar[ClassCapabilities]

    type: SpecialMethodType
    statements: List[StatementParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, class_capabilities):
        super(SpecialMethodStatementParserInfo, self).__post_init__(regions)

        # BugBug: Validate class

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, *args, **kwargs):
        return self._ScopedAcceptImpl(cast(List[ParserInfo], self.statements), *args, **kwargs)
