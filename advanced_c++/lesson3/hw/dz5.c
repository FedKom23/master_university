#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    int n;
    long long int c;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    if (scanf("%lld", &c) != 1) {
        return 1;
    }

    long long int s = 0;
    long long int water = c;

    for (int i = 0; i < n; i++) {
        long long int temp;
        if (scanf("%lld", &temp) != 1) {
            return 1;
        }

        if (water < temp) {
            s += (long long)i * 2;
            water = c;
        }
        water -= temp;
        s++;
    }

    printf("%lld\n", s);
    return 0;
}