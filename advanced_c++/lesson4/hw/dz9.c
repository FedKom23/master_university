#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int check_palindrom(char* str, size_t len)
{
    char out[len];
    int j = 0;
    for (int i = 0; str[i] != '\0'; i++) {
        if (!isspace(str[i]) && !ispunct(str[i])) {
            out[j++] = tolower(str[i]);
        }
    }
    out[j] = '\0';
    size_t clean_len = j;
    for (size_t i = 0; i < clean_len / 2; i++) {
        if (out[i] != out[clean_len - i - 1]) {
            return 0;
        }
    }
    return 1;
}

int main()
{
    char buf[500];
    int count = 0;
    int* ind = malloc(1 * sizeof(int));
    int capacity = 1;
    int i = 0;
    while (fgets(buf, sizeof(buf), stdin) != NULL) {
        size_t len = strlen(buf);
        if (len > 0 && buf[len - 1] == '\n') {
            buf[len - 1] = '\0';
        }
        if (strlen(buf) == 0) {
            continue;
        }
        if (check_palindrom(buf, len)) {
            if (count >= capacity) {
                capacity *= 2;
                int* temp = realloc(ind, capacity * sizeof(int));
                if (temp == NULL) {
                    free(ind);
                    return 1;
                }
                ind = temp;
            }
            ind[count] = i;
            count++;
        }
        i++;
    }
    printf("\n");
    printf("%d\n", count);
    for (int i = 0; i < count; i++) {
        printf("%d ", ind[i]);
    }

    return 0;
}