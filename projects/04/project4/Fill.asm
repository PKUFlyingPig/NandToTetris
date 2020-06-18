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

@8192
D=A
@len
M=D

(LOOP1)
@KBD
D=M
@WHITE
D;JEQ
@BLACK
0;JMP

(WHITE)
@i
M=0

(LOOP2)
@len
D=M
@i
D=D-M
@LOOP1
D;JEQ

@SCREEN
D=A
@i
A=D+M
M=0

@i
M=M+1

@LOOP2
0;JMP

(BLACK)
@i
M=0

(LOOP3)
@len
D=M
@i
D=D-M
@LOOP1
D;JEQ

@SCREEN
D=A
@i
A=D+M
M=-1

@i
M=M+1

@LOOP3
0;JMP