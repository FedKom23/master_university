#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void my_strncat(char* dest, const char* src, long unsigned n)
{
    while (*dest) {
        dest++;
    }

    while (n-- && *src) {
        *dest++ = *src++;
    }

    *dest = '\0';
}

int main()
{
    char str1[100] = "";
    char str2[100] = "";
    int n;

    if (scanf("%99s", str1) != 1)
        return 1;
    if (scanf("%99s", str2) != 1)
        return 1;
    if (scanf("%d", &n) != 1)
        return 1;

    my_strncat(str1, str2, n);

    printf("%s\n", str1);

    return 0;
}