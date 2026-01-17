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
    for (int i = 0; i < (int)n; i++) {
        int dot_wide = n - i - 1;
        int star_wide = 2 * i + 1;
        for (int j = 0; j < dot_wide; j++) {
            printf(".");
        }
        for (int j = 0; j < star_wide; j++) {
            printf("*");
        }
        for (int j = 0; j < dot_wide; j++) {
            printf(".");
        }
        printf("\n");
    }
    return 0;
}