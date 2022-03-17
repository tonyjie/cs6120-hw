# LLVM

## Implement a Pass
I choose to implement an unambitious pass. The `DivToMul` pass would inspect the integer division instruction (`OpCodeName == 'sdiv'`), and transform the instruction with an integer multiplication instruction. 

This was achieved by using `IRBuilder` and `CreateMul` method. 

### Build the Pass
```
mkdir build
cd build
cmake ..
make
cd ..
```

### Run it! 
```
clang++ -Xclang -load -Xclang build/DivToMul/libDivToMul.so -flegacy-pass-manager simple.cpp -o simple
./simple
```

When compiling, the Pass would print `OpCodeName` and `Instruction` when it find an **Integer Division instruction**, and print the **Integer Multiplication Instruction** after transformation. 

When executing, we can see the result of `10 / 2` and `8 / 2` become `20` and `16`. So we implement the pass successfully! 

```
int x = 2;
int y = 10;
int z = 8;

int res0 = y / x;
int res1 = z / x;
printf("res0 = %d; res1 = %d;\n", res0, res1);
```

Output: 
```
res0 = 20; res1 = 16;
```


## Find a real-ish C/C++ program somewhere and run the pass on it to observe the results. 
