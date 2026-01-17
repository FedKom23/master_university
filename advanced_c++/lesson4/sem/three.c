#include <stdio.h>
#include <stdlib.h>

void swap(int* arr, int n)
{
    int temp = n / 2;
    for (int i = 0; i <= (temp - 1); i++) {
        int tek = arr[i];
        arr[i] = arr[n - i - 1];
        arr[n - i - 1] = tek;
    }
}

void plus_m(int* arr, int n, int m)
{
    int shift = m % n;
    if (shift == 0)
        return;

    int temp[shift];

    for (int i = 0; i < shift; i++) {
        temp[i] = arr[n - shift + i];
    }

    for (int i = n - 1; i >= shift; i--) {
        arr[i] = arr[i - shift];
    }

    for (int i = 0; i < shift; i++) {
        arr[i] = temp[i];
    }
}

int main()
{
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) {
        return 1;
    }
    int arr[n];
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &arr[i]) != 1) {
            return 1;
        }
    }
    swap(arr, n);
    plus_m(arr, n, m);
    swap(arr, n);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
}