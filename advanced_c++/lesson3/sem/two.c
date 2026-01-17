#include <stdio.h>

int main()
{
    unsigned long long a;
    if (scanf("%llu", &a) != 1) {
        return 1;
    }
    int printed_chars = 0;

    printf("0x%llx%n\n", a, &printed_chars);
    printf("%d\n", printed_chars);

    return 0;
}