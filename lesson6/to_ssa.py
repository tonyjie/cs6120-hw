from collections import OrderedDict, namedtuple
import json
import sys

from utils import form_blocks, flatten, fresh
from cfg import block_map, add_entry, get_succ, get_pred
from dom import find_dom, get_dom_tree, get_dom_frontier

# def_blocks: list. A list of block names that define this var. e.g. ['entry', 'left', 'right']
# type: str. The data type of a variable. e.g. "int"
VAR_INFO = namedtuple('VAR_INFO', ['def_blocks', 'type'])

def get_var_infos(blocks: OrderedDict, func_args: list) -> dict:
    '''
    Get all the variable infos, including `def_blocks`: definitions (variable name and in which blocks it is defined) given the blocks; `type`: data type. 
    `func_args` is the variables that are defined in the first block. 

    Arguments:
        OrderedDict. 
        list. 
    Return:
        dict(str, VAR_INFO). Key: var name; Value: var info, a namedtuple containing def_blocks and type. 
    '''
    var_infos = dict()

    first_label = next(iter(blocks.keys()))

    # `func_args` is the input arguments in the function. 
    # It is equivalent with: they are defined in the first block. 
    for func_arg in func_args:
        var_info = VAR_INFO([first_label], func_arg['type'])
        var_infos[func_arg['name']] = var_info


    for name, block in blocks.items():
        for instr in block:
            if 'dest' in instr:
                var_name = instr['dest']
                var_type = instr['type']

                # add into dict. 
                if var_name not in var_infos: # initialize list
                    var_info = VAR_INFO([name], var_type)
                    var_infos[var_name] = var_info

                else: # append to the existing list
                    var_infos[var_name].def_blocks.append(name)
                    if var_infos[var_name].type != var_type: # Assume that the type of same var should be consistent all the time
                        raise RuntimeError(f"Inconsistent data type for one variable: {var_infos[var_name].type} != {var_type}")

    return var_infos

def insert_phi_nodes(blocks: OrderedDict, var_infos: dict, DF: dict, cfg_pred: dict):
    '''
    Step 1: Insert Phi Nodes into blocks. 
    e.g. `print a` -> `a: int = phi a .left a .right` + `print a`

    Note that, here the number of *a* in `labels` and `args` are the same with the # of predecessors of the block. Even though there are some predecessor blocks that don't define *a*. For this case, we should remove them in Step 2 when renaming. 
    '''

    def add_phi_node(var_name, var_info, preds): # each def_block -> one args and one labels in `phi` instr
        # print(f"preds: {preds}")
        phi_node = dict()
        phi_node['op'] = 'phi'
        phi_node['type'] = var_info.type
        phi_node['dest'] = var_name
        
        phi_node['labels'] = list(preds)
        phi_node['args'] = [var_name for pred in preds]

        return phi_node

    # 1. store a phi node for each block, each var (if needed)
    # 2. Then insert phi nodes into the block after completing storing

    # there's at most one phi node for each var in each block (if needed)
    # dict(str: block_name, dict(str, dict): phi node for each var). Key: block_name; Value: dict(str: var_name, dict: instr). Here instr is Phi Nodes. 
    phi_node_var_block = {name: dict() for name in blocks.keys()}

    # 1. store a phi node for each block, each var (if needed)
    for var_name, var_info in var_infos.items():
        for def_block in var_info.def_blocks: # blocks where var_name is assigned      
            for block in DF[def_block]: # Dominance frontier
                if var_name not in phi_node_var_block[block]: # first time to add the phi node of `var_name` in this block
                    phi_node = add_phi_node(var_name, var_info, cfg_pred[block])
                    phi_node_var_block[block][var_name] = phi_node           

                    # add block to defs[v] unless it's already in there
                    if block not in var_infos[var_name].def_blocks:
                        var_infos[var_name].def_blocks.append(block)

    # 2. insert phi nodes into the block
    for block_name, phi_node_var in phi_node_var_block.items():
        for var_name, phi_node in phi_node_var.items():
            blocks[block_name].insert(1, phi_node) 



