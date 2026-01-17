#include <stdio.h>

void print_fibo(int n, int i, long int a, long int b)
{
    if (i >= n)
        return;
    print_fibo(n, i + 1, b, a + b);
    printf("%ld ", a);
}

int main(void)
{
    long int n;
    if (scanf("%ld", &n) != 1) {
        return 1;
    }
    print_fibo(n, 0, 0, 1);
    return 0;
}