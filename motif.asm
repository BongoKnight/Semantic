global main 
extern printf, atoi

section .data
message: db 'Hello World %d', 10, 0
message_erreur: db "Il y a %d arguments requis", 10, 0
VAR_DECL

section .text
main:

mov eax, [esp + 4]
cmp eax, LEN_INPUT + 1
mov eax, [esp + 8]
jne erreur_nb_entree
VAR_INIT
jmp debut_prog
erreur_nb_entree:
mov eax, LEN_INPUT
push eax
lea eax, [message_erreur]
push eax
call printf
add esp, 8
jmp fin

debut_prog:
COMMAND_EXEC

EVAL_OUTPUT

push eax
lea eax, [message]
push eax
call printf
add esp, 8

fin: ret

