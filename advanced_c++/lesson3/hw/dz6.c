#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    unsigned long int n = 0;
    char temp;
    while (1) {
        if (scanf("%c", &temp) != 1) {
            return 1;
        }
        if (temp == '\n') {
            break;
        }
        if ((n & (1 << (temp - 'a'))) == 0) {
            n |= (1 << (temp - 'a'));
        }
    }
    int suma = 0;
    unsigned long int count = 0;
    int flag = 0;
    while (1) {
        if (scanf("%c", &temp) != 1) {
            return 1;
        }
        if (temp == '\n') {
            if (count == n && flag == 0) {
                suma++;
            }
            break;
        }
        if (temp == ' ') {
            if (count == n && flag == 0) {
                suma++;
            }
            count = 0;
            flag = 0;
            continue;
        }

        if ((n & (1 << (temp - 'a'))) != 0) {
            if ((count & (1 << (temp - 'a'))) == 0) {
                count |= (1 << (temp - 'a'));
            }
        } else {
            flag = 1;
        }
    }
    printf("%d", suma);
    printf("\n");
    return 0;
}