// test at manually translating SimpleAdd.vm
@256
D=A
@SP
M=D
@7
D=A
// the following will move the value in D to the location specified in 0 (=@SP)
// i.e. @SP (=@0) --> A=M --> M=D results in the content of A being used as a pointer 
// and the location that is pointed to gets the value in D
@SP
A=M
M=D
// now increase the value of @SP
@SP
M=M+1
// add 8 to the stack and increase value in SP by 1:
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
// 'add' command: 
// reduce SP by 1
@SP
M=M-1
// retrieve value pointed to and store in D register
@SP
A=M
D=M
// reduce SP by 1
@SP
M=M-1
// retrieve value pointed to and update D register
@SP
A=M
D=D+M
// store value from D in location pointed to
@SP
A=M
M=D
// increase SP by 1
@SP
M=M+1
