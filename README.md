# Semantic
Optimisation code source par Simon Vernin et François Torregrossa

# Affichage

## Installation du package
Pour l'affichage, il faut installer le module python ete3.
```bash
pip3 install ete3
```

## Principe d'affichage
Nous parcourons l'arbre de synthaxe abstraite de classe AST, et nous formons des TreeNode récursivement selon leur type. L'affichage final est produit en ascii en console.
```bash
>>> print(yacc.parse("main(x,y,z,t) {while(48 == 48){a = 2 * 3 + 4; b = 5 + 6; a = b + 2};; print(3+4)}"))

Out:
      /-['x', 'y', 'z', 't']
     |
     |        /-Number : 48
     |     /==
     |    |   \-Number : 48
     |    |
     |    |      /-Id : a
     |-while  /=|
     |    |  |  |   /-Number : 2
     |    |  |   \*|
     |    |  |     |   /-Number : 3
     |    |  |      \+|
     |     \;|         \-Number : 4
-main()      |
     |       |      /-Id : b
     |       |   /=|
     |       |  |  |   /-Number : 5
     |       |  |   \+|
     |        \;|      \-Number : 6
     |          |
     |          |   /-Id : a
     |           \=|
     |             |   /-Id : b
     |              \+|
     |                 \-Number : 2
     |
     |   /-Number : 3
      \+|
         \-Number : 4
```

# Langage de programmation
## Description
Un programme se décompose de la manière suivante, avec les éléments de la grammaire entre guillemets :
```python
main ( "enum" ) { "command" ;; print( "expression" ) }
```
Notez le ';;' qui met fin aux commandes avant le print.
```python
enum : ID | ID COMMA enum
```

```python
expression : ID | NUMBER | expression OPBIN expression
```

```python
command : ID AFFECT expression | WHILE LPAREN expression RPAREN LACO commande RACO | command END command
```

Les tokkens associés, non explicites dans leur nom, sont :
- ID : combinaison de lettres non associée aux mots-clefs
- AFFECT : '='
- OPBIN : '+', '-', '*', '/'

## Exemple

```c++
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
}
```
L'arbre de synthaxe affiché est alors :
```bash
      /-['x', 'y', 'z']
     |
     |      /-Id : t
     |   /=|
     |  |  |   /-Id : x
     |  |   \+|
     |  |     |   /-Id : y
     |  |      \+|
     |-;|         \-Id : z
     |  |
     |  |      /-Id : a
     |  |   /=|
     |  |  |   \-Number : 0
     |  |  |
-main()  \;|     /-Id : t
     |     |    |
     |     |    |      /-Id : t
     |      \while  /=|
     |          |  |  |   /-Id : t
     |          |  |   \-|
     |           \;|      \-Number : 1
     |             |
     |             |   /-Id : a
     |              \=|
     |                |   /-Id : t
     |                 \+|
     |                    \-Id : a
     |
      \-Id : a
```

# Optimisation du code source

Un programme se divise en trois blocs : les variables, les commandes et la sortie. Nous simplifions la partie commande indépendamment des autres blocs.

## Simplification des affectations futiles dans une commande

### Exemple :
```c++
x = 5;
y = 8;
x = y + 3
```
```bash
      /-Id : x
   /=|
  |   \-Number : 5
  |
-;|      /-Id : y
  |   /=|
  |  |   \-Number : 8
   \;|
     |   /-Id : x
      \=|
        |   /-Id : y
         \+|
            \-Number : 3
```
La suppression de la première ligne est possible.


### Méthode :

Nous avons une fonction récursive *simplifyID* et son auxiliaire *simplifyID_aux*.

