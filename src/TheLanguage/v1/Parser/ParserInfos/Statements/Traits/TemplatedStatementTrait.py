# ----------------------------------------------------------------------
# |
# |  TemplatedStatementTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 12:59:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TemplatedStatementTrait object"""

import os
import threading

from contextlib import ExitStack
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ...Common.TemplateParametersParserInfo import ResolvedTemplateArguments, TemplateParametersParserInfo

    from ...ParserInfo import ParserInfo
    from ...Statements.StatementParserInfo import StatementParserInfo

    from ...EntityResolver import EntityResolver
    from ...Traits.NamedTrait import NamedTrait
    from ...Types import ConcreteType


# ----------------------------------------------------------------------
# TODO: This should be based on NamedTrait

@dataclass(frozen=True, repr=False)
class TemplatedStatementTrait(Interface.Interface):
    """Apply to statements that may have templates"""

    # ----------------------------------------------------------------------
    # |  Public Types
    GetOrCreateConcreteTypeFactoryResultType            = Tuple[
        bool,                                           # is_cached_result
        Union[
            ConcreteType,                               # is_cached_result == True
            Tuple[                                      # is_cached_result == False
                Optional[ResolvedTemplateArguments],
                Callable[
                    [],
                    ConcreteType,
                ],
            ],
        ],
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    templates_param: InitVar[Optional[TemplateParametersParserInfo]]
    templates: Optional[TemplateParametersParserInfo]   = field(init=False, default=None)

    is_default_initializable: bool                      = field(init=False, default=False)

    _cache_lock: threading.Lock                         = field(init=False, default_factory=threading.Lock)
    _cache_info: "TemplatedStatementTrait._CacheInfo"   = field(init=False, default_factory=lambda: TemplatedStatementTrait._CacheInfo())  # pylint: disable=unnecessary-lambda

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self, templates_param):
        object.__setattr__(self, "templates", templates_param)

        object.__setattr__(
            self,
            "is_default_initializable",
            not self.templates or self.templates.is_default_initializable,  # pylint: disable=no-member
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [
            "templates",
            "is_default_initializable",
        ]

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {
            "is_default_initializable": None,
        }

    # ----------------------------------------------------------------------
    def CreateConcreteTypeFactory(
        self,
        entity_resolver: EntityResolver,
    ) -> Callable[
        [
            Optional[TemplateArgumentsParserInfo],
        ],
        ConcreteType,
    ]:
        dedicated_resolver = entity_resolver.Clone()

        # ----------------------------------------------------------------------
        def ConcreteTypeFactory(
            template_arguments: Optional[TemplateArgumentsParserInfo],
        ) -> ConcreteType:
            if self.templates is None:
                if template_arguments:
                    raise Exception("BugBug: Templates where none were expected")

                resolved_template_arguments = None
                cache_key = None
            else:
                resolved_template_arguments = self.templates.MatchCall(  # pylint: disable=no-member
                    self.name,              # type: ignore # pylint: disable=no-member
                    self.regions__.name,    # type: ignore # pylint: disable=no-member
                    self.regions__.self__,  # type: ignore # pylint: disable=no-member
                    template_arguments,
                    dedicated_resolver,
                )

                cache_key = resolved_template_arguments.cache_key

            # Is the concrete type cached?
            event: Optional[threading.Event] = None
            should_wait: Optional[bool] = None

            with self._cache_lock:  # pylint: disable=not-context-manager
                result = self._cache_info.values.get(cache_key, None)  # pylint: disable=no-member

                if result is None:
                    event = threading.Event()
                    self._cache_info.values[cache_key] = event  # pylint: disable=no-member

                    should_wait = False

                elif isinstance(result, threading.Event):
                    event = result
                    should_wait = True

                else:
                    return result

            assert event is not None
            assert should_wait is not None

            if should_wait:
                event.wait()

                while self._cache_lock:
                    result = self._cache_info.values[cache_key]  # type: ignore # pylint: disable=no-member

                assert isinstance(result, ConcreteType), result
                return result

            # Create the ConcreteType
            result: Optional[ConcreteType] = None
            updated_entity_resolver: Optional[EntityResolver] = None

            with ExitStack() as exit_stack:
                # ----------------------------------------------------------------------
                def SetResult():
                    with self._cache_lock:  # pylint: disable=not-context-manager
                        self._cache_info.values[cache_key] = result # type: ignore # pylint: disable=no-member

                # ----------------------------------------------------------------------

                exit_stack.callback(SetResult)
                exit_stack.callback(event.set)

                # ----------------------------------------------------------------------
                def Impl(
                    new_entity_resolver: EntityResolver,
                ):
                    nonlocal updated_entity_resolver

                    updated_entity_resolver = new_entity_resolver
                    return self._CreateConcreteType(new_entity_resolver)

                # ----------------------------------------------------------------------

                result = dedicated_resolver.CreateConcreteType(
                    self,  # type: ignore
                    resolved_template_arguments,
                    Impl,
                )

            assert result is not None
            assert updated_entity_resolver is not None

            # Finalize must be called after the result is cached, as circular references
            # will attempt to create the concrete type again if we attempt to finalize before
            # the concrete type has been cached.
            result.Finalize(updated_entity_resolver)

            return result

        # ----------------------------------------------------------------------

        # If the type can be initialized without any template arguments, do it now
        # so that we see errors sooner rather than later. Without this, the errors only
        # appear when the type is actually used,
        if self.templates is None or self.templates.is_default_initializable:  # pylint: disable=no-member
            should_initialize = False

            with self._cache_lock:  # pylint: disable=not-context-manager
                if not self._cache_info.default_initialized:  # pylint: disable=no-member
                    should_initialize = True
                    self._cache_info.default_initialized = True  # pylint: disable=assigning-non-slot

            if should_initialize:
                ConcreteTypeFactory(None)

        return ConcreteTypeFactory

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass
    class _CacheInfo(object):
        values: Dict[Any, Union[threading.Event, ConcreteType]]             = field(init=False, default_factory=dict)
        default_initialized: bool                                           = field(init=False, default=False)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteType(
        entity_resolver: EntityResolver,
    ) -> ConcreteType:
        raise Exception("Abstract method")  # pragma: no cover
