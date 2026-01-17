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

    long long result = 0;
    for (int i = 0; i < n; i++) {
        long long num;

        if (scanf("%lld", &num) != 1) {
            return 1;
        }
        result ^= num;
    }

    printf("%lld\n", result);
    return 0;
}