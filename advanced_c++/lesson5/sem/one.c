#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main()
{
    FILE* fptr = fopen("lines.txt", "r");
    if (fptr == NULL) {
        return 1;
    }

    int c;
    char* res = NULL;
    int maxi = 0;

    while ((c = fgetc(fptr)) != EOF) {
        int count = 0;
        int ind = 0;
        int capacity = 16;
        char* buffer = malloc(capacity * sizeof(char));
        if (buffer == NULL) {
            fclose(fptr);
            return 1;
        }

        buffer[ind++] = (char)c;
        while ((c = fgetc(fptr)) != EOF && c != '\n') {
            if (ind + 1 == capacity) {
                capacity *= 2;
                char* temp = realloc(buffer, capacity * sizeof(char));
                if (temp == NULL) {
                    free(buffer);
                    fclose(fptr);
                    return 1;
                }
                buffer = temp;
            }
            if (c == ' ') {
                count++;
            }
            buffer[ind++] = (char)c;
        }
        if (strlen(buffer) != 0) {
            count++;
        }
        buffer[ind] = '\0';
        if (count > maxi) {
            maxi = count;
            free(res);
            res = malloc((ind + 1) * sizeof(char));
            if (res != NULL) {
                strcpy(res, buffer);
            }
        }

        free(buffer);
    }

    if (res != NULL) {
        printf("%s\n", res);
        printf("%d\n", maxi);
        free(res);
    }

    fclose(fptr);
    return 0;
}