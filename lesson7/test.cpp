#include <stdio.h>
using namespace std;

int gcd(int a, int b) {
    if (b == 0)
        return a;
    return gcd(b, a % b);
}


int test_div(int a, int b) {
    if (a > b) {
        return a / b;
    } else {
        return b / a;
    }
}

int main() {
    int a = 105, b = 15;
    
    int c = test_div(a, b);

    printf("test_div(%d, %d) = %d\n", a, b, c);

    return 0;
}