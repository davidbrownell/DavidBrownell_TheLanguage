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
    from ..Common import AttributesPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common.ClassModifier import ClassModifier
    from ..Common.VisibilityModifier import VisibilityModifier
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
# TODO: Rename to ClassMemberStatement (since Attribute has meaning)
class ClassAttributeStatement(GrammarPhrase):
    """\
    Defines a class attribute.

    <attributes>? <visibility>? <type> <name> <class_modifier>? ('=' <expr>)? (':' <<Attribute Items>>)?

    Examples:
        Int foo
        Int bar = 42

        @Member(init=True, serialize=False)
        Int var baz immutable

        @Member(compare=False)
        Int var biz immutable = 42
    """

    PHRASE_NAME                             = "Class Attribute Statement"

    # TODO (Lexer Impl): Potential Attributes: Init, ToStr, Serialize, Equality # <TODO> pylint: disable=W0511

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassAttributeStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <attributes>*
                    AttributesPhraseItem.Create(),

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

                    CommonTokens.Newline,
                ],
            ),
        )
