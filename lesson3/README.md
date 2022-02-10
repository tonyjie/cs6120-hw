# Dead Code Elimination
`dce.py` implements dead code elimination. It has two modes: `trivial_dce` and `plus_dce`.  

`trivial_dce` only does global analysis within a function that would deletes instructions that are never used before they are reassigned. `plus_dce` also implements local analysis within each basic block, deleting the instructions with unused destination variables. (e.g. The destination variable is overwritten later. )    

The default mode is `trivial_dce`. When given the input argument `dce+`, `plus_dce` mode is turned on. 

## Correctness
It would pass the test cases with different input args. 

```
cd dce/test
turnt *.bril
```

## Optimization Results
- Static code size differences
```
cd dce/test
bril2json < combo.bril | wc -l                                  # 51
bril2json < combo.bril | python ../dce.py | wc -l               # 41
bril2json < combo.bril | python ../dce.py dce+ | wc -l          # 35
```

- Dynamic instruction count
```
cd dce/test
bril2json < combo.bril | brili -p                               # total_dyn_inst: 6
bril2json < combo.bril | python ../dce.py | brili -p            # total_dyn_inst: 5
bril2json < combo.bril | python ../dce.py dce+ | brili -p       # total_dyn_inst: 4
```

# Local Value Numbering
`lvn.py` implements local value numbering. It has 3 optional arguments: `-p`, `-c`, `-f`.   

- `-p`: enable constant propagation. 
- `-c`: enable commutativity. 
- `-f`: enable constant folding. 


## Correctness
It would pass the test cases under `lvn/test/`. But it would fail on the test cases under `lvn/test_nonlocal/`. To succesfully optimize the nonlocal programs, I think control flow graph is required. 

```
cd lvn/test
turnt *.bril
```

## Optimization Results
- Static code size differences
```
cd lvn/test
bril2json < clobber-fold.bril | python3 ../../dce/dce.py tdce | wc -l                               # 44
bril2json < clobber-fold.bril | python3 ../lvn.py | python3 ../../dce/dce.py tdce | wc -l           # 44
bril2json < clobber-fold.bril | python3 ../lvn.py -f | python3 ../../dce/dce.py tdce | wc -l        # 20
```

- Dynamic instruction count
```
cd lvn/test
bril2json < clobber-fold.bril | python3 ../../dce/dce.py tdce | brili -p                            # total_dyn_inst: 5
bril2json < clobber-fold.bril | python3 ../lvn.py | python3 ../../dce/dce.py tdce | brili -p        # total_dyn_inst: 5
bril2json < clobber-fold.bril | python3 ../lvn.py -f | python3 ../../dce/dce.py tdce | brili -p     # total_dyn_inst: 2
```

## Discussion
- When changing name for overwritten variables, we need to change corresponding variable name used in the later instructions. 
- When the function has arguments, in my implmenetation, I need to store those arguments into the *Table* before we go into the loop of the block. 