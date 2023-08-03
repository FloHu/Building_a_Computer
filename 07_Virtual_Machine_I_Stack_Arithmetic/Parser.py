import re
import os

class Parser:
    comment_pattern = re.compile(r"//.*")

    def __init__(self, file) -> None:
        with open(file, "r") as f:
            # store all lines from input file into an array
            # then remove all comments and whitespaces and empty lines with self.clean_code
            # what is left is assumed to be valid code
            inputlines = f.readlines()
            self.codelines = self.clean_code(inputlines=inputlines)
            self.currentCommand = ''
    
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
            self.codelines = self.codelines[1:]
        else:
            raise EOFError("No more commands in current .vm file.")

    def hasMoreCommands(self):
        return len(self.codelines) > 0
