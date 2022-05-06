# ----------------------------------------------------------------------
# |
# |  NamespaceInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-06 09:28:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NamespaceInfo object"""

import os

from collections import OrderedDict
from typing import Dict, List, Optional, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfos.ParserInfo import ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NamespaceInfo(ObjectReprImplBase):
    # ----------------------------------------------------------------------
    # |  Public Types
    ChildrenDict                            = Dict[
        Optional[str],
        Union[
            "NamespaceInfo",
            ParserInfo,
            List[
                Union[
                    "NamespaceInfo",
                    ParserInfo,
                ]
            ],
        ]
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    parser_info: ParserInfo
    children: ChildrenDict                  = field(init=False, default_factory=OrderedDict)

    # ----------------------------------------------------------------------
    # |  Public Methods
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(NamespaceInfo, self).__init__(
            parser_info=type,
        )

    # ----------------------------------------------------------------------
    def AddChild(
        self,
        child: Union["NamespaceInfo", ParserInfo],
    ) -> None:
        if isinstance(child, NamespaceInfo):
            parser_info = child.parser_info
        elif isinstance(child, ParserInfo):
            parser_info = child
        else:
            assert False, child  # pragma: no cover

        key = getattr(parser_info, "name", None)

        existing_value = self.children.get(key, None)  # pylint: disable=no-member

        if isinstance(existing_value, list):
            existing_value.append(child)
        else:
            if existing_value is None:
                value = child
            else:
                value = [existing_value, child]

            self.children[key] = value  # pylint: disable=no-member,unsupported-assignment-operation

    # ----------------------------------------------------------------------
    def AugmentChildren(
        self,
        source_children: ChildrenDict,
    ) -> None:
        for source_key, source_value in source_children.items():
            existing_value = self.children.get(source_key, None)  # pylint: disable=no-member

            if isinstance(existing_value, list):
                if isinstance(source_value, list):
                    existing_value.extend(source_value)
                else:
                    existing_value.append(source_value)

                continue

            if existing_value is None:
                value = source_value
            elif isinstance(source_value, list):
                value = [existing_value] + source_value
            else:
                value = [existing_value, source_value]

            self.children[source_key] = value  # pylint: disable=no-member,unsupported-assignment-operation
