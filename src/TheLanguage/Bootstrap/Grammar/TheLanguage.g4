// ----------------------------------------------------------------------
// |
// |  TheLanguage.g4
// |
// |  David Brownell <db@DavidBrownell.com>
// |      2021-12-28 10:01:15
// |
// ----------------------------------------------------------------------
// |
// |  Copyright David Brownell 2021
// |  Distributed under the Boost Software License, Version 1.0. See
// |  accompanying file LICENSE_1_0.txt or copy at
// |  http://www.boost.org/LICENSE_1_0.txt.
// |
// ----------------------------------------------------------------------
grammar TheLanguage;

tokens {
    INDENT, DEDENT,
    PUSH_IGNORE_WHTIESPACE, POP_IGNORE_WHITESPACE
}

// ----------------------------------------------------------------------
STANDARD_CASE_STRICT: [a-z][a-zA-Z0-9_]*;
STANDARD_CASE: '_'* STANDARD_CASE_STRICT '_'*;
STANDARD_CASE_COMPILE_TIME: '_'* STANDARD_CASE_STRICT '\'' '_'*;

PASCAL_CASE_STRICT: [A-Z][a-zA-Z0-9_]*;
PASCAL_CASE: '_'* PASCAL_CASE_STRICT '_'*;
PASCAL_CASE_COMPILE_TIME: '_'* PASCAL_CASE_STRICT '\''? '_'*;
PASCAL_CASE_WITH_QUESTION: '_'* PASCAL_CASE_STRICT '?'? '_'*;

PERFECT_FORWARD: '***';

NEWLINE: '\r'? '\n';

// TODO: Comma sep
NUM_LITERAL: [+-]? [0-9]+ '.' [0-9]+;
INT_LITERAL: [+-]? [0-9]+;
BOOL_LITERAL: 'True' | 'False';
NONE_LITERAL: 'None';
CHAR_LITERAL: '\'\\?.\'';
STRING_LITERAL: '"' ('\\"' | '\\\\' | ~'"')*? '"';

// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// |
// |  Fragments
// |
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------

// ----------------------------------------------------------------------
// |  Name Fragments
module_name: PASCAL_CASE_STRICT;
type_name: PASCAL_CASE;
function_name: PASCAL_CASE_WITH_QUESTION;
variable_name: STANDARD_CASE;
template_variable_name: PASCAL_CASE_COMPILE_TIME;
constraint_variable_name: STANDARD_CASE_COMPILE_TIME;

// ----------------------------------------------------------------------
// |  Miscellaneous

// |------------|----------|--------|
// | mutability | isolated | shared |
// |------------|----------|--------|
// | mutable    |    var   |   ref  |
// | immutable  |  iso_val |   val  |
// |------------|----------|--------|

// Argument -> Parameter conversion

var: mutable, immutable, var
ref: mutable, immutable, ref ????
val: immutable, val

Concepts:
- As a function, I will not modify the argument (mutable vs. immutable)
- As a function, I do not expect the argument to be modified under me (isolated vs. shared)


type_modifier: 'immutable' | 'mutable' | 'var' | 'ref' | 'iso_val' | 'val';
method_modifier: 'abstract' | 'final' | 'override' | 'standard' | 'virtual';
visibility_modifier: 'public' | 'protected' | 'private' | 'internal';

new_style_parameters_indicator: 'any' | 'pos' | 'key';
traditional_parameters_indicator: '/' | '*';

// ----------------------------------------------------------------------
// |  Attributes
attributes: '[' PUSH_IGNORE_WHTIESPACE attributes_list POP_IGNORE_WHITESPACE ']';
attributes_list: attributes_list_item (',' attributes_list_item)* ','?;
attributes_list_item: function_name function_arguments?;

// ----------------------------------------------------------------------
// |  Captured Variables
captured_variables: '|' PUSH_IGNORE_WHTIESPACE captured_variables_list POP_IGNORE_WHITESPACE '|';
captured_variables_list: captured_variables_list_item (',' captured_variables_list_item)* ','?;
captured_variables_list_item: variable_name;

// ----------------------------------------------------------------------
// |  Constraint Arguments
constraint_arguments: '{' PUSH_IGNORE_WHTIESPACE constraint_arguments_list POP_IGNORE_WHITESPACE '}';
constraint_arguments_list: constraint_arguments_list_item (',' constraint_arguments_list_item)* ','?;
constraint_arguments_list_item: (constraint_variable_name '=')? constraint_expression;

// ----------------------------------------------------------------------
// |  Constraint Parameters
constraint_parameters: '{' PUSH_IGNORE_WHTIESPACE constraint_parameters_list POP_IGNORE_WHITESPACE '}';
constraint_parameters_list: constraint_parameters_list_new | constraint_parameters_list_trad;
constraint_parameters_list_item: constraint_type constraint_variable_name ('=' constraint_expression)?;

