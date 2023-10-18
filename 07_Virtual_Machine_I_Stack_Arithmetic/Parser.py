import re
import os

class Parser:
    comment_pattern = re.compile(r"//.*")
    commandTypeLUT = {
        'push' : 'C_PUSH', 
        'pop' : 'C_POP', 
        'label' : 'C_LABEL', 
        'goto' : 'C_GOTO', 
        'if-goto' : 'C_IF', 
        'function' : 'C_FUNCTION', 
        'return' : 'C_RETURN', 
        'call' : 'C_CALL'
    }

    def __init__(self, file) -> None:
        with open(file, "r") as f:
            # store all lines from input file into an array
            # then remove all comments and whitespaces and empty lines with self.clean_code
            # what is left is assumed to be valid code
            inputlines = f.readlines()
            self.codelines = self.clean_code(inputlines=inputlines)
            self.currentCommand = ''
            self.currentFunction = ''
    
    def clean_line(self, line):
        # remove all comments and whitespace/newlines from a line
        line = self.comment_pattern.sub('', line)
        line = line.lstrip()
        line = line.rstrip()
        line = line.rstrip(os.linesep)
        return line
    
    def clean_code(self, inputlines):
        codelines = []
        for line in inputlines:
            line = self.clean_line(line)
            if len(line) > 0:
                codelines.append(line)
        return codelines

    def advance(self):
        if self.hasMoreCommands():
            self.currentCommand = self.codelines[0]
            self.currentCommandTokens = self.getCurrentCommandTokens()
            self.currentCommandType = self.getCurrentCommandType()
            self.codelines = self.codelines[1:]
        else:
            raise EOFError("No more commands in current .vm file.")

    def hasMoreCommands(self):
        return len(self.codelines) > 0
    
    def getCurrentCommandTokens(self):
        tokens = self.currentCommand.split()
        return tokens
    
    def getCurrentFunction(self):
        return self.currentFunction

    def getCurrentCommandType(self):
        ## TO DO: could introduce syntax check here if command type is not found
        cmd_type = self.commandTypeLUT.get(self.currentCommandTokens[0], 'C_ARITHMETIC')
        return cmd_type
    
    def getArg1(self):
        if self.currentCommandType == "C_RETURN":
            self.currentFunction = ''
            return ''
        elif self.currentCommandType == "C_ARITHMETIC":
            return self.currentCommandTokens[0]
        elif self.currentCommandType in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL", "C_LABEL", "C_GOTO", "C_IF"]:
            ## to do: can retrieval/parsing of current function be solved in a more elegant way? 
            if self.currentCommandType == "C_FUNCTION":
                self.currentFunction = self.currentCommandTokens[1]
            return self.currentCommandTokens[1]

    def getArg2(self):
        if self.currentCommandType in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            return int(self.currentCommandTokens[2])
        else:
            return ''
