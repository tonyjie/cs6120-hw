import json
import sys

from utils import form_blocks, flatten, fresh
from cfg import block_map, add_entry, get_succ, get_pred
from dom import find_dom, get_dom_tree, get_dom_frontier


def from_ssa(func):
    # function input args
    func_args = func.get('args', [])

    blocks = block_map(list(form_blocks(func['instrs'])))


    def add_id_instr(arg, label, instr):
        '''
        add `id` instruction in the block `label`
        '''
        # generate add_instr
        id_instr = dict()
        id_instr['op'] = 'id'
        id_instr['type'] = instr['type']
        id_instr['dest'] = instr['dest']
        id_instr['args'] = [arg]

        blocks[label].insert(-1, id_instr) # insert before the last instruction
        



    for name, block in blocks.items():
        phi_node_idx = list()
        for idx, instr in enumerate(block):
            
            if instr.get('op', None) == 'phi':
                phi_node_idx.append(idx)
                for arg, label in zip(instr['args'], instr['labels']):
                    # print(f"name: {name}, dest: {instr['dest']}, arg: {arg}, label: {label}")
                    add_id_instr(arg, label, instr)
                
        # remove this phi node. Need to delete from bottom to top, otherwise there would be some index error. 
        for phi_idx in sorted(phi_node_idx, reverse=True):
            del block[phi_idx]
    
    # Assemble instructions
    func['instrs'] = flatten(blocks.values())

                    


if __name__ == "__main__":
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        from_ssa(func)
    
    print(json.dumps(prog, indent=2, sort_keys=True))