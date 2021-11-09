# ----------------------------------------------------------------------
# |
# |  ClassTypeInfos.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 10:51:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains type information about classes"""

import os
import textwrap

from enum import Enum
from typing import Dict, List, Optional, Tuple, Type

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.ClassModifier import ClassModifier as ClassModifierType
    from ...Common.ClassType import ClassType
    from ...Common.MethodModifier import MethodModifier
    from ...Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeInfo(object):
    # TODO: This needs refinement:
    #          - Address allowed bases, implements, uses

    # Visibility
    DefaultClassVisibility: VisibilityModifier
    AllowedClassVisibilities: List[VisibilityModifier]

    DefaultMemberVisibility: VisibilityModifier
    AllowedMemberVisibilities: List[VisibilityModifier]

    # Base
    DefaultBaseVisibility: Optional[VisibilityModifier]
    AllowedBaseVisibilities: List[VisibilityModifier]
    AllowedBaseTypes: List[ClassType]

    # Extends
    DefaultExtendsVisibility: Optional[VisibilityModifier]
    AllowedExtendsVisibilities: List[VisibilityModifier]
    AllowedExtendsTypes: List[ClassType]

    # Implements
    DefaultImplementsVisibility: Optional[VisibilityModifier]
    AllowedImplementsVisibilities: List[VisibilityModifier]
    AllowedImplementsTypes: List[ClassType]

    # Uses
    DefaultUsesVisibility: Optional[VisibilityModifier]
    AllowedUsesVisibilities: List[VisibilityModifier]
    AllowedUsesTypes: List[ClassType]

    # Modifiers
    DefaultClassModifier: ClassModifierType
    AllowedClassModifiers: List[ClassModifierType]

    # Methods
    DefaultMethodModifier: MethodModifier
    AllowedMethodModifiers: List[MethodModifier]

    # Members
    AllowDataMembers: bool
    AllowMutablePublicDataMembers: bool

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.DefaultClassVisibility in self.AllowedClassVisibilities
        assert self.DefaultMemberVisibility in self.AllowedMemberVisibilities
        assert self.DefaultBaseVisibility is None or self.DefaultBaseVisibility in self.AllowedBaseVisibilities
        assert self.DefaultExtendsVisibility is None or self.DefaultExtendsVisibility in self.AllowedExtendsVisibilities
        assert self.DefaultImplementsVisibility is None or self.DefaultImplementsVisibility in self.AllowedImplementsVisibilities
        assert self.DefaultUsesVisibility is None or self.DefaultUsesVisibility in self.AllowedUsesVisibilities
        assert self.DefaultClassModifier in self.AllowedClassModifiers
        assert self.DefaultMethodModifier in self.AllowedMethodModifiers


# ----------------------------------------------------------------------
# |
# |  Create TypeInfo instances for all ClassType values
# |
# ----------------------------------------------------------------------
_all_method_types                           = list(MethodModifier)
_all_modifiers                              = list(ClassModifierType)
_all_visibilities                           = list(VisibilityModifier)


