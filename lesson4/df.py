import sys
import json
from typing import Tuple, Callable
from collections import namedtuple
from utils import form_blocks, fresh

# A single dataflow analysis consists of these part:
# - forward: True for forward, False for backward.
# - init: An initial value (bottom or top of the latice).
# - merge: Take a list of values and produce a single value.
# - transfer: The transfer function.
Analysis = namedtuple('Analysis', ['forward', 'init', 'merge', 'transfer'])


def get_block_name(blocks: list) -> dict:
    '''
    Get the label names for each block. 
    Return: dict. Key: index of original block list; Value: label for each block. 
    '''
    block_labels = dict()

    label_names = list()
    for i, block in enumerate(blocks):
        
        label = block[0].get('label', None)
        if label is None:
            label = fresh('block.', label_names)
            label_names.append(label)
        block_labels[i] = label
    
    return block_labels

def get_cfg(blocks: list, block_labels: dict) -> dict:
    '''
    Get the control flow graph given blocks (list of block). 

    Arguments: blocks, block_labels. 
    Return: dict. Key: label; Value: List of labels (successor).
    '''
    cfg = dict()

    for i, block in enumerate(blocks):
        succ = list()
        
        curr_label = block_labels[i]     
        last_instr = block[-1]
        if last_instr['op'] == 'jmp':
            succ.append(last_instr['labels'][0])
        elif last_instr['op'] == 'br':
            succ.extend(last_instr['labels']) # append all the labels for 'br' instr (actually only 2 labels)
        elif i < (len(blocks) - 1):
            succ.append(block_labels[i+1])

        cfg[curr_label] = succ

    return cfg

def find_predecessor(cfg: dict, curr_label: str) -> list:
    '''
    Given CFG (dict) and current label, return the labels of all predecessor blocks. 
    Return: list of str.  
    '''
    predec_labels = list()
    for label, succ in cfg.items():
        if curr_label in succ:
            predec_labels.append(label)
    return predec_labels

def defined_func(block: list, In: set) -> set:
    '''
    Forward Transfer function: Reaching Definition. 
    Go through a block with several instrs. Get the Out of the block, given In. 
    '''

    # Transfer function: Out(In) = Def(b) U In
    Out = set()
    defined = set()
    
    for instr in block:
        if 'dest' in instr:
            dest = instr['dest']
            defined.add(dest)
    
    # print("Defined: ", defined)
    Out = defined.union(In)

    return Out

def live_func(block: list, Out: set) -> set:
    '''
    Backward Transfer function: Live Variables. 
    A variable is live at some point if it holds a vlue that may be needed in the future, or equivalently if its value may be read before the next time the variable is written to. 
    '''

    # Transfer function: In(Out) = (Used(b)) Union (Out - Def(b)). 
    # Do it each line from the last instr to the first instr, so that we can handle `a=a+1`. --> a is still a live variable. 
    In = Out.copy()

    for instr in reversed(block): # from the last instr -> first instr
        if 'dest' in instr:
            dest = instr['dest']
            In.discard(dest) # - Def
        if 'args' in instr:
            args = instr['args']
            In.update(args)

    return In

def cprop_func(block: list, In: dict) -> dict:
    '''
    Forward Transfer function: Constant propagation. 
    Which variables have statically knowable constant values?
    In: dict. Key: variable name (dest); Value: value. 
    '''
    Out = In.copy()

    for instr in block:
        if 'dest' in instr:
            if instr.get('op', None) == 'const': # const op
                Out[instr['dest']] = instr['value']
            else: # Arithmetic / Logic / Comparison op
                Out[instr['dest']] = '?'

    return Out



def cprop_merge(dicts):
    '''
    Merge function for *cprop* (Constant Propagation)
    For the same var, if value is the same -> keep it; if value is different -> value = ?
    '''
    out = dict()
    for d in dicts:
        for var, value in d.items():
            if var in out: # same var
                if value == out[var]: # value is the same
                    out[var] = value
                else:
                    out[var] = '?' # value is different
            else: # new var
                out[var] = value

    return out


def union(sets):
    '''
    Merge function for *defined* and *live*
    '''
    out = set()
    for s in sets:
        out.update(s)
    return out

def print_df(In: dict, Out: dict):
    '''
    Print the result of Dataflow Analysis based on certain format. 
    in_var, out_var could be *set* or *dict*
    '''


    for block_label in In.keys():
        in_var = In[block_label]
        out_var = Out[block_label]

        if isinstance(in_var, set):
            in_var = ', '.join(sorted(in_var)) if (len(in_var) != 0) else '∅'
            out_var = ', '.join(sorted(out_var)) if (len(out_var) != 0) else '∅'
        elif isinstance(in_var, dict):
            if (len(in_var) != 0):
                in_var = ', '.join('{}: {}'.format(k, v)
                                            for k,v in sorted(in_var.items()))
            else:
                in_var = '∅'
            
            if (len(out_var) != 0):
                out_var = ', '.join('{}: {}'.format(k, v)
                                        for k,v in sorted(out_var.items()))
            else:
                out_var = '∅'

        print(f"{block_label}:")
        # print(f"  in:  {', '.join(sorted(in_var))}")
        # print(f"  out: {', '.join(sorted(Out[block_label]))}")
        print(f"  in:  {in_var}")
        print(f"  out: {out_var}")


