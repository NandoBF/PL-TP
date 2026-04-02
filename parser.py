import ply.yacc as yacc
from lexer import tokens

# arithmetic expression priority order
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_program(p):
    '''program : PROGRAM ID statements END'''
    p[0] = ('program', p[2], p[3])

def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]



    # '''statement : declaration
    #              | assignment
    #              | print_statement
    #              | read_statement
    #              | if_statement
    #              | goto_statement
    #              | do_loop
    #              | continue_statement'''
def p_statement(p):
    '''statement : declaration
                 | assignment
                 | if_statement'''
    p[0] = p[1]    

def p_var_dec(p):
    '''var_dec : ID
               | ID LPAREN NUMBER RPAREN'''
    if len(p) == 2:
        p[0] = ('var', p[1])
    else:
        p[0] = ('array', p[1], p[3])


# relational expressions
def p_expression_relational(p):
    '''expression : expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression'''
    p[0] = ('relop', p[2], p[1], p[3])



# binary (two sided) operations
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = ('binop', p[2], p[1], p[3])


# boolean logical operators
def p_expression_logical_binop(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = ('logop', p[2], p[1], p[3])


# NOT operator
def p_expression_logical_not(p):
    '''expression : NOT expression'''
    p[0] = ('not', p[2])



# literal booleans 
def p_expression_boolean(p):
    '''expression : TRUE
                  | FALSE'''
    if p[1].upper() == '.TRUE.':
        p[0] = ('bool', True)
    else:
        p[0] = ('bool', False)


def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN THEN statements ENDIF
                    | IF LPAREN expression RPAREN THEN statements ELSE statements ENDIF'''

    if len(p) == 8:
        p[0] = ('if', p[3], p[6], None)
    else:
        p[0] = ('if', p[3], p[6], p[8])

# parenthesis 
def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]


# basic expression for assignment
def p_expression_basic(p):
    '''expression : NUMBER
                  | ID'''
    if type(p[1]) == int:
        p[0] = ('num', p[1])
    else:
        p[0] = ('var_ref', p[1])

# decides wether we're assigning value to a simple variable or array
def p_assign_target(p):
    '''assign_target : ID
                     | ID LPAREN expression RPAREN'''
    if len(p) == 2:
        p[0] = ('var_ref', p[1])
    else:
        p[0] = ('array_ref', p[1], p[3])


def p_id_list(p):
    '''id_list : var_dec
               | id_list COMMA var_dec'''
    if len(p) == 2:
        # Just one ID
        p[0] = [p[1]]
    else:
        # more than 1 ID
        p[1].append(p[3])
        p[0] = p[1]

def p_type(p):
    '''type : INTEGER
            | REAL
            | LOGICAL'''
    p[0] = p[1]


# handles value assignment to variables/arrays
def p_assignment(p):
    '''assignment : assign_target EQUALS expression'''
    p[0] = ('assign', p[1], p[3])

# Handles arrays and normal variables
def p_declaration(p):
    '''declaration : type id_list'''
    p[0] = ('declare', p[1], p[2])


parser = yacc.yacc()
