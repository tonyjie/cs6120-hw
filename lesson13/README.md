# Boolean Expression Simplifier
I change the original [ex2](https://github.com/sampsyo/minisynth/blob/master/ex2.py) program to a Boolean Expression Simplifier: with the input of an boolean expression, it would return a simplified version. This is similar to what [K-map](https://en.wikipedia.org/wiki/Karnaugh_map) would do. 

The searching phase is an iterative process, like what [superoptimizer](https://en.wikipedia.org/wiki/Superoptimization) would do. 

## How to use & Testcases
- one term has 2 variables: `AB + AB' = A`
```
cat test/2_var.txt
# (a and b) or (a and not b)
python bool_simplify.py < test/2_var.txt
```

Output is as follows
```
Original boolean expression:
(a and b) or (a and not b)

Simplified expression:
Or(And(a))
```

- one term has 3 variables: `ABC + ABC' + A'BC + AB'C = AC + AB + BC`
```
cat test/3_var.txt
# (a and b and c) or (a and b and not c) or (not a and b and c) or (a and not b and c)
python bool_simplify.py < test/3_var.txt
```

Output is as follows:
```
Original boolean expression:
((((a and b) and c) or ((a and b) and not c)) or ((not a and b) and c)) or ((a and not b) and c)

Simplified expression:
Or(And(a, c), And(a, b), And(b, c))
```

- one term has 4 variables: `A'BC'D' + ABC'D' + A'B'C'D + A'B'CD + AB'C'D + AB'CD = BC'D' + B'D`
```
cat test/4_var.txt
# (not a and b and not c and not d) or (a and b and not c and not d) or (not a and not b and not c and d) or (not a and not b and c and d) or (a and not b and not c and d) or (a and not b and c and d)
python bool_simplify.py < test/4_var.txt
```

Output is as follows:
```
Original boolean expression:
(((((((not a and b) and not c) and not d) or (((a and b) and not c) and not d)) or (((not a and not b) and not c) and d)) or (((not a and not b) and c) and d)) or (((a and not b) and not c) and d)) or (((a and not b) and c) and d)

Simplified expression:
Or(And(b, Not(c), Not(d)),
   And(Not(b), c, d),
   And(Not(b), Not(c), d))
```
Note that the simplified expression is `BC'D' + B'CD + BC'D`, which is not the most simplified expression. This is a limitation of current implementation due to Z3 solver. 

## Implementation
- Add support for boolean expression. 

    3 ops: `and`, `or`, `not` are added. I use `z3.Bool(name)` for each variable and `z3.And()`, `z3.Or()`, `z3.Not()` to build z3 expressions. 

- Build template expression with holes. 

    This is implemented in [`def get_match_template_expr`](https://github.com/tonyjie/cs6120-hw/blob/08f0ad32b9d090f5251f0ab1b494b9c882beb45d/lesson13/bool_simplify.py#L184). I list all the possible `and terms` with a `hole variable`, and `or` them together. 

    E.g. vars includes 3 variables: a, b, c. Template expr would be: 
    ```
    (a*h111) + (a'*h112) + (b*h121) + (b'*h122) + (c*h131) + (c'*h132) 
    + (a*b*h211) + (a*b'*h212) + (a'*b*h213) + (a'*b'*h214) + (a*c*h221) + (a*c'*h222) + (a'*c*h231) * (a'*c'*232)
    + (a*b*c*h311) + ........'
    ```

    Then use `z3.Solver` to solve these holes (True or False). 

- Get final simplified boolean expression. 

    This is implemented in [`def get_simplified_expr()`](https://github.com/tonyjie/cs6120-hw/blob/08f0ad32b9d090f5251f0ab1b494b9c882beb45d/lesson13/bool_simplify.py#L242). Given the values of solved holes, print the simplified boolean expression. 


## Limitation
Can't guarantee to find the most simplified version due to the naive usage of Z3 solver, shown in the testcases `test/4_var.txt`. Z3 solver would search and find one correct answer and stop searching for more. So the result is simplified, but might not be the most simplified version. 