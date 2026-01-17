#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int val;
    int flg;
} noda;

void dfs(noda** a, int n, int m, int i, int j)
{
    if (i >= n || j >= m || i < 0 || j < 0 || a[i][j].flg == 1 || a[i][j].val == 0) {
        return;
    }
    a[i][j].flg = 1;
    dfs(a, n, m, i + 1, j);
    dfs(a, n, m, i - 1, j);
    dfs(a, n, m, i, j + 1);
    dfs(a, n, m, i, j - 1);
}

int main()
{
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    int m;
    if (scanf("%d", &m) != 1) {
        return 1;
    }
    noda** a = malloc(n * sizeof(noda*));
    for (int i = 0; i < n; i++) {
        a[i] = malloc(m * sizeof(noda));
        for (int j = 0; j < m; j++) {
            if (scanf("%d", &a[i][j].val) != 1) {
                return 1;
            }
            a[i][j].flg = 0;
        }
    }
    int ans = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (a[i][j].flg == 0 && a[i][j].val == 1) {
                dfs(a, n, m, i, j);
                ans++;
            }
        }
    }
    printf("%d\n", ans);
    for (int i = 0; i < n; i++) {
        free(a[i]);
    }
    free(a);
    return 0;
}