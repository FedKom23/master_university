#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    long unsigned int n;
    if (scanf("%lu", &n) != 1) {
        return 1;
    };
    int res_1 = -10000;
    int res_2 = -10000;
    int res_3 = -10000;
    int res_4 = 10000;
    int res_5 = 10000;
    for (long unsigned int i = 0; i < n; i++) {
        int temp;
        if (scanf("%d", &temp) != 1) {
            return 1;
        };
        if (temp > res_1) {
            res_3 = res_2;
            res_2 = res_1;
            res_1 = temp;
        } else if (temp > res_2) {
            res_3 = res_2;
            res_2 = temp;
        } else if (temp > res_3) {
            res_3 = temp;
        }

        if (temp < res_4) {
            res_5 = res_4;
            res_4 = temp;
        } else if (temp < res_5) {
            res_5 = temp;
        }
    };

    long int res1 = res_1 * res_2 * res_3;

    long int res2 = res_1 * res_4 * res_5;

    if (res1 > res2) {
        printf("%ld\n", res1);
    } else {
        printf("%ld\n", res2);
    }

    return 0;
};