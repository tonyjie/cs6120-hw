# Static Single Assignment - SSA
## into SSA transformation
`to_ssa.py` is the implementation that transform a normal bril code into its SSA form. 

It can be tested as follows, , which is actually running: 

`bril2json < {filename} | python ../to_ssa.py | bril2txt`
```
cd to_ssa/
turnt *.bril
```

One thing worth mentioned is dealing with variables that are undefined along some paths. I need to look at the stack and see if the argument variable in phi node is actually defined or not. Set it as `__undefined` if it's not. 

I also spent a lot of time in the beginning thinking of how to determine the number of `args` and `labels` in the phi node at each block. That's because I make it wrong at the beginning. I thought when inserting phi node at step 1, we need to know where the argument variables come from (in which block are they defined) and set them as `labels`. However, I found that the `labels` are just simply the predecessors of the block!


## out of SSA transformation
`from_ssa.py` is the implementation that transform SSA-form code into normal bril code without phi-nodes. 

It can be tested as follows, which is actually running:

`bril2json < {filename} | python ../to_ssa.py | python ../from_ssa.py | bril2txt`
```
cd from_ssa/
turnt *.bril
```

## SSA Roundtrip Test
We can also stitch the `to_ssa` and `from_ssa` and `dce` together, and then use `brili` to test if the result is still correct. The testcases are copied from [the bril repo](https://github.com/sampsyo/bril/tree/main/examples/test/ssa_roundtrip). 

Here `dce.py` is added to help remove unused variable. If I don't do Dead Code Elimination, `brili` will raise an error `error: undefined variable __undefined`

It can be tested as follows, which is actually running: 

`bril2json < {filename} | python ../to_ssa.py | python ../from_ssa.py | python ../dce.py | brili {args}`
```
cd from_ssa/
turnt *.bril
```

## Bonus: global value numbering for SSA-form Bril code
TODO :)


## Limitations
`to_ssa_fail.` dir contains the special testcases that this implementation haven't covered yet.    
- `if_ssa.bril` is bril code with phi nodes. Current implementation doesn't support bril program with phi nodes. To support it, I should also give the destination of phi node a fresh new name, and save it in the stack and maintain it. But my implementation is kind of complicated (messy...?), so I just choose to not support it currently XD. Hope it didn't influence a lot. 
- `loop-branch.bril` contains several functions and `call` op. This need some additional effort to analyze its control flow graph, etc. 