constraint_parameters_list_new: (new_style_parameters_indicator ':' constraint_parameters_list_item (',' constraint_parameters_list_item)* ','?)+;
constraint_parameters_list_trad: constraint_parameters_list_trad_item (',' constraint_parameters_list_trad_item)* ','?;
constraint_parameters_list_trad_item: traditional_parameters_indicator | constraint_parameters_list_item;

// ----------------------------------------------------------------------
// |  Function Arguments
function_arguments: '(' PUSH_IGNORE_WHTIESPACE function_arguments_list? POP_IGNORE_WHITESPACE ')';
function_arguments_list: (PERFECT_FORWARD | (function_arguments_list_item (',' function_arguments_list_item)* ','?));
function_arguments_list_item: (variable_name '=')? standard_expression;

// ----------------------------------------------------------------------
// |  Function Parameters
function_parameters: '(' PUSH_IGNORE_WHTIESPACE function_parameters_list? POP_IGNORE_WHITESPACE ')';
function_parameters_list: PERFECT_FORWARD | function_parameters_list_new | function_parameters_list_trad;
function_parameters_list_item: standard_type /*type_modifier is required*/ '...'? variable_name ('=' standard_expression)?;

function_parameters_list_new: (new_style_parameters_indicator ':' function_parameters_list_item (',' function_parameters_list_item)* ','?)+;
function_parameters_list_trad: function_parameters_list_trad_item (',' function_parameters_list_trad_item)* ','?;
function_parameters_list_trad_item: traditional_parameters_indicator | function_parameters_list_item;

// ----------------------------------------------------------------------
// |  Scoped Statements
scoped_statements: scoped_statements_single_line | scoped_statements_multiple_lines;
scoped_statements_single_line: ':' standard_statement;
scoped_statements_multiple_lines: ':' NEWLINE INDENT standard_statement+ DEDENT;

// ----------------------------------------------------------------------
// |  Template Arguments
template_arguments: '<' PUSH_IGNORE_WHTIESPACE template_arguments_list POP_IGNORE_WHITESPACE '>';
template_arguments_list: template_arguments_list_item (',' template_arguments_list_item)* ','?;
template_arguments_list_item: template_arguments_list_item_type | template_arguments_list_item_expression;

template_arguments_list_item_type: (type_name '=')? standard_type /*type_modifier is optional*/;
template_arguments_list_item_expression: (template_variable_name '=')? template_expression;

// ----------------------------------------------------------------------
// |  Template Parameters
template_parameters: '<' PUSH_IGNORE_WHTIESPACE template_parameters_list POP_IGNORE_WHITESPACE '>';
template_parameters_list: template_parameters_list_new | template_parameters_list_trad;
template_parameters_list_item: template_parameters_list_item_type | template_parameters_list_item_expression;

template_parameters_list_item_type: type_name '...'? ('=' standard_type /*type_modifier is optional*/)?;
template_parameters_list_item_expression: template_type template_variable_name ('=' template_expression)?;

template_parameters_list_new: (new_style_parameters_indicator ':' template_parameters_list_item (',' template_parameters_list_item)* ','?)+;
template_parameters_list_trad: template_parameters_list_trad_item (',' template_parameters_list_trad_item)* ','?;
template_parameters_list_trad_item: traditional_parameters_indicator | template_parameters_list_item;

// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// |
// |  Constraints
// |
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
constraint_type: constraint_type_fundamental | constraint_type_variant;
constraint_type_fundamental: 'Bool\'' | 'Char\'' | 'Int\'' | 'None\'' | 'Num\'' | 'String\'';
constraint_type_variant: (
    '('
    PUSH_IGNORE_WHTIESPACE
    constraint_type_fundamental
    ('|' constraint_type_fundamental)*
    '|'
    constraint_type_fundamental
    POP_IGNORE_WHITESPACE
    ')'
);

constraint_expression: (
    constraint_expression_binary
    | constraint_expression_bool
    | constraint_expression_char
    | constraint_expression_int
    | constraint_expression_none
    | constraint_expression_num
    | constraint_expression_string
    | constraint_expression_unary
);

constraint_expression_binary: (
    constraint_expression
    (
        // BugBug: Group these according to precedence
        'and' | 'or'
        | '<' | '<=' | '>' | '>=' | '==' | '!='
        | '+' | '-' | '*' | '**' | '/' | '//' | '%'
        | '<<' | '>>' | '^' | '&' | '|'
    )
    constraint_expression
);

