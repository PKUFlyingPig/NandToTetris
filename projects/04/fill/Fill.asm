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
// Pseudocode:
// kbd = GetKBD();
// if(kbd>0) goto BLACK;
// if(kbd==0) goto WHITE;
// WHITE:
//     for(int i=0;i<8192;i++) M[i+SCREEN]=0;
// BLACK:
//     for(int i=0;i<8192;i++) M[i+SCREEN]=1;

@SCREEN

(CHECK)
    @KBD
    D=M
    @BLACK
    D;JGT
    @WHITE
    0;JMP

(WHITE)
    // i = 0
    @i
    M=0
    (LOOPA)
        // if(i==8192) goto CHECK;
        @8192
        D=A
        @i
        D=M-D
        @CHECK
        D;JEQ

        @i
        D=M
        @SCREEN
        A=A+D
        M=0

        @i
        M=M+1

        @LOOPA
        0;JMP


(BLACK)
    // i = 0
    @i
    M=0
    (LOOPB)
        // if(i==8192) goto CHECK;
        @8192
        D=A
        @i
        D=M-D
        @CHECK
        D;JEQ

        @i
        D=M
        @SCREEN
        A=A+D
        M=-1

        @i
        M=M+1

        @LOOPB
        0;JMP