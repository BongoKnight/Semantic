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
        try :
            if self.nature == "expression":
                return self.e_toArbre().get_ascii(attributes=["name"])
                
            elif self.nature == "commande":
                return self.c_toArbre().get_ascii(attributes=["name"])
                
            else :
                return self.p_toArbre().get_ascii(attributes=["name"])
        except :
            return str(self.value) + str(self.sons)
        
    def __repr__(self):
        try :
            if self.nature == "expression":
                return self.e_toArbre().get_ascii(attributes=["name"])
                
            elif self.nature == "commande":
                return self.c_toArbre().get_ascii(attributes=["name"])
                
            else :
                return self.p_toArbre().get_ascii(attributes=["name"])
        except :
            return str(self.value) + str(self.sons)
    
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
        AST.idWhile = 0
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
        ## useful est une liste de liste contenant : le nom de la variable, le niveau dans l'arbre, le chemin jusqu'à lui, l'arbre
        ##      un booléen disant si la variable a servi dans une affectation
        
        ## useless ne sert pas dans le programme, on le laisse pour une éventuelle utilité.
        j = 0
        for son in self.sons:
            ## parcourt les fils
            if type(son) == str: ## si le fils est de type str alors c'est un ID (du fait de la construction de l'arbre)
                ind = AST.isInList(useful, son) ## on regarde l'indice de la variable dans la liste, dans les éléments n'ayant pas été affectés jusqu'ici
                if ind >= 0: ## si la variable est dans la liste
                    useless.append(useful[ind])
                    useful.remove(useful[ind])  ## on retire de la liste la variable homonyme qui n'a pas servi dans une affectation
                useful.append([son, i, path + str(j), self, False])
            elif son.value == "while":
                son.simplifyWhile() ## Simplification du while
                useful.append(['while', i, path + str(j), son, True]) ## on noté qu'un while sert toujours sauf exception sur l'expression et sera remis
            else:
                if son.type == "AFFECT":
                    ## On reconstitue l'affectation en string et on observe si 
                    ## pour les variables pour lesquelles on n'a pas trouvé d'affectation utile
                    ## elles apparaissent dans l'affectation 
                    s = son.sons[1].reconstitueExpression()
                    for x in useful:
                        if x[0] in s and not x[4]:
                            x[4] = True
                            indic = s.index(x[0])
                            s = s[:indic] + s[indic+1:]
                son.simplifyID_aux(i + 1, useful, useless, path + str(j))
                ## on simplifie sur le fils récursivement
            j += 1
            
    def isInList(useful, item):
        ## Retourne l'emplacement de la variable item dans la liste des éléments utiles
        ## En ne regardant seulement les éléments pour lesquelles on n'a pas vérifié s'ils ont auparavant servi dans une affectation.
        for i in range(len(useful)):
            if not useful[i][4] and item == useful[i][0]:
                return i
        return -1

    def simplifyID(self):
        useful = []
        useless = []
        self.simplifyID_aux(0, useful, useless, "")
        tree = AST("END", ";", "commande")  ## on crée le nouvelle arbre débutant comme une commande
        treeson = tree
        for x in useful:
            ## Retrait des while inutiles (d'expressioin évaluée à zéros)
            if type(x[3].sons[0]) != str and x[3].sons[0].value == "toremove":
                useful.remove(x)
        if len(useful) == 1:
            tree = useful[0][3] ## si le programme ne contient plus qu'une affectation utile, alors on retourne l'affectation agissant comme commande
        else:
            for i in range(len(useful)):
                # on parcourt la liste des affectations utiles
                while len(treeson.sons) > 1: ## on cherche l'emplacement de la nouvelle affectation
                    treeson =  treeson.sons[1]
                if i + 2 < len(useful):
                    treeson.sons.append(useful[i][3])
                    treeson.sons.append(AST("END", ";", "commande"))
                else:
                    treeson.sons.append(useful[i][3])

        return tree
        
    def simplifyExpression_aux(self, affect):
        if self.value == "while":
            ## On retient l'état du magasin à l'entrée de la boucle while
            ## pour qu'on puisse calculer l'expression au moment de la boucle
            ## cela sert pour la simplification des while.
            self.mag = dict(affect)
        elif self.value == ";":
            for son in self.sons:
                if son.type == "AFFECT":
                    ## on calcule l'expression et on la range dans le dictionnaire
                    affect[son.sons[0]] = son.sons[1].calculeExpression(affect)
                    if type(affect[son.sons[0]]) in [int, float]:
                        ## si l'expression est de type int, ou float
                        ## on la range dans le magasin.
                        son.sons[1] = AST("NUMBER", affect[son.sons[0]], "expression")
                else:
                    son.simplifyExpression_aux(affect)
        elif self.value == "AFFECT":
            ## Si c'est une affectation, on calcule l'expression
            ## on fait cela dans le cas où la commande se résume à une affectation (dans un while par ex).
            affect[son.sons[0]] = son.sons[1].calculeExpression(affect)
            if type(affect[son.sons[0]]) in [int, float]:
                son.sons[1] = AST("NUMBER", affect[son.sons[0]], "expression")

    def simplifyExpression(self):
        affect = {}
        self.simplifyExpression_aux(affect)
        
    def simplifyWhile(self, ful = [], less = []):
        if self.value == "while":
            ## Simplification du programme interne
            ## cela se fait sur de nouvelles listes useful et useless,
            ## pour ne pas que des simplifications du bloc principal
            ## viennent altérer le bloc while.
            self.sons[1] = self.sons[1].simplifyID()
            
            ## Simplification des expressions dans la boucle,
            ## en prenant un nouveau magasin, pour les mêmes raisons.
            self.sons[1].simplifyExpression()
            
            ## calcul de l'expression sur le bon magasin
            e = self.sons[0].calculeExpression(self.mag)
            if e == 0:
            ## si l'expression est nulle, alors on doit retirer la boucle
            ## on note la valeur de l'expression à 'toremove', de sorte 
            ## qu'elle ne soit pas remise dans l'arbre lors du
            ## simplifyID suivant
                self.sons[0] = AST("NUMBER", "toremove", "remove")

    def reconstitueExpression(self):
        """
        Sous forme de chaine de caractère recopie l'expression associé à self.
        """
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
            x = self.sons[0].calculeExpression(dic)
            y = self.sons[1].calculeExpression(dic)
            if type(x) in [int, float] and type(y) in [int, float]:
                if self.value == "+":
                    return x + y 
                elif self.value == "-":
                    return x - y
                elif self.value == "/":
                    return x / y
                elif self.value == "*":
                    return x * y
                else:
                    return "Not known opbin"
            else:
                return "Id in expression"
        elif self.type == "ID":
            if self.value in dic.keys():
                return dic[self.value]
            else:
                return self.value
        else:
            return self.value

    def makeBlock_aux(self,listBlock,idBlock, idParent, pere):
        ## On parcourt récursivement, lorsqu'on rencontre un
        ## nouveau bloc on ajoute à la liste une liste contenant les blocs.
        if self.value == ";":
            ## Si on est dans un nouveau bloc on le rajoute
            if not len(listBlock)>idBlock:
                listBlock.append([idParent])
            if self.sons[1].value!=";":
                    # cas d'une commande finale
                    if self.sons[1].value=="=" and self.sons[0].value=="=":
                        listBlock[idBlock].append([self.sons[0], pere, self])
                        listBlock[idBlock].append([self.sons[1], pere, self])
                    if self.sons[0].value=="while" and self.sons[1].value=="=":
                        if not len(listBlock)>idBlock:
                            listBlock.append([])
                        listBlock[idBlock].append([self.sons[1], pere, self])
                        self.sons[0].sons[1].makeBlock_aux(listBlock,len(listBlock), idBlock, self)
                    elif self.sons[1].value=="while" and self.sons[0].value=="=":
                        if not len(listBlock)>idBlock:
                            listBlock.append([])
                        listBlock[idBlock].append([self.sons[0], pere, self])
                        self.sons[1].sons[1].makeBlock_aux(listBlock,len(listBlock), idBlock, self)
                    else:
                        self.sons[0].sons[1].makeBlock_aux(listBlock,len(listBlock),idBlock, self)
                        self.sons[1].sons[1].makeBlock_aux(listBlock,len(listBlock),idBlock,self)
                        
            else:
                # sinon on parcourt récursivement l'arbre
                if self.sons[0].value=="=":
                    listBlock[idBlock].append([self.sons[0], pere, self])
                elif self.sons[0].value=="while":
                    #cas du while
                    self.sons[0].sons[1].makeBlock_aux(listBlock,len(listBlock), idBlock,self)
                self.sons[1].makeBlock_aux(listBlock,idBlock, idBlock,self)
        elif self.value == "=":
            if not len(listBlock)>idBlock:
                listBlock.append([idParent])
            listBlock[idBlock].append([self, pere, self])
            
    def makeBlock(self):
        listBlock=[]
        self.makeBlock_aux(listBlock,0, -1, self)
        return listBlock
        
    def simplifyVariables(self):
        ## On parcourt les blocs obtenus
        ## On calcule tous les blocs fils
        ## On regarde si la variables est utilisé, cf isUseless
        listBlock=self.makeBlock()
        for block in listBlock:
            childBlock=[b for b in listBlock if b[0]==listBlock.index(block)]
            for x in block[1:]:
                if isUseless(childBlock, x):
                    if x[0] in x[1].sons:
                        x[1].sons = x[2].sons[1].sons
                    else:
                        x[1].sons[1] = x[2].sons[1]

            
    
def isUseless(childBlock, commande):
    ## On parcourt tous les block des enfants, et 
    ## on regarde si la variable est affectée.
    if commande[0].sons[1].type!="NUMBER":
        return False
    for block in childBlock:
        for x in block[1:]:
            if x[0].sons[0]==commande[0].sons[0]:
                return False
        return True
        
                        
                        
        
            
            
                            
            
                        