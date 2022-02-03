import json
import json
import sys

def dce(func):
    # Global analysis
    used = set()

    remove = True # Flag for remove insts. True if there is a removal in this iteration. If not, the loop is done. 
    while (remove == True):
        remove = False
        used.clear()

        for instr in func['instrs']:
            if 'args' in instr:
                # print(instr['args'])
                for arg in instr['args']:
                    used.add(arg)
        # print(used)
        for instr in func['instrs']:
            if ('dest' in instr) and (instr['dest'] not in used):
                func['instrs'].remove(instr) # delete instr in json
                remove = True


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        dce(func)
    # Emit JSON IR
    json.dump(prog, sys.stdout, indent=2)