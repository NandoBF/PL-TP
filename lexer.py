import ply.lex as lex


reserved = {
    'PROGRAM': 'PROGRAM',
    'INTEGER': 'INTEGER',
    'REAL': 'REAL',
    'LOGICAL': 'LOGICAL',
    'IF': 'IF',
    'THEN': 'THEN',
    'ELSE': 'ELSE',
    'ENDIF': 'ENDIF',
    'DO': 'DO',
    'GOTO': 'GOTO',
    'CONTINUE': 'CONTINUE',
    'PRINT': 'PRINT',
    'READ': 'READ',
    'END': 'END',
    'FUNCTION': 'FUNCTION',
    'RETURN': 'RETURN'
}

tokens_relational = ['EQ', 'NE', 'LT', 'LE', 'GT', 'GE']
tokens_logics = ['AND', 'OR', 'NOT', 'TRUE', 'FALSE']

tokens = [
    'ID', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'LPAREN', 'RPAREN', 'COMMA', 'STRING' 
] + tokens_relational + tokens_logics + list(reserved.values())

t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EQUALS    = r'='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r','
t_EQ        = r'\.EQ\.'
t_NE        = r'\.NE\.'
t_LT        = r'\.LT\.'
t_LE        = r'\.LE\.'
t_GT        = r'\.GT\.'
t_GE        = r'\.GE\.'
t_AND       = r'\.AND\.'
t_OR        = r'\.OR\.'
t_NOT       = r'\.NOT\.'
t_TRUE      = r'\.TRUE\.'
t_FALSE     = r'\.FALSE\.'
t_ignore    = ' \t'


def t_STRING(t):
    r"'[^']*'"
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.upper(), 'ID')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Ilegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()



