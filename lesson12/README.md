# Trace-based Speculative Optimizer for Bril

The task is to implement a trace-based speculative optimizer for Bril. You’ll implement the same concept as in a tracing JIT, but in a profile-guided AOT setting: profiling, transformation, and execution will be distinct phases. The idea is to implement the “heavy lifting” for a trace-based JIT without needing all the scaffolding that a complete JIT requires, such as on-stack replacement.

## Setup
The whole procedure is illustrated here. Take the `test_loop/loop.bril` as an example. 

- Build the modified reference intepreter with tracing

cd [here](https://github.com/tonyjie/bril/tree/trace/bril-ts) under `trace` branch of bril. 
```
yarn build
```
Then `brili` could generate tracing for the whole program. 

- Convert original bril program to json file
```
bril2json < test_loop/loop.bril > test_loop/loop.json
```

- Extract the trace
```
bril2json < test_loop/loop.bril | brili | python trace.py > test_loop/loop.trace
```

- use `transform.py` to transform and stitch tracing program into the original program
```
python transform.py -trace test_loop/loop.trace -src test_loop/loop.json > loop_opt.json
```

- use `brili` to check the answer and total dynamic instructions
```
brili -p < test_loop/loop.json          # original
brili -p < test_loop/loop_opt.json      # with tracing
```

## Test
Here for simplicity, I only test on two examples: `loop` and `if-const`. 

The output is correct, and the dynamic instrs between original program and tracing program is nearly the same. That's because I haven't implemented optimizations here. The difference is that tracing program would add some `label`, `speculate`, `commit`, and remove `jmp`. DCE and LVN optimizations could be applied here to reduce the dynamic instructions. 

- `loop`

The output answer remains the same. The original program has dynamic instrs = 26; the tracing program has dynamic instrs = 25. 

- `if-const`

The output answer remains the same. The original program has dynamic instrs = 5; the tracing program has dynamic instrs = 7. 


## Implementation
### Modify the reference interpreter to produce traces
Insert `console.log(">", JSON.stringify(instr));` in the `evalInstr()` function to record every instruction as it executes. 

">" prefix is added to distinguish the instruction tracing from the normal print output.

### Transform tracing instructions to required straight-line code
- Eliminate jumps. 
- replace branched `br` with `guard` instructions. Here is something tricky: as we trace the whole program for simplicity, if we fail on any guard in the loop, we would fallback to the beginning of the original program and run it again. In the `loop` example, if we directly use `cond` of `br` as the `cond` of `guard`, this would lead to all the success guard and a fail at the last guard. This would lead to very bad performance: it nearly run the program twice! 

So a workaround is that we change the condition of guard instruction based on profiling result (take cond or not): we want the whole trace to be executed. This is not what `guard` is designed to do for sure, but it is implemented here just because we trace the whole program and don't want it to be bad on the loop example. 

### Stitch the trace back into the program
As we trace the whole program, we add `speculate` at the beginning, and `commit` at the end of tracing code. Add another `ret` after `commit` so that we can end the tracing program if all the `guard` succeed in the speculate block. 

After that, the original program block is added as the fallback of the `guard`. 