// initialization
@256
D=A
@SP
M=D
// push 7 and 8
@7
D=A
// step 2: use value stored in SP as a pointer ...
@SP
A=M
// ... and then M=... can be used to push to that memory address the value that is in D:
M=D
// step 3: increase SP by 1
@SP
M=M+1
// do the same for pushing 8
@7
D=A
@SP
A=M
M=D
@SP
M=M+1
//testing for equality: eq - ???
// assuming R5 contains -1 (true) and R6 contains 0 (false)
// run sub:
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D // contains now the result of the comparison
@IFTRUEGOHERE
D;JEQ
D=0
@CONTINUEHERE
0;JMP
(IFTRUEGOHERE)
D=-1
// continue here
(CONTINUEHERE)
@SP
A=M
M=D
// increase SP