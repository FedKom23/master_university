#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    long int n;
    if (scanf("%ld", &n) != 1) {
        return 1;
    }

    long int res = 0;
    long int l = 0;

    for (int i = 0; i < n; i++) {
        long int a;
        if (scanf("%ld", &a) != 1) {
            return 1;
        }

        if (i == 0) {
            l = a;
            continue;
        }

        if (a > l) {
            res = (a - l > res) ? (a - l) : res;
        } else {
            l = a;
        }
    }

    printf("%ld", res);
    printf("\n");

    return 0;
}