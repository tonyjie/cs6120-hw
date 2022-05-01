from re import template
import lark
import z3
import sys
import itertools

# A language based on a Lark example from:
# https://github.com/lark-parser/lark/wiki/Examples
GRAMMAR = """
?start: sum
  | sum "?" sum ":" sum -> if

?sum: term
  | sum "and" term      -> and
  | sum "or" term       -> or
  | sum "+" term        -> add
  | sum "-" term        -> sub

?term: item
  | term "*"  item      -> mul
  | term "/"  item      -> div
  | term ">>" item      -> shr
  | term "<<" item      -> shl

?item: NUMBER           -> num
  | "not" item          -> not
  | "-" item            -> neg
  | CNAME               -> var
  | "(" start ")"

%import common.NUMBER
%import common.WS
%import common.CNAME
%ignore WS
""".strip()


def interp(tree, lookup):
    """Evaluate the arithmetic expression.

    Pass a tree as a Lark `Tree` object for the parsed expression. For
    `lookup`, provide a function for mapping variable names to values.
    """

    op = tree.data
    if op in ('add', 'sub', 'mul', 'div', 'shl', 'shr', 'and', 'or'):  # Binary operators.
        lhs = interp(tree.children[0], lookup)
        rhs = interp(tree.children[1], lookup)
        if op == 'add':
            return lhs + rhs
        elif op == 'sub':
            return lhs - rhs
        elif op == 'mul':
            return lhs * rhs
        elif op == 'div':
            return lhs / rhs
        elif op == 'shl':
            return lhs << rhs
        elif op == 'shr':
            return lhs >> rhs
        elif op == 'and': # for boolean support
            return z3.And(lhs, rhs)
        elif op == 'or':  # for boolean support
            return z3.Or(lhs, rhs)
    
    elif op == 'not': # for boolean support
        sub = interp(tree.children[0], lookup)
        return z3.Not(sub)

    elif op == 'neg':  # Negation.
        sub = interp(tree.children[0], lookup)
        return -sub
    elif op == 'num':  # Literal number.
        return int(tree.children[0])
    elif op == 'var':  # Variable lookup.
        return lookup(tree.children[0])
    elif op == 'if':  # Conditional.
        cond = interp(tree.children[0], lookup)
        true = interp(tree.children[1], lookup)
        false = interp(tree.children[2], lookup)
        return (cond != 0) * true + (cond == 0) * false


def pretty(tree, subst={}, paren=False):
    """Pretty-print a tree, with optional substitutions applied.

    If `paren` is true, then loose-binding expressions are
    parenthesized. We simplify boolean expressions "on the fly."
    """

    # Add parentheses?
    if paren:
        def par(s):
            return '({})'.format(s)
    else:
        def par(s):
            return s

    op = tree.data
    if op in ('add', 'sub', 'mul', 'div', 'shl', 'shr', 'and', 'or'):
        lhs = pretty(tree.children[0], subst, True)
        rhs = pretty(tree.children[1], subst, True)
        c = {
            'add': '+',
            'sub': '-',
            'mul': '*',
            'div': '/',
            'shl': '<<',
            'shr': '>>',
            'and': 'and',
            'or': 'or'
        }[op]
        return par('{} {} {}'.format(lhs, c, rhs))
    elif op == 'not':
        sub = pretty(tree.children[0], subst)
        return 'not {}'.format(sub)
    elif op == 'neg':
        sub = pretty(tree.children[0], subst)
        return '-{}'.format(sub, True)
    elif op == 'num':
        return tree.children[0]
    elif op == 'var':
        name = tree.children[0]
        return str(subst.get(name, name))
    elif op == 'if':
        cond = pretty(tree.children[0], subst)
        true = pretty(tree.children[1], subst)
        false = pretty(tree.children[2], subst)
        return par('{} ? {} : {}'.format(cond, true, false))


def run(tree, env):
    """Ordinary expression evaluation.

    `env` is a mapping from variable names to values.
    """

    return interp(tree, lambda n: env[n])


def z3_expr(tree, vars=None):
    """Create a Z3 expression from a tree.

    Return the Z3 expression and a dict mapping variable names to all
    free variables occurring in the expression. All variables are
    represented as BitVecs of width 8. Optionally, `vars` can be an
    initial set of variables.
    """

    vars = dict(vars) if vars else {}

    # Lazily construct a mapping from names to variables.
    def get_var(name):
        if name in vars:
            return vars[name]
        else:
            # v = z3.BitVec(name, 8)
            # v = z3.BitVec(name, 1) # Bool
            v = z3.Bool(name)
            vars[name] = v
            return v

    return interp(tree, get_var), vars


def solve(phi):
    """Solve a Z3 expression, returning the model.
    """

    s = z3.Solver()
    s.add(phi)
    s.check()
    return s.model()


def model_values(model):
    """Get the values out of a Z3 model.
    """
    return {
        d.name(): model[d]
        for d in model.decls()
    }

