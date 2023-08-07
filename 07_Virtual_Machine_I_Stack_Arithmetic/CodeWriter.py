class CodeWriter:
    StackAddress = 256
    # this class variable keeps a record of how often one of eq/gt/lt operations have been run
    # since these will be implemented by jumps. There is apparently a (presumably) more clever solution 
    # (https://stackoverflow.com/questions/30154665/how-can-i-write-an-interpreter-for-eq-for-hack-assembly-language) 
    # but this is not the one I came up with by myself
    RunningIndComps = 0
    segment_map = {
        'local': 'LCL', 
        'argument': 'ARG', 
        'this': 'THIS', 
        'that': 'THAT'
    }

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
            self.writePop(segment=arg1, index=arg2)
        elif cmd_type == "C_ARITHMETIC":
            self.writeArithmetic(command=arg1)

    def writeArithmetic(self, command):
        if command == "add":
            self.writePop(segment="constant", index=None) # top value now in D
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=D+M\n")
            self.increaseSP()
        elif command == "sub":
            self.writePop(segment="constant", index=None)
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=M-D\n")
            self.increaseSP()
        elif command == "and":
            self.writePop(segment="constant", index=None)
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=D&M\n")
            self.increaseSP()
        elif command == "or":
            self.writePop(segment="constant", index=None)
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("M=D|M\n")
            self.increaseSP()
        elif command == "eq":
            self.writePop(segment="constant", index=None)
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
            self.writePop(segment="constant", index=None)
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
            self.writePop(segment="constant", index=None)
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
            self.writePop(segment="constant", index=None)
            self.outfile.write("D=-D\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif command == "not":
            self.writePop(segment="constant", index=None)
            self.outfile.write("D=!D\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        else:
            raise ValueError(f"Command {command} does not exist")

    def writePush(self, segment, index):
        if segment == "constant":
            self.outfile.write(f"@{index}\n")
            self.outfile.write("D=A\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif segment in self.segment_map:
            # e.g. 'push argument 1': just like with 'pop argument 1' need to add argument and index, 
            # dereference and store, then put on the stack
            self.outfile.write(f"@{index}\n") 
            self.outfile.write("D=A\n")
            self.outfile.write(f"@{self.segment_map[segment]}\n")
            self.outfile.write("A=D+M\n")
            self.outfile.write("D=M\n")
            self.outfile.write("@SP\n")
            self.outfile.write("A=M\n")
            self.outfile.write("M=D\n")
            self.increaseSP()
        elif segment == "temp":
            ## TO DO: can be generalized together with this and that
            ram_loc = 5 + index
            # get value from ram location and then put on stack
            self.outfile.write(f"@{str(ram_loc)}\n")
            self.outfile.write("D=M\n")
            self.outfile.write("@SP\n")
            self.outfile.write("A=M\n")
            self.outfile.write("M=D\n")
            self.increaseSP()
    
    def writePop(self, segment, index):
        ## TO DO: calls to writePop() from arithmetic commands or using segment = 'constant' don't need an index
        # handle this better
        if segment == "constant":
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M\n")
        elif segment in self.segment_map:
            ## TO DO: later check if this is true, perhaps generalise/refactor
            # at the moment: segment_map contains pointers to somewhere in memory: 
            # index needs to be added to those pointers before dereferencing them
            self.outfile.write(f"@{index}\n")
            self.outfile.write("D=A\n")
            self.outfile.write(f"@{self.segment_map[segment]}\n")
            self.outfile.write("D=D+M\n") # = index + M[@LCL]
            self.outfile.write("@R13\n")# intermediate storage in R13 
            self.outfile.write("M=D\n")
            # now pop stack into D, dereference address in R13 and put D there
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M\n")
            self.outfile.write("@R13\n")
            self.outfile.write("A=M\n")
            self.outfile.write("M=D\n")
        elif segment == "temp":
            ram_loc = 5 + index
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M\n")
            self.outfile.write(f"@{str(ram_loc)}\n")
            self.outfile.write("M=D\n")
    
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