TYPE_INFOS: Dict[ClassType, TypeInfo]       = {
    # TODO: This needs to be completed
    # TODO: Cog nice tables for this

    # ----------------------------------------------------------------------
    # |  Class
    ClassType.Class: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Extends
        None,
        [],
        [],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifierType.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Enum
    ClassType.Enum: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        None,
        [],
        [],

        # Extends
        None,
        [],
        [],

        # Implements
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Interface, ClassType.Trait],

        # Uses
        None,
        [],
        [],

        # Modifier
        ClassModifierType.immutable,
        [ClassModifierType.immutable],

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,

        # TODO: children can only be:
        #   - VariableDeclaration: Value = 1
        #       - No modifier
        #       - expr is literal int or bit manipulation
        #       - If class has flag attribute, must be power of 2
        #   - GenericName: Value
    ),

    # ----------------------------------------------------------------------
    # |  Exception
    ClassType.Exception: TypeInfo(
        # Class
        VisibilityModifier.public,
        [VisibilityModifier.public],

        # Members
        VisibilityModifier.public,
        _all_visibilities,

        # Base
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Exception],

        # Extends
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Exception],

        # Implements
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Mixin],

        # Modifier
        ClassModifierType.immutable,
        [ClassModifierType.immutable],

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Interface
    ClassType.Interface: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.public,
        [VisibilityModifier.public],

        # Base
        None,
        [],
        [],

        # Extends
        None,
        [],
        [],

        # Implements
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Interface, ClassType.Trait],

        # Uses
        None,
        [],
        [],

        # Modifier
        ClassModifierType.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.abstract,
        [MethodModifier.abstract, MethodModifier.override, MethodModifier.virtual],

        # Members
        AllowDataMembers=False,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Mixin
    ClassType.Mixin: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Class],

        # Extends
        None,
        [],
        [],

        # Implements
        VisibilityModifier.public,
        _all_visibilities,
        [ClassType.Interface, ClassType.Trait],

        # Uses
        VisibilityModifier.private,
        _all_visibilities,
        [ClassType.Mixin],

        # Modifier
        ClassModifierType.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=False,
    ),

    # ----------------------------------------------------------------------
    # |  Struct
    ClassType.Struct: TypeInfo(
        # Class
        VisibilityModifier.public,
        _all_visibilities,

        # Members
        VisibilityModifier.public,
        _all_visibilities,

        # Base
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Struct],

        # Extends
        None,
        [],
        [],

        # Implements
        None,
        [],
        [],

        # Uses
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Struct],

        # Modifier
        ClassModifierType.mutable,
        _all_modifiers,

        # Methods
        MethodModifier.standard,
        _all_method_types,

        # Members
        AllowDataMembers=True,
        AllowMutablePublicDataMembers=True,
    ),

    # ----------------------------------------------------------------------
    # |  Trait
    ClassType.Trait: TypeInfo(
        # Class
        VisibilityModifier.private,
        _all_visibilities,

        # Members
        VisibilityModifier.private,
        _all_visibilities,

        # Base
        None,
        [],
        [],

        # Extends
        None,
        [],
        [],

        # Implements
        VisibilityModifier.public,
        [VisibilityModifier.public],
        [ClassType.Interface, ClassType.Trait],

        # Uses
        None,
        [],
        [],

        # Modifier
        ClassModifierType.immutable,
        _all_modifiers,

        # Methods
        MethodModifier.abstract,
        [MethodModifier.abstract, MethodModifier.override, MethodModifier.virtual],

        # Members
        AllowDataMembers=False,
        AllowMutablePublicDataMembers=False,
    ),
}

assert len(TYPE_INFOS) == len(ClassType)

del _all_visibilities
del _all_modifiers
del _all_method_types


