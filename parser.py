import ply.yacc as yacc
from lexer import tokens

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
    '''statement : declaration'''
    p[0] = p[1]    

def p_var_dec(p):
    '''var_dec : ID
               | ID LPAREN NUMBER RPAREN'''
    if len(p) == 2:
        p[0] = ('var', p[1])
    else:
        p[0] = ('array', p[1], p[3])

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



# Handles arrays and normal variables
def p_declaration(p):
    '''declaration : type id_list'''
    p[0] = ('declare', p[1], p[2])


parser = yacc.yacc()
