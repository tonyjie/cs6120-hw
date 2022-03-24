# Loop Optimization

## LICM: Loop-Invariant Code Motion
I use LLVM to implement LICM for this task. In the beginning, I'm trying to follow the pseudo code for identifying loop-invariant instructions by checking the reaching definitions. But then looking through the method of `llvm::Loop`, I found the straightforward function `makeLoopInvariant(&I)` which can directly detect the loop-invariant instructions and move it to the pre-header of the loop. 

Therefore, the implementation is just simply go over all the instructions of the loop, and call `makeLoopInvariant(&I)` to each instruction. If a loop-invariant instruction is found, we break this cycle and continue this until convergence (no loop-invariant instruction can be found.)

## Rigorously evaluate its performance impact.
If you choose LLVM, select an existing (small!) benchmark suite such as [Embench](https://www.embench.org/).

I'm still figuring out how to use `Embench`. It seems that I can't directly use its source code as it doesn't have a `main` function. 


## Commands
- Build shared library for the Pass. 

```
cd LoopOptimize/
cmake ..
make
cd ..
```

- Run it. 

```
# bash run.sh
clang simple.c -S -emit-llvm -Xclang -disable-O0-optnone
opt -mem2reg -S simple.ll -o simple-mem2reg.ll
clang simple-mem2reg.ll -Xclang -load -Xclang build/LICM/libLICM.so -flegacy-pass-manager -o simple.out
clang simple-mem2reg.ll -Xclang -load -Xclang build/LICM/libLICM.so -flegacy-pass-manager -S -emit-llvm -o simple-licm.ll
```

1. To allow optimization under `-O0`, we need to provide `-Xclang -disable-O0-optnone` option. Otherwise, we cannot apply `-mem2reg` pass later. 
2. `-mem2reg` pass allows us to have normal SSA-form IR with phi nodes instead of load/store, which prevents us from detecting loop-invariant operands and instructions. 
3. 
4. Generate the LLVM IR after LICM. Comparing the `simple-licm.ll` with `simple-mem2reg.ll`, it is easy to find that the loop invariant instruction is moved ahead the loop. 

```
define i32 @main() #0 {
  %1 = add nsw i32 2, 2
  %2 = mul nsw i32 2, 2
  br label %3

... # Basic Block for Loop
```



## Discussions
As LLVM already has corresponding helper function to handle loop-invariant detecting, the hardest part of this task for me is those tricky things with `clang`. It's kind of hard to search for the answer on how to removing unexpected load/store and the necessary `disable-O0-optnone` option, until I see it on Zulip and discussions from others. 