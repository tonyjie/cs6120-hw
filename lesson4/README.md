# Dataflow Analysis
`df.py` show the implementation of dataflow analysis using worklist algorithms. It provides a general framework for several kinds of analyses, including forward dataflow problem and backward dataflow problem. 

You can easily use different analysis by giving certain arguments as follows. 
- `bril2json < {filename.bril} | python3 df.py defined` : Reaching Definitions (Forward)
- `bril2json < {filename.bril} | python3 df.py live` : Live Variables (Backward)





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