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
clang++ -Xclang -load -Xclang build/DivToMul/libDivToMul.so -flegacy-pass-manager simple.cpp -o simple_trans
./simple_trans
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
I just wrote another simple program `test.cpp` with a `test_div` function with a if branch. 

The running command is the same. 
```
clang++ -Xclang -load -Xclang build/DivToMul/libDivToMul.so -flegacy-pass-manager test.cpp -o test_trans
```
This will print the **Integer Division Instruction** and the transformed instruction. 

`./test_trans` will give the multiplication result instead of division result. 

## Discussion
I was planning to transform the floating division instruction to floating multiplication instruction (`fmul`), but it seems that the `IRBuilder.CreateMul()` cannot generate a `fmul` instruction. The output of two floating points is not as expected. I think this is because that `CreateMul()` still generates a integer multiplication instruction, while its operands are floating points. then something went wrong. 

I tried, but didn't found a function like `CreateFMul()` for `IRBuilder`. 