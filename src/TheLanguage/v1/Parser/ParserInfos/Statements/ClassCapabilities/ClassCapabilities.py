# ----------------------------------------------------------------------
# |
# |  ClassCapabilities.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-31 09:46:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassCapabilities object"""

import os

from dataclasses import dataclass
from typing import List, Optional

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.ClassModifier import ClassModifier
    from ...Common.MethodHierarchyModifier import MethodHierarchyModifier

    from ...Common.MutabilityModifier import (
        InvalidNewMutabilityModifierError,
        MutabilityModifier,
        MutabilityModifierRequiredError,
    )

    from ...Common.VisibilityModifier import VisibilityModifier

    from ....Parser import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
VisibilityRequiredError                     = CreateError(
    "A visibility value is required for '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidVisibilityError                      = CreateError(
    "'{visibility_str}' is not a valid visibility value for '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidProtectedVisibilityError             = CreateError(
    "The visibility 'protected' is only valid when nested within a class-like object",
)

ClassModifierRequiredError                  = CreateError(
    "A class modifier is required for '{type}' types; valid values are {valid_class_modifiers_str}",
    type=str,
    valid_class_modifiers=List[ClassModifier],
    valid_class_modifiers_str=str,
)

InvalidClassModifierError                   = CreateError(
    "'{class_modifier_str}' is not a valid class modifier value for '{type}' types; valid values are {valid_class_modifiers_str}",
    type=str,
    class_modifier=ClassModifier,
    class_modifier_str=str,
    valid_class_modifiers=List[ClassModifier],
    valid_class_modifiers_str=str,
)

InvalidDependencyError                      = CreateError(
    "'{type}' types do not support '{desc}' dependencies",
    type=str,
    desc=str,
)