def get_match_template_expr(vars1):
    """Given vars1 of the input boolean expression, return the template simplified boolean expression. 

    E.g. vars1 includes 3 variables: a, b, c
    
    template expr would be: (here for simplicity: * denotes z3.And, + denotes z3.Or, - denotes z3.Not)
    (a*h111) + (-a*h112) + (b*h121) + (-b*h122) + (c*h131) + (-c*h132) 
    + (a*b*h211) + (a*-b*h212) + (-a*b*h213) + (-a*-b*h214) + (a*c*h221) + (a*-c*h222) + (-a*c*h231) * (-a*-c*232)
    + (a*b*c*h311) + ........
    """
    
    def new_h(i, h_names): # return new name for h
        j = 0
        while True:
            h = z3.Bool('h_{}_{}'.format(i, j))
            if h not in h_names:
                h_names.append(h)
                return h
            j += 1

    def get_var_combine_expr(vars_all, level):
        '''
        return list: each element is a z3 expr. 
        '''
        permutate = list(itertools.combinations(vars_all, level))
        for idx, term in enumerate(permutate):
            if (idx == 0):
                expr_part = z3.And(*term, new_h(level, h_names))
            else:
                expr = z3.And(*term, new_h(level, h_names))
                expr_part = z3.Or(expr, expr_part)
        return expr_part


    var_num = len(vars1)
    h_names = list()

    # get vars_all: include all variables and the negating of them. [a, b, c, Not(a), Not(b), Not(c)]
    vars_all = list()
    values = vars1.values()
    for var in values:
        not_var = z3.Not(var)
        vars_all.append(var)
        vars_all.append(not_var)
    
    for level in range(1, var_num): # i = # of var in one term. 
        # @TODO: Here we set the loop upper bound as var_num-1 instead of var_num. This is to avoid some redundant (but also correct) results which is not simplified. -> Z3 solver will find a correct solution, and then stop; but the answer might not be simplified. 
        # So here the limitation is: if input boolean expr has maximum = N levels, we must ensure that it could be simplified to max = N-1 levels. Otherwise it would fail. 
        if (level == 1):
            template_expr = get_var_combine_expr(vars_all, level)
        else:
            expr_part = get_var_combine_expr(vars_all, level)
            template_expr = z3.Or(expr_part, template_expr)


    return template_expr


def get_simplified_expr(vars1, model_values_list):
    '''
    Get the simplified expr, given template_expr and model_values already solved by Z3 solver. 
    Specifically, we want to remove the terms with False h, and only leave the terms with True h. 
    '''

    def get_expr(vars_all, level, perm_idx):
        '''
        return list: each element is a z3 expr. 
        '''
        permutate = list(itertools.combinations(vars_all, level))
        expr_part = z3.And(*permutate[perm_idx])
        return expr_part

    level_perm_pair = tuple()
    true_pairs = list() # to check which terms are True or False. Key: level_perm_pair; Value: True or False (acquired by model_values_list)

    for key, value in model_values_list.items():
        if (value == True):
            level_perm_pair = int(key.split("_")[1]), int(key.split("_")[2])
            true_pairs.append(level_perm_pair)

    vars_all = list()
    values = vars1.values()
    for var in values:
        not_var = z3.Not(var)
        vars_all.append(var)
        vars_all.append(not_var)
    
    expr_part_list = list()
    for true_level, true_perm in true_pairs:
        expr_part_list.append(get_expr(vars_all, true_level, true_perm))
    
    simplified_expr = z3.Or(*expr_part_list)
    
    return simplified_expr
        
        


def synthesize(tree):
    """
    Given original boolean program tree, synthesize the simplified version of boolean expression. 
    """

    expr, vars = z3_expr(tree)

    template_expr = get_match_template_expr(vars)

    # Formulate the constraint for Z3.
    goal = z3.ForAll(
        list(vars.values()),  # For every valuation of variables...
        expr == template_expr,  # ...the two expressions produce equal results.
    )

    model = solve(goal)
    model_values_list = model_values(model)

    simplified_expr = get_simplified_expr(vars, model_values_list)

    return simplified_expr


def bool_simplify(source):
    src = source.strip()

    parser = lark.Lark(GRAMMAR)
    tree = parser.parse(src)
    
    print("Original boolean expression:")
    print(pretty(tree))

    simplified_expr = synthesize(tree)

    print("\nSimplified expression:")
    print(simplified_expr)

    


if __name__ == '__main__':

    # test
    '''
    a = z3.Bool('a')
    b = z3.Bool('b')
    c = z3.Bool('c')


    h1 = z3.Bool('h1')
    h2 = z3.Bool('h2')
    h3 = z3.Bool('h3')    


    expr1 = z3.Or(z3.And(a, b, c), z3.And(a, b, z3.Not(c)), z3.And(z3.Not(a), b, c), z3.And(a, z3.Not(b), c))

    expr2 = z3.Or(z3.And(a, b, h1), z3.And(b, c, h2), z3.And(a, c, h3))

    print(f"expr1: {expr1}\n\nexpr2: {expr2}")

    plain_vars = {'a': a, 'b': b, 'c': c}

    goal = z3.ForAll(
        list(plain_vars.values()),  # For every valuation of variables...
        expr1 == expr2,  # ...the two expressions produce equal results.
    )    

    print(solve(goal))
    '''

    bool_simplify(sys.stdin.read())

