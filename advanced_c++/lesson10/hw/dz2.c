#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int x, y;
} point;

typedef struct {
    int u, v;
    unsigned int weight;
} edge;

void swap(edge* a, edge* b)
{
    edge t = *a;
    *a = *b;
    *b = t;
}

void quicksort(edge* e, int l, int r)
{
    if (l >= r)
        return;
    unsigned int pivot = e[(l + r) / 2].weight;
    int i = l, j = r;
    while (i <= j) {
        while (e[i].weight < pivot)
            i++;
        while (e[j].weight > pivot)
            j--;
        if (i <= j) {
            swap(&e[i], &e[j]);
            i++;
            j--;
        }
    }
    quicksort(e, l, j);
    quicksort(e, i, r);
}

int find(int* parent, int x)
{
    while (parent[x] != x)
        x = parent[x];
    return x;
}

void unite(int* parent, int* rank, int a, int b)
{
    if (rank[a] < rank[b])
        parent[a] = b;
    else if (rank[a] > rank[b])
        parent[b] = a;
    else {
        parent[b] = a;
        rank[a]++;
    }
}

int main()
{
    int n;
    if (scanf("%d", &n) != 1)
        return 1;

    point* p = malloc(n * sizeof(point));
    for (int i = 0; i < n; i++)
        if (scanf("%d %d", &p[i].x, &p[i].y) != 2)
            return 1;

    int m = n * (n - 1) / 2;
    edge* e = malloc(m * sizeof(edge));

    int idx = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            e[idx].u = i;
            e[idx].v = j;
            e[idx].weight = abs(p[i].x - p[j].x) + abs(p[i].y - p[j].y);
            idx++;
        }
    }

    quicksort(e, 0, m - 1);

    int* parent = malloc(n * sizeof(int));
    int* rank = calloc(n, sizeof(int));
    for (int i = 0; i < n; i++)
        parent[i] = i;

    unsigned long long sum = 0;
    int edges_used = 0;

    for (int i = 0; i < m && edges_used < n - 1; i++) {
        int a = find(parent, e[i].u);
        int b = find(parent, e[i].v);
        if (a != b) {
            unite(parent, rank, a, b);
            sum += e[i].weight;
            edges_used++;
        }
    }

    printf("%llu\n", sum);

    free(p);
    free(e);
    free(parent);
    free(rank);

    return 0;
}