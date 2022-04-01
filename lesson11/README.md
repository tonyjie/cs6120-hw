# Memory Management

My implementation is [here](https://github.com/tonyjie/bril/blob/GC/bril-ts/brili.ts)

## Design

I implement a Reference Counting-based Garbage Collector. It is implemented in `brili.ts` to extend the `brili` interpreter. The main idea is to maintain a `Map<address, reference count>` which `address` is the memory location, and `reference count` is the referenced times of this location. 

I implemented several functions for our `RCGC class`
- `inc(base)`: increment the reference count of the given address by one
- `dec(base)`: decrement the reference count of the given address by one
- `incAll()`: increment all the reference counts in counts Map by one
- `decAll()`: decrement all the reference counts in counts Map by one. If the count==0, free the address in the heap. 

I need to update this map using the above functions when encountering every instruction: 
- `alloc`: use `inc(base)`
- `id`: use `inc(base)`
- `call`: use `incAll()`
- `ret`: if the return value is a Pointer, we need to keep it: so we `inc` the count of return pointer. Then use `decAll()`. 

The reason we `incAll()` and `decAll()` when encountering `call` and `ret` bril instruction is because: we want to distinguish pointers initialized in different functions. When a function return, the pointers initialized in the scope of this function should be freed. 

## Build the new brili interpreter with GC
under the GC branch in my `bril` repo

`cd` [here](https://github.com/tonyjie/bril/tree/GC/bril-ts)

```
yarn
yarn build
yarn link
```

## Test
I created several testcases with different features [here](https://github.com/tonyjie/bril/tree/GC/bril-ts/test_gc). `bril2json < {filename} | brili` would PASS all the testcases. 

I also removed all the `free` in benchmarks dir to get a new [benchmarks-gc](https://github.com/tonyjie/bril/tree/GC/benchmarks-gc)

`turnt *.bril` would PASS all the benchmarks. 

## Discussion
- The first thing I learned is how interpreter works, which is not clear to me before. A read-eval-print loop [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) expresses it clearly. We can also see that from `brili.ts` code. 

- I also noticed that there are still some corner (or not corner) cases that I didn't cover yet. When I'm wondering if I need to deal with `ptradd` instruction, I came up with a tricky bril example as follows:

```
@f : ptr<int> {
  one: int = const 1;
  ten: int = const 10;
  ptr_base: ptr<int> = alloc ten;
  ptr_move: ptr<int> = ptradd ptrbase one;
  ret ptr1;
}

@main {
  five: int = const 5;
  ptr_move : ptr<int> = call @f;
  store ptr_move five; 
  # ERROR here: we would FREE the memory allocated when f end, because we return ptr_move but not ptr_base. 
}
```

In `brili.ts`, we would only really alloc memory in heap when calling `alloc`, while `ptradd` would just add an offset to the Pointer value. In my current implementation, I would just free the memory when `ptr_base` is not alive anymore, regardless of other pointers like `ptr_move`. 

It's possible to support above example, but if `ptr_move: ptr<int> = ptradd ptrbase eleven` makes it out of the scope of allocated memory, we need to consider it again...