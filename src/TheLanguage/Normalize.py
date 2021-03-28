# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 10:31:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types that facilitate the tokenization process"""

import os
import string

from typing import List

import six

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

import Errors

# ----------------------------------------------------------------------
def Normalize(
    source_name: str,
    content: str,
) -> List[str]:
    """\
    Removes comments and converts multiline strings into single line-strings.

    In traditional parsers, a lexer can do these types of things inline while
    processing content. However, this parser combines the ideas of a lexer and
    parser and therefore must handle some of these activities before lexing can
    begin.
    """

    if content[-1] != "\n":
        content += "\n"

    # When we encounter a newline, we will append to one of these lists
    lines = []
    string_lines = []
    active_lines_list = lines

    # ----------------------------------------------------------------------
    def InMultilineString() -> bool:
        return active_lines_list is string_lines

    # ----------------------------------------------------------------------
    def ExtractStringContent(line_index: int) -> str:
        assert line_index > 0 and line_index < len(string_lines)

        reference_line = string_lines[0]
        this_line = string_lines[line_index]

        index = 0

        if (
            this_line[0] != this_line[1]
            or content[this_line[0]] != "\n"
        ):
            while (
                content[reference_line[0] + index] != '"'
                and index != reference_line[1]
                and index != this_line[1]
                and content[this_line[0] + index] == content[reference_line[0] + index]
            ):
                index += 1

            if content[reference_line[0] + index] != '"':
                raise Errors.InvalidMultilineStringPrefixError(
                    source_name,
                    len(lines) + line_index + 1,
                    index + 1,
                )

        assert index <= reference_line[1]

        return content[
            this_line[0] + index
            : this_line[1]
        ]

    # ----------------------------------------------------------------------

    line_start_offset = 0

    offset = 0
    len_content = len(content)
    len_token = len('"""')

    comment_token_offset = None

    while offset < len_content:
        if (
            offset + 2 < len_content
            and content[offset] == '"'
            and content[offset + 1] == '"'
            and content[offset + 2] == '"'
        ):
            if (
                offset + len_token == len_content
                or content[offset + len_token] != "\n"
            ):
                raise Errors.MissingMultilineTokenNewlineSuffixError(
                    source_name,
                    len(lines) + len(string_lines),
                    offset - line_start_offset + len_token + 1,
                )

            if InMultilineString():
                # We are looking at a closing token
                string_lines.append((line_start_offset, offset))

                # Get the string lines without the prefix
                string_content = [
                    ExtractStringContent(index) for index in range(1, len(string_lines))
                ]

                assert string_content
                assert not string_content[-1]

                string_content_lines = len(string_content) - 1
                line_start_offset = offset + len_token

                # Add the new string and empty lines for the content that is no longer valid
                string_content = "\n".join(string_content[:-1]).replace('"', '\\"')

                lines.append('"{}"'.format(string_content))
                lines += [""] * string_content_lines

                active_lines_list = lines
                string_lines = []

            else:
                # We are looking at an opening token
                active_lines_list = string_lines

            # Move beyond the triple quote
            offset += len_token

        if content[offset] == "\n":
            line_end_offset = offset

            if not InMultilineString():
                # Capture the extent of the line without trailing comments
                if comment_token_offset is not None:
                    line_end_offset = comment_token_offset

                # Remove trailing whitespace
                while line_end_offset > line_start_offset and content[line_end_offset - 1] in string.whitespace:
                    line_end_offset -= 1

            active_lines_list.append((line_start_offset, line_end_offset))

            line_start_offset = offset + 1
            comment_token_offset = None

        elif content[offset] == "#" and comment_token_offset is None:
            comment_token_offset = offset

        offset += 1

    if InMultilineString():
        raise Errors.MissingMultilineStringTerminatorError(
            source_name,
            len(lines) + 1,
            # The column will be the length of the first string line minus the length of the token
            string_lines[0][1] - string_lines[0][0] - len_token + 1,
        )

    assert offset == line_start_offset, (offset, line_start_offset)

    # Convert the lines to strings
    return [
        line if isinstance(line, six.string_types) else content[line[0]:line[1]]
        for line in lines
    ]
