# ----------------------------------------------------------------------
# |
# |  ClassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 14:28:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassStatement object"""

import os

from enum import auto, Enum
from typing import cast, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassMethods.BitManipulationMethods import BitManipulationMethods as BitManipulationMethodsType
    from .ClassMethods.ComparisonMethods import ComparisonMethods as ComparisonMethodsType
    from .ClassMethods.ContainerMethods import ContainerMethods as ContainerMethodsType
    from .ClassMethods.DynamicMethods import DynamicMethods as DynamicMethodsType
    from .ClassMethods.InitMethods import InitMethods as InitMethodsType
    from .ClassMethods.LogicalMethods import LogicalMethods as LogicalMethodsType
    from .ClassMethods.MathematicalMethods import MathematicalMethods as MathematicalMethodsType
    from .ClassMethods.RequiredMethods import RequiredMethods as RequiredMethodsType

    from .Interfaces.IDocstring import IDocstring

    from ..AST import StatementNode
    from ..Common import Flags


# Primitives:
#   - String
#   - Decimal
#   - Integer
#   - Boolean
#   - None?

#   - Datetime?
#   - Date?
#   - Time?
#   - Duration?
#   - Enum?



# ----------------------------------------------------------------------
class ClassType(Enum):
    """\
    TODO: Describe
    """

    Primitive                               = auto()
    Class                                   = auto()
    Interface                               = auto()
    Mixin                                   = auto()
    Exception                               = auto()
    Enum                                    = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassStatement(StatementNode, IDocstring):
    """\
    TODO: Describe
    """

    Visibility: Flags.VisibilityType
    Type: ClassType

    Name: str
    BaseClasses: Optional[List[str]]
    Interfaces: Optional[List[str]]
    Mixins: Optional[List[str]]

    # TODO: Probably need an attribute statement type that includes visibility
    Statements: List[StatementNode]

    # TODO: Attributes

    # Special Methods
    RequiredMethods: RequiredMethodsType                = field(init=False)
    InitMethods: InitMethodsType                        = field(init=False)
    LogicalMethods: LogicalMethodsType                  = field(init=False)
    ContainerMethods: ContainerMethodsType              = field(init=False)
    ComparisonMethods: ComparisonMethodsType            = field(init=False)
    MathematicalMethods: MathematicalMethodsType        = field(init=False)
    BitManipulationMethods: BitManipulationMethodsType  = field(init=False)
    DynamicMethods: DynamicMethodsType                  = field(init=False)

    requiredMethods: InitVar[Optional[RequiredMethodsType]]                 = None
    initMethods: InitVar[Optional[InitMethodsType]]                         = None
    logicalMethods: InitVar[Optional[LogicalMethodsType]]                   = None
    containerMethods: InitVar[Optional[ContainerMethodsType]]               = None
    comparisonMethods: InitVar[Optional[ComparisonMethodsType]]             = None
    mathematicalMethods: InitVar[Optional[MathematicalMethodsType]]         = None
    bitManipulationMethods: InitVar[Optional[BitManipulationMethodsType]]   = None
    dynamicMethods: InitVar[Optional[DynamicMethodsType]]                   = None

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        requiredMethods,
        initMethods,
        logicalMethods,
        containerMethods,
        comparisonMethods,
        mathematicalMethods,
        bitManipulationMethods,
        dynamicMethods,
    ):
        object.__setattr__(self, "RequiredMethods", requiredMethods or RequiredMethodsType())
        cast(RequiredMethodsType, self.RequiredMethods).__class_init__(self)

        object.__setattr__(self, "InitMethods", initMethods or InitMethodsType())
        cast(InitMethodsType, self.InitMethods).__class_init__(self)

        object.__setattr__(self, "LogicalMethods", logicalMethods or LogicalMethodsType())
        cast(LogicalMethodsType, self.LogicalMethods).__class_init__(self)

        object.__setattr__(self, "ContainerMethods", containerMethods)
        cast(ContainerMethodsType, self.ContainerMethods).__class_init__(self)

        object.__setattr__(self, "ComparisonMethods", comparisonMethods or ComparisonMethodsType())
        cast(ComparisonMethodsType, self.ComparisonMethods).__class_init__(self)

        object.__setattr__(self, "MathematicalMethods", mathematicalMethods or MathematicalMethodsType())
        cast(MathematicalMethodsType, self.MathematicalMethods).__class_init__(self)

        object.__setattr__(self, "BitManiuplationMethods", bitManipulationMethods or BitManipulationMethodsType())
        cast(BitManipulationMethodsType, self.BitManipulationMethods).__class_init__(self)

        object.__setattr__(self, "DynamicMethods", dynamicMethods or DynamicMethodsType())
        cast(DynamicMethodsType, self.DynamicMethods).__class_init__(self)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetTypeDescriptions() -> List[str]:
        return [
            class_type.name.lower()
            for class_type in ClassType
            if class_type.name != "Primitive"
        ]
