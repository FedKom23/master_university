#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    int c;
    int n = 0;
    int flg = 0;
    int prev = -1;
    int inc = 1;

    while ((c = getchar()) != EOF && c != '\n') {
        if (isdigit(c)) {
            n = n * 10 + (c - '0');
            flg = 1;
        } else if (c == ' ') {
            if (flg) {
                if (prev == -1) {
                    prev = n;
                } else {
                    if (n <= prev)
                        inc = 0;
                    prev = n;
                }
                n = 0;
                flg = 0;
            }
        } else {
            if (flg) {
                n = 0;
                flg = 0;
            }
        }
    }
    if (flg) {
        if (prev == -1) {
            prev = n;
        } else {
            if (n <= prev)
                inc = 0;
        }
    }
    printf("%d\n", inc);
    return 0;
}