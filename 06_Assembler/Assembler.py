import os
import re
import sys
import Code

class AssemblyError(Exception):
    pass

class SymbolTable:
    def __init__(self):
        self.table = {
            'variables': 
                {
                'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 
                'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 
                'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14
                }, 
            'labels': {}
            }
        self.next_free_address = 15
    
    def addVariable(self, variable):
        self.table['variables'][variable] = self.next_free_address
        self.next_free_address += 1

    def addLabel(self, label, value):
        self.table['labels'][label] = value


class Assembler:
    def __init__(self, parser):
        self.parser = parser

    def assemble(self, infile):
        basename, _ = os.path.splitext(infile)
        # first pass through file to generate symbol table
        self.first_pass(infile)
        # after creating symbol table run actual assembly
        outfile = basename + ".hack"
        outfile = open(outfile, "w")
        cur_line = 0
        with open(infile, "r") as input:
            for nextline in input:
                try:
                    self.parser.parse_line(nextline, current_line = cur_line)
                except AssemblyError:
                    outfile.close()
                    raise
                outfile.write(self.parser.decoded + '\n')
                print(f"Decoded nextline to {self.parser.decoded}")
                cur_line += 1
        outfile.close()

    def first_pass(self, infile):
        cur_line = 0
        with open(infile, "r") as input:
            for nextline in input:
                self.parser.parse_line(nextline, current_line = cur_line)

    def second_pass(self, infile):
        pass


class Parser:
    def __init__(self):
        self.symbolTable = SymbolTable()
    
    def parse_line(self, nextline, current_line):
        p = re.compile('//.*')
        nextline = p.sub('', nextline)
        nextline = nextline.rstrip()
        if not nextline:
            raise AssemblyError(f"Assembly of empty or comment-only lines currently not supported (in input line {current_line}).")
        nextline = nextline.rstrip(os.linesep)
        decoded = ''
        if nextline:
            if nextline.startswith("@"):
                self.commandType = "A_COMMAND"
                nextline = nextline[1:]
                # can be either a value or a variable
                ## TO DO: handle syntax errors
                varpattern = re.compile(r"(?P<var>[A-Za-z])+")
                has_varmatch = varpattern.match(nextline)
                if has_varmatch:
                    var = has_varmatch.groupdict()['var']
                    address = self.symbolTable.table['variables'].get(var)
                    if not address:
                        self.symbolTable.addVariable(var)
                    decoded = self.translate_mnemonics(self.symbolTable.table['variables'].get(var), self.commandType)
                else:
                    decoded = self.translate_mnemonics(nextline, self.commandType)
            elif nextline.startswith("("):
                self.commandType = "L_COMMAND"
            else:
                self.commandType = "C_COMMAND"
                pattern = re.compile("(?P<dest>[AMD]*)?(=)?(?P<comp>[01\-D!AM|+]+)(;)?(?P<jump>.*)?")
                components = pattern.search(nextline)
                components = components.groupdict()
                for key, value in components.items():
                    if value == '':
                        components[key] = 'null'
                decoded = self.translate_mnemonics(components, self.commandType)
        ## TO DO: separate into fields
        self.decoded = decoded
    
    def translate_mnemonics(self, components, command_type):
        decoded = ''
        if command_type == 'A_COMMAND':
            prefix = '0'
            decoded = prefix + format(int(components), "015b")
        elif command_type == 'C_COMMAND':
            prefix = '111'
            for key in ['comp', 'dest', 'jump']:
                decoded += Code.lookup_table[key][components[key]]
            decoded = prefix + decoded
        elif command_type == 'L_COMMAND':
            pass
        else:
            raise ValueError()
        return decoded


