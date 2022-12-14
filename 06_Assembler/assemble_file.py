import sys
import os
from Assembler import Assembler, Parser

assert len(sys.argv) == 2, "Please provide exactly one file to be processed by the assembler."
infile = sys.argv[1]
assert os.path.exists(infile), f"Provided file {infile} does not exist"

def main():
    parser = Parser()
    assembler = Assembler(parser)
    assembler.assemble(infile)

if __name__ == '__main__':
    main()

