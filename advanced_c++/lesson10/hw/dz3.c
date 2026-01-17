#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#define INF (INT_MAX / 2)

int dejikstra_from_k(int** arr, int* dist, int n, int k)
{
    int* visited = calloc(n, sizeof(int));

    for (int i = 0; i < n; i++)
        dist[i] = INF;

    dist[k - 1] = 0;

    for (int iter = 0; iter < n; iter++) {
        int v = -1;
        for (int i = 0; i < n; i++)
            if (!visited[i] && (v == -1 || dist[i] < dist[v]))
                v = i;

        if (v == -1)
            break;

        visited[v] = 1;

        for (int i = 0; i < n; i++) {
            if (arr[v][i] < INF) {
                int new_dist = dist[v] + arr[v][i];
                if (new_dist < dist[i])
                    dist[i] = new_dist;
            }
        }
    }

    free(visited);
    return 0;
}

int main()
{
    int n, k, m;
    if (scanf("%d %d %d", &n, &k, &m) != 3)
        return 1;

    int** arr = malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        arr[i] = malloc(n * sizeof(int));
        for (int j = 0; j < n; j++)
            arr[i][j] = INF;
    }

    for (int i = 0; i < m; i++) {
        int x, y, w;
        if (scanf("%d %d %d", &x, &y, &w) != 3)
            return 1;
        arr[x - 1][y - 1] = w;
    }

    int* dist = malloc(n * sizeof(int));
    dejikstra_from_k(arr, dist, n, k);

    int maxi = 0;
    for (int i = 0; i < n; i++) {
        if (dist[i] == INF) {
            printf("-1\n");
            goto end;
        }
        if (dist[i] > maxi)
            maxi = dist[i];
    }

    printf("%d\n", maxi);

end:
    free(dist);
    for (int i = 0; i < n; i++)
        free(arr[i]);
    free(arr);
    return 0;
}