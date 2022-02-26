import json
import sys

from utils import form_blocks
from cfg import block_map, add_entry, get_succ, get_pred

def to_ssa(func):
    blocks = block_map(list(form_blocks(func['instrs'])))

    add_entry(blocks)
    # add terminators? Maybe some bugs are due to this. Currently I don't add terminators manually. 

    succ = get_succ(blocks)
    print(f"succ: {succ}")
    
    pred = get_pred(blocks)
    print(f"pred: {pred}")



if __name__ == "__main__":

    # read .json file
    # with open(sys.argv[1], 'r') as f:
    #     prog = json.load(f)

    # directly read .json input
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        to_ssa(func)