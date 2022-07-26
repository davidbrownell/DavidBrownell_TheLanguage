# ----------------------------------------------------------------------
# |
# |  ConcreteType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 13:30:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConcreteType object"""

import os

from contextlib import ExitStack
from enum import auto, Enum
from typing import Generator, Optional, TYPE_CHECKING

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo

    from ..Traits.NamedTrait import NamedTrait

    from ...Error import CreateError, ErrorException

    if TYPE_CHECKING:
        from .ConstrainedType import ConstrainedType  # pylint: disable=unused-import


# ----------------------------------------------------------------------
CircularDependencyError                     = CreateError(
    "A circular dependency was detected with '{name}'",
    name=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ConcreteType(Interface.Interface):
    """Type with a specific set of template parameters (if required)"""

    # TODO: Create a wrapper, where the actual type can only be used within a generator, where
    #       any exceptions are decorated with all of the aliases. Should be impossible to use the
    #       underlying type outside of that generator.

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class State(Enum):
        Created                             = auto()

        FinalizingPass1                     = auto()
        FinalizedPass1                      = auto()

        FinalizingPass2                     = auto()
        FinalizedPass2                      = auto()

        Finalized                           = auto()

    # ----------------------------------------------------------------------
    parser_info: ParserInfo

    state: State                            = field(init=False, default_factory=lambda: ConcreteType.State.Created)  # pylint: disable=undefined-variable

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumAliases(self) -> Generator["ConcreteType", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveAliases(self) -> "ConcreteType":
        *_, last = self.EnumAliases()
        return last

    # ----------------------------------------------------------------------
    def FinalizePass1(self) -> None:
        if self.state.value > ConcreteType.State.FinalizingPass1.value:  # pylint: disable=no-member
            return

        if self.state == ConcreteType.State.FinalizingPass1:
            assert isinstance(self.parser_info, NamedTrait), self.parser_info

            raise ErrorException(
                CircularDependencyError.Create(
                    region=self.parser_info.regions__.self__,
                    name=self.parser_info.name,
                ),
            )

        object.__setattr__(self, "_state", ConcreteType.State.FinalizingPass1)

        # ----------------------------------------------------------------------
        def RestorePrevStateOnError():
            if self.state != ConcreteType.State.FinalizedPass1:
                object.__setattr__(
                    self,
                    "_state",
                    ConcreteType.State(ConcreteType.State.FinalizingPass1.value - 1),
                )

        # ----------------------------------------------------------------------

        with ExitStack() as exit_stack:
            exit_stack.callback(RestorePrevStateOnError)

            self._FinalizePass1Impl()

            object.__setattr__(self, "_state", ConcreteType.State.FinalizedPass1)

    # ----------------------------------------------------------------------
    def FinalizePass2(self) -> None:
        if self.state.value >= ConcreteType.State.FinalizingPass2.value:  # pylint: disable=no-member
            return

        object.__setattr__(self, "_state", ConcreteType.State.FinalizingPass2)

        # ----------------------------------------------------------------------
        def RestorePrevStateOnError():
            if self.state != ConcreteType.State.FinalizedPass2:
                object.__setattr__(
                    self,
                    "_state",
                    ConcreteType.State(ConcreteType.State.FinalizingPass2.value - 1),
                )

        # ----------------------------------------------------------------------

        with ExitStack() as exit_stack:
            exit_stack.callback(RestorePrevStateOnError)

            self._FinalizePass2Impl()

            object.__setattr__(self, "_state", ConcreteType.State.FinalizedPass2)

        # We are done
        object.__setattr__(self, "_state", ConcreteType.State.Finalized)

    # ----------------------------------------------------------------------
    def CreateConstrainedType(self) -> "ConstrainedType":
        if self.state != ConcreteType.State.Finalized:
            BugBug = 10

        assert self.state == ConcreteType.State.Finalized, self.state
        return self._CreateConstrainedTypeImpl()

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _FinalizePass1Impl() -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _FinalizePass2Impl() -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConstrainedTypeImpl() -> "ConstrainedType":
        raise Exception("Abstract method")  # pragma: no cover
