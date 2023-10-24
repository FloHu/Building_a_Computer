from pathlib import Path

class CodeWriter:
    StackAddress = 256
    # this class variable keeps a record of how often one of eq/gt/lt operations have been run
    # since these will be implemented by jumps. There is apparently a (presumably) more clever solution 
    # (https://stackoverflow.com/questions/30154665/how-can-i-write-an-interpreter-for-eq-for-hack-assembly-language) 
    # but this is not the one implemented here as I did not came up with it by myself
    RunningIndComps = 0
    segment_name_map = {
        'local': 'LCL', 
        'argument': 'ARG', 
        'this': 'THIS', 
        'that': 'THAT'
    }
    pointer_temp_addresses = {
        'temp': 5, 
        'pointer': 3
    }

    def __init__(self, outfilename: str) -> None:
        self.outfilename = outfilename
        self.outfile = open(outfilename, "w")
        self.ncalls = 0
        self.current_input_file = ''
        # initialise SP value:
        self.outfile.write(f"@{self.StackAddress}\n")
        self.outfile.write("D=A\n")
        self.outfile.write("@SP\n")
        self.outfile.write("M=D\n")
        # write Sys.init: 
        self.writeCall(functionName="Sys.init", numArgs=0)
        
        self.arithmetic_operations = {
            "add": self.add, 
            "sub": self.sub, 
            "and": self.and_op, 
            "or": self.or_op, 
            "neg": self.neg_op, 
            "not": self.not_op
        }

        self.comparison_operations = {
            "eq": self.eq, 
            "gt": self.gt, 
            "lt": self.lt
        }

    
    def writeCommand(self, cmd_type: str, arg1: str, arg2: str, current_func: str):
        ## TO DO: switch case in Python available since 3.10 - use here? 
        ## or what other construct could we use? 
        if cmd_type == "C_PUSH":
            self.writePush(segment=arg1, index=arg2)
        elif cmd_type == "C_POP":
            self.writePop(segment=arg1, index=arg2)
        elif cmd_type == "C_ARITHMETIC":
            self.writeArithmetic(command=arg1)
        ## TO DO: improve scoping of label names - this looks rather brittle
        elif cmd_type == "C_LABEL":
            self.writeLabel(label=arg1, current_func=current_func)
        elif cmd_type == "C_GOTO":
            self.writeGoTo(label=arg1, current_func=current_func)
        elif cmd_type == "C_IF":
            self.writeIf(label=arg1, current_func=current_func)
        elif cmd_type == "C_FUNCTION":
            self.writeFunction(functionName=arg1, numLocals=arg2)
        elif cmd_type == "C_RETURN":
            self.writeReturn()
        elif cmd_type == "C_CALL":
            self.writeCall(functionName=arg1, numArgs=arg2)

    def writeArithmetic(self, command):
        self.popIntoDRegister()

        if command in ["eq", "gt", "lt"]:
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M-D\n") # D now contains the result of the comparison

            self.RunningIndComps += 1
            iftrueloc = "IFTRUELOC." + str(self.RunningIndComps)
            continueloc = "CONTINUELOC." + str(self.RunningIndComps)

            self.outfile.write("@" + iftrueloc + "\n")
            operation = self.comparison_operations[command]
            ## TO DO: self passed also here? was this the thing with bound methods?
            operation()
            
            self.outfile.write("D=0\n")
            self.outfile.write("@" + continueloc + "\n")
            self.outfile.write("0;JMP\n")
            self.outfile.write("(" + iftrueloc + ")\n")
            self.outfile.write("D=-1\n")
            self.outfile.write("(" + continueloc + ")\n")
            self.outfile.write("@SP\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
        elif command in ["add", "sub", "and", "or"]:
            self.decreaseSP()
            self.dereferenceSP()
            operation = self.arithmetic_operations[command]
            operation()
        elif command in ["neg", "not"]:
            operation = self.arithmetic_operations[command]
            operation()

        self.increaseSP()
    
    def add(self):
        self.outfile.write("M=D+M\n")
    
    def sub(self):
        self.outfile.write("M=M-D\n")
    
    def and_op(self):
        self.outfile.write("M=D&M\n")

    def or_op(self):
        self.outfile.write("M=D|M\n")
    
    def neg_op(self):
        self.outfile.write("M=-D\n")
    
    def not_op(self):
        self.outfile.write("M=!D\n")
    
    def eq(self):
        self.outfile.write("D;JEQ\n")

    def gt(self):
        self.outfile.write("D;JGT\n")

    def lt(self):
        self.outfile.write("D;JLT\n")

    def writePush(self, segment, index):
        if segment == "constant":
            self.outfile.write(f"@{index}\n")
            self.outfile.write("D=A\n")
            self.pushDRegisterOntoStack()
        elif segment in ["local", "argument", "this", "that"]:
            # these are all pointers: fetch value, add index, dereference, fetch value, put on the stack
            self.outfile.write(f"@{index}\n") 
            self.outfile.write("D=A\n")
            self.outfile.write(f"@{self.segment_name_map[segment]}\n")
            self.outfile.write("A=D+M\n")
            self.outfile.write("D=M\n")
            self.pushDRegisterOntoStack()
        elif segment in ["temp", "pointer"]:
            ram_loc = self.pointer_temp_addresses[segment] + index
            # get value from ram location and then put on stack
            self.outfile.write(f"@{str(ram_loc)}\n")
            self.outfile.write("D=M\n")
            self.pushDRegisterOntoStack()
        elif segment == "static":
            varname = self.make_static_varname(index)
            self.outfile.write(f"@{varname}\n")
            self.outfile.write("D=M\n")
            self.pushDRegisterOntoStack()
        self.increaseSP()
    
    def writePop(self, segment, index):
        if segment in ["local", "argument", "this", "that"]:
            # first store target address in @R13
            self.outfile.write(f"@{index}\n")
            self.outfile.write("D=A\n")
            self.outfile.write(f"@{self.segment_name_map[segment]}\n")
            self.outfile.write("D=D+M\n") # = index + M[@LCL]/M[@ARG] etc.
            self.outfile.write("@R13\n")
            self.outfile.write("M=D\n")
            # now pop top of stack into D, dereference address in R13 and put D there
            self.popIntoDRegister()
            self.outfile.write("@R13\n")
            self.dereferenceSP()
            self.outfile.write("M=D\n")
        elif segment in ["temp", "pointer"]:
            ram_loc = self.pointer_temp_addresses[segment] + index
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M\n")
            self.outfile.write(f"@{str(ram_loc)}\n")
            self.outfile.write("M=D\n")
        elif segment == "static":
            varname = self.make_static_varname(index)
            self.decreaseSP()
            self.dereferenceSP()
            self.outfile.write("D=M\n")
            self.outfile.write(f"@{varname}\n")
            self.outfile.write("M=D\n")
    
    def writeLabel(self, label, current_func):
        if current_func:
            label = f"{current_func}${label}"
        self.outfile.write(f"({label})\n")
    
    def writeIf(self, label, current_func):
        # fetch value from top of the stack, load into D, check condition
        if current_func:
            label = f"{current_func}${label}"
        self.popIntoDRegister()
        self.outfile.write(f"@{label}\n")
        self.outfile.write("D;JNE\n")
    
    def writeGoTo(self, label, current_func):
        if current_func:
            label = f"{current_func}${label}"
        self.outfile.write(f"@{label}\n") 
        self.outfile.write("0;JMP\n")
    
    def writeFunction(self, functionName, numLocals):
        # define a label
        ## TO DO: get file name information? 
        self.writeLabel(label=functionName, current_func='')
        for ind in range(numLocals):
            self.writePush(segment="constant", index=0)

    def writeCall(self, functionName, numArgs):
        # keep track of total number of all function calls
        self.ncalls += 1
        # make unique label for return-address
        return_addr = f"{functionName}.{self.ncalls}"
        # push return-address (label declaration is after goto f)
        self.outfile.write(f"@{return_addr}\n")
        self.outfile.write("D=A\n")
        self.pushDRegisterOntoStack()
        self.increaseSP()
        # push LCL
        self.outfile.write("@LCL\n")
        self.outfile.write("D=M\n")
        self.pushDRegisterOntoStack()
        self.increaseSP()
        # push ARG
        self.outfile.write("@ARG\n")
        self.outfile.write("D=M\n")
        self.pushDRegisterOntoStack()
        self.increaseSP()
        # push THIS
        self.outfile.write("@THIS\n")
        self.outfile.write("D=M\n")
        self.pushDRegisterOntoStack()
        self.increaseSP()
        # push THAT
        self.outfile.write("@THAT\n")
        self.outfile.write("D=M\n")
        self.pushDRegisterOntoStack()
        self.increaseSP()
        # ARG = SP - n - 5
        self.outfile.write("@SP\n")
        self.outfile.write("D=M\n")
        for _ in range(5 + numArgs):
            self.outfile.write("D=D-1\n")
        self.outfile.write("@ARG\n")
        self.outfile.write("M=D\n")
        # LCL = SP
        self.outfile.write("@SP\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@LCL\n")
        self.outfile.write("M=D\n")
        # goto f
        self.writeGoTo(label=functionName, current_func='')
        self.outfile.write(f"({return_addr})\n")

    def writeReturn(self):
        # FRAME = LCL in VM language, FRAME is a temporary variable
        # save value of LCL in D then update value in FRAME
        self.outfile.write("@LCL\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@FRAME\n")
        self.outfile.write("M=D\n")
        # RET = *(FRAME-5)
        for _ in range(5):
            self.outfile.write("D=D-1\n")
        # D is now FRAME - 5
        self.outfile.write("A=D\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@RET\n")
        self.outfile.write("M=D\n")
        # *ARG = pop()
        self.popIntoDRegister()
        self.outfile.write("@ARG\n")
        self.outfile.write("A=M\n")
        self.outfile.write("M=D\n")
        # SP = ARG + 1
        self.outfile.write("@ARG\n")
        self.outfile.write("D=M+1\n")
        self.outfile.write("@SP\n") 
        self.outfile.write("M=D\n")
        # THAT = *(FRAME - 1)
        self.outfile.write("@FRAME\n")
        # D is now the correct address, now need to set value in @THAT to that address' value
        # self.outfile.write("D=M-1\n")
        self.outfile.write("AM=M-1\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@THAT\n")
        self.outfile.write("M=D\n")
        # THIS = *(FRAME - 2)
        self.outfile.write("@FRAME\n")
        self.outfile.write("AM=M-1\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@THIS\n")
        self.outfile.write("M=D\n")
        # ARG = *(FRAME - 3)
        self.outfile.write("@FRAME\n")
        self.outfile.write("AM=M-1\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@ARG\n")
        self.outfile.write("M=D\n")
        # LCL = *(FRAME - 4)
        self.outfile.write("@FRAME\n")
        self.outfile.write("AM=M-1\n")
        self.outfile.write("D=M\n")
        self.outfile.write("@LCL\n")
        self.outfile.write("M=D\n")
        # goto RET
        self.outfile.write("@RET\n")
        self.outfile.write("A=M\n")
        self.outfile.write("0;JMP\n")

    def popIntoDRegister(self):
        self.decreaseSP()
        self.dereferenceSP()
        self.outfile.write("D=M\n")
    
    def pushDRegisterOntoStack(self):
        self.outfile.write("@SP\n")
        self.dereferenceSP()
        self.outfile.write("M=D\n")

    def increaseSP(self):
        self.outfile.write("@SP\n")
        self.outfile.write("M=M+1\n")
    
    def decreaseSP(self):
        self.outfile.write("@SP\n")
        self.outfile.write("M=M-1\n")
    
    def dereferenceSP(self):
        self.outfile.write("A=M\n")

    def make_static_varname(self, index):
        var_name = Path(self.current_input_file).stem + "." + str(index)
        return var_name

    def close(self):
        self.outfile.close()


