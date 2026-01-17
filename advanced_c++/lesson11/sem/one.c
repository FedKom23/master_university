#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct
{
    double x, y;
} points;

double lagrange(points* arr, int n, double x)
{
    double res = 0;
    for (int i = 0; i < n; i++) {
        double temp = arr[i].y;
        for (int j = 0; j < n; j++) {
            if (i != j) {
                temp *= (x - arr[j].x) / (arr[i].x - arr[j].x);
            }
        }
        res += temp;
    }
    return res;
}

int main()
{
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    points* arr = malloc(n * sizeof(points));
    for (int i = 0; i < n; i++) {
        if (scanf("%lf %lf", &arr[i].x, &arr[i].y) != 2) {
            return 1;
        }
    }
    int m;
    if (scanf("%d", &m) != 1) {
        return 1;
    }
    for (int i = 0; i < m; i++) {
        double x;
        if (scanf("%lf", &x) != 1) {
            return 1;
        }
        printf("%.3f\n", lagrange(arr, n, x));
    }

    return 0;
}