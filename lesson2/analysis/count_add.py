import json
import sys

def count_add():
    count = 0
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        for instr in func['instrs']:
            if 'op' in instr:
                if instr['op'] == 'add':
                    count += 1
    print(f"The number of add instructions: {count}")

if __name__ == "__main__":
    count_add()