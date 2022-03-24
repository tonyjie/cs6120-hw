#include <stdio.h>

void double_it(int n) {
    n = n * 2;
}

int main() {
    int a = 2;
    int b = 2;
    for (int i = 0; i < 100; i++) {
        int c = a + b;
        double_it(c);

        for (int j = 0; j < 20; j++) {
            int d = a * b;
            double_it(d);
        }

        printf("c = %d\n", c);
    }

  return 0;
}