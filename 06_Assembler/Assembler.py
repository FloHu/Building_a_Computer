import os
import re
import Code

VAR_ADDRESS_START = 16

class AssemblyError(Exception):
    pass

class SymbolTable:
    def __init__(self):
        self.table = {
            'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 
            'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 
            'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
            'SCREEN': 16384, 'KBD': 24576
            }
        self.next_free_address = VAR_ADDRESS_START
    
    def addVariable(self, variable):
        self.table[variable] = self.next_free_address
        self.next_free_address += 1

    def addLabel(self, label, address):
        # address is a ROM address
        self.table[label] = address
    
    def __getitem__(self, key):
        return self.table[key]
    
    def __contains__(self, key):
        return key in self.table


class Assembler:
    def __init__(self, parser):
        self.parser = parser

    def assemble(self, infile):
        basename, _ = os.path.splitext(infile)
        # first pass through file to generate symbol table
        with open(infile, "r") as file:
            inputlines = file.readlines()
        self.parser.first_pass(inputlines)
        # after creating symbol table run actual assembly
        outfile = basename + ".hack"
        with open(outfile, "w") as outfilehandle:
            self.parser.second_pass(inputlines, outfilehandle)


class Parser:
    def __init__(self):
        self.comment_pattern = re.compile(r"//.*")
        self.label_pattern = re.compile(r"\((?P<label>END)\)")
        self.var_pattern = re.compile(r"(?P<var>[A-Za-z])+")
        self.c_command_pattern = re.compile(r"(?P<dest>[AMD]*)?(=)?(?P<comp>[01\-D!AM|+]+)(;)?(?P<jump>.*)?")
    
    def clean_line(self, line):
        # remove comments and newlines
        line = self.comment_pattern.sub('', line)
        line = line.rstrip()
        line = line.rstrip(os.linesep)
        return line
    
    def first_pass(self, inputlines):
        self.symbol_table = SymbolTable()
        cur_line = 0
        for line in inputlines:
            line = self.clean_line(line)
            if not line:
                raise AssemblyError(f"Assembly of empty or comment-only lines currently not supported (in input line {cur_line}).")
            labelmatch = self.label_pattern.fullmatch(line)
            if not labelmatch:
                cur_line += 1
            else:
                # populate symbol_table
                label = labelmatch.groupdict()['label']
                if not label in self.symbol_table:
                    self.symbol_table.addLabel(label=label, address=cur_line)
    
    def second_pass(self, inputlines, outfilehandle):
        # symbol table, syntax checks already done in first pass
        for line in inputlines:
            line = self.clean_line(line)
            # skip lines containing label definitions (Xxx)
            if self.label_pattern.fullmatch(line):
                next
            if line.startswith("@"):
                command_type = "A_COMMAND"
                line = line[1:]
                # if variable pattern does not match it must be a value
                varmatch = self.var_pattern.match(line)
                if varmatch:
                    var = varmatch.groupdict()['var']
                    if not var in self.symbol_table:
                        self.symbol_table.addVariable(variable=var)
                    var_address = self.symbol_table[var]
                    decoded = self.translate_mnemonics(var_address, command_type)
                else:
                    decoded = self.translate_mnemonics(line, command_type)
            else:
                command_type = "C_COMMAND"
                components = self.c_command_pattern.search(line)
                components = components.groupdict()
                for key, value in components.items():
                    if value == '':
                        components[key] = 'null'
                decoded = self.translate_mnemonics(components, command_type)

            outfilehandle.write(decoded + "\n")
    
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