# ----------------------------------------------------------------------
# |
# |  The following methods are used by Cog when generating documentation;
# |  it should not be used by production code.
# |
# ----------------------------------------------------------------------
def CogCreateMembershipTable(
    header: str,
    enum_type: Type[Enum],
    default_attribute_name: Optional[str],
    allowed_attribute_name: str,
    line_width: int=80,
) -> str:

    # Create the template
    class_width, class_left, class_right = _CogGenerateNamesTemplate()

    template_cols = [class_left, ]
    header_cols = [class_left, ]

    template_content_width = class_width

    for e in enum_type:
        col_width = len(e.name)

        # We want to maintain alignment, so take things into our own hands if looking at an
        # odd-numbered number of chars
        if col_width & 1:
            col_width += 1

        template_cols.append(" {{:^{}}} ".format(col_width))

        header_cols.append(" {{:^{}}} ".format(col_width))
        template_content_width += col_width

    header_cols.append(class_right)
    template_cols.append(class_right)

    template_content_width += class_width

    template = "|{}|".format("|".join(template_cols))
    header_template = "|{}|".format("|".join(header_cols))

    # Adjust the template width to account for padding on each side of the content
    template_width = template_content_width + (2 * len(template_cols))

    # Adjust the template width to account for the separators
    template_width += len(template_cols) + 1

    # Create the rows
    rows = [
        "=" * template_width,
        "||{}||".format(" " * (template_width - 4)),
        "||{:^{}}||".format(header, template_width - 4),
        "||{}||".format(" " * (template_width - 4)),
        "=" * template_width,
        header_template.format(*(["",] + list(e.name for e in enum_type) + ["",])),
        "-" * template_width,
    ]

    for class_type, type_info in TYPE_INFOS.items():
        if default_attribute_name is not None:
            default_value = getattr(type_info, default_attribute_name)
        else:
            default_value = None

        allowed_values = set(getattr(type_info, allowed_attribute_name))

        column_values = []

        for e in enum_type:
            if e in allowed_values:
                if e == default_value:
                    value = "Yes*"
                else:
                    value = "Yes"
            else:
                value = " - "

            column_values.append(value)

        rows.append(template.format(*([class_type.name,] + column_values + [class_type.name])))

    rows.append("-" * template_width)

    return textwrap.dedent(
        """\
        # region {header}
        {content}
        # endregion ({header})

        """,
    ).format(
        header=header,
        content="\n".join(["# {:^{}}".format(row, line_width).rstrip() for row in rows]),
    )


# ----------------------------------------------------------------------
def CogCreateFlagsTable(
    line_width: int=80,
) -> str:
    flag_attribute_names = [
        "AllowDataMembers",
        "AllowMutablePublicDataMembers",
    ]

    # Create the template
    class_width, class_left, class_right = _CogGenerateNamesTemplate()

    template_cols = [class_left, ]
    template_content_width = class_width

    for flag_attribute_name in flag_attribute_names:
        template_cols.append(" {{:^{}}} ".format(len(flag_attribute_name)))
        template_content_width += len(flag_attribute_name)

    template_cols.append(class_right)
    template_content_width += class_width

    template = "|{}|".format("|".join(template_cols))

    # Adjust the template width to account for padding on each side of the content
    template_width = template_content_width + (2 * len(template_cols))

    # Adjust the template width to account for the separators
    template_width += len(template_cols) + 1

    rows = [
        "=" * template_width,
        "||{}||".format(" " * (template_width - 4)),
        "||{:^{}}||".format("Flags", template_width - 4),
        "||{}||".format(" " * (template_width - 4)),
        "=" * template_width,
        template.format(*(["",] + flag_attribute_names + ["",])),
    ]

    for class_type, type_info in TYPE_INFOS.items():
        column_values = []

        for flag_attribute_name in flag_attribute_names:
            column_values.append("Y" if getattr(type_info, flag_attribute_name) else "-")

        rows.append(template.format(*([class_type.name,] + column_values + [class_type.name])))

    rows.append("-" * template_width)

    return textwrap.dedent(
        """\
        # region Flags
        {}
        # endregion (Flags)
        """,
    ).format(
        "\n".join(["# {:^{}}".format(row, line_width).rstrip() for row in rows]),
    )


