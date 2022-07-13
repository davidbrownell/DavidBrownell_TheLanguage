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
    from ...Types import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConcreteEntity(object):
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplatedStatementTrait(Interface.Interface):
    """Apply to statements that may have templates"""

    # ----------------------------------------------------------------------
    # |  Public Types
    GetOrCreateConcreteEntityFactoryResultType          = Tuple[
        bool,                                           # is_cached_result
        Union[
            Type,                                       # is_cached_result == True
            ConcreteEntity,                             # is_cached_result == True
            Tuple[                                      # is_cached_result == False
                Optional[ResolvedTemplateArguments],
                Callable[
                    [],
                    Union[
                        Type,
                        ConcreteEntity,
                    ],
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
    _cache: Dict[Any, Union[Type, ConcreteEntity]]      = field(init=False, default_factory=dict)

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
    @staticmethod
    @Interface.abstractmethod
    def GetOrCreateConcreteEntityFactory(
        template_arguments: Optional[TemplateArgumentsParserInfo],
        entity_resolver: EntityResolver,
    ) -> "TemplatedStatementTrait.GetOrCreateConcreteEntityFactoryResultType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Protected Methods
    def _GetOrCreateConcreteEntityFactoryImpl(
        self,
        template_arguments: Optional[TemplateArgumentsParserInfo],
        entity_resolver: EntityResolver,
        create_entity_func: Callable[[], Union[Type, ConcreteEntity]],
    ) -> "TemplatedStatementTrait.GetOrCreateConcreteEntityFactoryResultType":
        if self.templates is None:
            if template_arguments:
                raise Exception("BugBug: Template arguments where templates are not expected")

            resolved_template_arguments = None
            cache_key = None

        else:
            assert isinstance(self, NamedTrait), self
            assert isinstance(self, ParserInfo), self

            resolved_template_arguments = self.templates.MatchCall(  # pylint: disable=no-member
                self.name,                  # pylint: disable=no-member
                self.regions__.name,        # pylint: disable=no-member
                self.regions__.self__,      # pylint: disable=no-member
                template_arguments,
                entity_resolver,
            )

            cache_key = resolved_template_arguments.cache_key

        with self._cache_lock:  # pylint: disable=not-context-manager
            result = self._cache.get(cache_key, None)  # pylint: disable=no-member
            if result is not None:
                return True, result

        # ----------------------------------------------------------------------
        def CreateEntityWrapper() -> Union[Type, ConcreteEntity]:
            result = create_entity_func()

            with self._cache_lock:  # pylint: disable=not-context-manager
                self._cache[cache_key] = result

            return result

        # ----------------------------------------------------------------------

        return False, (resolved_template_arguments, CreateEntityWrapper)