La fonction auxiliaire remplit une liste d'éléments utiles, et une liste d'éléments inutiles, selon que les éléments utiles sont utilisés dans des affectations à droite lors du parcours de l'arbre de synthaxe abstraite.
```python
def simplifyID_aux(self, i, useful, useless, path):
    """
    useful est une liste de liste contenant : le nom de la variable, le niveau dans l'arbre,
    le chemin jusqu'à lui, l'arbre, un booléen disant si la variable a servi dans une affectation

    useless ne sert pas dans le programme, on le laisse pour une éventuelle utilité.
    """
    j = 0
    for son in self.sons:
        ## parcourt les fils
        if type(son) == str:
        ## si le fils est de type str alors c'est un ID (du fait de la construction de l'arbre)
        ## on regarde l'indice de la variable dans la liste, dans les éléments n'ayant pas été affectés
        ## jusqu'ici
            ind = AST.isInList(useful, son)
            if ind >= 0: ## si la variable est dans la liste
            	useless.append(useful[ind])
            	useful.remove(useful[ind]) 
            ## on retire de la liste la variable homonyme qui n'a pas servi dans une affectation
            useful.append([son, i, path + str(j), self, False])
        elif son.value == "while":
        	son.simplifyWhile() ## Simplification du while
            useful.append(['while', i, path + str(j), son, True])
            ## on noté qu'un while sert toujours sauf exception sur l'expression et sera remis
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
            son.simplifyID_aux(i + 1, useful, useless, path + str(j)
            ## on simplifie sur le fils récursivement
        j += 1
```
Fonctions annexes utilisées :
```python
def isInList(useful, item):
    """
    Retourne l'emplacement de la variable item dans la liste des éléments utiles
    En ne regardant seulement les éléments pour lesquelles,
    on n'a pas vérifié s'ils ont auparavant servi dans une affectation.
    """
    for i in range(len(useful)):
    	if not useful[i][4] and item == useful[i][0]:
    		return i
    return -1
    
def reconstitueExpression(self):
	"""
    Sous forme de chaine de caractère recopie l'expression associé à self.
    """
    if self.nature == "expression":
        if self.type == "OPBIN":
            return self.sons[0].reconstitueExpression() + " " + self.value + " " + self.sons[1].reconstitueExpression()
        else:
            return str(self.value)
```

L'arbre est ensuite reconstité dans la fonction principale grâce à la liste des éléments utiles. La reconstitution se fait dans l'ordre de la liste, car le parcours se fait en largeur, et par conséquent on collecte les éléments par niveaux et dans l'ordre.
```python
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
	## si le programme ne contient plus qu'une affectation utile,
	## alors on retourne l'affectation agissant comme commande
		tree = useful[0][3]
	else:
		for i in range(len(useful)):
		## on parcourt la liste des affectations utiles
			while len(treeson.sons) > 1: ## on cherche l'emplacement de la nouvelle affectation
				treeson =  treeson.sons[1]
			if i + 2 < len(useful):
				treeson.sons.append(useful[i][3])
				treeson.sons.append(AST("END", ";", "commande"))
			else:
				treeson.sons.append(useful[i][3])
	return tree
```

L'arbre produit à partir du précédent est le suivant :

```bash
      /-Id : y
   /=|
  |   \-Number : 8
-;|
  |   /-Id : x
   \=|
     |   /-Id : y
      \+|
         \-Number : 3
```
Pour la simplification au sein des commandes **while**, on rappelle récursivement avec la fonction principale dans la fonction auxiliaire (visible dans le ```elif son.value == "while"```), on n'y vient plus tard.

## Simplification des expressions

### Exemple :

```c++
x = 4;
y = x + 2;
z = 8 + x + y
```
```bash
      /-Id : x
   /=|
  |   \-Number : 4
  |
-;|      /-Id : y
  |   /=|
  |  |  |   /-Id : x
  |  |   \+|
   \;|      \-Number : 2
     |
     |   /-Id : z
      \=|
        |   /-Number : 8
         \+|
           |   /-Id : x
            \+|
               \-Id : y
```

