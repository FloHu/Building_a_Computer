# The main program should construct a Parser to parse the VM input 
# file and a CodeWriter to generate code in the corresponding output 
# file. 
# If the program's argument is a directory name rather than a file name, 
# the main program should process all the .vm files in the directory. 
# In doing so, it should use a separate Parser for handling each input 
# file and a single CodeWriter for handling the output. 

import argparse
from pathlib import Path
import os
from Parser import Parser
from CodeWriter import CodeWriter

parser = argparse.ArgumentParser(
    description = """
    Virtual machine translator.
    Handles a single command line argument, which can be either a .vm file or a directory containing one or more .vm files."""
)
parser.add_argument("input", 
                    help = "A single .vm file or a directory containing one or more .vm files", 
                    type = str)

args = parser.parse_args()
input_path = Path(args.input)

if not input_path.exists():
    raise FileNotFoundError("The file or directory you specified does not exist.")

vm_files = []

if input_path.is_dir():
    vm_files.extend(list(input_path.glob('*.vm')))
    outfilename = Path(input_path, input_path.stem + ".asm")
elif input_path.is_file() and input_path.match('*.vm'):
    vm_files.append(input_path)
    outfilename = Path(input_path.parents[0], input_path.stem + ".asm")

if len(vm_files) > 0:
    print(f"vm_files: {vm_files}")
    print()
else:
    raise Exception("No .vm files found.")

code_writer = CodeWriter(outfilename=outfilename)
print(f"Writing code to {outfilename}")

for vm_file in vm_files:
    parser = Parser(file=vm_file)
    """
    print(f"parser.codelines: {parser.codelines}")
    print()
    while True:
        try:
            parser.advance()
            print(f"parser.currentCommand: {parser.currentCommand}")
            print(f"parser.currentCommandType: {parser.currentCommandType}")
            print(f"parser.currentCommandTokens: {parser.currentCommandTokens}")
            print(f"parser.getArg1: {parser.getArg1()}")
            print(f"parser.getArg2: {parser.getArg2()}")
            print()
        except Exception as e:
            print(e)
            break
    """
    while parser.hasMoreCommands():
        try:
            parser.advance()
            cmd_type, arg1, arg2 = parser.currentCommandType, parser.getArg1(), parser.getArg2()
            code_writer.writeCommand(cmd_type=cmd_type, arg1=arg1, arg2=arg2)

        except EOFError:
            print("\nTranslation of .vm files finished")
            code_writer.close()
            break

#code_writer.close()
