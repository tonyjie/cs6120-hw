import argparse
import json

def transform(prog, trace):
    new_instrs = list() # instructions after transformation
    speculate_instr = {
        "op": "speculate"
    }
    new_instrs.append(speculate_instr) # add speculate instruction at the beginning, as we trace the whole program


    for trace_func in trace['functions']:
        for index, trace_instr in enumerate(trace_func['instrs']):
            if trace_instr['op'] == 'br':
                # replace branch instruction with guard instruction. 
                # But here we need to change the condition of guard instruction based on profiling result (take cond or not) for the performance reason: we want the whole trace to be executed. 
                # Otherwise, it would fall back to the beginning of the program, and run it again. -> Leads to nearly double instruction count in total. 
                
                # So the tricky part is that we need to know which branch is taken, and guard the correct condition.

                take_cond = False # whether to take the conditional branch
                fail_label = "main_entry"

                next_instr = trace_func['instrs'][index+1] # next instruction after `br`
                label0 = trace_instr['labels'][0] # label0 is the label being jumped to if cond is true
                
                for prog_func in prog['functions']:
                    for idx, prog_instr in enumerate(prog_func['instrs']):
                        if 'label' in prog_instr and prog_instr['label'] == label0: # the label (cond true) matches
                            if prog_func['instrs'][idx+1] == next_instr: # next_instr is the next instruction after label0
                                take_cond = True
                                break

                if take_cond:
                    # if we are guarding cond, jump to label1 if failed
                    cond = trace_instr['args']
                    # fail_label = trace_instr['labels'][1]
                else:
                    # if we are guarding not cond, jump to label0 if failed
                    cond_not_op = {"op" : "not", "args" : trace_instr['args'], "type" : "bool", "dest" : "not_cond"}
                    new_instrs.append(cond_not_op)
                    cond = ['not_cond']
                    # fail_label = trace_instr['labels'][0]

                guard_instr = {
                    "op": "guard",
                    "args" : cond,
                    "labels" : [fail_label]
                }
                new_instrs.append(guard_instr)
            
            else:
                if trace_instr['op'] != 'jmp': # eliminate `jmp`
                    new_instrs.append(trace_instr)
    
    new_instrs.append({"op": "commit"}) # add commit instruction at the end    
    new_instrs.append({"op": "ret"}) # add ret instruction after "speculate - commit" block


    new_instrs.append({"label": "main_entry"}) # add main_entry label at the beginning of the whole program. If trace guard fails, it would fall back to here. 
    
    # Add new_instrs ahead of instructions in main function of `prog`
    for prog_func in prog['functions']:
        if prog_func['name'] == 'main':
            new_instrs.extend(prog_func['instrs'])
            prog_func['instrs'] = new_instrs
            break
    
    return prog



def main(args):
    with open(args.src, 'r') as f:
        prog = json.load(f)
    with open(args.trace, 'r') as f:
        trace = json.load(f)
        
    prog_transform = transform(prog, trace)

    print(json.dumps(prog_transform, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-trace', dest='trace', 
                        action='store', type=str, help='json trace file')
    parser.add_argument("-src", dest='src',
                        action='store', type=str, help="bril source file")
    args = parser.parse_args()
    main(args)