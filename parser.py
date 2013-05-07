import ply.lex as lex
import ply.yacc as yacc

tokens = [
  # 'IDENTIFIER',
  'URL',
  'VALUE',
  # 'INTEGER',
  'EQUAL',
  'L2BRACE',
  'R2BRACE',
  'PIPE',
]

# tokens

# t_IDENTIFIER = r'[a-zA-Z][a-zA-Z0-9]*'
t_URL = r'http://[a-zA-Z0-9:/\.?_\-=&]+'
t_VALUE = r'[^|{}=\n\t]+'
t_EQUAL = r'='
t_L2BRACE = r'{{'
t_R2BRACE = r'}}'
t_PIPE = r'\|'
t_ignore = ' \t'

# def t_INTEGER(t):
#   r'\d+'
#   try:
#     t.value = int(t.value)
#   except ValueError:
#     print("Integer overflow: %d", t.value)
#     t.value = 0
#   return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

lexer = lex.lex()

# parsing rules

def p_error(e):
  print('error: %s'%e)

def p_object(p):
  'object : L2BRACE VALUE statement_list R2BRACE'
  p[0] = { p[2]: p[3] }

def p_statement_list(p):
  '''statement_list : statement
  | statement statement_list'''
  if len(p) == 2:
    p[0] = p[1]
  else:
    p[0] = dict(p[1].items() + p[2].items())

def p_statement(p):
  '''statement : assignment
  | expression'''
  p[0] = p[1]

def p_expression(p):
  'expression : PIPE VALUE'
  p[0] = { 'SINGLETON': p[2] }

def p_assignment(p):
  '''assignment : PIPE VALUE EQUAL URL
  | PIPE VALUE EQUAL VALUE
  | PIPE VALUE EQUAL
  | PIPE VALUE EQUAL object'''
  # | PIPE VALUE EQUAL INTEGER
  if len(p) == 5:
    if (isinstance(p[4], str)): p[4] = p[4].strip()
    p[0] = { p[2]: p[4] }
  else:
    p[0] = { p[2]: "" }

yaccer = yacc.yacc()