# -*- coding: utf-8 -*-
"""
Created on Tue May 16 19:40:30 2017

@author: François
"""

## lexeur
import ply.lex as lex

mots_clefs = {'if': 'IF', 'while': 'WHILE', 'main': 'MAIN', 'return': 'RETURN', 'print': 'PRINT'}
tokens = ['NUMBER', 'ID', 'OPBIN', 'LPAREN', 'RPAREN', 'LACO', 'RACO', 'END', 'AFFECT', 'COMMA', 'FINISH'] + list(mots_clefs.values())

#t_NUMBER = r"\d+"
#t_PLUS = r"\+"
#t_MOINS = r"\-"
#t_ID = r"[a-zA-Z_]+"
#t_IF = r"if" #pas prioritaire

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LACO = r'\{'
t_RACO = r'\}'
t_COMMA = r','

def t_END(t):
    r';+'
    if t.value == ";;":
        t.type = "FINISH"
    return t

def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t

def t_newline(t):
    r"\n"
    t.lexer.lineno = t.lexer.lineno + 1

def t_OPBIN(t):
    r"[\+\-\*\=\<\>\!\/]+"
    if t.value == "=":
        t.type = "AFFECT"
    return t
#def t_IF(t):
#    # prioritaire sur les expressions régulières
#    r"if"
#    return t
# pb aucune variable ne peut commencer par if

def t_ID(t):
    r"[a-zA-Z]+"
    if t.value in mots_clefs.keys():
        t.type = mots_clefs[t.value]
    return t

def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

t_ignore = " \t"
lexer = lex.lex()

lexer.input(
"""
main(X) {Y = 200; X = 100; print(Y)}
"""
)

while True:
    tok = lexer.token()
    if tok:
        print(tok)
    else:
        break

## parseur
import ply.yacc as yacc # lexer nécessaire
import ASTree

def p_programme(p):
    '''programme : MAIN LPAREN enum RPAREN LACO commande FINISH PRINT LPAREN expression RPAREN RACO
    '''
    try:
        p[0] = ASTree.AST("programme","main", "programme")
        p[0].sons = [p[3], p[6], p[10]]
    except:
        pass
 
def p_enum(p):
    '''enum : ID
              | ID COMMA enum
    '''
    if len(p) == 4:
        p[0] = p[3]
        p[0].insert(0, p[1])
    else:
        p[0] = [p[1]]

def p_empty(p):
    '''empty :'''

def p_commande(p):
    '''commande : ID AFFECT expression
                  | commande END commande
                  | WHILE LPAREN expression RPAREN LACO commande RACO'''
    try: 
        if len(p) == 8:
            p[0] = ASTree.AST("commande", "while", "commande")
            p[0].sons = [p[3], p[6]]
        else:
            if p[2] == "=":
                p[0] = ASTree.AST("AFFECT", "=", "commande")
                p[0].sons = [p[1], p[3]]
            else:
                p[0] = ASTree.AST("END", ";", "commande")
                p[0].sons =[p[1], p[3]]
    except:
        pass

def p_expression(p):
    '''expression :  NUMBER
                    | ID
                    | expression OPBIN expression'''
    try:
        if len(p) > 2:
            p[0] = ASTree.AST("OPBIN", p[2], "expression")
            p[0].sons = [p[1], p[3]]
            
        else:
            if type(p[1]) == str:
                p[0] = ASTree.AST("ID", p[1], "expression")
            else:
                p[0] = ASTree.AST("NUMBER", p[1], "expression")
    except:
        pass

def p_error(p):
    print("erreur : " + str(p))

start = 'programme'
parser = yacc.yacc()

#Arbre = yacc.parse("main(x,y,z,t) {while(48 == 48){a = 2 * 3 + 4; b = 5 + 6; a = b + 2};; print(3+4)}")
#print(Arbre)
#Arbre = yacc.parse("x = 5; x=x+1; y = 6; y = 4; z = 3; while(x){z = 8; y = 4 ;z = x + 5;  y = z + x; x = 3; x = 4; x = y + 7}; z=10")
#Arbre = yacc.parse("t=3; y=t; x=y; z=x")

#Arbre = yacc.parse("x=3; y = 3; while(x){y = y + 1}; z=z-1")
print(yacc.parse("""
main(x,y,z) 
{
	t = x + y + z;
    a = 0;
    while(t)
    {
    	t = t - 1;
        a = t + a
    };;
    print(a)
}"""))

print(Arbre)
Arbre = Arbre.simplifyID()
print(Arbre)
Arbre.simplifyExpression()
print(Arbre)
Arbre = Arbre.simplifyID()
print(Arbre)
Arbre = Arbre.simplifyID()
print(Arbre)
Arbre.simplifyofdoom()
print(Arbre)

#arbre = yacc.parse("main(X) {while(X) {Y=Y+1; X=X-1}; t = 3;; print(Y)}")

#print(arbre.p_toASM())