DependencyVisibilityRequiredError           = CreateError(
    "A visibility value is required for '{desc}' dependencies on '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    desc=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidDependencyVisibilityError            = CreateError(
    "'{visibility_str}' is not a valid visibility value for '{desc}' dependencies on '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    desc=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

AttributeVisibilityRequiredError            = CreateError(
    "A visibility value is required for attributes in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidAttributeError                       = CreateError(
    "'{type}' types do not support attributes",
    type=str,
)

InvalidAttributeVisibilityError             = CreateError(
    "'{visibility_str}' is not a valid visibility value for attributes in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidAttributeMutabilityModifierError     = CreateError(
    "'{mutability_str}' is not a valid mutability modifier for attributes in '{type}' types; valid values are {valid_mutabilities_str}",
    type=str,
    mutability=MutabilityModifier,
    valid_mutabilities=List[MutabilityModifier],
    mutability_str=str,
    valid_mutabilities_str=str,
)

InvalidMutablePublicAttributeError          = CreateError(
    "'{type}' types do not support public mutable attributes",
    type=str,
)

TypeAliasVisibilityRequiredError            = CreateError(
    "A visibility value is required for type aliases in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidTypeAliasError                       = CreateError(
    "'{type}' types do not support type aliases",
    type=str,
)

InvalidTypeAliasVisibilityError             = CreateError(
    "'{visibility_str}' is not a valid visibility value for type aliases in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

FuncDefinitionVisibilityRequiredError       = CreateError(
    "A visibility value is required for methods in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidFuncDefinitionError                  = CreateError(
    "'{type}' types do not support methods",
    type=str,
)

InvalidFuncDefinitionVisibilityError        = CreateError(
    "'{visibility_str}' is not a valid visibility value for methods of '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

FuncDefinitionMethodHierarchyModifierRequiredError      = CreateError(
    "A method modifier is required for methods in '{type}' types; valid values are {valid_modifiers_str}",
    type=str,
    valid_modifiers=List[MethodHierarchyModifier],
    valid_modifiers_str=str,
)

InvalidFuncDefinitionMethodHierarchyModifierError       = CreateError(
    "'{method_hierarchy_modifier_str}' is not a valid modifier for methods of '{type}' types; valid values are {valid_method_hierarchy_modifiers_str}",
    type=str,
    method_hierarchy_modifier=MethodHierarchyModifier,
    method_hierarchy_modifier_str=str,
    valid_method_hierarchy_modifiers=List[MethodHierarchyModifier],
    valid_method_hierarchy_modifiers_str=str,
)

FuncDefinitionMutabilityRequiredError       = CreateError(
    "A mutability value is required for methods in '{type}' types; valid values are {valid_mutabilities_str}",
    type=str,
    valid_mutabilities=List[MutabilityModifier],
    valid_mutabilities_str=str,
)

InvalidFuncDefinitionMutabilityError        = CreateError(
    "'{mutability_str}' is not a valid mutability modifier value for methods in '{type}' types; valid values are {valid_mutabilities_str}",
    type=str,
    mutability=MutabilityModifier,
    mutability_str=str,
    valid_mutabilities=List[MutabilityModifier],
    valid_mutabilities_str=str,
)

InvalidStaticMethodError                    = CreateError(
    "'{type}' types do not support static methods",
    type=str,
)

InvalidNestedClassError                     = CreateError(
    "'{type}' types do not support nested class-like objects",
    type=str,
)

InvalidNestedClassTypeError                 = CreateError(
    "'{nested_type}' is not a valid nested class-like object for '{type}' types; valid values are {valid_nested_types_str}",
    type=str,
    nested_type=str,
    valid_nested_types=List[str],
    valid_nested_types_str=str,
)

NestedClassVisibilityRequiredError          = CreateError(
    "A visibility value is required for nested class-like objects in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidNestedClassVisibilityError           = CreateError(
    "'{visibility_str}' is not a valid visibility value for nested class-like objects in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibility_str=str,
)

UsingVisibilityRequiredError                = CreateError(
    "A visibility value is required for using statements in '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

InvalidUsingError                           = CreateError(
    "'{type}' types do not support using statements",
    type=str,
)

InvalidUsingVisibilityError                 = CreateError(
    "'{visibility_str}' is not a valid visibility value for '{type}' types; valid values are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    visibility_str=str,
    valid_visibilities=List[VisibilityModifier],
    valid_visibilities_str=str,
)

# TODO: Should be ResolvedType-based error
MultipleExtendsError                        = CreateError(
    "'{type}' types may only extend one other type",
    type=str,
)

# TODO: Should be ResolvedType-based error
InvalidDependencyTypeError                  = CreateError(
    "'{dependency_type}' is not a valid dependency type for '{desc}' dependencies of '{type}' types; valid values are {valid_types_str}",
    type=str,
    desc=str,
    dependency_type=str,
    valid_types=List[str],
    valid_types_str=str,
)


# ----------------------------------------------------------------------
# TODO: All of the capabilities need some TLC


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassCapabilities(ObjectReprImplBase):
    """\
    Classes come in different forms; this class defines capabilities
    that dictate what is and isn't valid for an instance of a class.
    """

    name: str
    is_instantiable: bool

    valid_visibilities: List[VisibilityModifier]
    default_visibility: Optional[VisibilityModifier]

    valid_class_modifiers: List[ClassModifier]
    default_class_modifier: Optional[ClassModifier]

    valid_extends_visibilities: List[VisibilityModifier]
    default_extends_visibility: Optional[VisibilityModifier]

    valid_implements_types: List[str]
    valid_implements_visibilities: List[VisibilityModifier]
    default_implements_visibility: Optional[VisibilityModifier]

    valid_uses_types: List[str]
    valid_uses_visibilities: List[VisibilityModifier]
    default_uses_visibility: Optional[VisibilityModifier]

    valid_type_alias_visibilities: List[VisibilityModifier]
    default_type_alias_visibility: Optional[VisibilityModifier]

    valid_nested_class_types: List[str]
    valid_nested_class_visibilities: List[VisibilityModifier]
    default_nested_class_visibility: Optional[VisibilityModifier]

    valid_method_hierarchy_modifiers: List[MethodHierarchyModifier]
    default_method_hierarchy_modifier: Optional[MethodHierarchyModifier]
    valid_method_visibilities: List[VisibilityModifier]
    default_method_visibility: Optional[VisibilityModifier]
    valid_method_mutabilities: List[MutabilityModifier]
    default_method_mutability: Optional[MutabilityModifier]
    allow_static_methods: bool

    valid_using_visibilities: List[VisibilityModifier]
    default_using_visibility: Optional[VisibilityModifier]

    valid_attribute_visibilities: List[VisibilityModifier]
    default_attribute_visibility: Optional[VisibilityModifier]
    valid_attribute_mutabilities: List[MutabilityModifier]
    allow_mutable_public_attributes: bool

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.valid_visibilities
        assert self.default_visibility is None or self.default_visibility in self.valid_visibilities

        assert self.valid_class_modifiers
        assert self.default_class_modifier is None or self.default_class_modifier in self.valid_class_modifiers

        assert self.default_extends_visibility is None or self.default_extends_visibility in self.valid_extends_visibilities

        assert (self.valid_implements_types and self.valid_implements_visibilities) or (not self.valid_implements_types and not self.valid_implements_visibilities)
        assert all(implements_type in ["Concept", "Interface"] for implements_type in (self.valid_implements_types or []))
        assert self.default_implements_visibility is None or self.default_implements_visibility in self.valid_implements_visibilities

        assert (self.valid_uses_types and self.valid_uses_visibilities) or (not self.valid_uses_types and not self.valid_uses_visibilities)
        assert all(uses_type in ["Mixin"] for uses_type in (self.valid_uses_types or []))
        assert self.default_uses_visibility is None or self.default_uses_visibility in self.valid_uses_visibilities

        assert self.default_type_alias_visibility is None or self.default_type_alias_visibility in self.valid_type_alias_visibilities

        assert (self.valid_nested_class_types and self.valid_nested_class_visibilities) or (not self.valid_nested_class_types and not self.valid_nested_class_visibilities)
        assert self.default_nested_class_visibility is None or self.default_nested_class_visibility in self.valid_nested_class_visibilities

        assert (self.valid_method_hierarchy_modifiers and self.valid_method_visibilities and self.valid_method_mutabilities) or (not self.valid_method_hierarchy_modifiers and not self.valid_method_visibilities and not self.valid_method_mutabilities)
        assert self.default_method_hierarchy_modifier is None or self.default_method_hierarchy_modifier in self.valid_method_hierarchy_modifiers
        assert self.default_method_visibility is None or self.default_method_visibility in self.valid_method_visibilities
        assert self.default_method_mutability is None or self.default_method_mutability in self.valid_method_mutabilities
        assert not self.allow_static_methods or self.valid_method_visibilities

        assert self.default_using_visibility is None or self.default_using_visibility in self.valid_using_visibilities

        assert (self.valid_attribute_visibilities and self.valid_attribute_mutabilities) or (not self.valid_attribute_visibilities and not self.valid_attribute_mutabilities)
        assert self.default_attribute_visibility is None or self.default_attribute_visibility in self.valid_attribute_visibilities
        assert not self.allow_mutable_public_attributes or (VisibilityModifier.public in self.valid_attribute_visibilities and MutabilityModifier.var in self.valid_attribute_mutabilities)

        ObjectReprImplBase.__init__(self)

    # ----------------------------------------------------------------------
    def ValidateClassStatementCapabilities(
        self,
        parser_info, # : ClassStatementParserInfo
        has_parent_class: bool,
    ) -> None:
        errors: List[Error] = []

        # visibility
        if parser_info.visibility is None:
            if self.valid_visibilities:
                errors.append(
                    VisibilityRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_visibilities=self.valid_visibilities,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_visibilities),
                    ),
                )
        elif parser_info.visibility not in self.valid_visibilities:
            errors.append(
                InvalidVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                    type=self.name,
                    visibility=parser_info.visibility,
                    visibility_str=parser_info.visibility.name,
                    valid_visibilities=self.valid_visibilities,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_visibilities),
                ),
            )
        elif parser_info.visibility == VisibilityModifier.protected and not has_parent_class:
            errors.append(
                InvalidProtectedVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                ),
            )

        # class_modifier
        if parser_info.class_modifier is None:
            if self.valid_class_modifiers:
                errors.append(
                    ClassModifierRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_class_modifiers=self.valid_class_modifiers,
                        valid_class_modifiers_str=", ".join("'{}'".format(v.name) for v in self.valid_class_modifiers),
                    ),
                )
        elif parser_info.class_modifier not in self.valid_class_modifiers:
            errors.append(
                InvalidClassModifierError.Create(
                    region=parser_info.regions__.class_modifier,
                    type=self.name,
                    class_modifier=parser_info.class_modifier,
                    class_modifier_str=parser_info.class_modifier.name,
                    valid_class_modifiers=self.valid_class_modifiers,
                    valid_class_modifiers_str=", ".join("'{}'".format(v.name) for v in self.valid_class_modifiers),
                ),
            )

        # extends / implements / uses
        for desc, dependencies, dependencies_region, valid_visibilities in [
            (
                "extend",
                parser_info.extends,
                parser_info.regions__.extends,
                self.valid_extends_visibilities,
            ),
            (
                "implement",
                parser_info.implements,
                parser_info.regions__.implements,
                self.valid_implements_visibilities,
            ),
            (
                "use",
                parser_info.uses,
                parser_info.regions__.uses,
                self.valid_uses_visibilities,
            ),
        ]:
            # Do not check for errors if there isn't anything to check
            if dependencies is None:
                continue

            if not valid_visibilities:
                errors.append(
                    InvalidDependencyError.Create(
                        region=dependencies_region,
                        type=self.name,
                        desc=desc,
                    ),
                )
                continue

            for dependency in dependencies:
                if dependency.visibility is None:
                    errors.append(
                        DependencyVisibilityRequiredError.Create(
                            region=dependency.regions__.self__,
                            type=self.name,
                            desc=desc,
                            valid_visibilities=valid_visibilities,
                            valid_visibilities_str=", ".join("'{}'".format(v.name) for v in valid_visibilities),
                        ),
                    )
                elif dependency.visibility not in valid_visibilities:
                    errors.append(
                        InvalidDependencyVisibilityError.Create(
                            region=dependency.regions__.visibility,
                            type=self.name,
                            desc=desc,
                            visibility=dependency.visibility,
                            visibility_str=dependency.visibility.name,
                            valid_visibilities=valid_visibilities,
                            valid_visibilities_str=", ".join("'{}'".format(v.name) for v in valid_visibilities),
                        ),
                    )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def ValidateNestedClassStatementCapabilities(
        self,
        parser_info, # : ClassStatementParserInfo
    ) -> None:
        errors: List[Error] = []

        # type
        if not self.valid_nested_class_types:
            errors.append(
                InvalidNestedClassError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.class_capabilities.name not in self.valid_nested_class_types:
            errors.append(
                InvalidNestedClassTypeError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                    nested_type=parser_info.class_capabilities.name,
                    valid_nested_types=self.valid_nested_class_types,
                    valid_nested_types_str=", ".join("'{}'".format(nested_type_name) for nested_type_name in self.valid_nested_class_types),
                ),
            )

        # visibility
        if parser_info.visibility is None:
            if self.valid_nested_class_visibilities:
                errors.append(
                    NestedClassVisibilityRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_visibilities=self.valid_nested_class_visibilities,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_nested_class_visibilities),
                    ),
                )
        elif not self.valid_nested_class_visibilities:
            errors.append(
                InvalidNestedClassError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.visibility not in self.valid_nested_class_visibilities:
            errors.append(
                InvalidNestedClassVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                    type=self.name,
                    visibility=parser_info.visibility,
                    visibility_str=parser_info.visibility.name,
                    valid_visibilities=self.valid_nested_class_visibilities,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_nested_class_visibilities),
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def ValidateClassAttributeStatementCapabilities(
        self,
        parser_info, # : ClassAttributeStatementParserInfo
    ) -> None:
        errors: List[Error] = []

        # visibility
        if parser_info.visibility is None:
            if self.valid_attribute_visibilities:
                errors.append(
                    AttributeVisibilityRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_visibilities=self.valid_attribute_visibilities,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_attribute_visibilities),
                    ),
                )
        elif not self.valid_attribute_visibilities:
            errors.append(
                InvalidAttributeError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.visibility not in self.valid_attribute_visibilities:
            errors.append(
                InvalidAttributeVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                    type=self.name,
                    visibility=parser_info.visibility,
                    visibility_str=parser_info.visibility.name,
                    valid_visibilities=self.valid_attribute_visibilities,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_attribute_visibilities),
                ),
            )

        # mutability
        if parser_info.type.mutability_modifier is None:
            errors.append(
                MutabilityModifierRequiredError.Create(
                    region=parser_info.type.regions__.self__,
                ),
            )
        elif parser_info.type.mutability_modifier == MutabilityModifier.new:
            errors.append(
                InvalidNewMutabilityModifierError.Create(
                    region=parser_info.type.regions__.mutability_modifier,
                ),
            )
        else:
            if parser_info.type.mutability_modifier not in self.valid_attribute_mutabilities:
                errors.append(
                    InvalidAttributeMutabilityModifierError.Create(
                        region=parser_info.type.regions__.mutability_modifier,
                        type=self.name,
                        mutability=parser_info.type.mutability_modifier,
                        mutability_str=parser_info.type.mutability_modifier.name,
                        valid_mutabilities=self.valid_attribute_mutabilities,
                        valid_mutabilities_str=", ".join("'{}'".format(v.name) for v in self.valid_attribute_mutabilities),
                    ),
                )

            if (
                parser_info.visibility == VisibilityModifier.public
                and parser_info.type.mutability_modifier.IsMutable()
                and not self.allow_mutable_public_attributes
            ):
                errors.append(
                    InvalidMutablePublicAttributeError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                    ),
                )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def ValidateTypeAliasStatementCapabilities(
        self,
        parser_info, # : TypeAliasStatementParserInfo
    ) -> None:
        errors: List[Error] = []

        # visibility
        if parser_info.visibility is None:
            if self.valid_type_alias_visibilities:
                errors.append(
                    TypeAliasVisibilityRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_visibilities=self.valid_type_alias_visibilities,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_type_alias_visibilities),
                    ),
                )
        elif not self.valid_type_alias_visibilities:
            errors.append(
                InvalidTypeAliasError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.visibility not in self.valid_type_alias_visibilities:
            errors.append(
                InvalidTypeAliasVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                    type=self.name,
                    visibility=parser_info.visibility,
                    visibility_str=parser_info.visibility.name,
                    valid_visibilities=self.valid_type_alias_visibilities,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_type_alias_visibilities),
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def ValidateFuncDefinitionStatementCapabilities(
        self,
        parser_info, # : FuncDefinitionStatementParserInfo
    ) -> None:
        errors: List[Error] = []

        # visibility
        if parser_info.visibility is None:
            if self.valid_method_visibilities:
                errors.append(
                    FuncDefinitionVisibilityRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_visibilities=self.valid_method_visibilities,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_method_visibilities),
                    ),
                )
        elif not self.valid_method_visibilities:
            errors.append(
                InvalidFuncDefinitionError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.visibility not in self.valid_method_visibilities:
            errors.append(
                InvalidFuncDefinitionVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                    type=self.name,
                    visibility=parser_info.visibility,
                    visibility_str=parser_info.visibility.name,
                    valid_visibilities=self.valid_method_visibilities,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_method_visibilities),
                ),
            )

        # method_hierarchy_modifier
        if parser_info.method_hierarchy_modifier is None:
            if self.valid_method_hierarchy_modifiers:
                errors.append(
                    FuncDefinitionMethodHierarchyModifierRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_modifiers=self.valid_method_hierarchy_modifiers,
                        valid_modifiers_str=", ".join("'{}'".format(v.name) for v in self.valid_method_hierarchy_modifiers),
                    ),
                )
        elif not self.valid_method_hierarchy_modifiers:
            errors.append(
                InvalidFuncDefinitionError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.method_hierarchy_modifier not in self.valid_method_hierarchy_modifiers:
            errors.append(
                InvalidFuncDefinitionMethodHierarchyModifierError.Create(
                    region=parser_info.regions__.method_hierarchy_modifier,
                    type=self.name,
                    method_hierarchy_modifier=parser_info.method_hierarchy_modifier,
                    method_hierarchy_modifier_str=parser_info.method_hierarchy_modifier.name,
                    valid_method_hierarchy_modifiers=self.valid_method_hierarchy_modifiers,
                    valid_method_hierarchy_modifiers_str=", ".join("'{}'".format(v.name) for v in self.valid_method_hierarchy_modifiers),
                ),
            )

        if parser_info.is_static:
            if not self.allow_static_methods:
                errors.append(
                    InvalidStaticMethodError.Create(
                        region=parser_info.regions__.self__,
                    ),
                )
        else:
            # mutability
            if parser_info.mutability is None:
                if self.valid_method_mutabilities:
                    errors.append(
                        FuncDefinitionMutabilityRequiredError.Create(
                            region=parser_info.regions__.self__,
                            type=self.name,
                            valid_mutabilities=self.valid_method_mutabilities,
                            valid_mutabilities_str=", ".join("'{}'".format(v.name) for v in self.valid_method_mutabilities),
                        ),
                    )
            elif not self.valid_method_mutabilities:
                errors.append(
                    InvalidFuncDefinitionError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                    ),
                )
            elif parser_info.mutability == MutabilityModifier.new:
                errors.append(
                    InvalidNewMutabilityModifierError.Create(
                        region=parser_info.regions__.mutability,
                    ),
                )
            elif parser_info.mutability not in self.valid_method_mutabilities:
                errors.append(
                    InvalidFuncDefinitionMutabilityError.Create(
                        region=parser_info.mutability,
                        type=self.name,
                        mutability=parser_info.mutability,
                        mutability_str=parser_info.mutability.name,
                        valid_mutabilities=self.valid_attribute_mutabilities,
                        valid_mutabilities_str=", ".join("'{}'".format(v.name) for v in self.valid_method_mutabilities),
                    ),
                )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def ValidateUsingStatementCapabilities(
        self,
        parser_info, # ClassUsingStatementParserInfo
    ) -> None:
        errors: List[Error] = []

        # visibility
        if parser_info.visibility is None:
            if self.valid_using_visibilities:
                errors.append(
                    UsingVisibilityRequiredError.Create(
                        region=parser_info.regions__.self__,
                        type=self.name,
                        valid_visibilities=self.valid_using_visibilities,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_using_visibilities),
                    ),
                )
        elif not self.valid_using_visibilities:
            errors.append(
                InvalidUsingError.Create(
                    region=parser_info.regions__.self__,
                    type=self.name,
                ),
            )
        elif parser_info.visibility not in self.valid_using_visibilities:
            errors.append(
                InvalidUsingVisibilityError.Create(
                    region=parser_info.regions__.visibility,
                    type=self.name,
                    visibility=parser_info.visibility,
                    visibility_str=parser_info.visibility.name,
                    valid_visibilities=self.valid_using_visibilities,
                    valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.valid_using_visibilities),
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def ValidateDependencies(
        self,
        parser_info, # ClassStatementParserInfo
    ) -> None:
        errors: List[Error] = []

        # Check for multiple extends
        has_extends = False

        for dependency in (parser_info.extends or []):
            if dependency.is_disabled__:
                continue

            if has_extends:
                errors.append(
                    MultipleExtendsError.Create(
                        region=dependency.regions__.self__,
                        type=self.name,
                    ),
                )

                continue

            has_extends = True

        for desc, dependencies, valid_type_names in [
            (
                "extend",
                parser_info.extends,
                [self.name, ],
            ),
            (
                "implement",
                parser_info.implements,
                self.valid_implements_types,
            ),
            (
                "uses",
                parser_info.uses,
                self.valid_uses_types,
            ),
        ]:
            # Do not check for errors if there isn't anything to check
            if dependencies is None:
                continue

            # We checked for the error where dependencies were provided but dependencies aren't
            # supported when validating supported dependency visibility, so we don't need to check
            # for that condition again.
            assert valid_type_names

            for dependency in dependencies:
                if dependency.is_disabled__:
                    continue

                dependency_parser_info = dependency.type.resolved_type__.Resolve().parser_info

                if dependency_parser_info.class_capabilities.name not in valid_type_names:
                    errors.append(
                        InvalidDependencyTypeError.Create(
                            region=dependency.type.regions__.self__,
                            type=self.name,
                            desc=desc,
                            dependency_type=dependency_parser_info.class_capabilities.name,
                            valid_types=valid_type_names,
                            valid_types_str=", ".join("'{}'".format(type_name) for type_name in valid_type_names),
                        ),
                    )

        if errors:
            raise ErrorException(*errors)
