import json
import sys
from utils import form_blocks
from cfg import get_block_labels, get_succ, get_pred

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
        

def get_dom_tree(dom: dict) -> dict:
    '''
    Get the Dominator Tree given the dom dict, return a dict called `dom_tree`.

    Arguments:
        dom: dict. Key: block label; Value: *set* of block labels.
    Return:
        dom_tree: dict. Key: block label; Value: *list* of block labels. Each element in the list is a child node of the Key node. 
    '''
    dom_tree = dict()
    # initialization: empty list
    for block_label in dom.keys():
        dom_tree[block_label] = list()
    
    for block_label, dom_labels in dom.items():
        for dom_label in list(dom_labels):
            if dom_label != block_label: # not itself. e.g. 'loop' is the dominator of 'loop'
                dom_tree[dom_label].append(block_label)
    
    return dom_tree




def find_dom(func):
    '''
    Algorithm for Finding Dominators. 
    A dominates B iff all paths from the entry to B include A. --> A is the dominator of B. 

    Return: dict. Key: block label; Value: *set* of block labels.
    Note that block labels are all unique. 
    '''

    blocks = list(form_blocks(func['instrs']))

    block_labels = get_block_labels(blocks)
    cfg_succ = get_succ(blocks, block_labels)
    cfg_pred = get_pred(blocks, block_labels)

    # print(f"Succ: {cfg_succ}")
    # print(f"Pred: {cfg_pred}")

    dom = dict()
    # initialization: {every block -> all blocks}
    all_blocks = set(block_labels.values())
    for block_label in block_labels.values():
        dom[block_label] = all_blocks


    while True:
        changed = False
        for block_label in block_labels.values():

            new_dom = {block_label} | (intersect([dom[p] for p in cfg_pred[block_label]]))

            if dom[block_label] != new_dom:
                changed = True
                dom[block_label] = new_dom

            # print(f"Block_Label: {block_label}, dom: {dom}")

        if changed == False:
            break

    print(f"Dom: {dom}")

    dom_tree = get_dom_tree(dom)
    print(f"Dom Tree: {dom_tree}")
    
    


if __name__ == "__main__":
    prog = json.load(sys.stdin)
    
    for func in prog['functions']:
        find_dom(func)

