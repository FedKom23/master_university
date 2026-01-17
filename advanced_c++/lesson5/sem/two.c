#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int find_ind(const char* str, char target)
{
    char target_lower = tolower(target);

    for (int i = 0; str[i] != '\0'; i++) {
        if (tolower(str[i]) == target_lower) {
            return i;
        }
    }
    return -1;
}

int main()
{
    FILE* fptr = fopen("lines.txt", "r");
    if (fptr == NULL) {
        return 1;
    }
    char mass_letters[] = "abcdefghijklmnopqrstuvwxyz";
    size_t len = strlen(mass_letters);
    int* counter_mass = calloc(len, sizeof(int));
    int c;
    while (c = fgetc(fptr), c != EOF) {
        if (c == '\n')
            continue;
        int ind = find_ind(mass_letters, c);
        if (ind != -1) {
            counter_mass[ind]++;
        }
    }
    fclose(fptr);
    for (long unsigned int i = 0; i < len; i++) {
        printf("%c: %d\n", mass_letters[i], counter_mass[i]);
    }
    free(counter_mass);
    return 0;
}