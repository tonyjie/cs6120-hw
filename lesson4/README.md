# Dataflow Analysis
`df.py` show the implementation of dataflow analysis using worklist algorithms. It provides a general framework for several kinds of analyses, including forward dataflow problem and backward dataflow problem. 

You can easily use different analysis by giving certain arguments as follows. 
- `bril2json < {filename.bril} | python3 df.py defined` : Reaching Definitions (Forward)
- `bril2json < {filename.bril} | python3 df.py live` : Live Variables (Backward)
- `bril2json < {filename.bril} | python3 df.py cprop` : Constant Propagation (Forward)

## Limitations & Rules
### Reaching Definition
I decide not to consider the function arguments here for simplicity and brevity. It is easy to add the func arguments to the `init` of `In`, but for the other analysis, it is someting else. 

### Constant Propagation
There is some limitations or so-called rules for my implementation on Constant Propagation analysis. It is also because of simplicity. 

There's no constant folding and any actual computation involved. For a `.bril` program as follows: 
```
@main(cond: bool) {
  a: int = const 47;
  b: int = const 42;
  c: int = add a b;
}
```
It would not recognize that both args of `c` are const, and compute the result of c. Its dataflow output would be:
```
block.0:
  in:  ∅
  out: a: 47, b: 42, c: ?
```


## Testing
### Reaching Definition
```
cd test/defined
turnt *.bril
```

### Live Variables
```
cd test/live
turnt *.bril
```

### Constant Propagation
```
cd test/cprop
turnt *.bril
```