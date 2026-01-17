#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    unsigned int ish;
    unsigned int vh;
} noda;

int main()
{
    unsigned int n;
    if (scanf("%u", &n) != 1) {
        return 1;
    }
    unsigned int m;
    if (scanf("%u", &m) != 1) {
        return 1;
    }
    noda* a = malloc(n * sizeof(noda));
    for (unsigned int i = 0; i < m; i++) {
        unsigned int x, y;
        if (scanf("%u %u", &x, &y) != 2) {
            return 1;
        }
        a[x - 1].ish++;
        a[y - 1].vh++;
    }
    int flg = 0;
    for (unsigned int i = 0; i < n; i++) {
        if (a[i].ish == 0 && a[i].vh == n - 1) {
            flg = 1;
            printf("%u", i + 1);
        }
    }
    if (flg == 0) {
        printf("-1");
    }
    free(a);
    return 0;
}