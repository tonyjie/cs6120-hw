# Global Analysis
## Implement dominance utilities

`dom.py` implements several dominance utilities with different input arguments (they are complimentary, you can use them together). 
- `-dom`: Find dominators for a function.
- `-tree`: Construct the dominance tree.
- `-frontier`: Compute the dominance frontier.

Examples: 

`bril2json < test/while.bril | python3 dom.py -dom -tree -frontier`

## Test Correctness
All the testcases under `test/` (`loopcond` and `while`) would pass. The results are verified manually. 

```
cd test/
turnt *.bril
```


## Test the Implementations Algorithmically
I use DFS (Depth First Search) algorithm on the Control-Flow-Graph to test the implementations. Using DFS traversal, I can get all the possible paths from Entry to B. Then I check if every path include A: if so, A dominates B correctly; otherwise, A is not the dominator of B. 

The code passes all the testcases. If I manually make it wrong as follows in the benchmark `loopcond`: 
```
dom['endif'].add('then')
dom['endif'].add('exit')
dom['body'].add('then')
```

The testing function would print the error message as follows: 
```
then is not the Dominator of body
exit,then is not the Dominator of endif
```

## Discussion
It is worth to note that when testing the `test/while.bril` initially, my code fails. After investigating, I found this is due to the first block has in-edges. We need to ensure that a CFG has a unique entry block with no predecessors to make the algorithm work. So I add another entry block and jump to the original first block to solve this problem. 