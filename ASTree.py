# -*- coding: utf-8 -*-
"""
Created on Wed May 17 08:11:17 2017

@author: François


"""
from ete3 import TreeNode

class AST:
    
    idWhile = 0
    
    def __init__(self, _type, _value, _nature):
        self.nature = _nature
        self.type = _type
        self.value = _value
        self.sons = []
        self.mag = {}
        
    def __str__(self):
        
        if self.nature == "expression":
            return self.e_toArbre().get_ascii(attributes=["name"])
            
        elif self.nature == "commande":
            return self.c_toArbre().get_ascii(attributes=["name"])
            
        else :
            return self.p_toArbre().get_ascii(attributes=["name"])
        
    def __repr__(self):
        if self.nature == "expression":
            return self.e_toArbre().get_ascii(attributes=["name"])
            
        elif self.nature == "commande":
            return self.c_toArbre().get_ascii(attributes=["name"])
            
        else :
            return self.p_toArbre().get_ascii(attributes=["name"])
    
    def e_toASM(self):
        
        if self.type == "NUMBER":
            return "mov eax, %s\n" % self.value
            
        elif self.type == "ID":
            return "mov eax, [%s]\n" % self.value
            
        elif self.type == "OPBIN":
            op1 = self.sons[0].e_toASM()
            op2 = self.sons[1].e_toASM()
            
            if self.value == '+':
                res = "%spush eax\n%spop ebx\nadd eax, ebx\n" % (op1, op2)
            else:
                res = "%spush eax\n%spop ebx\nsub eax, ebx\n" % (op2, op1)
            return res
    
    def c_toASM(self):
        
        if self.value == "=":
            return "%s\nmov[%s], eax" % (self.sons[1].e_toASM(), self.sons[0])
        
        elif self.value == ';':
            return"%s\n%s" % (self.sons[0].c_toASM(), self.sons[1].c_toASM())
            
        else:
            AST.idWhile += 1
            return """debutboucle%s:
%s
cmp eax, 0
jz finboucle%s
%s
jmp debutboucle%s
finboucle%s:
""" % (AST.idWhile, self.sons[0].e_toASM(), AST.idWhile, self.sons[1].c_toASM(), AST.idWhile, AST.idWhile)


    def fvars(self):
        var = set()
        if self.type == "programme":
            var.update(self.sons[0])
            var.update(self.sons[1].fvars())
            var.update(self.sons[2].fvars())
            return var
        
        elif self.type == "AFFECT":
            var.add(self.sons[0])
            var.update(self.sons[1].fvars())
            return var
            
        elif self.value == "while":
            var.update(self.sons[0].fvars())
            var.update(self.sons[1].fvars())
            return var
    
        elif self.type == "END":
            var.update(self.sons[0].fvars())
            var.update(self.sons[1].fvars())
            return var
            
        elif self.type == "OPBIN":
            var.update(self.sons[0].fvars())
            var.update(self.sons[1].fvars())
            return var
            
        elif self.type == "NUMBER":
            return var
            
        else:
            var.add(self.value)
            return var
            
            
    def init_var(self, var, i):
        return """mov ebx, [eax + %s]
push eax
push ebx
call atoi
add esp, 4
mov [%s], eax
pop eax
""" % (str(4*(i+1)), var)
        
    def init_vars(self, motif):
        motif = motif.replace("LEN_INPUT", str(len(self.sons[0])))
        init = [self.init_var(self.sons[0][i], i) for i in range(len(self.sons[0]))]
        motif = motif.replace("VAR_INIT", "\n".join(init))
        return motif
            
    def p_toASM(self):
        ## Ouverture Lecture
        f = open("motif.asm")
        motif = f.read()
        
        ## Création liste variable
        var = self.fvars()
        dvar = {"%s: dd 0" % v for v in var}
        var_decl = "\n".join(dvar)
        motif = motif.replace("VAR_DECL", var_decl)
        motif = self.init_vars(motif)
        
        ## Commande
        motif = motif.replace("COMMAND_EXEC", self.sons[1].c_toASM())
        
        ## Evaluation
        motif = motif.replace("EVAL_OUTPUT", self.sons[2].e_toASM())
        
        g = open("motifrempli.asm", "w")
        g.write(motif)
        
        
        return motif
        
    def e_toArbre(self):
        
        if self.type == "NUMBER":
            n = TreeNode()
            n.name = "Number : " + str(self.value)
            return n
            
        elif self.type == "ID":
            n = TreeNode()
            n.name = "Id : " + self.value
            return n
            
        elif self.type == "OPBIN":
            n = TreeNode()
            n.name = self.value
            n1 = self.sons[0].e_toArbre()
            n2 = self.sons[1].e_toArbre()
            n.add_child(n1)
            n.add_child(n2)
            
            return n
        
    def c_toArbre(self):

        if self.value == "=":
            n = TreeNode()
            n.name = self.value
            
            n1 = TreeNode()
            n1.name = "Id : " + self.sons[0]
            n2 = self.sons[1].e_toArbre()
            n.add_child(n1)
            n.add_child(n2)
            
            return n
        
        elif self.value == ';':
            n = TreeNode()
            n.name = self.value
            
            n1 = self.sons[0].c_toArbre()
            n2 = self.sons[1].c_toArbre()
            n.add_child(n1)
            n.add_child(n2)
            
            return n
            
        else:
            n = TreeNode()
            n.name = self.value
            
            n1 = self.sons[0].e_toArbre()
            n2 = self.sons[1].c_toArbre()
            n.add_child(n1)
            n.add_child(n2)
            
            return n
        
    def p_toArbre(self):
        
        n = TreeNode()
        n.name = "main()"
        
        n1 = TreeNode()
        n1.name = str(self.sons[0])
        
        n2= self.sons[1].c_toArbre()
        
        n3 = self.sons[2].e_toArbre()
        
        n.add_child(n1)
        n.add_child(n2)
        n.add_child(n3)
        
        return n
        
    def simplifyID_aux(self, i, useful, useless, path):
        j = 0
        for son in self.sons:
            if type(son) == str:
                ind = AST.isInList(useful, son)
                if ind >= 0:
                    useless.append(useful[ind])
                    useful.remove(useful[ind]) 
                useful.append([son, i, path + str(j), self, False])
            elif son.value == "while":
                son.simplifyWhile()
                useful.append(['while', i, path + str(j), son, True])
            else:
                if son.type == "AFFECT":
                    s = son.sons[1].reconstitueExpression()
                    for x in useful:
                        if x[0] in s and not x[4]:
                            x[4] = True
                            indic = s.index(x[0])
                            s = s[:indic] + s[indic+1:]
                son.simplifyID_aux(i + 1, useful, useless, path + str(j))
            j += 1
            
    def isInList(useful, item):
        for i in range(len(useful)):
            if not useful[i][4] and item == useful[i][0]:
                return i
        return -1

    def simplifyID(self):
        useful = []
        useless = []
        self.simplifyID_aux(0, useful, useless, "")
        tree = AST("END", ";", "commande")
        treeson = tree
        for x in useful:
            if type(x[3].sons[0]) != str and x[3].sons[0].value == "toremove":
                useful.remove(x)
        for i in range(len(useful)):
            while len(treeson.sons) > 1:
                treeson =  treeson.sons[1]
            if i + 2 < len(useful):
                treeson.sons.append(useful[i][3])
                treeson.sons.append(AST("END", ";", "commande"))
            else:
                treeson.sons.append(useful[i][3])

        return tree
        
    def simplifyExpression_aux(self, affect):
        if self.value == "while":
            self.mag = dict(affect)
        for son in self.sons:
            if son.type == "AFFECT":
                affect[son.sons[0]] = son.sons[1].calculeExpression(affect)
                if type(affect[son.sons[0]]) in [int, float]:
                    son.sons[1] = AST("NUMBER", affect[son.sons[0]], "expression")
            else:
                son.simplifyExpression_aux(affect)

    def simplifyExpression(self):
        affect = {}
        self.simplifyExpression_aux(affect)
        
    def simplifyWhile(self, ful = [], less = []):
        if self.value == "while":
            self.sons[1] = self.sons[1].simplifyID()
            e = self.sons[0].calculeExpression(self.mag)
            if e == 0:
                self.sons[0] = AST("NUMBER", "toremove", "remove")

    def reconstitueExpression(self):
        if self.nature == "expression":
            if self.type == "OPBIN":
                return self.sons[0].reconstitueExpression() + " " + self.value + " " + self.sons[1].reconstitueExpression()
            else:
                return str(self.value)
                
    def reconstitueCommande(self):
        if self.type == "AFFECT":
            return self.sons[0] + " = " + self.sons[1].reconstitueExpression()
        elif self.value == ";":
            return self.sons[0].reconstitueCommande() + "; " + self.sons[1].reconstitueCommande()
        else:
            return "while(" + self.sons[0].reconstitueExpression() + ")" + " { " + self.sons[1].reconstitueCommande() + " }"

    def calculeExpression(self, dic):
        if self.type == "OPBIN":
            if self.value == "+":
                return self.sons[0].calculeExpression(dic) + self.sons[1].calculeExpression(dic)
            elif self.value == "-":
                return self.sons[0].calculeExpression(dic) - self.sons[1].calculeExpression(dic)
            elif self.value == "/":
                return self.sons[0].calculeExpression(dic) / self.sons[1].calculeExpression(dic)
            elif self.value == "*":
                return self.sons[0].calculeExpression(dic) + self.sons[1].calculeExpression(dic)
            else:
                return "Not known opbin"
        elif self.type == "ID":
            if self.value in dic.keys():
                return dic[self.value]
            else:
                return "do not change"
        else:
            return self.value