constraint_expression_bool: BOOL_LITERAL;
constraint_expression_char: CHAR_LITERAL;
constraint_expression_int: INT_LITERAL;
constraint_expression_none: NONE_LITERAL;
constraint_expression_num: NUM_LITERAL;
constraint_expression_string: STRING_LITERAL;

constraint_expression_unary: (
    (
        // BugBug: Group these according to precedence
        'not'
        | '+' | '-'
        | '~'
    )
    constraint_expression
);

// BugBug: constraint_statements

// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// |
// |  Standard
// |
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------

// ----------------------------------------------------------------------
// |
// |  Expressions
// |
// ----------------------------------------------------------------------
standard_expression: (
    standard_expression_binary
    | standard_expression_bool
    | standard_expression_cast
    | standard_expression_char
    | standard_expression_func
    | standard_expression_generator
    | standard_expression_group
    | standard_expression_index
    | standard_expression_int
    | standard_expression_lambda
    | standard_expression_match_type
    | standard_expression_match_value
    | standard_expression_name
    | standard_expression_none
    | standard_expression_num
    | standard_expression_slice
    | standard_expression_string
    | standard_expression_ternary
    | standard_expression_tuple
    | standard_expression_unary
);

standard_expression_binary: (
    standard_expression
    (
        // BugBug: Group these according to precedence
        'and' | 'or' | 'in' | 'not in'
        | '.' | '->'
        | '<' | '<=' | '>' | '>=' | '==' | '!='
        | '+' | '-' | '*' | '**' | '/' | '//' | '%'
        | '<<' | '>>' | '^' | '&' | '|'
    )
    standard_expression
);

standard_expression_bool: BOOL_LITERAL;

standard_expression_cast: (
    standard_expression
    (
        'as' | 'is'
    )
    (type_modifier | standard_type)
);

standard_expression_char: CHAR_LITERAL;

standard_expression_func: (
    standard_expression
    template_arguments?
    function_arguments
);

standard_expression_generator: (
    standard_expression
    'for'
    standard_name
    'in'
    standard_expression
    ('if' standard_expression)?
);

standard_expression_group: (
    '('
    PUSH_IGNORE_WHTIESPACE
    standard_expression
    POP_IGNORE_WHITESPACE
    ')'
);

standard_expression_index: (
    standard_expression
    '['
    PUSH_IGNORE_WHTIESPACE
    standard_expression
    POP_IGNORE_WHITESPACE
    ']'
);

standard_expression_int: INT_LITERAL;

standard_expression_lambda: (
    'lambda'
    captured_variables?
    function_parameters
    ':'
    standard_expression
);

standard_expression_match_type: (
    'BugBug'
);

standard_expression_match_value: (
    'BugBug'
);

standard_expression_name: variable_name;

standard_expression_none: NONE_LITERAL;
standard_expression_num: NUM_LITERAL;

standard_expression_slice: (
    standard_expression?
    ':'
    standard_expression?
);

standard_expression_string: STRING_LITERAL;

standard_expression_ternary: (
    standard_expression
    'if'
    standard_expression
    'else'
    standard_expression
);

standard_expression_tuple: (
    '('
    PUSH_IGNORE_WHTIESPACE
    standard_expression_tuple_single | standard_expression_tuple_multiple
    POP_IGNORE_WHITESPACE
    ')'
);

standard_expression_tuple_single: standard_expression ',';
standard_expression_tuple_multiple: standard_expression (',' standard_expression)+ ','?;

standard_expression_unary: (
    (
        // BugBug: Order by precedence
        'await'
        | 'move' | 'ref'
        | 'not'
        | '+' | '-'
        | '~'
    )
    standard_expression
);

// ----------------------------------------------------------------------
// |
// |  Names
// |
// ----------------------------------------------------------------------
standard_name: variable_name | standard_name_tuple;
standard_name_tuple: (
    '('
    standard_name
    (',' standard_name)+
    ','?
    ')'
);

// ----------------------------------------------------------------------
// |
// |  Statements
// |
// ----------------------------------------------------------------------
standard_statement: (
    standard_statement_assert
    | standard_statement_assignment
    | standard_statement_binary
    | standard_statement_break
    | standard_statement_class
    | standard_statement_class_member
    | standard_statement_class_member_enum
    | standard_statement_class_property
    | standard_statement_continue
    | standard_statement_delete
    | standard_statement_docstring
    | standard_statement_exit
    | standard_statement_for
    | standard_statement_func_def
    | standard_statement_func_inv
    | standard_statement_if
    | standard_statement_import
    | standard_statement_init
    | standard_statement_pass
    | standard_statement_raise
    | standard_statement_return
    | standard_statement_try
    | standard_statement_using
    | standard_statement_variable_declaration
    | standard_statement_with
    | standard_statement_while
    | standard_statement_yield
);

