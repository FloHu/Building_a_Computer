// initialize value of SP (address: 0, see previous chapter) to 256
@256
D=A
@SP
M=D
// move constant value to location stored in SP:
// step 1: load into D register:
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
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
// 'add' command: 
// step 1: reduce SP by 1 (note: we could save this and the previous step if we know that the next 
// command is add - but I don't think we can actually know e.g. with if there is some branching command)
@SP
M=M-1
// retrieve value pointed to and store in D register
A=M
D=M
// reduce SP by 1
@SP
M=M-1
// retrieve value pointed to and update D register
A=M
D=D+M
M=D
// increase SP by 1
@SP
M=M+1
