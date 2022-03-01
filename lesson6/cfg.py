from collections import OrderedDict
from utils import fresh, flatten

def block_map(blocks: list) -> OrderedDict:
    """Given a sequence of basic blocks, which are lists of instructions,
    produce a `OrderedDict` mapping names to blocks.

    The name of the block comes from the label it starts with, if any.
    Anonymous blocks, which don't start with a label, get an
    automatically generated name. Blocks in the mapping have their
    labels removed.

    Arguments:
        blocks: list
    Return:
        OrderedDict. 
    """
    by_name = OrderedDict()

    label_names = list()

    for block in blocks:
        # Generate a name for the block.
        name = block[0].get('label', None)
        if name is None:
            name = fresh('block', label_names)
            # directly add the label instr into the blocks
            label_instr = {"label": name}
            block.insert(0, label_instr)

        # Add the block to the mapping.
        by_name[name] = block

    return by_name


def add_entry(blocks: OrderedDict):
    """Ensure that a CFG has a unique entry block with no predecessors.

    If the first block already has no in-edges, do nothing. Otherwise,
    add a new block before it that has no in-edges but transfers control
    to the old first block. 

    How to judge whether the first block has in-edges: if it has a label, and the label is used later. 
    """
    first_label = next(iter(blocks.keys()))

    found = False
    for instr in flatten(blocks.values()):
        if 'labels' in instr and first_label in instr['labels']: # find in-edges to the first block. 
            found = True
            break

    if found: # insert an entry block at the beginning: including an entry label, and a jmp instruction to the first block
        insert_entry_name = 'entry.insert'
        new_block = [{"label": insert_entry_name}, {"labels": [first_label], "op": "jmp"}]
        blocks[insert_entry_name] = new_block
        blocks.move_to_end(insert_entry_name, last=False) # insert at the beginning


def get_succ(blocks: OrderedDict) -> dict:
    '''
    Analyze the control flow graph and get the *Successors* given blocks. 

    Arguments: OrderedDict. Key: name; Value: block
    Return: dict. Key: label; Value: List of labels (Successors).
    '''
    cfg_succ = dict()

    for i, (name, block) in enumerate(blocks.items()):
        succ = list() 
        last_instr = block[-1]
        if last_instr['op'] == 'jmp':
            succ.append(last_instr['labels'][0])
        elif last_instr['op'] == 'br':
            succ.extend(last_instr['labels']) # append all the labels for 'br' instr (actually only 2 labels)
        elif i < (len(blocks) - 1):
            succ.append(list(blocks.keys())[i+1])

        cfg_succ[name] = succ

    return cfg_succ

def get_pred(blocks: OrderedDict) -> dict:
    '''
    Analyze the control flow graph and get the *Predecessors* given blocks. 

    Arguments: OrderedDict. Key: name; Value: block
    Return: dict. Key: label; Value: List of labels (Predecessors).    
    '''
    def find_predecessor(cfg_succ: dict, curr_label: str) -> list:
        '''
        Given CFG (dict) and current label, return the labels of all predecessor blocks. 
        Return: list of str.  
        '''
        pred = list()
        for label, succ in cfg_succ.items():
            if curr_label in succ:
                pred.append(label)
        return pred

    cfg_pred = dict()

    cfg_succ = get_succ(blocks)

    for i, (name, block) in enumerate(blocks.items()):
        # curr_label = block_labels[i]
        pred = find_predecessor(cfg_succ, name)
        cfg_pred[name] = pred

    return cfg_pred