# ----------------------------------------------------------------------
def CogCreateCompleteTable(
    line_width: int=80,
) -> str:

    # ----------------------------------------------------------------------
    def CalcMembershipColumnValue(
        type_info: TypeInfo,
        enum_type: Type[Enum],
        default_attribute_name: Optional[str],
        allowed_attribute_names: str,
    ) -> str:
        if default_attribute_name is not None:
            default_value = getattr(type_info, default_attribute_name)
        else:
            default_value = None

        allowed_values = set(getattr(type_info, allowed_attribute_names))

        content = []

        for e in enum_type:
            if e in allowed_values:
                content.append(e.name)

                if default_attribute_name is not None:
                    assert default_value is not None

                    if e == default_value:
                        content[-1] += "* "

                    if e != default_value:
                        content[-1] += "  "

            else:
                content.append(
                    "{:^{}}{}".format(
                        "-",
                        len(e.name),
                        "  " if default_attribute_name is not None else "",
                    ),
                )

        return " ".join(content)

    # ----------------------------------------------------------------------
    def CalcFlagsColumnValue(
        type_info: TypeInfo,
        attribute_name: str,
    ) -> str:
        return "Y" if getattr(type_info, attribute_name) else "-"

    # ----------------------------------------------------------------------

    # Create the template and get the values at the same time
    class_width, class_left, class_right = _CogGenerateNamesTemplate()

    template_cols = [class_left, ]

    template_content_width = class_width

    all_column_values = []

    for column_value_func, extraction_items in [
        (
            CalcMembershipColumnValue,
            [
                ("Class Visibility", (VisibilityModifier, "DefaultClassVisibility", "AllowedClassVisibilities")),
                ("Member Visibility", (VisibilityModifier, "DefaultMemberVisibility", "AllowedMemberVisibilities")),
                ("Allowed Bases", (ClassType, None, "AllowedBaseTypes")),
                ("Base Visibility", (VisibilityModifier, "DefaultBaseVisibility", "AllowedBaseVisibilities")),
                ("Allowed Implements", (ClassType, None, "AllowedImplementsTypes")),
                ("Implements Visibility", (VisibilityModifier, "DefaultImplementsVisibility", "AllowedImplementsVisibilities")),
                ("Allowed Uses", (ClassType, None, "AllowedUsesTypes")),
                ("Uses Visibility", (VisibilityModifier, "DefaultUsesVisibility", "AllowedUsesVisibilities")),
                ("Class Modifier", (ClassModifierType, "DefaultClassModifier", "AllowedClassModifiers")),
                ("Method Modifier", (MethodModifier, "DefaultMethodModifier", "AllowedMethodModifiers")),
            ],
        ),
        (
            CalcFlagsColumnValue,
            [
                ("AllowDataMembers", ("AllowDataMembers", )),
                ("AllowMutablePublicDataMembers", ("AllowMutablePublicDataMembers", )),
            ],
        ),
    ]:
        for column_name, func_args in extraction_items:
            column_values = [column_name, ]

            for type_info in TYPE_INFOS.values():
                column_values.append(column_value_func(type_info, *func_args))

            max_width = max(*[len(value) for value in column_values])

            template_cols.append(" {{:^{}}} ".format(max_width))
            template_content_width += max_width


            all_column_values.append(column_values)

    template_cols.append(class_right)
    template_content_width += class_width

    template = "|{}|".format("|".join(template_cols))

    # Adjust the template width to account for padding on each side of the content
    template_width = template_content_width + (2 * len(template_cols))

    # Adjust the template width to account for the separators
    template_width += len(template_cols) + 1

    # Create the rows
    rows = [
        "=" * template_width,
        "||{}||".format(" " * (template_width - 4)),
        "||{:^{}}||".format("All Info", template_width - 4),
        "||{}||".format(" " * (template_width - 4)),
        "=" * template_width,
        template.format(*(["",] + [column_values[0] for column_values in all_column_values] + ["",])),
        "-" * template_width,
    ]

    for index, class_type in enumerate(TYPE_INFOS.keys()):
        index += 1

        rows.append(
            template.format(
                *(
                    [class_type.name, ]
                    + [column_values[index] for column_values in all_column_values]
                    + [class_type.name]
                ),
            ),
        )

    rows.append("-" * template_width)

    return textwrap.dedent(
        """\
        # region All Info
        {}
        # endregion (All Info)

        """,
    ).format(
        "\n".join(["# {:^{}}".format(row, line_width).rstrip() for row in rows]),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CogGenerateNamesTemplate() -> Tuple[
    int,  # Column width
    str,  # Left aligned
    str,  # Right aligned
]:
    max_name_length = max(len(e.name) for e in ClassType)

    return (
        max_name_length,
        " {{:<{}s}} ".format(max_name_length),
        " {{:>{}s}} ".format(max_name_length),
    )
