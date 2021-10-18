Lexer vs. Parser vs. Grammar
============================
The distinction between a Lexer, Parser, and Grammar can be subtle, and therefore confusing. Here is how these terms are applied in this project.

Definitions
-----------
Token
: A collection of characters, often described as a regular expression.

Phrase
: A collection of tokens.

Attribute Phrase Type
: A phrase type used to augment the compilation process. Example TBD.

Expression Phrase Type
: A phrase that returns a value. Example TBD.

Name Phrase Type
: A phrase that defines a variable name. Example TBD.

Statement Phrase Type
: A phrase that defines a stand-alone statement. For example, a class statement. Example TBD.

Type Phrase Type
: A phrase that defined a type declaration. Example TBD.

Lexer
-----
The lexer matches input using a provided set of phrases organized into Attributes, Expressions, Names, Statements, and Types. The Lexer does not impute semantic value to the tokens associated with the phrases, only that each part of the input matches one and only one phrase.

Example: The lexer recognizes a class statement, but not that the class is named correctly or if it has expected method definitions.

Parser
------
Ensures that the phrases lexed according to the input is semantically valid.

Example: The parser ensures that all class statements create unique class types and that they contain the expected method definitions.

Grammar
-------
Uniquely identifies a collection of potential Attributes, Expressions, Names, Statements, and Types. As a grammar evolves, some of these values may change resulting in a new Grammar. To avoid modifying code when a new grammar is released, code may specify which grammar they are using at any point in time.
