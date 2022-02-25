import json
import sys

from utils import form_blocks
from cfg import get_block_labels, get_succ, get_pred, add_entry

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
        

def get_dom_tree(dom: dict, cfg_pred: dict) -> dict:
    '''
    Get the Dominator Tree given the dom dict, return a dict called `dom_tree`.
    If A is predecessor of B, and A is also dominator of B, then node A immediately dominates B. 
    We compute the intersection of `dom` and `cfg_pred` to get the immediate dominator -> form the dominator tree. 

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
    
    for block_label, dom_labels in dom.items():
        pred_set = set(cfg_pred[block_label])
        imm_doms = pred_set.intersection(dom_labels) # imm_doms: set containing the immediate dominators of block_labels. 
        # print(f"block_label: {block_label}, imm_doms: {imm_doms}")
        for imm_dom in imm_doms:
            dom_tree[imm_dom].append(block_label) # A is immediate dominator of B -> A is the parent node of B in Dominator Tree. 
    
    return dom_tree

def get_dom_frontier(dom: dict, cfg_succ: dict) -> dict:
    '''
    A's domination frontier contains B if A does not dominate B, but A dominates a predecessor of B. 
    Equal to: A's domination frontier contains C, if A dominates B, and A does not dominate C (the successor of B)

    Arguments:
        dom: dict. Key: block label; Value: *set* of block labels.
        cfg_succ: dict. Key: block label; Value: *list* of block labels. 
    Return:
        df: dict. Key: block label; Value: *list* of block labels. 
    '''
    df = dict()
    # initialization: empty list
    for block_label in dom.keys():
        df[block_label] = list()
    
    for block_label, dom_labels in dom.items(): # block_label: B
        succ_list = cfg_succ[block_label]
        for dom_label in dom_labels: # dom_label: A
            for succ in succ_list:
                if dom_label not in dom[succ]: # dom[succ] is the dominators of succ (C). If A is not the dominator of C
                    df[dom_label].append(succ)

    return df

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


def dom_analysis(func, modes):
    '''
    Dominance Analysis. 
    '''
    for mode in modes:
        if mode not in ['-dom', '-tree', '-frontier']:
            raise ValueError(f"Invalid Argument: {mode}")


    blocks = list(form_blocks(func['instrs']))
    # Ensure that a CFG has a unique entry block with no predecessor
    add_entry(blocks)

    block_labels = get_block_labels(blocks)
    cfg_succ = get_succ(blocks, block_labels)
    cfg_pred = get_pred(blocks, block_labels)

    # print(f"Succ: {cfg_succ}")
    # print(f"Pred: {cfg_pred}")

    dom = find_dom(cfg_pred)

    dom_tree = get_dom_tree(dom, cfg_pred)

    df = get_dom_frontier(dom, cfg_succ)

    if '-dom' in modes: # Find Dominators for a function
        print(f"Dom: {dom}\n")
    if '-tree' in modes: # Construct the dominance tree
        print(f"Dom Tree: {dom_tree}\n")
    if '-frontier' in modes: # Compute the dominance frontier
        print(f"Dom Frontier: {df}\n")


if __name__ == "__main__":
    if (len(sys.argv) > 1):
        modes = sys.argv[1:]

    prog = json.load(sys.stdin)

    for func in prog['functions']:
        dom_analysis(func, modes)

