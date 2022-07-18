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
    from ...Types import ClassType, Type


# ----------------------------------------------------------------------
# TODO: This should be based on NamedTrait

@dataclass(frozen=True, repr=False)
class TemplatedStatementTrait(Interface.Interface):
    """Apply to statements that may have templates"""

    # ----------------------------------------------------------------------
    # |  Public Types
    CreateConcreteTypeFactoryResultType     = Callable[
        [
            Optional[TemplateArgumentsParserInfo],
            Optional[ClassType],
        ],
        Type,
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
    ) -> "TemplatedStatementTrait.CreateConcreteTypeFactoryResultType":
        # ----------------------------------------------------------------------
        def CreateConcreteType(
            template_arguments: Optional[TemplateArgumentsParserInfo],
            instantiated_class: Optional[ClassType],
        ) -> Type:
            if self.templates is None:
                if template_arguments:
                    raise Exception("BugBug: Templates where none were expected")

                resolved_template_arguments = None
                template_cache_key = None
            else:
                resolved_template_arguments = self.templates.MatchCall(  # pylint: disable=no-member
                    self.name,              # type: ignore # pylint: disable=no-member
                    self.regions__.name,    # type: ignore # pylint: disable=no-member
                    self.regions__.self__,  # type: ignore # pylint: disable=no-member
                    template_arguments,
                    entity_resolver,
                )

                template_cache_key = resolved_template_arguments.cache_key

            if instantiated_class is None:
                class_cache_key = None
            else:
                class_cache_key = id(instantiated_class)

            cache_key = (template_cache_key, class_cache_key)

            # Is the concrete type cached?
            event: Optional[threading.Event] = None
            should_wait: Optional[bool] = None

            with self._cache_lock:  # pylint: disable=not-context-manager
                result = self._cache_info.values.get(cache_key, None)  # type: ignore # pylint: disable=no-member

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

                if result is None:
                    raise Exception("BugBug: bad type")

                # TODO: There are issue here:
                #   - In some cases, need to wait until finalization is complete.
                #   - In some cases, finalization will fail

                assert isinstance(result, Type), result
                return result

            # Create the Type
            concrete_type: Optional[Type] = None

            with ExitStack() as exit_stack:
                # ----------------------------------------------------------------------
                def SetResult():
                    with self._cache_lock:  # pylint: disable=not-context-manager
                        self._cache_info.values[cache_key] = concrete_type # type: ignore # pylint: disable=no-member

                # ----------------------------------------------------------------------

                exit_stack.callback(SetResult)
                exit_stack.callback(event.set)

                concrete_type = entity_resolver.CreateConcreteTypeImpl(
                    self,  # type: ignore
                    resolved_template_arguments,
                    instantiated_class,
                    self._CreateConcreteType,
                )

            assert concrete_type is not None

            # Finalize must be called after the result is cached, as circular references
            # will attempt to create the concrete type again if we attempt to finalize before
            # the concrete type has been cached.
            concrete_type.Finalize()

            return concrete_type

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
                CreateConcreteType(None, None)

        return CreateConcreteType

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass
    class _CacheInfo(object):
        values: Dict[Any, Union[threading.Event, Type]] = field(init=False, default_factory=dict)
        default_initialized: bool                       = field(init=False, default=False)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteType(
        entity_resolver: EntityResolver,
    ) -> Type:
        raise Exception("Abstract method")  # pragma: no cover
