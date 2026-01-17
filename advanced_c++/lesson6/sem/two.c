void* cool_memmove(void* dest, const void* src, unsigned long long bytes)
{
    if (dest < src) {
        for (unsigned long long i = 0; i < bytes; i++) {
            ((char*)dest)[i] = ((char*)src)[i];
        }
    } else {
        for (unsigned long long i = bytes; i > 0; i--) {
            ((char*)dest)[i - 1] = ((char*)src)[i - 1];
        }
    }
    return dest;
}