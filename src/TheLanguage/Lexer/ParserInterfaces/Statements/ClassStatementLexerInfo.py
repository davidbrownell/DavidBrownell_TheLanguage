# ----------------------------------------------------------------------
# |
# |  ClassStatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 14:58:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassDependencyLexerInfo and ClassStatementLexerInfo objects"""

import os

from enum import auto, Enum
from typing import Any, Optional, List

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ...LexerInfo import LexerInfo


# ----------------------------------------------------------------------
class ClassType(Enum):
    # <Line too long> pylint: disable=C0301
    """\
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
    |           | Default Visibility |    Allowed Visibilities    | Default Member Visibility | Allowed Member Visibilities | Default Method Type |               Allowed Method Types                   |    Allow Method Definitions?   | Default Class Modifier | Allowed Class Modifiers | Requires Special Member Definitions | Allows Data Members? | Allows Mutable Public Data Members? |          Can Be Instantiated Directly?           | Bases? | Interfaces? | Mixins? |           |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
    | Primitive |      private       | public, protected, private |          public           |           public            |      deferred       |        deferred, standard (for special members)      | yes (only for special members) |        immutable       |    mutable, immutable   |                 yes                 |          yes         |                 no                  |                       yes                        |   no   |      no     |   no    | Primitive |
    | Class     |      private       | public, protected, private |          private          | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      yes    |   yes   |     Class |
    | Struct    |      private       |          private           |          public           |           public            |      standard       | standard, static, abstract, virtual, override, final |               yes              |         mutable        |         mutable         |   no (defaults will be generated)   |          yes         |                 yes                 |                       yes                        |   yes  |      no     |   no    |    Struct |
    | Exception |      public        |          public            |          public           | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |        immutable        |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      yes    |   yes   | Exception |
    | Enum      |      private       | public, protected, private |          public           |           public            |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      no     |   no    |      Enum |
    | Interface |      private       | public, protected, private |          public           |           public            |      abstract       |       static, abstract, virtual, override, final     |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          no          |                 no                  |     no (must be implemented by a super class)    |   no   |      yes    |   no    | Interface |
    | Mixin     |      private       | public, protected, private |          private          | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |                 no                  |          yes         |                 no                  | no (functionality is "grafted" into super class) |   yes  |      no     |   yes   |     Mixin |
    |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
    """

    Primitive                               = "primitive"
    Class                                   = "class"
    Struct                                  = "struct"
    Exception                               = "exception"
    Enum                                    = "enum"
    Interface                               = "interface"
    Mixin                                   = "mixin"

    # TODO: Enum doesn't seem to fit here


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassDependencyLexerInfo(LexerInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility):
        # TODO

        object.__setattr__(self, "Visibility", visibility)

        super(ClassDependencyLexerInfo, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassStatementLexerInfo(LexerInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier          = field(init=False)

    class_modifier: InitVar[Optional[ClassModifier]]
    ClassModifier: ClassModifier            = field(init=False)

    ClassType: ClassType
    Name: str
    Base: Optional[ClassDependencyLexerInfo]
    Interfaces: List[ClassDependencyLexerInfo]
    Mixins: List[ClassDependencyLexerInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility, class_modifier):
        # TODO

        object.__setattr__(self, "Visibility", visibility)
        object.__setattr__(self, "ClassModifier", class_modifier)

        super(ClassStatementLexerInfo, self).__post_init__()
