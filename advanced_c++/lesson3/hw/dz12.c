#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void print_array(int suma, int tek, int pos, int n)
{
    if (suma < 0) {
        return;
    }
    if (pos == 2 * n) {
        if (suma == 0) {
            int temp = tek;
            for (int i = 0; i < 2 * n; i++) {
                if (temp & 1) {
                    printf("{");
                } else {
                    printf("}");
                }
                temp >>= 1;
            }
            printf("\n");
        }
        return;
    }

    print_array(suma - 1, tek, pos + 1, n);
    print_array(suma + 1, tek + (1 << pos), pos + 1, n);
}

int main()
{
    unsigned int n;
    if (scanf("%u", &n) != 1) {
        return 1;
    }
    print_array(1, 1, 1, n);

    return 0;
}