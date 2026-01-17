#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }

    long long result = 1;
    for (int i = 1; i <= n; i++) {

        result *= i;
    }

    printf("%lld\n", result);
    return 0;
}