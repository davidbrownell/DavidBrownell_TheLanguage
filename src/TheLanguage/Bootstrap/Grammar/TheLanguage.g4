// Note that this file will not work with ANTLR (as it has left-recursive definitions),
// but is rather a reference for implemtning the grammar in different languages.
grammar TheLanguage;

tokens { INDENT, DEDENT }

// BugBug:
// - We may need to move the location for attributes, as they are likley to be included for derived methods.
//   Make the location consistent across all phrases that use them.

// ----------------------------------------------------------------------
STANDARD_CASE_STRICT: [a-z][a-zA-Z0-9_]*;
STANDARD_CASE: '_'* STANDARD_CASE_STRICT '_'*;
STANDARD_CASE_WITH_EXCLAMATION: '_'* STANDARD_CASE_STRICT '!'? '_'*;

PASCAL_CASE_STRICT: [A-Z][a-zA-Z0-9_]*;
PASCAL_CASE: '_'* PASCAL_CASE_STRICT '_'*;
PASCAL_CASE_WITH_EXCLAMATION: '_'* PASCAL_CASE_STRICT '!'? '_'*;
PASCAL_CASE_WITH_QUESTION: '_'* PASCAL_CASE_STRICT '?'? '_'*;

PERFECT_FORWARD: '***';

NEWLINE: '\r'? '\n';

INT_LITERAL: [+-]? [0-9]+;
BOOL_LITERAL: 'True'|'False';
CHAR_LITERAL: '\'\\?.\'';
NUM_LITERAL: '-'? [0-9]* '.' [0-9]+;
STRING_LITERAL: '"' ('\\"' | '\\\\' | ~'"')*? '"';
NONE_LITERAL: 'None';

// ----------------------------------------------------------------------
// |  Names
module_name: PASCAL_CASE_STRICT;
type_name: PASCAL_CASE;
function_name: PASCAL_CASE_WITH_QUESTION;
parameter_name: STANDARD_CASE;
template_decl_parameter_name: PASCAL_CASE_WITH_EXCLAMATION;
constraint_parameter_name: STANDARD_CASE_WITH_EXCLAMATION;
variable_name: STANDARD_CASE;

// ----------------------------------------------------------------------
// |  Miscellaneous
class_modifier: 'immutable' | 'mutable';
method_modifier: 'abstract' | 'final' | 'override' | 'standard' | 'static' | 'virtual';
parameters_indicator: 'pos' | 'any' | 'key';
type_modifier: 'mutable' | 'immutable' | 'isolated' | 'shared' | 'var' | 'ref' | 'val' | 'view';
visibility_modifier: 'public' | 'protected' | 'private';

// ----------------------------------------------------------------------
// |  Attributes
attributes: '[' attributes_list ']';
attributes_list: attributes_list_item (',' attributes_list_item)* ','?;
attributes_list_item: function_name function_arguments?;

// ----------------------------------------------------------------------
// |  Captured Variables
captured_variables: '|' captured_variables_list '|';
captured_variables_list: captured_variables_list_item (',' captured_variables_list_item)* ','?;
captured_variables_list_item: variable_name;

// ----------------------------------------------------------------------
// |  Constraint Arguments
constraint_arguments: '{' constraint_arguments_list '}';
constraint_arguments_list: constraint_arguments_list_item (',' constraint_arguments_list_item)* ','?;
constraint_arguments_list_item: (constraint_parameter_name '=')? constraint_expression;

// ----------------------------------------------------------------------
// |  Constraint Parameters
constraint_parameters: '{' (constraint_parameters_new_list | constraint_parameters_traditional_list) '}';

constraint_parameters_new_list: (parameters_indicator ':' constraint_parameters_list_item (',' constraint_parameters_list_item)* ','?)+;
constraint_parameters_traditional_list: constraint_parameters_traditional_list_item (',' constraint_parameters_traditional_list_item)* ','?;
constraint_parameters_traditional_list_item: '*' | '/' | constraint_parameters_list_item;

constraint_parameters_list_item: constraint_type constraint_parameter_name ('=' constraint_expression)?;