On aimerait, lorsque cela est possible, remplacer les affectations par le calcul explicite de l'expression. Ici cela donnerait :
```c++
x = 4;
y = 6;
z = 18
```
On simplifiera plus tard le cas où les affectations sont inutiles (c'est-à-dire non utilisées dans des sous blocs, ou dans le print du programme).

### Méthode : 

De la même manière que précédemment, nous aurons une fonction principale récursive *simplifyExpression*, et son auxiliaire *simplifyExpression_aux*.
```python
def simplifyExpression(self):
     affect = {}
     self.simplifyExpression_aux(affect)
```
On assimile la magasin des variables à un dictionnaire *affect*. Dans ce dictionnaire, les clefs seront les variables au format **string**, et les valeurs seront la valeur de la variable. Cette valeur est mise à jour à chaque fois que la variable associé subit une affectation. Pour cela on parcourt l'arbre en largeur, ce qui permet de lire ligne par ligne le programme et d'obtenir la bonne valeur du magasin à chaque ligne.
```python
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
```
Fonction annexe :
```python
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
```
La simplification nous donne :
```bash
      /-Id : x
   /=|
  |   \-Number : 4
  |
-;|      /-Id : y
  |   /=|
  |  |   \-Number : 6
   \;|
     |   /-Id : z
      \=|
         \-Number : 18
```
## Simplification des boucles while
### Exemple :

```c++
x = 5;
x = x + 1;
y = 6;
y = 4;
z = 3;
while (x)
{
	z = 8;
    y = 4;
    z = x + 5;
    y = z + x;
    x = 3;
    x = 4;
    x = y + 7
};
z = 10
```
```bash
      /-Id : x
   /=|
  |   \-Number : 5
  |
  |      /-Id : x
-;|   /=|
  |  |  |   /-Id : x
  |  |   \+|
  |  |      \-Number : 1
  |  |
   \;|      /-Id : y
     |   /=|
     |  |   \-Number : 6
     |  |
     |  |      /-Id : y
     |  |   /=|
      \;|  |   \-Number : 4
        |  |
        |  |      /-Id : z
        |  |   /=|
        |  |  |   \-Number : 3
        |  |  |
         \;|  |        /-Id : x
           |  |       |
           |  |       |      /-Id : z
           |  |   /while  /=|
           |  |  |    |  |   \-Number : 8
           |  |  |    |  |
           |  |  |    |  |      /-Id : y
           |  |  |     \;|   /=|
            \;|  |       |  |   \-Number : 4
              |  |       |  |
              |  |       |  |      /-Id : z
              |  |        \;|   /=|
              |  |          |  |  |   /-Id : x
              |  |          |  |   \+|
              |  |          |  |      \-Number : 5
              |  |          |  |
              |  |           \;|      /-Id : y
              |  |             |   /=|
              |  |             |  |  |   /-Id : z
              |  |             |  |   \+|
               \;|             |  |      \-Id : x
                 |              \;|
                 |                |      /-Id : x
                 |                |   /=|
                 |                |  |   \-Number : 3
                 |                |  |
                 |                 \;|      /-Id : x
                 |                   |   /=|
                 |                   |  |   \-Number : 4
                 |                    \;|
                 |                      |   /-Id : x
                 |                       \=|
                 |                         |   /-Id : y
                 |                          \+|
                 |                             \-Number : 7
                 |
                 |   /-Id : z
                  \=|
                     \-Number : 10
```
On veut que la boucle while se simplifie, avec le reste du programme sans altérer le sens de la boucle. Dans le cas où l'expression booléen du while s'évalue à 0, il faut aussi éliminer la boucle.

### Méthode :

Pour ce faire, on utilise la fonction *simplifyWhile*, qui n'est pas récursive, mais qui utilise les fonctions précédentes. Vous avez noté que dans la fonction *simplifyID_aux*, on faisait appel à *simplifyWhile* :
```python
def simplifyID_aux(self, i, useful, useless, path):
   	...
        elif son.value == "while":
            son.simplifyWhile() ## Simplification du while
            useful.append(['while', i, path + str(j), son, True])
            ## on noté qu'un while sert toujours sauf exception sur l'expression et sera remis
    ...
 ```
 ```python
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
```
 Voici dans *simplifyID*, la partie du code s'occupant du retrait des while inutiles :
 
```python
def simplifyID(self):
	...
    for x in useful:
        ## Retrait des while inutiles (d'expressioin évaluée à zéros)
        if type(x[3].sons[0]) != str and x[3].sons[0].value == "toremove":
            useful.remove(x)
    ...
```
Après un *simplifyID* :
```bash
      /-Id : x
   /=|
  |   \-Number : 5
  |
  |      /-Id : x
  |   /=|
-;|  |  |   /-Id : x
  |  |   \+|
  |  |      \-Number : 1
  |  |
  |  |      /-Id : y
   \;|   /=|
     |  |   \-Number : 4
     |  |
     |  |        /-Id : x
     |  |       |
     |  |       |      /-Id : z
     |  |   /while  /=|
      \;|  |    |  |  |   /-Id : x
        |  |    |  |   \+|
        |  |    |  |      \-Number : 5
        |  |     \;|
        |  |       |      /-Id : y
        |  |       |   /=|
        |  |       |  |  |   /-Id : z
        |  |       |  |   \+|
         \;|        \;|      \-Id : x
           |          |
           |          |   /-Id : x
           |           \=|
           |             |   /-Id : y
           |              \+|
           |                 \-Number : 7
           |
           |   /-Id : z
            \=|
               \-Number : 10
```
Après un *simplifyEpression* :
```bash
      /-Id : x
   /=|
  |   \-Number : 5
  |
  |      /-Id : x
-;|   /=|
  |  |   \-Number : 6
  |  |
  |  |      /-Id : y
  |  |   /=|
   \;|  |   \-Number : 4
     |  |
     |  |        /-Id : x
     |  |       |
     |  |       |      /-Id : z
     |  |   /while  /=|
      \;|  |    |  |  |   /-Id : x
        |  |    |  |   \+|
        |  |    |  |      \-Number : 5
        |  |     \;|
        |  |       |      /-Id : y
        |  |       |   /=|
        |  |       |  |  |   /-Id : z
        |  |       |  |   \+|
         \;|        \;|      \-Id : x
           |          |
           |          |   /-Id : x
           |           \=|
           |             |   /-Id : y
           |              \+|
           |                 \-Number : 7
           |
           |   /-Id : z
            \=|
               \-Number : 10
```
Après un nouveau *simplifyID* :
```bash
      /-Id : x
   /=|
  |   \-Number : 6
  |
  |      /-Id : y
  |   /=|
-;|  |   \-Number : 4
  |  |
  |  |        /-Id : x
  |  |       |
  |  |       |      /-Id : z
  |  |   /while  /=|
   \;|  |    |  |  |   /-Id : x
     |  |    |  |   \+|
     |  |    |  |      \-Number : 5
     |  |     \;|
     |  |       |      /-Id : y
     |  |       |   /=|
     |  |       |  |  |   /-Id : z
     |  |       |  |   \+|
      \;|        \;|      \-Id : x
        |          |
        |          |   /-Id : x
        |           \=|
        |             |   /-Id : y
        |              \+|
        |                 \-Number : 7
        
        |
        |   /-Id : z
         \=|
            \-Number : 10
```
## Simplification des variables inutiles
### Exemple :

```c++
x = 4;
y = 6;
t = 8;
while(t)
{
	t = t - 1;
    y = y + 1
}
```
```bash
      /-Id : x
   /=|
  |   \-Number : 4
  |
-;|      /-Id : y
  |   /=|
  |  |   \-Number : 6
  |  |
   \;|      /-Id : t
     |   /=|
     |  |   \-Number : 8
     |  |
      \;|     /-Id : t
        |    |
        |    |      /-Id : t
         \while  /=|
             |  |  |   /-Id : t
             |  |   \-|
              \;|      \-Number : 1
                |
                |   /-Id : y
                 \=|
                   |   /-Id : y
                    \+|
                       \-Number : 1
```
L'objectif ici est de supprimer la variable x, qui ne sert pas dans le programme.

### Méthode :

Pour résoudre ce problème, il faut décomposer le programme en bloc, dépendants les uns des autres. A la fin on vérifie que les variables utilisées dans un bloc sont utilisés ou non dans des blocs fils. Dans le premier cas, la variable doit être conservée, dans le second cas, elle doit être supprimée.

Voici la fonction calculant les blocs.
```python
def makeBlock(self):
    listBlock=[]
    self.makeBlock_aux(listBlock,0, -1, self)
    return listBlock
```
```python
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
```
Une fois qu'on a les blocs, on simplifie de la manière suivante :
```python
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
```
```python
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
```
On reçoit l'arbre suivant après les simplifications usuelles :
```bash      
	  /-Id : y
   /=|
  |   \-Number : 6
  |
-;|      /-Id : t
  |   /=|
  |  |   \-Number : 8
  |  |
   \;|     /-Id : t
     |    |
     |    |      /-Id : t
      \while  /=|
          |  |  |   /-Id : t
          |  |   \-|
           \;|      \-Number : 1
             |
             |   /-Id : y
              \=|
                |   /-Id : y
                 \+|
                    \-Number : 1
```
