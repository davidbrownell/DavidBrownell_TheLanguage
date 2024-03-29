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
from typing import Callable, Generator, Optional, TYPE_CHECKING

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

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
    def __init__(
        self,
        parser_info: ParserInfo,
        *,
        is_default_initializable: bool,
    ):
        self._parser_info                   = parser_info
        self.is_default_initializable       = is_default_initializable

        self.state                          = ConcreteType.State.Created

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def parser_info(self):
        """Returns the parser info with the correct type"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumAliases(self) -> Generator["ConcreteType", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveAliases(self) -> "ConcreteType":
        *_, last = self.EnumAliases()
        return last

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        state: Optional["ConcreteType.State"]=None,
    ) -> None:
        state = state or ConcreteType.State.Finalized

        if state.value >= ConcreteType.State.FinalizedPass1.value:
            if self.state == ConcreteType.State.FinalizingPass1:
                assert isinstance(self._parser_info, NamedTrait), self._parser_info

                raise ErrorException(
                    CircularDependencyError.Create(
                        region=self._parser_info.regions__.self__,
                        name=self._parser_info.name,
                    ),
                )

            self._InvokeFinalization(
                ConcreteType.State.FinalizingPass1,
                ConcreteType.State.FinalizedPass1,
                self._FinalizePass1Impl,
            )

        if state.value >= ConcreteType.State.FinalizedPass2.value:
            self._InvokeFinalization(
                ConcreteType.State.FinalizingPass2,
                ConcreteType.State.FinalizedPass2,
                self._FinalizePass2Impl,
            )

            # We are done
            object.__setattr__(self, "state", ConcreteType.State.Finalized)

    # ----------------------------------------------------------------------
    def CreateConstrainedType(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> "ConstrainedType":
        assert self.state == ConcreteType.State.Finalized, self.state
        return self._CreateConstrainedTypeImpl(expression_parser_info)

    # ----------------------------------------------------------------------
    def CreateDefaultConstrainedType(self) -> "ConstrainedType":
        assert self.is_default_initializable
        assert self.state == ConcreteType.State.Finalized, self.state
        return self._CreateDefaultConstrainedTypeImpl()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsMatch(
        other: "ConcreteType",
    ) -> bool:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsCovariant(
        other: "ConcreteType",
    ) -> bool:
        raise Exception("Abstract method")  # pragma: no cover

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
    def _CreateConstrainedTypeImpl(
        expression_parser_info: ExpressionParserInfo,
    ) -> "ConstrainedType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateDefaultConstrainedTypeImpl() -> "ConstrainedType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def _InvokeFinalization(
        self,
        in_process_state: "ConcreteType.State",
        completed_state: "ConcreteType.State",
        impl_func: Callable[[], None],
    ) -> None:
        if self.state.value >= in_process_state.value:
            return

        object.__setattr__(self, "state", in_process_state)

        # ----------------------------------------------------------------------
        def RestorePrevStateOnError():
            if self.state != completed_state:
                object.__setattr__(
                    self,
                    "state",
                    ConcreteType.State(in_process_state.value - 1),
                )

        # ----------------------------------------------------------------------

        with ExitStack() as exit_stack:
            exit_stack.callback(RestorePrevStateOnError)

            impl_func()

            object.__setattr__(self, "state", completed_state)
