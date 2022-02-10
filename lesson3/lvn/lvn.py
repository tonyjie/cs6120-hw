import json
import sys
import copy
from collections import namedtuple
from utils import form_blocks, flatten

# cloud = dict() # key: variable; value: #
# table = dict() # key: #; value: (VAL, HOME)

# table = mapping from value tuples to canonical variables, with each row numbered
# var2num = mapping from variable names to their current value numbers

# table: a List that is indexed by the *NUMBER*. The value is Tuple = (*VALUE*, *Variable*). *VALUE* is a namedtuple, containing *op*, *args*, *value*
# var2num: a Dict with the key as variable (in program) and the value as *NUMBER*. 


Value = namedtuple('Value', ['op', 'args'])

def fresh(seed, names):
    '''Generate a new name that is not in `names` starting with `seed`.
    '''
    i = 0
    while True:
        name = seed + str(i)
        if name not in names:
            return name
        i += 1


def value_equal(val0: Value, val1: Value, commute: bool) -> bool:
    '''Check if two Value object is equal. Might consider commutativity, etc. 
    '''

    def commute_equal_args(args0, args1):
        '''Check if two args are equal, considering commutativity. 
        '''
        if (args0[0] == args1[0] and args0[1] == args1[1]) or (args0[0] == args1[1] and args0[1] == args1[0]):
            return True
        else:
            return False

    # Check Commutativity
    if commute:
        if (val0.op == val1.op) and (val0.op in ['add', 'mul']): # only these two op have commutativity
            return commute_equal_args(val0.args, val1.args)

    else:
        if val0 == val1:
            return True
        else:
            return False

def find(table, val, prop, commute):
    '''find the *num* and *var* in the table if exists, according to the *val*
    '''

    if prop:
        # Constant Propagation
        if val.op == 'id':
            num = val.args[0]
            return True, (num, None)

    found = False

    if val.op != 'const': # we don't search for CONST op. We just directly put the const value into the table. 
        for i, element in enumerate(table): # element is a tuple. element[0]: a Value object; element[1]: Variable (canonical)            
            # if element[0] == val: # TODO: change the '==' into an "Equal function"     
            if value_equal(element[0], val, commute):
                found = True
                # found (num, var) according to the value in the table
                var = element[1]
                num = i
                if (DEBUG):
                    print(f'Found value in the table!  Var: {var}, Num: {num}')
                break    
    
    if found:
        return True, (num, var)
    else:
        return False, (None, None)

FOLDABLE_OPS = {
    'add': lambda a, b: a + b,
    'mul': lambda a, b: a * b,
    'sub': lambda a, b: a - b,
    'div': lambda a, b: a // b,
    'gt': lambda a, b: a > b,
    'lt': lambda a, b: a < b,
    'ge': lambda a, b: a >= b,
    'le': lambda a, b: a <= b,
    'ne': lambda a, b: a != b,
    'eq': lambda a, b: a == b,
    'or': lambda a, b: a or b,
    'and': lambda a, b: a and b,
    'not': lambda a: not a
}

def const_fold(value, num2const):
    '''Compute the result as constant value if the args are constants. Transform the instruction into *const* inst. 
    Add (num, value) key-value pair into num2const.  

    Return: constant result if it is foldable. Otherwise return None. 
    '''

    # Special cases: 
    # for Comparison op: gt, lt, ge, le, ne, eq. 
    # If value.arg[0] == value.arg[1], (e.g. 'arg1' == 'arg1'), even it is not a constant arg, we should fold and give constant result. 
    if value.op in ['gt', 'lt', 'ge', 'le', 'ne', 'eq']:
        if value.args[0] == value.args[1]:
            const_args = [0, 0] # give any two args with the same value
            return FOLDABLE_OPS[value.op](*const_args)

    # for Logic op: and, or
    if value.op == 'and':
        for arg in value.args:
            const_arg = num2const.get(arg, None) # if arg is not in num2const Dict, const_arg = None
            if const_arg == False:
                return False

    if value.op == 'or':
        for arg in value.args:
            const_arg = num2const.get(arg, None) # if arg is not in num2const Dict, const_arg = None
            if const_arg == True:
                return True

    args_are_const = True
    for arg in value.args:
        if arg not in num2const:
            args_are_const = False
            break

    if (args_are_const) and (value.op in FOLDABLE_OPS):
        const_args = [num2const[arg] for arg in value.args]

        return FOLDABLE_OPS[value.op](*const_args)
    
    else:
        return None



