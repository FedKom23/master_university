int* cool_int_arr_dup(const int* arr, unsigned long long size, void* (*malloc_func)(unsigned long long num))
{
    int* new_arr = malloc_func(size * sizeof(int));
    for (unsigned long long i = 0; i < size; i++) {
        new_arr[i] = arr[i];
    }
    return new_arr;
}