#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    FILE* fptr = fopen("text.txt", "r");
    if (fptr == NULL) {
        return 1;
    }
    int capacity = 16;
    int c;
    int count = 0;
    int count2 = 1;
    int maxi = 0;
    char* str = malloc(capacity);
    char* result = NULL;
    while (c = fgetc(fptr), c != EOF) {
        if (count == capacity) {
            capacity *= 2;
            str = realloc(str, capacity);
        }
        if (((char)c == ' ' || (char)c == '\n') && count != 0) {
            count2++;
        } else if (((char)c == ' ' || (char)c == '\n') && count == 0) {
            continue;
        }
        str[count++] = c;
        if ((char)c == '.') {
            if (count2 > maxi) {
                if (result != NULL) {
                    free(result);
                }
                maxi = count2;
                result = malloc(count);
                memcpy(result, str, count);
            }
            free(str);
            str = malloc(capacity);
            count = 0;
            count2 = 1;
        }
    }
    printf("%s", result);
    printf("\n%d", maxi);
    fclose(fptr);
    free(result);
    return 0;
}