def change_overwritten_name(block):
    '''Loop once to change the names of overwritten variables. Note that When we change one variable's name, we need to change all the following argument's name that use this variable. 
    Therefore, we need to track where those dest variables are used. 
    '''
    last_write = dict() # key: dest variable; value: instr number that writes to the dest variable
    # When we change one variable's name, we need to change all the following argument's name that use this variable
    used_instr = dict() # key: overwritten variable; value: List containing the instr number that used the overwritten variable. 
    used_args = dict() # corresponding to the `used_instr`. key: overwritten variable; value: List consists of list, showing which argument(s) is (are) used in each used instr. 

    lvn_names = list() # names generated for the overwritten dest

    # loop once: generate names for the overwritten dest, so that we can avoid wrong argument substitutions
    for instr_index, instr in enumerate(block):
        # Check Used Arguments First. 
        # Otherwise, for testcases like: `a = 4; a = a + 1`, it would transform to 'lvn.0 = 4; a = a + 1'. 
        # The correct transformation should be `lvn.0 = 4; a = lvn.0 + 1`
        if 'args' in instr:
            # args_list = list() # used args index for each used_instr. E.g. sum1: int = add a a; If a is written before, args_list will be [0,0]
            for arg_index, arg in enumerate(instr['args']):
                if arg in last_write:
                    # args_list.append(i)
                    if arg not in used_instr:
                        used_instr[arg] = list()
                        used_args[arg] = list()

                    used_instr[arg].append(instr_index)
                    used_args[arg].append(arg_index)

        # Check Written Variables
        if 'dest' in instr:
            dest = instr['dest']

            if dest in last_write.keys(): # if instr (its index is last_write[dest]) is overwritten #TODO: this should be examines for every instr? 
                # print(f"Found in Last Write, Dest: {dest}")
                lvn_name = fresh('lvn.', lvn_names) # generate a fresh variable name
                lvn_names.append(lvn_name)
                block[last_write[dest]]['dest'] = lvn_name # change the dest name of the overwritten variable
                
                instr_id_list = used_instr.get(dest, [])
                arg_id_list = used_args.get(dest, [])

                for i, instr_id in enumerate(instr_id_list):
                    block[instr_id]['args'][arg_id_list[i]] = lvn_name

                # clean used_instr, used_args
                used_instr.pop(dest, None)
                used_args.pop(dest, None)
            
            last_write[dest] = instr_index

def lvn(func, prop, commute, fold):
    '''Local Value Numbering. 
    '''
    # deal with functions with args
    func_args = func.get('args', [])
    blocks = list(form_blocks(func['instrs']))
    for block in blocks:
        lvn_block(block, func_args, prop, commute, fold)
    func['instrs'] = flatten(blocks)


def lvn_block(block, func_args, prop, commute, fold):
    '''Local Value Numbering for each blocks. 
    '''
    
    # a List that is indexed by the *NUMBER*. The value is Tuple = (*VALUE*, *Variable*). *VALUE* is a namedtuple, containing *op*, *args*, *value*
    table = list()
    # Key: current number index of every defined variable. Value: number in the Table. Different variables can have the same number in the Table. 
    var2num = dict()
    # Key: number in the Table. Value: const value (if the value of variable could be computed)
    num2const = dict()

    # loop once to change the names of overwritten variables
    change_overwritten_name(block)

    # if func has args, put each arg into one row of table. Give each a number. var2num. table. 
    for func_arg in func_args:
        pseudo_op = 'func_arg'
        pseudo_args = list()

        num = len(table)

        val = Value(pseudo_op, pseudo_args)
        dest = func_arg['name']
        table.append((val, dest))
        
        var2num[dest] = num


    for instr in block:

        if 'op' in instr: # if this is an operation

            val_op = instr['op']
            argsvar = instr.get('args', [])
            argsnum = [var2num[argvar] for argvar in argsvar]

            # generate Value object
            val = Value(val_op, argsnum) # TODO: some op don't have args. Like `ret`, `const`

            # find the *num* and *var* in the table if exists, according to the *val*
            found, (num, var) = find(table, val, prop, commute)

            if DEBUG:
                print(f'found: {found}, num: {num}, var: {var}')

                    
            if found: # value is in the table
                # current instr is 'id', returned *num* holds a constant value

                # Replace instr with constant op
                if num in num2const:
                    const_value = num2const[num]
                    instr.update({
                        'op': 'const',
                        'value': const_value,
                    })
                    instr.pop('args', None)

                else:
                    # Replace instr with copy of var
                    instr.update({
                        'op': 'id',
                        'args': [var]
                    })

            else: # value not in table
                num = len(table)

                # Constant Folding: Compute the constant value if the *args* are all in num2constant. Compute based on the *op*
                if fold:
                    const_result = const_fold(val, num2const) # compute the constant value, and put it into num2const Dict
                    # update instruction: transform inst to *const*
                    if const_result != None:
                        instr.update({
                            'op': 'const',
                            'value': const_result,
                        })
                        instr.pop('args', None)
                    
                    
                    if DEBUG:
                        print("Const Result: ", const_result)


                if 'dest' in instr:
                    dest = instr['dest']

                    # Record constant values
                    if instr['op'] == 'const':
                        num2const[num] = instr['value'] # update num2const

                    table.append((val, dest)) # add a new line into table

                # Replace the args of the instr
                if 'args' in instr:
                    new_args = list()
                    for arg in instr['args']:
                        new_args.append(table[var2num[arg]][1])
                    instr['args'] = new_args
            
            # Update var2num dict
            if 'dest' in instr:
                var2num[instr['dest']] = num

            if DEBUG:
                print("Value: {}, Var: {}".format(val, dest))
                print("var2num: ", var2num)
                print("num2const: ", num2const)
                print("\n")


        else: # this is a label. Label can only appear at the start of the block. 
            pass



DEBUG = False



if __name__ == "__main__":
    prop = True if '-p' in sys.argv else False # constant propagation
    commute = True if '-c' in sys.argv else False # commutativity
    fold = True if '-f' in sys.argv else False # constant folding

    prog = json.load(sys.stdin)
    for func in prog['functions']:
        lvn(func, prop=prop, commute=commute, fold=fold)

    # Emit JSON IR
    json.dump(prog, sys.stdout, indent=2)
