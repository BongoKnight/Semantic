# Semantic
Optimisation code source par Simon Vernin et François Torregrossa

# Affiche
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


