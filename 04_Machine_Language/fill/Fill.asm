// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// SCREEN: 256 rows with 32 16-bit words each; 256 * 32 = 8192
// base address of SCREEN: 16384

//THIS CANNOT BE DONE:
//@targetaddress
//M=16384
//see https://stackoverflow.com/questions/13654066/nand-2-tetris-asm-expression-expected
(RESETVALUES)
@16384
D=A
@targetaddress
M=D
@8191
D=A
@counter
M=D

(LISTENING)
@KBD
D=M
@WHITEN
D;JEQ

(BLACKEN)
@targetaddress
AD=M
M=-1
@targetaddress
M=M+1
@counter
M=M-1
D=M
@BLACKEN
D;JNE
//check if keyboard input changed before resetting and potentially run the whole 
// blackening procedure all over again
@KBD
D=M
@RESETVALUES
D;JNE

(WHITEN)
@targetaddress
AD=M
M=0
@targetaddress
M=M+1
@counter
M=M-1
D=M
@WHITEN
D;JNE
@RESETVALUES
0;JMP
