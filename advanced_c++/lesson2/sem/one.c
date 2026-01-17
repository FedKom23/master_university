#include <stdbool.h>
#include <stdio.h>

bool stepen_chisla(int number)
{
    if (number <= 0)
        return false;
    if (number == 1)
        return true;
    return ((number & (number - 1)) == 0) && ((number & 0x55555555) != 0);
}

int main()
{
    int number;
    if (scanf("%d", &number) != 1) {
        return 1;
    }

    printf("%s\n", stepen_chisla(number) ? "true" : "false");
    return 0;
}