#include <stdio.h>
int main(int argc, char **argv) {
    int x = 2;
    int y = 10;
    int z = 8;

    float a = 2.3;
    float b = 3.7;
    
    int res0 = y / x;
    int res1 = z / x;
    printf("res0 = %d; res1 = %d;\n", res0, res1);


    float res2 = a / x;
    float res3 = a / b;

    printf("res2 = %f; res3 = %f;\n", res2, res3);

    return 0;
}