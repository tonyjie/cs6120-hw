import sys
import json
from typing import Tuple, Callable
from utils import form_blocks, fresh

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
    

def print_df(In: dict, Out: dict):
    '''
    Print the result of Dataflow Analysis based on certain format. 
    '''
    for block_label in In.keys():
        in_var = In[block_label]
        out_var = Out[block_label]
        in_var = ', '.join(sorted(in_var)) if (len(in_var) != 0) else '∅'
        out_var = ', '.join(sorted(out_var)) if (len(out_var) != 0) else '∅'

        print(f"{block_label}:")
        # print(f"  in:  {', '.join(sorted(in_var))}")
        # print(f"  out: {', '.join(sorted(Out[block_label]))}")
        print(f"  in:  {in_var}")
        print(f"  out: {out_var}")


def forward_worklist(worklist: set, cfg: dict, block_labels: dict, blocks: list, In: dict, Out: dict, transfer: Callable) -> Tuple[dict, dict]:
    '''
    Worklist algorithms with forward propagation. 
    Args: worklist, cfg, block_labels, blocks, In, Out
    Return: (In, Out)
    '''
    while len(worklist) > 0: # not empty
        curr_label = worklist.pop() # pick a block from worklist

        if DEBUG:
            print(f"Curr label: {curr_label}")
        for pred_label in find_predecessor(cfg, curr_label):
            if DEBUG:
                print(f"Pred: {pred_label}, Out[p]: {Out[pred_label]}")
            In[curr_label] = In[curr_label].union(Out[pred_label]) # merge function: Union
            
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


def backward_worklist(worklist: set, cfg: dict, block_labels: dict, blocks: list, In: dict, Out: dict, transfer: Callable) -> Tuple[dict, dict]:
    '''
    Worklist algorithms with backward propagation. 
    Args: worklist, cfg, block_labels, blocks, In, Out
    Return: (In, Out)
    '''
    while len(worklist) > 0: # not empty
        curr_label = worklist.pop() # pick a block from worklist

        if DEBUG:
            print(f"Curr label: {curr_label}")
        for succ_label in cfg[curr_label]:
            Out[curr_label] = Out[curr_label].union(In[succ_label]) # merge function: Union


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
    transfer_func = analysis[0]
    worklist_algo = analysis[1]


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
        In[labels] = set()
        Out[labels] = set()
    
    # worklist algorithm
    In, Out = worklist_algo(worklist, cfg, block_labels, blocks, In, Out, transfer_func)

    print_df(In, Out)
            

DEBUG = False

ANALYSIS = {
    'defined': (defined_func, forward_worklist),
    'live': (live_func, backward_worklist)
}

if __name__ == "__main__":
    if (len(sys.argv) > 1):
        analysis = ANALYSIS[sys.argv[1]]

    prog = json.load(sys.stdin)
    for func in prog['functions']:
        run_df(func, analysis)
