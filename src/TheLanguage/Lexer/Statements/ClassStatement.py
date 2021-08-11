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

    requiredMethods: InitVar[Optional[RequiredMethodsType]]
    initMethods: InitVar[Optional[InitMethodsType]]
    logicalMethods: InitVar[Optional[LogicalMethodsType]]
    containerMethods: InitVar[Optional[ContainerMethodsType]]
    comparisonMethods: InitVar[Optional[ComparisonMethodsType]]
    mathematicalMethods: InitVar[Optional[MathematicalMethodsType]]
    bitManipulationMethods: InitVar[Optional[BitManipulationMethodsType]]
    dynamicMethods: InitVar[Optional[DynamicMethodsType]]

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
        requiredMethods = requiredMethods or RequiredMethodsType()
        requiredMethods.Init(self)
        object.__setattr__(self, "RequiredMethods", requiredMethods)

        initMethods = initMethods or InitMethodsType()
        initMethods.Init(self)
        object.__setattr__(self, "InitMethods", initMethods)

        logicalMethods = logicalMethods or LogicalMethodsType()
        logicalMethods.Init(self)
        object.__setattr__(self, "LogicalMethods", logicalMethods)

        containerMethods = containerMethods or ContainerMethodsType()
        containerMethods.Init(self)
        object.__setattr__(self, "ContainerMethods", containerMethods)

        comparisonMethods = comparisonMethods or ComparisonMethodsType()
        comparisonMethods.Init(self)
        object.__setattr__(self, "ComparisonMethods", comparisonMethods)

        mathematicalMethods = mathematicalMethods or MathematicalMethodsType()
        mathematicalMethods.Init(self)
        object.__setattr__(self, "MathematicalMethods", mathematicalMethods)

        bitManipulationMethods = bitManipulationMethods or BitManipulationMethodsType()
        bitManipulationMethods.Init(self)
        object.__setattr__(self, "BitManipulationMethods", bitManipulationMethods)

        dynamicMethods = dynamicMethods or DynamicMethodsType()
        dynamicMethods.Init(self)
        object.__setattr__(self, "DynamicMethods", dynamicMethods)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetTypeDescriptions() -> List[str]:
        return [
            class_type.name.lower()
            for class_type in ClassType
            if class_type.name != "Primitive"
        ]