def rename_vars(blocks: OrderedDict, var_infos: dict, cfg_succ: dict, dom_tree: dict, func_args: list):
    '''
    Step 2: rename variables. Basically we need to walk the Dominance-Tree and renaming variables as you go. Replace uses with more recent renamed def. 
    
    It's easier to understand with an example. Recursive call rename_vars(), so we are actually visiting the Dominance-Tree by Pre-Order. 

    '''
    if DEBUG:
        print(f"dom_tree: {dom_tree}")
        print(f"var infos: {var_infos}\n")

    # stack: dict(str: list). Key: var; Value: a stack of variable names (used for renaming)
    # stack is implemented by list(). append() / pop() -> push / pop. stack.top() -> stack[-1]
    stack = {var: [var] for var in var_infos.keys()}
    # func_arg is defined at the very beginning, so push it into the stack. 
    for func_arg in func_args:
        func_arg_name = func_arg['name']
        stack[func_arg_name].append(func_arg_name)

    # dict(str: list). Key: var; Value: a list containing all of the used names for this variables. This dict is recorded for generating fresh new name each time. 
    var_names = {var: list() for var in var_infos.keys()} 

    def rename(block_tuple: tuple): # block[0]: name; block[1]: block (list of instrs)
        '''
        rename function targeted at one block. This function is called recursively. 
        '''
        name, block = block_tuple

        if DEBUG:
            print(f"\nname: {name}, block: {block}")
        # record the number of `push` for each stack[var]
        # dict[str: int]. Key: var; Value: number of push in this certain function call. 
        push_num = {var: 0 for var in var_infos.keys()} 


        for instr in block:
            # replace each argument to instr with stack[old_name]. Note that here we don't take Phi-Node! 
            if ('args' in instr) and (instr.get('op', None) != 'phi'):
                # print(f"[{name}] stack: {stack}")
                for i, arg_var in enumerate(instr['args']):
                    arg_new = stack[arg_var][-1]
                    instr['args'][i] = arg_new

                    if DEBUG:
                        print(f"[{name}] arg_new: {arg_new}, arg_old: {instr['args'][i]}")

            # replace instr's destination with a new name
            if 'dest' in instr:
                dest_var = instr['dest']
                dest_new = fresh(dest_var, var_names[dest_var])
                instr['dest'] = dest_new
                # push that new name onto stack[old name]
                stack[dest_var].append(dest_new)
                push_num[dest_var] += 1

                if DEBUG:
                    print(f"[{name}] dest_new: {dest_new}, dest_old: {dest_var}")
            
        for succ in cfg_succ[name]:
            for idx, instr in enumerate(blocks[succ]): # for p in succ's Phi-Nodes
                if instr.get('op', None) == 'phi':
                    pred_idx = instr['labels'].index(name) # get the index of predecessor in instr['labels']. It should be the same order with instr['args]
                    # [TODO] can break in advance (need some extra logic to confirm that there is no more phi node)
                    phi_var = instr['args'][pred_idx]

                    if len(stack[phi_var]) > 1:
                        instr['args'][pred_idx] = stack[phi_var][-1] # read from stack[phi_var]
                    else: # len(stack[phi_var]) = 1: undefined
                        instr['args'][pred_idx] = '__undefined'

                    if DEBUG:
                        print(f"[{name}]; succ: {succ}; phi_var: {phi_var}")
                        print(f"[{name}] After renaming, phi node: {instr}")
        
        for b in dom_tree[name]: # children in the dominance tree, namely b is immediately dominated by block
            rename((b, blocks[b]))

        # pop all the names we just pushed onto the stacks (in this certain call of rename()). We only `push` for instr['dest']
        for var, num in push_num.items():
            for i in range(num):
                stack[var].pop()

        if DEBUG:
            print(f"[{name}] After popping, stack: {stack}")

    entry_block = next(iter(blocks.items()))
    rename(entry_block)
    

def to_ssa(func):
    # function input args
    func_args = func.get('args', [])

    blocks = block_map(list(form_blocks(func['instrs'])))

    add_entry(blocks)
    # add terminators? Maybe some bugs are due to this. Currently I don't add terminators manually. 

    if DEBUG:
        print(f"Blocks: \n{blocks}")

    cfg_succ = get_succ(blocks)
    cfg_pred = get_pred(blocks)

    # Dominance Analysis
    dom = find_dom(cfg_pred)
    dom_tree = get_dom_tree(dom)
    DF = get_dom_frontier(dom, cfg_succ)

    var_infos = get_var_infos(blocks, func_args)

    # Step 1: insert phi nodes
    insert_phi_nodes(blocks, var_infos, DF, cfg_pred)

    if DEBUG:
        print(f"After Step 1: \nblocks: {blocks}\n")

    # Step 2: rename variables
    rename_vars(blocks, var_infos, cfg_succ, dom_tree, func_args)


    # Assemble instructions
    func['instrs'] = flatten(blocks.values())

DEBUG = False

if __name__ == "__main__":

    # read .json file
    # with open(sys.argv[1], 'r') as f:
    #     prog = json.load(f)

    # directly read .json input
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        to_ssa(func)
        
    print(json.dumps(prog, indent=2, sort_keys=True))


# miss adding terminator

# [BUG] `if-ssa.bril` already have phi-node. 
# [BUG] `loop-branch.bril` FAIL. Multiple functions. `call`.