void* cool_memset(void* str, int c, unsigned long long n)
{
    unsigned long long i = 0;
    while (i < n) {
        ((char*)str)[i] = c;
        i++;
    };
    return str;
}