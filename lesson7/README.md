# LLVM
## A Skeleton LLVM Pass
1. Add the llvm-pass-skeleton repository as a submodule. 
```
git submodule add git@github.com:sampsyo/llvm-pass-skeleton.git
```

2. Build it
```
cd llvm-pass-sksleton
mkdir build
cd build
cmake ..
make
cd ..
```

3. Run it
In the `lesson7/` dir, invoke `clang` on the C program. Note that `-flegacy-pass-manager` is needed to force it to use the legacy pass manager. Otherwise, my LLVM 13.0 can compile succesfully, but there's no outputs when running the pass. 
```
clang -Xclang -load -Xclang build/skeleton/libSkeletonPass.so -flegacy-pass-manager first.c
```

## Implement a Pass





## Find a real-ish C/C++ program somewhere and run the pass on it to observe the results. 
