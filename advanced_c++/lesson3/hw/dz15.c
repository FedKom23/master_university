#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    unsigned int n;
    if (scanf("%u", &n) != 1) {
        return 1;
    }

    for (int i = n - 1; i >= 0; i--) {
        long long int a = 0;
        long long int power = 1;

        for (int j = 0; j < (int)(n - i); j++) {
            a += power;
            power *= 8;
        }

        int zeros_count = i;
        if (i == 0) {
            printf("%llo\n", a);
        } else {
            printf("%0*d%llo\n", zeros_count, 0, a);
        }
    }
    return 0;
}