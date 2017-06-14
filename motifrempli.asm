global main 
extern printf, atoi

section .data
message: db 'Hello World %d', 10, 0
message_erreur: db "Il y a %d arguments requis", 10, 0
Y: dd 0
X: dd 0
t: dd 0

section .text
main:

mov eax, [esp + 4]
cmp eax, 1 + 1
mov eax, [esp + 8]
jne erreur_nb_entree
mov ebx, [eax + 4]
push eax
push ebx
call atoi
add esp, 4
mov [X], eax
pop eax

jmp debut_prog
erreur_nb_entree:
mov eax, 1
push eax
lea eax, [message_erreur]
push eax
call printf
add esp, 8
jmp fin

debut_prog:
debutboucle1:
mov eax, [X]

cmp eax, 0
jz finboucle1
mov eax, [Y]
push eax
mov eax, 1
pop ebx
add eax, ebx

mov[Y], eax
mov eax, 1
push eax
mov eax, [X]
pop ebx
sub eax, ebx

mov[X], eax
jmp debutboucle1
finboucle1:

mov eax, 3

mov[t], eax

mov eax, [Y]


push eax
lea eax, [message]
push eax
call printf
add esp, 8

fin: ret

