# Semantic
Optimisation code source par Simon Vernin et François Torregrossa

# Affiche
Pour l'affichage, il faut installer le module python ete3.
```bash
pip3 install ete3
```

## Principe d'affichage
Nous parcourons l'arbre de synthaxe abstraite de classe AST, et nous formons des TreeNode récursivement selon leur type. L'affichage final est produit en ascii en console.
```python
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

```C++
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
```python
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




