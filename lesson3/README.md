# Lesson 3
## Dead Code Elimination
`dce.py` implements dead code elimination. It has two modes: `trivial_dce` and `plus_dce`.  

`trivial_dce` only does global analysis within a function that would deletes instructions that are never used before they are reassigned. `plus_dce` also implements local analysis within each basic block, deleting the instructions with unused destination variables. (e.g. The destination variable is overwritten later. )    

The default mode is `trivial_dce`. When given the input argument `dce+`, `plus_dce` mode is turned on. 


It would pass the test cases with different input args. 

```
cd dce/test
turnt *.bril
```

## Local Value Numbering


