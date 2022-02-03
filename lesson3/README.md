# Lesson 3
## Dead Code Elimination
`trivial_dce.py` implements "trivial" dead code elimination. It only does global analysis within a function that would deletes instructions that are never used before they are reassigned. It would pass the `test_trivial` test cases, but fail on the `test_complicated` test cases which require other optimizations. 

```
cd dce/test_trivial
turnt *.bril
```

## Local Value Numbering


