# Lesson 2

## Write a new benchmark. 
Bubble sort for an array containing 5 elements in ascending order.  
```
cd benchamrk
turnt bubblesort.bril
```

## Write a program to analyze Bril programs: Count the number of add instructions
- Check the number of add instructions for these test cases. 
```
cd analysis
bril2json < test/add.bril | python count_add.py
bril2json < test/bubble.bril | python count_add.py
bril2json < test/fib.bril | python count_add.py
```
- Use Turnt to test the analysis program in batch
```
cd analysis/test
turnt *.bril
```