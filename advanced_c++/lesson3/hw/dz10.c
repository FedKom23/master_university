#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

long long factorial(int n)
{
    if (n == 0 || n == 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

int main()
{
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    int k;
    if (scanf("%d", &k) != 1) {
        return 1;
    }
    long long int result = factorial(n) / (factorial(k) * factorial(n - k));

    printf("%lld\n", result);
    return 0;
}