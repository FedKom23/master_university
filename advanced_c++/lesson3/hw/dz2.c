#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    long long int n;
    if (scanf("%lld", &n) != 1) {
        return 1;
    }
    if (n == 0) {
        printf("%d", 1);
        return 0;
    }
    long long int temp = 1;
    while (temp <= n) {
        temp <<= 1;
    };
    printf("%lld", n ^ (temp - 1));

    return 0;
};