standard_statement_assert: (
    ('assert' | 'ensure')
    standard_expression
    (',' standard_expression)?
    NEWLINE
);

standard_statement_assignment: (
    standard_expression
    '='
    standard_expression
    NEWLINE
);

standard_statement_binary: (
    standard_name
    (
        // BugBug: Order by precedence
        '+=' | '-=' | '*=' | '**=' | '/=' | '//=' | '%='
        | '<<=' | '>>=' | '^=' | '&=' | '|='
    )
    standard_expression
    NEWLINE
);

standard_statement_break: 'break' NEWLINE;

standard_statement_class: 'BugBug';
standard_statement_class_member: 'BugBug';
standard_statement_class_member_enum: 'BugBug';
standard_statement_class_property: 'BugBug';

standard_statement_continue: 'continue' NEWLINE;

// SUGAR
standard_statement_delete: 'delete' variable_name (',' variable_name)* ','? NEWLINE;

// SUGAR
standard_statement_docstring: '<<<' .*? '>>>' NEWLINE;

standard_statement_exit: 'exit' ':' standard_expression NEWLINE;

standard_statement_for: (
    'for'
    standard_name
    'in'
    standard_expression
    scoped_statements
);

standard_statement_func_def: 'BugBug';

standard_statement_func_inv: standard_expression_func NEWLINE;

standard_statement_if: (
    'if' standard_expression scoped_statements
    ('elif' standard_expression scoped_statements)*
    ('else' scoped_statements)?
);

standard_statement_import: (
    visibility_modifier?
    'from'
    module_name ('.' module_name)*
    'import'
    (
        (
            '('
            PUSH_IGNORE_WHTIESPACE
            standard_statement_import_list
            POP_IGNORE_WHITESPACE
            ')'
        )
        | standard_statement_import_list
    )
    NEWLINE
);

standard_statement_import_list: standard_statement_import_list_item (',' standard_statement_import_list_item)* ','?;
standard_statement_import_list_item: standard_statement_import_list_item_name ('as' standard_statement_import_list_item_name)?;
standard_statement_import_list_item_name: module_name | type_name | function_name;

// SUGAR
standard_statement_init: (
    standard_type /*type_modifier is None*/
    'init'
    variable_name NEWLINE
);

standard_statement_pass: 'pass' NEWLINE;

standard_statement_raise: 'raise' standard_expression? NEWLINE;

standard_statement_return: 'return' standard_expression? NEWLINE;

standard_statement_try: (
    'try'
    scoped_statements

    // One of the following is required
    (
        'except'
        standard_type_fundamental
        variable_name?
        scoped_statements
    )*
    (
        'except'
        scoped_statements
    )?
);

standard_statement_using: (
    visibility_modifier?
    'using'
    type_name
    '='
    standard_type /*type_modifier is None*/
    NEWLINE
);

standard_statement_variable_declaration: (
    type_modifier
    standard_name
    '='
    standard_expression
    NEWLINE
);

// SUGAR
standard_statement_with: (
    'with'
    standard_expression
    scoped_statements
);

standard_statement_while: (
    'while'
    standard_expression
    scoped_statements
);

standard_statement_yield: 'yield' ('from'? standard_expression)? NEWLINE;

// ----------------------------------------------------------------------
// |
// |  Types
// |
// ----------------------------------------------------------------------
standard_type: (
    (
        standard_type_func
        | standard_type_fundamental
        | standard_type_tuple
        | standard_type_typeof
        | standard_type_variant
    )
    type_modifier?
);

standard_type_func: (
    '('
    PUSH_IGNORE_WHTIESPACE
    standard_type
    function_parameters
    POP_IGNORE_WHITESPACE
    ')'
);

standard_type_fundamental: type_name ('::' type_name)* template_arguments? constraint_arguments?;

standard_type_tuple: (
    '('
    PUSH_IGNORE_WHTIESPACE
    (standard_type_tuple_single | standard_type_tuple_multiple)
    POP_IGNORE_WHITESPACE
    ')'
);

standard_type_tuple_single: standard_type ',';
standard_type_tuple_multiple: standard_type (',' standard_type)+ ','?;

standard_type_typeof: (
    'TypeOf\''
    '('
    PUSH_IGNORE_WHTIESPACE
    standard_expression
    POP_IGNORE_WHITESPACE
    ')'
);

standard_type_variant: (
    '('
    PUSH_IGNORE_WHTIESPACE
    standard_type
    ('|' standard_type)*
    '|'
    standard_type
    POP_IGNORE_WHITESPACE
    ')'
);

// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// |
// |  Templates
// |
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
// ----------------------------------------------------------------------
template_type: constraint_type;
template_expression: constraint_expression;

// BugBug: template_statements
