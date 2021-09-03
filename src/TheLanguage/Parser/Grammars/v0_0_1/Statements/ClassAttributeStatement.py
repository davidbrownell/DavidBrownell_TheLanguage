# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-02 12:03:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassAttributeStatement object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
# TODO: Consider an attribute syntax that is consistent between classes, functions, attributes, etc.  # <TODO> pylint: disable=W0511
class ClassAttributeStatement(GrammarPhrase):
    """\
    Defines a class attribute.

    <visibility>? <type> <name> <class_modifier>? ('=' <expr>)? (':' <<Attribute Items>>)?

    Examples:
        Int foo
        Int bar = 42
        Int var baz immutable: +Init, -Serialize
        Int var biz immutable = 42: +Init, -Serialize
    """

    PHRASE_NAME                             = "Class Attribute Statement"

    # TODO: Potential Attributes: Init, ToStr, Serialize, Equality # <TODO> pylint: disable=W0511

    # ----------------------------------------------------------------------
    def __init__(self):
        # '+'|'-' <type_name>
        attribute_item = PhraseItem(
            name="Item",
            item=[
                ("+", "-"),
                CommonTokens.TypeName,
            ],
        )

        # <attribute_item> (',' <attribute_item>)* ','?
        attribute_items = PhraseItem(
            name="Attribute Items",
            item=[
                # <attribute_item>
                attribute_item,

                # (',' <attribute_item>)*
                PhraseItem(
                    name="Comma and Content",
                    item=[
                        ",",
                        attribute_item,
                    ],
                    arity="*",
                ),

                # ','?
                PhraseItem(
                    name="Trailing Comma",
                    item=",",
                    arity="?",
                ),
            ],
        )

        super(ClassAttributeStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <visibility>?
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.GenericName,

                    # <class_type>?
                    PhraseItem(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # ('=' <expr>)?
                    PhraseItem(
                        name="Default Value",
                        item=[
                            "=",
                            DynamicPhrasesType.Expressions,
                        ],
                        arity="?",
                    ),

                    # (':' <<attributes>>)?
                    PhraseItem(
                        name="Attributes",
                        item=[
                            ":",

                            PhraseItem(
                                item=(
                                    # '(' <attribute_items> ')'
                                    PhraseItem(
                                        name="Grouped",
                                        item=[
                                            # '('
                                            "(",
                                            CommonTokens.PushIgnoreWhitespaceControl,

                                            # <attribute_items>
                                            attribute_items,

                                            # ')'
                                            CommonTokens.PopIgnoreWhitespaceControl,
                                            ")",
                                        ],
                                    ),

                                    # <attribute_items>>
                                    attribute_items,
                                ),

                                # Use the order to disambiguate between group clauses and tuples.
                                ordered_by_priority=True,
                            ),
                        ],
                        arity="?",
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )
