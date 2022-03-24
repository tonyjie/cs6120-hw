clang simple.c -S -emit-llvm -Xclang -disable-O0-optnone
opt -mem2reg -S simple.ll -o simple-mem2reg.ll
clang simple-mem2reg.ll -Xclang -load -Xclang build/LICM/libLICM.so -flegacy-pass-manager -o simple.out
clang simple-mem2reg.ll -Xclang -load -Xclang build/LICM/libLICM.so -flegacy-pass-manager -S -emit-llvm -o simple-licm.ll