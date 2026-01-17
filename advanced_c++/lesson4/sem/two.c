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

int main()
{
    int n;
    if (scanf("%d", &n) != 1) {
        return 1;
    }
    int arr[n];
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &arr[i]) != 1) {
            return 1;
        }
    }
    swap(arr, n);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
}