def forward_worklist(worklist: set, cfg: dict, block_labels: dict, blocks: list, In: dict, Out: dict, transfer: Callable, merge: Callable) -> Tuple[dict, dict]:
    '''
    Worklist algorithms with forward propagation. 
    Args: worklist, cfg, block_labels, blocks, In, Out
    Return: (In, Out)
    '''
    while len(worklist) > 0: # not empty
        curr_label = worklist.pop() # pick a block from worklist

        if DEBUG:
            print(f"Curr label: {curr_label}")
        
        In[curr_label] = merge(Out[pred_label] for pred_label in find_predecessor(cfg, curr_label)) # merge function
            
        block_index = list(block_labels.keys())[list(block_labels.values()).index(curr_label)] # find key by value in dict (block_labels)
        curr_block = blocks[block_index]
        
        Out_old = Out[curr_label] # set. old Out[b]

        if DEBUG:
            print(f"Before: In: {In[curr_label]}, Out: {Out[curr_label]}")
        Out[curr_label] = transfer(curr_block, In[curr_label]) # transfer function

        if Out[curr_label] != Out_old: # out[b] changed
            worklist.update(cfg[curr_label]) # add sucessors of b
        
        if DEBUG:
            print(f"After: In: {In[curr_label]}, Out: {Out[curr_label]}")
            print(f"Worklist: {worklist}")
            print("\n")
    
    return In, Out


def backward_worklist(worklist: set, cfg: dict, block_labels: dict, blocks: list, In: dict, Out: dict, transfer: Callable, merge: Callable) -> Tuple[dict, dict]:
    '''
    Worklist algorithms with backward propagation. 
    Args: worklist, cfg, block_labels, blocks, In, Out
    Return: (In, Out)
    '''
    while len(worklist) > 0: # not empty
        curr_label = worklist.pop() # pick a block from worklist

        if DEBUG:
            print(f"Curr label: {curr_label}")

        Out[curr_label] = merge(In[succ_label] for succ_label in cfg[curr_label]) # merge function


        block_index = list(block_labels.keys())[list(block_labels.values()).index(curr_label)] # find key by value in dict (block_labels)
        curr_block = blocks[block_index]
        
        In_old = In[curr_label] # set. old In[b]

        if DEBUG:
            print(f"Before: In: {In[curr_label]}, Out: {Out[curr_label]}")
        In[curr_label] = transfer(curr_block, Out[curr_label]) # transfer function

        if In[curr_label] != In_old: # in[b] changed
            worklist.update(find_predecessor(cfg, curr_label)) # add predecessors of b
        
        if DEBUG:
            print(f"After: In: {In[curr_label]}, Out: {Out[curr_label]}")
            print(f"Worklist: {worklist}")
            print("\n")
    
    return In, Out    



def run_df(func, analysis):
    '''
    Run dataflow analysis given the analysis method. 

    Data sturctures;
        blocks: list. Index -> Block.
        block_labels: dict. Key: Index; Value: Label name of the block. 
        In: dict. Key: Label; Value: variables (set)
        Out: dict. Key: Label; Value: variables (set)
        worklist: Set. Elements are Labels of *blocks*. 
        cfg: dict. Key: label; Value: list of labels. 
    '''

    if analysis.forward:
        worklist_algo = forward_worklist
    else:
        worklist_algo = backward_worklist

    blocks = list(form_blocks(func['instrs']))
    
    # get block name for each block
    block_labels = get_block_name(blocks)

    cfg = get_cfg(blocks, block_labels)

    # worklist = all blocks
    worklist = set(block_labels.values())

    # initialization
    In = dict()
    Out = dict()

    for labels in block_labels.values():
        In[labels] = analysis.init
        Out[labels] = analysis.init
    
    # worklist algorithm
    In, Out = worklist_algo(worklist, cfg, block_labels, blocks, In, Out, analysis.transfer, analysis.merge)

    print_df(In, Out)
            

DEBUG = False


ANALYSIS = {
    'defined': Analysis(True, init=set(), merge=union, transfer=defined_func),
    'live': Analysis(False, init=set(), merge=union, transfer=live_func),
    'cprop': Analysis(True, init=dict(), merge=cprop_merge, transfer=cprop_func)
}

if __name__ == "__main__":
    if (len(sys.argv) > 1):
        analysis = ANALYSIS[sys.argv[1]]

    prog = json.load(sys.stdin)
    for func in prog['functions']:
        run_df(func, analysis)
