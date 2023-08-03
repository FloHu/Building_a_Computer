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
    vm_files.append(list(input_path.glob('*.vm')))
elif input_path.is_file() and input_path.match('*.vm'):
    vm_files.append(input_path)

if len(vm_files) > 0:
    print(vm_files)
else:
    raise Exception("No .vm files found.")


# check file endings

