# ----------------------------------------------------------------------
# |
# |  MultilineFragmentFrag.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 15:37:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that is used when creating and parsing multiline phrases"""

import os
import re

from typing import cast, List, Union, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarPhrase import AST

    from ....Lexer.Components.Normalize import MultilineTokenDelimiterRegexTemplate, multiline_token_delimiter_length

    from ....Lexer.Phrases.DSL import (
        ExtractSequence,
        ExtractToken,
        PhraseItemItemType,
        RegexToken,
    )

    from ....Parser.Parser import CreateError, CreateRegion, Error


# ----------------------------------------------------------------------
InvalidMultilineHeaderError                 = CreateError(
    "The header '{header}' must be followed by a new line",
    header=str,
)

InvalidMultilineIndentError                 = CreateError(
    "Multiline content must be aligned horizontally with the header '{header}' [Line: {line_number}]",
    header=str,
    line_number=int,
)

InvalidMultilineFooterError                 = CreateError(
    "The footer '{footer}' must be aligned horizontally with the header '{header}' [Line: {line_number}]",
    header=str,
    footer=str,
    line_number=int,
)

InvalidMultilineContentError                = CreateError(
    "Multiline content cannot be empty",
)


# ----------------------------------------------------------------------
def Create(
    header: str,
    footer: str,
) -> PhraseItemItemType:
    assert len(header) % multiline_token_delimiter_length == 0, header
    assert len(footer) % multiline_token_delimiter_length == 0, footer

    return [
        RegexToken(
            "Multi-line Content",
            re.compile(
                MultilineTokenDelimiterRegexTemplate.format(
                    header=re.escape(header),
                    footer=re.escape(footer),
                ),
                re.DOTALL | re.MULTILINE,
            ),
            is_multiline=True,
        ),
    ]


# ----------------------------------------------------------------------
def Extract(
    header: str,
    footer: str,
    node: AST.Node,
) -> Union[
    Tuple[AST.Leaf, str],
    List[Error],
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 1

    errors: List[Error] = []

    leaf = cast(AST.Leaf, nodes[0])
    value = ExtractToken(leaf)

    if not value.startswith("\n"):
        errors.append(
            InvalidMultilineHeaderError.Create(
                region=CreateRegion(leaf),
                header=header,
            ),
        )
    else:
        value = value[1:]

    lines = value.split("\n")

    expected_indentation_len = leaf.iter_range.begin.offset - leaf.iter_range.begin.line_info.offset_begin
    if expected_indentation_len:
        expected_indentation = leaf.iter_range.begin.content[leaf.iter_range.begin.offset - expected_indentation_len : leaf.iter_range.begin.offset]

        for line_index, line in enumerate(lines):
            if not line:
                continue

            if not line.startswith(expected_indentation):
                if line.isspace() and line_index != len(lines) - 1:
                    line = ""
                else:
                    errors.append(
                        InvalidMultilineIndentError.Create(
                            region=CreateRegion(leaf),
                            header=header,
                            line_number=line_index + 1,
                        ),
                    )
            else:
                line = line[expected_indentation_len:]

            lines[line_index] = line

    # The last line should be empty, as it should be the indentation and footer
    if lines[-1]:
        errors.append(
            InvalidMultilineFooterError.Create(
                region=CreateRegion(leaf),
                header=header,
                footer=footer,
                line_number=len(lines),
            ),
        )

    lines.pop()

    value = "\n".join(lines)
    if not value:
        errors.append(
            InvalidMultilineContentError.Create(
                region=CreateRegion(leaf),
            ),
        )

    if errors:
        return errors

    value = value.replace("\\{}".format(footer), footer)

    return leaf, value
