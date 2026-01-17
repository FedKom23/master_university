#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BITS_PER_BYTE 8

uint32_t ip_to_int(const char* ip)
{
    unsigned int a, b, c, d;
    sscanf(ip, "%u.%u.%u.%u", &a, &b, &c, &d);
    return (a << 24) | (b << 16) | (c << 8) | d;
}

int main()
{
    const char* filename = "/tmp/ip_store";

    FILE* file = fopen(filename, "w+b");
    if (!file) {
        return 1;
    }

    uint32_t n;
    if (scanf("%u", &n) != 1)
        return 1;

    char ip[20];
    for (uint32_t i = 0; i < n; i++) {
        if (scanf("%s", ip) != 1)
            return 1;
        uint32_t ip_int = ip_to_int(ip);

        uint32_t byte_index = ip_int / BITS_PER_BYTE;
        uint32_t bit_index = ip_int % BITS_PER_BYTE;

        fseek(file, byte_index, SEEK_SET);
        unsigned char byte;
        if (fread(&byte, 1, 1, file) != 1) {
            byte = 0;
        }

        byte |= (1 << bit_index);

        fseek(file, byte_index, SEEK_SET);
        fwrite(&byte, 1, 1, file);
    }
    fflush(file);

    uint32_t m;
    if (scanf("%u", &m) != 1)
        return 1;

    for (uint32_t i = 0; i < m; i++) {
        if (scanf("%s", ip) != 1)
            return 1;
        uint32_t ip_int = ip_to_int(ip);

        uint32_t byte_index = ip_int / BITS_PER_BYTE;
        uint32_t bit_index = ip_int % BITS_PER_BYTE;

        fseek(file, byte_index, SEEK_SET);
        unsigned char byte;
        if (fread(&byte, 1, 1, file) == 1) {
            if ((byte >> bit_index) & 1) {
                printf("yes\n");
            } else {
                printf("no\n");
            }
        } else {
            printf("no\n");
        }
    }

    fclose(file);
    remove(filename);

    return 0;
}