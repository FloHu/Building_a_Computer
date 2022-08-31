import os
import re
import Code

class Parser:
    def __init__(self, infile):
        # open file and read the first line
        # currently assumes that empty lines mean EOF
        self.infile = open(infile, "r")
        basename, _ = os.path.splitext(infile)
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
            #print("Found another line:", nextline)
            if nextline.startswith("@"):
                commandType = "A_COMMAND"
                #print(self.translate_mnemonics(nextline, commandType))
                decoded = self.translate_mnemonics(nextline, commandType)
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
                #print(components)
                #print(self.translate_mnemonics(components, commandType))
                decoded = self.translate_mnemonics(components, commandType)
            #print(commandType)
            self.outfile.write(decoded + "\n")
    
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
        else:
            raise ValueError()
        return decoded



parser = Parser("test.asm")
parser.parse_nextline()
while parser.hasMoreCommands:
    parser.parse_nextline()