// ----------------------------------------------------------------------
// |  Function Arguments
function_arguments: '(' (PERFECT_FORWARD | function_arguments_list)? ')';
function_arguments_list: function_arguments_list_item (',' function_arguments_list_item)* ','?;
function_arguments_list_item: (parameter_name '=')? standard_expression;

// ----------------------------------------------------------------------
// |  Function Parameters
function_parameters: '(' (PERFECT_FORWARD | function_parameters_new_list | function_parameters_traditional_list)? ')';

function_parameters_new_list: (parameters_indicator ':' function_parameters_list_item (',' function_parameters_list_item)* ','?)+;
function_parameters_traditional_list: function_parameters_traditional_list_item (',' function_parameters_traditional_list_item)* ','?;
function_parameters_traditional_list_item: '*' | '/' | function_parameters_list_item;

function_parameters_list_item: standard_type /*type_modifier is required*/ '*'? parameter_name ('=' standard_expression)?;

// ----------------------------------------------------------------------
// |  Scoped Statements
scoped_statements: scoped_statements_single_line | scoped_statements_multiple_lines;
scoped_statements_single_line: ':' standard_statement;
scoped_statements_multiple_lines: ':' NEWLINE INDENT standard_statement+ DEDENT;

// ----------------------------------------------------------------------
// |  Template Arguments
template_arguments: '<' template_arguments_list '>';
template_arguments_list: template_arguments_list_item (',' template_arguments_list_item)* ','?;
template_arguments_list_item: (
    ((type_name '=')? standard_type /*type_modifier must be None*/)
    | ((template_decl_parameter_name '=')? template_decl_expression)
);

// ----------------------------------------------------------------------
// |  Template Parameters
template_parameters: '<' (template_parameters_new_list | template_parameters_traditional_list) '>';

template_parameters_new_list: (parameters_indicator ':' template_parameters_list_item (',' template_parameters_list_item)* ','?)+;
template_parameters_traditional_list: template_parameters_traditional_list_item (',' template_parameters_traditional_list_item) ','?;
template_parameters_traditional_list_item: '*' | '/' | template_parameters_list_item;

