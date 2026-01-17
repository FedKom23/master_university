#include <stdio.h>

int main()
{
    char c;
    unsigned int once = 0;
    unsigned int not_once = 0;

    while (1) {
        if (scanf("%c", &c) != 1) {
            break;
        }
        if (c == '\n') {
            break;
        }

        if ((not_once & (1 << (c - 'a'))) == 0) {
            if ((once & (1 << (c - 'a'))) == 0) {
                once |= (1 << (c - 'a'));
            } else {

                once &= ~(1 << (c - 'a'));
                not_once |= (1 << (c - 'a'));
            }
        }
    }

    int count = 0;
    int flag = 0;
    while (once != 0) {
        if (once & 1) {
            flag = 1;
            printf("%c", 'a' + count);
        }
        once >>= 1;
        count++;
    }

    if (flag == 0) {
        printf("N");
    }
    printf("\n");
    return 0;
}