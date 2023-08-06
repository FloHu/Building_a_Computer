class CodeWriter:
    StackAddress = 256
    # this class variable keeps a record of how often one of eq/gt/lt operations have been run
    # since these will be implemented by jumps. There is apparently a (presumably) more clever solution 
    # (https://stackoverflow.com/questions/30154665/how-can-i-write-an-interpreter-for-eq-for-hack-assembly-language) 
    # but this is not the one I came up with by myself
    RunningIndComps = 0

    def __init__(self, outfilename: str) -> None:
        self.outfile = open(outfilename, "w")
        # initialise SP value:
        self.outfile.write(f"@{self.StackAddress}\n")
        self.outfile.write("D=A\n")
        self.outfile.write("@SP\n")
        self.outfile.write("M=D\n")
    
    def writeCommand(self, cmd_type: str, arg1: str, arg2: str):
        ## TO DO: switch case in Python available since 3.10 - use here? 
        if cmd_type == "C_PUSH":
            self.writePush(segment=arg1, index=arg2)
        elif cmd_type == "C_POP":
            #self.writePop(segment=arg1, index=arg2)
            self.writePop()
        elif cmd_type == "C_ARITHMETIC":
            self.writeArithmetic(command=arg1)

    def writeArithmetic(self, command):
        if command == "add":
            self.writePop() # top value now in D
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=D+M\n")
            self.increaseSP()
        elif command == "sub":
            self.writePop()
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=M-D\n")
            self.increaseSP()
        elif command == "and":
            self.writePop()
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=D&M\n")
            self.increaseSP()
        elif command == "or":
            self.writePop()
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=D|M\n")
            self.increaseSP()
        elif command == "eq":
            self.writePop()
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M-D\n") # D now contains the result of the comparison

            self.RunningIndComps += 1
            iftrueloc = "IFTRUELOC." + str(self.RunningIndComps)
            continueloc = "CONTINUELOC." + str(self.RunningIndComps)

            self.outfile.write("@" + iftrueloc + "\n")
            self.outfile.write("D;JEQ\n")
            self.outfile.write("D=0\n")
            self.outfile.write("@" + continueloc + "\n")
            self.outfile.write("0;JMP\n")
            self.outfile.write("(" + iftrueloc + ")\n")
            self.outfile.write("D=-1\n")
            self.outfile.write("(" + continueloc + ")\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif command == "gt":
            ## TO DO: refactor eq/gt/lt  
            self.writePop()
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M-D\n") # D now contains the result of the comparison

            self.RunningIndComps += 1
            iftrueloc = "IFTRUELOC." + str(self.RunningIndComps)
            continueloc = "CONTINUELOC." + str(self.RunningIndComps)

            self.outfile.write("@" + iftrueloc + "\n")
            self.outfile.write("D;JGT\n")
            self.outfile.write("D=0\n")
            self.outfile.write("@" + continueloc + "\n")
            self.outfile.write("0;JMP\n")
            self.outfile.write("(" + iftrueloc + ")\n")
            self.outfile.write("D=-1\n")
            self.outfile.write("(" + continueloc + ")\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif command == "lt":
            self.writePop()
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M-D\n") # D now contains the result of the comparison

            self.RunningIndComps += 1
            iftrueloc = "IFTRUELOC." + str(self.RunningIndComps)
            continueloc = "CONTINUELOC." + str(self.RunningIndComps)

            self.outfile.write("@" + iftrueloc + "\n")
            self.outfile.write("D;JLT\n")
            self.outfile.write("D=0\n")
            self.outfile.write("@" + continueloc + "\n")
            self.outfile.write("0;JMP\n")
            self.outfile.write("(" + iftrueloc + ")\n")
            self.outfile.write("D=-1\n")
            self.outfile.write("(" + continueloc + ")\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif command == "neg":
            self.writePop()
            self.outfile.write("D=-D\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif command == "not":
            self.writePop()
            self.outfile.write("D=!D\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        else:
            raise ValueError(f"Command {command} does not exist")

    def writePush(self, segment, index):
        ## TO DO: fix/modify: this here at the moment only supports 'push'
        ## also: like this only works for the constant segments - how to translate the others?
        self.outfile.write(f"@{index}\n") # can probably be abstracted into another method (?)
        self.outfile.write("D=A\n")
        ## TO DO: consider moving this to a method 'dereference SP'
        self.outfile.write("@SP\n")
        self.dereferenceSP()
        self.outfile.write("M=D\n")
        self.increaseSP()
    
    def writePop(self):
        ## TO DO: needs to be able to accep segment and index arguments 
        self.decreaseSP()
        self.dereferenceSP()
        self.outfile.write("D=M\n")
        ## TO DO: missing: writing to the corresponding segment[index]
    
    def increaseSP(self):
        self.outfile.write("@SP\n")
        self.outfile.write("M=M+1\n")
    
    def decreaseSP(self):
        self.outfile.write("@SP\n")
        self.outfile.write("M=M-1\n")
    
    def dereferenceSP(self):
        self.outfile.write("A=M\n")

    def close(self):
        self.outfile.close()


