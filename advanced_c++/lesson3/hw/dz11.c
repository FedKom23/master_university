#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void reverse()
{
    char c = getchar();
    if (c == '\n' || c == EOF) {
        return;
    }
    reverse();
    putchar(c);
}

int main()
{
    reverse();
    return 0;
}