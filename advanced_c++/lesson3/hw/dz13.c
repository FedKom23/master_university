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

    int flg = 0;
    for (int i = 0; i < 16; i++) {
        unsigned int left_bit = (n >> i) & 1;
        unsigned int right_bit = (n >> (31 - i)) & 1;

        if (left_bit != right_bit) {
            flg = 1;
            break;
        }
    }

    if (flg == 1) {
        printf("false");
    } else {
        printf("true");
    }
    return 0;
}