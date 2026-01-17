#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int* v;
    int size;
    int cap;
} vec;

void vec_init(vec* t)
{
    t->size = 0;
    t->cap = 2;
    t->v = malloc(sizeof(int) * t->cap);
}

void vec_push(vec* t, int x)
{
    if (t->size == t->cap) {
        t->cap *= 2;
        t->v = realloc(t->v, sizeof(int) * t->cap);
    }
    t->v[t->size++] = x;
}

int bfs(vec* g, int n, int start, int end)
{
    int* used = calloc(n, sizeof(int));
    int* queue = malloc(sizeof(int) * n);
    int head = 0, tail = 0;

    used[start] = 1;
    queue[tail++] = start;

    while (head < tail) {
        int v = queue[head++];
        if (v == end) {
            free(used);
            free(queue);
            return 1;
        }
        for (int i = 0; i < g[v].size; i++) {
            int to = g[v].v[i];
            if (!used[to]) {
                used[to] = 1;
                queue[tail++] = to;
            }
        }
    }

    free(used);
    free(queue);
    return 0;
}

int main()
{
    int n, m, start, end;
    if (scanf("%d %d %d %d", &n, &m, &start, &end) != 4) {
        return 1;
    }

    vec* g = malloc(sizeof(vec) * n);
    for (int i = 0; i < n; i++)
        vec_init(&g[i]);

    for (int i = 0; i < m; i++) {
        int x, y;
        if (scanf("%d %d", &x, &y) != 2) {
            return 1;
        }
        vec_push(&g[x], y);
        vec_push(&g[y], x);
    }

    int ans = bfs(g, n, start, end);
    printf("%s", ans ? "true" : "false");
    return 0;
}