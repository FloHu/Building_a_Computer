import os
import re
import Code

class Assembler:
    def __init__(self, parser):
        self.parser = parser
    
    def assemble(self, infile):
        basename, _ = os.path.splitext(infile)
        outfile = basename + ".hack"
        outfile = open(outfile, "w")
        with open(infile, "r") as input:
            for nextline in input:
                decoded = self.parser.parse_nextline(nextline)
                if decoded:
                    print(f"Decoded nextline to {decoded}")
                    outfile.write(decoded + '\n')
        outfile.close()

class Parser:
    def parse_nextline(self, nextline):
        p = re.compile('//.*')
        nextline = p.sub('', nextline)
        nextline = nextline.rstrip()
        nextline = nextline.rstrip(os.linesep)
        decoded = ''
        if nextline:
            if nextline.startswith("@"):
                commandType = "A_COMMAND"
                decoded = self.translate_mnemonics(nextline, commandType)
            elif nextline.startswith("("):
                commandType = "L_COMMAND"
            else:
                commandType = "C_COMMAND"
                components = re.search("(?P<dest>[AMD]*)?(=)?(?P<comp>[01\-D!AM|+]+)(;)?(?P<jump>.*)?", nextline)
                components = components.groupdict()
                for key, value in components.items():
                    if value == '':
                        components[key] = 'null'
                decoded = self.translate_mnemonics(components, commandType)
        return decoded
    
    def translate_mnemonics(self, components, command_type):
        decoded = ''
        if command_type == 'A_COMMAND':
            prefix = '0'
            decoded = prefix + format(int(components[1:]), "015b")
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


