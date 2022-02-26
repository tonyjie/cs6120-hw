from utils import fresh, flatten

def add_entry(blocks):
    """Ensure that a CFG has a unique entry block with no predecessors.

    If the first block already has no in-edges, do nothing. Otherwise,
    add a new block before it that has no in-edges but transfers control
    to the old first block. 

    How to judge whether the first block has in-edges: if it has a label, and the label is used later. 
    """
    if 'label' in blocks[0][0]:
        first_label = blocks[0][0]['label']
        # print(f"first_label: {first_label}")
    else:
        # return blocks
        return
    
    found = False
    for instr in flatten(blocks):
        if 'labels' in instr and first_label in instr['labels']: # find in-edges to the first block. 
            found = True
            print(f"instr: {instr}")
            break
    
    if found: # insert an entry block at the beginning: including an entry label, and a jmp instruction to the first block
        new_block = [{"label": "entry.insert"}, {"labels": [first_label], "op": "jmp"}]
        blocks.insert(0, new_block) # insert at the beginning
        
    return


def get_block_labels(blocks: list) -> dict:
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

def get_succ(blocks: list, block_labels: dict) -> dict:
    '''
    Analyze the control flow graph and get the *Successors* given blocks. 

    Arguments: blocks, block_labels. 
    Return: dict. Key: label; Value: List of labels (Successors).
    '''
    cfg_succ = dict()

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

        cfg_succ[curr_label] = succ

    return cfg_succ

def get_pred(blocks: list, block_labels: dict) -> dict:
    '''
    Analyze the control flow graph and get the *Predecessors* given blocks. 

    Arguments: blocks, block_labels. 
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

    cfg_succ = get_succ(blocks, block_labels)

    for i, block in enumerate(blocks):
        curr_label = block_labels[i]
        pred = find_predecessor(cfg_succ, curr_label)
        cfg_pred[curr_label] = pred

    return cfg_pred