template_parameters_list_item: (
    (type_name '*'? ('=' standard_type /*type_modifier must be None*/)?)
    | (template_decl_type template_decl_parameter_name ('=' template_decl_expression)?)
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
// |  Types
// |
// ----------------------------------------------------------------------
standard_type: standard_type_item type_modifier?;

standard_type_item: (
    standard_type_primitive
    | standard_type_tuple
    | standard_type_variant
    | standard_type_func
);

standard_type_primitive: type_name template_arguments? constraint_arguments?;

standard_type_tuple: (
    '('
    (standard_type_tuple_single | standard_type_tuple_multiple)
    ')'
);

standard_type_tuple_single: standard_type_item ',';
standard_type_tuple_multiple: standard_type_item (',' standard_type_item)+ ','?;

standard_type_variant: (
    '('
    standard_type_item
    ('|' standard_type_item)*
    '|'
    standard_type_item
    ')'
);

standard_type_func: (
    '('
    standard_type /*type_modifier is required*/
    function_parameters
    ')'
);

// ----------------------------------------------------------------------
// |
// |  Statements
// |
// ----------------------------------------------------------------------
standard_statement: (
    assert_statement
    | binary_statement
    | break_statement
    | class_statement
    | class_statement_member
    | continue_statement
    | delete_statement
    | docstring_statement
    | for_statement
    | func_definition_statement
    | if_statement
    | import_statement
    | pass_statement
    | raise_statement
    | return_statement
    | scoped_ref_statement
    | try_statement
    | using_statement
    | variable_declaration_statement
    | while_statement
    | yield_statement
);

// ----------------------------------------------------------------------
assert_statement: (
    'assert'
    standard_expression
    (',' standard_expression)?
    NEWLINE
);

// ----------------------------------------------------------------------
binary_statement: (
    standard_name
    (
        '+=' | '-=' | '*=' | '**=' | '/=' | '//=' | '%=' |
        '<<=' | '>>=' | '^=' | '&=' | '|='
    )
    standard_expression
    NEWLINE
);

// ----------------------------------------------------------------------
break_statement: 'break' NEWLINE;

// ----------------------------------------------------------------------
class_statement: (
    attributes?
    visibility_modifier?
    class_modifier?
    ('class' | 'enum' | 'exception' | 'interface' | 'mixin' | 'struct' | 'trait')
    type_name
    template_parameters?
    constraint_parameters?
    class_statement_dependency*
    scoped_statements
);

class_statement_dependency: (
    ('extends' | 'implements' | 'uses')
    (
        ('(' class_statement_dependency_list ')')
        | class_statement_dependency_list
    )
);

class_statement_dependency_list: class_statement_dependency_list_item (',' class_statement_dependency_list_item)* ','?;
class_statement_dependency_list_item: visibility_modifier? standard_type_primitive;

// ----------------------------------------------------------------------
class_statement_member: (
    attributes?
    visibility_modifier?
    standard_type /*type_modifier is required*/
    variable_name
    ('=' standard_expression)?
    NEWLINE
);

// ----------------------------------------------------------------------
continue_statement: 'continue' NEWLINE;

// ----------------------------------------------------------------------
delete_statement: 'delete' variable_name (',' variable_name)* ','? NEWLINE;

// ----------------------------------------------------------------------
docstring_statement: '<<<' .*? '>>>' NEWLINE;

// ----------------------------------------------------------------------
for_statement: (
    'for'
    standard_name
    'in'
    standard_expression
    scoped_statements
);

// ----------------------------------------------------------------------
func_definition_statement: (
    attributes?
    visibility_modifier?
    method_modifier?
    class_modifier?
    standard_type /*type_modifier is required*/
    function_name
    template_parameters?
    captured_variables?
    function_parameters
    (scoped_statements | NEWLINE)
);

// ----------------------------------------------------------------------
if_statement: (
    'if' standard_expression scoped_statements
    ('elif' standard_expression scoped_statements)*
    ('else' scoped_statements)?
);

// ----------------------------------------------------------------------
import_statement: (
    'from'
    module_name ('.' module_name)*
    'import'
    (
        ('(' import_statement_list ')')
        | import_statement_list
    )
    NEWLINE
);

import_statement_list: import_statement_list_item (',' import_statement_list_item)* ','?;
import_statement_list_item: import_statement_list_item_name ('as' import_statement_list_item_name)?;
import_statement_list_item_name: module_name | type_name | function_name;

// ----------------------------------------------------------------------
pass_statement: 'pass' NEWLINE;

// ----------------------------------------------------------------------
raise_statement: 'raise' standard_expression? NEWLINE;

// ----------------------------------------------------------------------
return_statement: 'return' standard_expression? NEWLINE;

// ----------------------------------------------------------------------
scoped_ref_statement: (
    'with'
    (
        ('(' scoped_ref_statement_list ')')
        | scoped_ref_statement_list
    )
    'as'
    'ref'
    scoped_statements
);

scoped_ref_statement_list: scoped_ref_statement_list_item (',' scoped_ref_statement_list_item)* ','?;
scoped_ref_statement_list_item: variable_name;

// ----------------------------------------------------------------------
try_statement: (
    'try'
    scoped_statements

    // One of the following is required
    (
        'except'
        standard_type_item
        variable_name?
        scoped_statements
    )*
    (
        'except'
        scoped_statements
    )?
);

// ----------------------------------------------------------------------
using_statement: (
    visibility_modifier?
    'using'
    type_name
    '='
    standard_type_item
    NEWLINE
);

// ----------------------------------------------------------------------
// BugBug: once?
variable_declaration_statement: (
    type_modifier?
    standard_name
    '='
    standard_expression
    NEWLINE
);

// ----------------------------------------------------------------------
while_statement: (
    'while'
    standard_expression
    scoped_statements
);

// ----------------------------------------------------------------------
yield_statement: 'yield' ('from'? standard_expression)? NEWLINE;


// ----------------------------------------------------------------------
// |
// |  Expressions
// |
// ----------------------------------------------------------------------
standard_expression: (
    binary_expression
    | bool_literal_expression
    | cast_expression
    | char_literal_expression
    | func_invocation_expression
    | generator_expression
    | generic_name_expression
    | group_expression
    | index_expression
    | int_literal_expression
    | lambda_expression
    | match_type_expression
    | match_value_expression
    | none_literal_expression
    | num_literal_expression
    | string_literal_expression
    | ternay_expression
    | tuple_expression
    | unary_expression
);

// ----------------------------------------------------------------------
binary_expression: (
    standard_expression
    (
        'and' | 'or' | 'in' | 'not in' | 'is' |
        '.' | '->' | '::' |
        '<' | '<=' | '>' | '>=' | '==' | '!=' |
        '+' | '-' | '*' | '**' | '/' | '//' | '%' |
        '<<' | '>>' | '^' | '&' | '|'
    )
    standard_expression
);

// ----------------------------------------------------------------------
bool_literal_expression: BOOL_LITERAL;

// ----------------------------------------------------------------------
cast_expression: (
    standard_expression
    'as'
    (type_modifier | (standard_type /*type_modifier is optional*/))
);

// ----------------------------------------------------------------------
char_literal_expression: CHAR_LITERAL;

// ----------------------------------------------------------------------
func_invocation_expression: (
    standard_expression
    template_arguments?
    function_arguments
);

// ----------------------------------------------------------------------
generator_expression: (
    standard_expression
    'for'
    standard_name
    'in'
    standard_expression
    ('if' standard_expression)?
);

// ----------------------------------------------------------------------
generic_name_expression: standard_type_primitive | variable_name;

// ----------------------------------------------------------------------
group_expression: '(' standard_expression ')';

// ----------------------------------------------------------------------
index_expression: (
    standard_expression
    '['
    standard_expression
    ']'
);

// ----------------------------------------------------------------------
int_literal_expression: INT_LITERAL;

// ----------------------------------------------------------------------
lambda_expression: (
    'lambda'
    captured_variables?
    function_parameters
    ':'
    standard_expression
);

// ----------------------------------------------------------------------
match_type_expression: 'BugBug';

// ----------------------------------------------------------------------
match_value_expression: 'BugBug';

// ----------------------------------------------------------------------
none_literal_expression: NONE_LITERAL;

// ----------------------------------------------------------------------
num_literal_expression: NUM_LITERAL;

// ----------------------------------------------------------------------
string_literal_expression: STRING_LITERAL;

// ----------------------------------------------------------------------
ternay_expression: (
    standard_expression
    'if'
    standard_expression
    'else'
    standard_expression
);

// ----------------------------------------------------------------------
tuple_expression: (
    '('
    (tuple_expression_single | tuple_expression_multiple)
    ')'
);

tuple_expression_single: standard_expression ',';
tuple_expression_multiple: standard_expression (',' standard_expression)+ ','?;

// ----------------------------------------------------------------------
unary_expression: (
    (
        'await' |
        'copy' | 'final' | 'move' |
        'not' |
        '+' | '-' |
        '~'
    )
    standard_expression
);

// ----------------------------------------------------------------------
// |
// |  Constraint Types
// |
// ----------------------------------------------------------------------
constraint_type: (
    'Bool'
    | 'Char'
    | 'Int'
    | 'Num'
    | 'String'
    | constraint_type_variant
);

constraint_type_variant: (
    '('
    constraint_type_variant_item
    ('|' constraint_type_variant_item)*
    '|'
    constraint_type_variant_item
    ')'
);

constraint_type_variant_item: constraint_type | 'None';

// ----------------------------------------------------------------------
// |
// |  Constraint Expressions
// |
// ----------------------------------------------------------------------
constraint_expression: (
    constraint_expression_bool
    | constraint_expression_char
    | constraint_expression_int
    | constraint_expression_num
    | constraint_expression_str
);

// ----------------------------------------------------------------------
constraint_expression_bool: BOOL_LITERAL;

// ----------------------------------------------------------------------
constraint_expression_char: CHAR_LITERAL;

// ----------------------------------------------------------------------
constraint_expression_int: INT_LITERAL;

// ----------------------------------------------------------------------
constraint_expression_num: NUM_LITERAL;

// ----------------------------------------------------------------------
constraint_expression_str: STRING_LITERAL;

// ----------------------------------------------------------------------
// |
// |  Template Decl Types
// |
// ----------------------------------------------------------------------
template_decl_type: constraint_type;

// ----------------------------------------------------------------------
// |
// |  Template Decl Expressions
// |
// ----------------------------------------------------------------------
template_decl_expression: constraint_expression;
