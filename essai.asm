global main 
extern printf, atoi ;; = include stdio.h

section .data
;; 4 type de variables
;; - db -> databyte : 1oct / char
;; - dw -> dataword : 2oct / short
;; - dd -> datadoubleword : 4oct / int
;; - dq -> dataquadword : 8oct / long int
message: db 'Hello world %d', 10, 0 
x: dd 42 


;; registres :
;; - eax, ebx, ecx, edx, esi, edi

section .text
main:
mov ebx, [x];; mov: 'ebx = 42' ou 'ebx = *x'
;; inc ebx ;-> ebx += 1
;; dec ebx ;-> ebx -= 1
add ebx, ebx ;-> ebx += ebx
;; sub ebx, eax ;-> ebx -= eax
;; imul ebx, eax ;-> ebx *= eax
;; idiv ebx, eax ;-> ebx /= eax
mov [x], ebx ;; '*x = ebx'

cmp ebx, 84 ; si ebx = 0
jz fin ; fin désigne une étiquette (jump zero)
;; jz jump zero
;; je jump equal
;; jl jump less than
;; jg jump greater than

mov eax, [x]
push eax
lea eax, [message] ;load effective adress
push eax
call printf
;;pop eax ;; pop sur un registre, il faut autant de pop que de push
;;pop eax
add esp, 8


fin :
	mov eax, [esp + 8]
	mov ebx, [eax + 4]
	;lea eax, [message]
	push ebx
	call atoi ; string to int
	pop ebx
	push eax ; eax contient le nombre calculé
	lea eax, [message]
	push eax
	call printf
	add esp, 8
	ret ; fin du programme en envoyant l'adresse d'exécution du programme suivant
