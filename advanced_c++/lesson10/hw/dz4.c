#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

int bfs(int** a, int n, int m, int x, int y)
{
    int** dist = malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        dist[i] = malloc(m * sizeof(int));
        for (int j = 0; j < m; j++)
            dist[i][j] = -1;
    }

    int max = n * m;
    int* x_2 = malloc(max * sizeof(int));
    int* y_2 = malloc(max * sizeof(int));
    int head = 0, tail = 0;

    dist[x][y] = 0;
    x_2[tail] = x;
    y_2[tail] = y;
    tail++;

    int dx[4] = { -1, 1, 0, 0 };
    int dy[4] = { 0, 0, -1, 1 };

    while (head < tail) {
        int x = x_2[head];
        int y = y_2[head];
        head++;

        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d];
            int ny = y + dy[d];

            if (nx < 0 || nx >= n || ny < 0 || ny >= m)
                continue;
            if (a[nx][ny] == 1)
                continue;
            if (dist[nx][ny] != -1)
                continue;

            dist[nx][ny] = dist[x][y] + 1;
            x_2[tail] = nx;
            y_2[tail] = ny;
            tail++;
        }
    }

    int best = INT_MAX;

    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) {
            int border = (i == 0 || i == n - 1 || j == 0 || j == m - 1);
            if (!border)
                continue;
            if (a[i][j] == 1)
                continue;
            if (dist[i][j] == -1)
                continue;
            if (i == x && j == y)
                continue;
            if (dist[i][j] < best)
                best = dist[i][j];
        }

    for (int i = 0; i < n; i++)
        free(dist[i]);
    free(dist);
    free(x_2);
    free(y_2);

    return (best == INT_MAX ? -1 : best);
}

int main()
{
    int n, m, x, y;
    if (scanf("%d %d %d %d", &n, &m, &x, &y) != 4)
        return 1;

    int** a = malloc(n * sizeof(int*));
    for (int i = 0; i < n; i++) {
        a[i] = malloc(m * sizeof(int));
        for (int j = 0; j < m; j++)
            if (scanf("%d", &a[i][j]) != 1)
                return 1;
    }

    int ans = bfs(a, n, m, x, y);
    printf("%d\n", ans);

    for (int i = 0; i < n; i++)
        free(a[i]);
    free(a);

    return 0;
}