import z3

def solve(phi):
    s = z3.Solver()
    s.add(phi)
    s.check()
    return s.model()

formula = (z3.Int('x') / 7 == 6)
print(solve(formula))

y = z3.BitVec('y', 8)
print(solve(y << 3 == 40))

z = z3.Int('z')
n = z3.Int('n')
print(solve(z3.ForAll([z], z * n == z)))