import copy

def intersect(sets: list) -> set:
    '''
    Get the intersection of a list of sets.
    If input list is empty, return a empty set. 

    Arguments: 
        sets: list of set. 
    Return:
        set
    '''
    out = set()
    # print(f"sets: {sets}")
    for i, input in enumerate(sets):
        if i == 0:
            out = input # first set
        else:
            out = out & input # intersect

    return out

def get_dom_frontier(dom: dict, cfg_succ: dict) -> dict:
    '''
    A's domination frontier contains B if A does not *strictly dominate* B, but A *dominates* a predecessor of B. 
    (Note that here: one is *strict dominate*, anotehr is *dominate*)

    Equal to: A's domination frontier contains C, if A *dominates* B, and A does not *strictly dominate* C (the successor of B)

    Arguments:
        dom: dict. Key: block label; Value: *set* of block labels.
        cfg_succ: dict. Key: block label; Value: *list* of block labels. 
    Return:
        df: dict. Key: block label; Value: *list* of block labels. 
    '''
    # generate a strict_dom dict
    strict_dom = copy.deepcopy(dom)
    for block_label, dom_labels in strict_dom.items():
        strict_dom[block_label].remove(block_label)

    df = dict()
    # initialization: empty list
    for block_label in dom.keys():
        df[block_label] = list()
    
    for block_label, dom_labels in dom.items(): # block_label: B
        succ_list = cfg_succ[block_label]
        for dom_label in dom_labels: # dom_label: A
            for succ in succ_list:
                # print(f"A: {dom_label}, B: {block_label}, C: {succ}")
                if dom_label not in strict_dom[succ]: # dom[succ] is the strict dominators of succ (C). If A is not the strict dominator of C
                    df[dom_label].append(succ)
                    # print(f"YES! A: {dom_label}, C: {succ}")

    return df

def get_dom_tree(dom: dict) -> dict:
    '''
    Get the Dominator Tree given the dom dict, return a dict called `dom_tree`.

    A immediately dominates B iff A strictly dominates B, but A does not strictly dominate any other node that strictly dominates B. 

    Arguments:
        dom: dict. Key: block label; Value: *set* of block labels.
        cfg_pred: dict. Key: block label; Value: *list* of block labels. 
    Return:
        dom_tree: dict. Key: block label; Value: *list* of block labels. Each element in the list is a child node of the Key node. 
    '''
    dom_tree = dict()
    # initialization: empty list
    for block_label in dom.keys():
        dom_tree[block_label] = list()

    # generate a strict_dom dict
    strict_dom = copy.deepcopy(dom)
    for block_label, dom_labels in strict_dom.items():
        strict_dom[block_label].remove(block_label)

    for block_label, dom_labels in strict_dom.items(): # B: block_label
        for dom_label in dom_labels: # A: dom_label
            result = True
            for strict_dom_label in strict_dom[block_label]: # node that strictly dominates B
                if dom_label in strict_dom[strict_dom_label]: # A dominate one node that strictly dominates B, then A does not imm dominates B. 
                    result = False
            if result:
                dom_tree[dom_label].append(block_label)

    return dom_tree

def find_dom(cfg_pred: dict) -> dict:
    '''
    Algorithm for Finding Dominators. 
    A dominates B iff all paths from the entry to B include A. --> A is the dominator of B. 

    Arguments: 
        cfg_pred: dict. Key: block label; Value: *list* of block labels. 
    Return: 
        dom: dict. Key: block label; Value: *set* of block labels.
    Note that block labels are all unique. 
    '''
    dom = dict()
    # initialization: {every block -> all blocks}
    all_blocks = set(cfg_pred.keys())
    for block_label in cfg_pred.keys():
        dom[block_label] = all_blocks    
    while True:
        changed = False
        for block_label in cfg_pred.keys():

            new_dom = {block_label} | (intersect([dom[p] for p in cfg_pred[block_label]]))

            if dom[block_label] != new_dom:
                changed = True
                dom[block_label] = new_dom

            # print(f"Block_Label: {block_label}, dom: {dom}")

        if changed == False:
            break   
 
    return dom