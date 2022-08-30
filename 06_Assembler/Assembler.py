import os
import re

class Parser:
    def __init__(self, infile):
        # open file and read the first line
        # currently assumes that empty lines mean EOF
        self.infile = open(infile, "r")
        basename, extension = os.path.splitext(infile)
        outfile = basename + ".hack"
        self.outfile = open(outfile, "w")

    def advance(self):
        nextline = self.infile.readline()
        # skip empty lines
        while nextline == '\n':
            nextline = self.infile.readline()
        if not nextline:
            self.infile.close()
            self.outfile.close()
            self.hasMoreCommands = False
            print("End of file reached, closing files.")
        else:
            self.hasMoreCommands = True
        return nextline
    
    def parse_nextline(self):
        nextline = self.advance()
        # remove comments if present
        p = re.compile('//.*')
        nextline = p.sub('', nextline)
        nextline = nextline.rstrip()
        nextline = nextline.rstrip(os.linesep)
        if nextline:
            print("Found another line:", nextline)
            if nextline.startswith("@"):
                commandType = "A_COMMAND"
                self.symbol = format(int(nextline[1:]), "b") 
            elif nextline.startswith("("):
                commandType = "L_COMMAND"
            else:
                commandType = "C_COMMAND"
                components = re.search("(?P<dest>[AMD]*)?(=)?(?P<comp>[01\-D!AM|+]+)(;)?(?P<jump>.*)?", nextline)
                components = components.groupdict()
                # TO DO: add check/tests if comp had no match or if there is only one of 3 components
                for key, value in components.items():
                    if value == '':
                        components[key] = 'null'
                print(components)
                print(self.translate_mnemonics(components))
            print(commandType)
    
    def translate_mnemonics(self, components):
        dest_lut = {
            'null': '000', 
            'M': '001', 
            'D': '010', 
            'MD': '011', 
            'A': '100', 
            'AM': '101', 
            'AD': '110', 
            'AMD': '111'
        }
        # value written in two parts to distinguish between a=0 and a=1
        comp_lut = {
            '0':    '0' + '101010', 
            '1':    '0' + '111111', 
            '-1':   '0' + '111010', 
            'D':    '0' + '001100', 
            'A':    '0' + '110000', 
            '!D':   '0' + '001101', 
            '!A':   '0' + '110001', 
            '-D':   '0' + '001111', 
            '-A':   '0' + '110011', 
            'D+1':  '0' + '011111', 
            'A+1':  '0' + '110111', 
            'D-1':  '0' + '001110', 
            'A-1':  '0' + '110010', 
            'D+A':  '0' + '000010', 
            'D-A':  '0' + '010011', 
            'A-D':  '0' + '000111', 
            'D&A':  '0' + '000000', 
            'D|A':  '0' + '010101', 
            # a=1
            'M':    '1' + '110000', 
            '!M':   '1' + '110001', 
            '-M':   '1' + '110011', 
            'M+1':  '1' + '110111', 
            'M-1':  '1' + '110010', 
            'D+M':  '1' + '000010', 
            'D-M':  '1' + '010011', 
            'M-D':  '1' + '000111', 
            'D&M':  '1' + '000000', 
            'D|M':  '1' + '010101'
        }
        jump_lut = {
            'null': '000', 
            'JGT': '001', 
            'JEQ': '010', 
            'JGE': '011', 
            'JLT': '100', 
            'JNE': '101', 
            'JLE': '110', 
            'JMP': '111'
        }
        lut = {'dest': dest_lut, 'comp': comp_lut, 'jump': jump_lut}
        decoded = ''
        c_instruction_prefix = '111'
        for key in ['comp', 'dest', 'jump']:
            decoded += lut[key][components[key]]
        decoded = c_instruction_prefix + decoded
        return decoded

    def dest(self):
        pass

    def comp(self):
        pass

    def jump(self):
        pass





parser = Parser("test.asm")
parser.parse_nextline()
while parser.hasMoreCommands:
    parser.parse_nextline()
