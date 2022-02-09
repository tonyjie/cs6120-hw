import json
import sys
from utils import form_blocks, flatten

def plus_dce(func):
    # Remove unused insts globally. 
    trivial_dce(func)

    # Optimize locally. 
    local_dce(func)


def trivial_dce(func):
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

def local_dce(func):
    '''Optimize locally: kill the insturction that has unused dest var. 
    last_def: defined but not used. Dict: key: dest var; value: instr. 
    When it is defined again, we delete the instr. 
    '''
    blocks = list(form_blocks(func['instrs']))

    for block in blocks:

        last_def = dict()
        for i, instr in enumerate(block):
            # check for uses
            for arg in instr.get('args', []):
                last_def.pop(arg, None)
                
            # check for defs
            if 'dest' in instr:
                dest = instr['dest']
                if dest in last_def:
                    block.pop(last_def[dest]) # delete the unused instr
                last_def[dest] = i # add this instr into last_def
            
            # print(f"Last Def: {last_def}")
        # print(block)
    
    func['instrs'] = flatten(blocks)


MODES = {
    'tdce': trivial_dce,
    'dce+': plus_dce
}

if __name__ == "__main__":
    if (len(sys.argv) > 1):
        dce_func = MODES[sys.argv[1]]
    else:
        dce_func = trivial_dce

    prog = json.load(sys.stdin)
    for func in prog['functions']:
        dce_func(func)

    # Emit JSON IR
    json.dump(prog, sys.stdout, indent=2)
